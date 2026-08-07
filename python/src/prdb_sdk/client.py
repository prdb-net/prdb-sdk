"""Client construction for the prdb Public API."""

from __future__ import annotations

from typing import Optional
from urllib.parse import urlparse

import httpx
from kiota_abstractions.authentication.anonymous_authentication_provider import (
    AnonymousAuthenticationProvider,
)
from kiota_abstractions.authentication.authentication_provider import (
    AuthenticationProvider,
)
from kiota_abstractions.authentication.api_key_authentication_provider import (
    ApiKeyAuthenticationProvider,
    KeyLocation,
)
from kiota_bundle.default_request_adapter import DefaultRequestAdapter
from kiota_http.kiota_client_factory import KiotaClientFactory
from kiota_http.middleware.options import RedirectHandlerOption

from .generated.prdb_client import PrdbClient

#: Header the API expects the key in.
API_KEY_HEADER = "X-Api-Key"

#: Production base URL, also the default baked into the generated client.
DEFAULT_BASE_URL = "https://api.prdb.net"


class CrossOriginRedirectError(RuntimeError):
    """Raised when the API redirects to a different origin.

    Following such a redirect would hand the API key to whoever answers at the
    new location, so the SDK refuses it. Redirects that stay on the same origin
    are followed normally.
    """


def create_client(
    api_key: str,
    *,
    base_url: str = DEFAULT_BASE_URL,
    http_client: Optional[httpx.AsyncClient] = None,
) -> PrdbClient:
    """Create a client authenticated with an API key.

    Args:
        api_key: The API key, sent in the ``X-Api-Key`` header on every request.
        base_url: Override the API root. Useful for a staging deployment. Must
            use ``https``, so the key never travels in cleartext.
        http_client: Supply your own ``httpx.AsyncClient`` to control timeouts,
            proxies or connection limits. One is created for you when omitted.
            Either way the SDK's middleware is installed on it, which modifies
            the client you pass in place.

    Returns:
        A client whose request builders mirror the API's URL structure, so
        ``GET /videos/{id}`` is ``client.videos.by_id(video_id).get()``.

    Raises:
        ValueError: If ``api_key`` is empty, or ``base_url`` is not an absolute
            ``https`` URL.
    """
    if not api_key:
        raise ValueError("api_key must not be empty")

    host = _resolve_host(base_url, require_https=True)

    auth_provider = ApiKeyAuthenticationProvider(
        key_location=KeyLocation.Header,
        api_key=api_key,
        parameter_name=API_KEY_HEADER,
        allowed_hosts=[host],
    )

    return _build_client(auth_provider, base_url, http_client)


def create_anonymous_client(
    *,
    base_url: str = DEFAULT_BASE_URL,
    http_client: Optional[httpx.AsyncClient] = None,
) -> PrdbClient:
    """Create a client without credentials.

    Only ``GET /health`` is reachable this way; every other endpoint answers
    401. Provided so health probes do not need an API key.

    With no key to protect, ``base_url`` may use plain ``http``.

    Raises:
        ValueError: If ``base_url`` is not an absolute URL.
    """
    _resolve_host(base_url, require_https=False)

    return _build_client(AnonymousAuthenticationProvider(), base_url, http_client)


def _build_client(
    auth_provider: AuthenticationProvider,
    base_url: str,
    http_client: Optional[httpx.AsyncClient],
) -> PrdbClient:
    request_adapter = DefaultRequestAdapter(
        authentication_provider=auth_provider,
        http_client=_build_http_client(http_client),
    )
    request_adapter.base_url = base_url

    return PrdbClient(request_adapter)


def _build_http_client(http_client: Optional[httpx.AsyncClient]) -> httpx.AsyncClient:
    """Load the SDK's middleware pipeline onto a client, creating one if needed.

    A client handed straight to the request adapter carries no middleware at
    all, which loses redirect handling, retries and Kiota's parameter name
    decoding. Routing both paths through this function keeps a caller-supplied
    client behaving like the one we build ourselves.
    """
    redirect_options = RedirectHandlerOption(
        scrub_sensitive_headers=_refuse_cross_origin_redirect,
    )

    return KiotaClientFactory.create_with_default_middleware(
        client=http_client,
        options={RedirectHandlerOption.get_key(): redirect_options},
    )


def _refuse_cross_origin_redirect(
    new_request: httpx.Request,
    original_url: httpx.URL,
) -> None:
    """Refuse a redirect that leaves the origin the request started on.

    This runs in place of Kiota's default header scrubbing, which drops only
    ``Authorization`` and ``Cookie``. The prdb API key travels in a custom
    header, and no layer below strips it: neither Kiota's redirect handler nor
    httpx's own touch anything but ``Authorization``. A redirect off the API
    host would therefore hand the credential to whoever answered.

    The header is removed before raising as well, so the key is gone even if a
    caller catches the error and reuses the request.
    """
    new_url = new_request.url
    same_origin = (
        original_url.scheme == new_url.scheme
        and original_url.host == new_url.host
        and original_url.port == new_url.port
    )
    if same_origin:
        return

    new_request.headers.pop(API_KEY_HEADER, None)
    new_request.headers.pop("Authorization", None)
    new_request.headers.pop("Cookie", None)

    raise CrossOriginRedirectError(
        f"refusing to follow a redirect from {original_url.host} to "
        f"{new_url.host}; the api key is bound to the first host"
    )


def _resolve_host(base_url: str, *, require_https: bool) -> str:
    parsed = urlparse(base_url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError(f"base_url must be an absolute URL, got {base_url!r}")

    if require_https and parsed.scheme != "https":
        raise ValueError(
            f"base_url must use https so the api key is not sent in cleartext, "
            f"got {base_url!r}"
        )

    return parsed.hostname
