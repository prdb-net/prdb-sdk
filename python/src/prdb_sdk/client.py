"""Client construction for the prdb Public API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from urllib.parse import urlparse

from kiota_abstractions.authentication.anonymous_authentication_provider import (
    AnonymousAuthenticationProvider,
)
from kiota_abstractions.authentication.api_key_authentication_provider import (
    ApiKeyAuthenticationProvider,
    KeyLocation,
)
from kiota_bundle.default_request_adapter import DefaultRequestAdapter

from .generated.prdb_client import PrdbClient

if TYPE_CHECKING:
    import httpx

#: Header the API expects the key in.
API_KEY_HEADER = "X-Api-Key"

#: Production base URL, also the default baked into the generated client.
DEFAULT_BASE_URL = "https://api.prdb.net"


def create_client(
    api_key: str,
    *,
    base_url: str = DEFAULT_BASE_URL,
    http_client: Optional["httpx.AsyncClient"] = None,
) -> PrdbClient:
    """Create a client authenticated with an API key.

    Args:
        api_key: The API key, sent in the ``X-Api-Key`` header on every request.
        base_url: Override the API root. Useful for a staging deployment.
        http_client: Supply your own ``httpx.AsyncClient`` to control timeouts,
            proxies or retries. One is created for you when omitted.

    Returns:
        A client whose request builders mirror the API's URL structure, so
        ``GET /videos/{id}`` is ``client.videos.by_id(video_id).get()``.

    Raises:
        ValueError: If ``api_key`` is empty or ``base_url`` is not absolute.
    """
    if not api_key:
        raise ValueError("api_key must not be empty")

    host = urlparse(base_url).hostname
    if not host:
        raise ValueError(f"base_url must be an absolute URL, got {base_url!r}")

    # Restricting the key to the API host means a redirect to somewhere else
    # cannot carry the credential off-site.
    auth_provider = ApiKeyAuthenticationProvider(
        key_location=KeyLocation.Header,
        api_key=api_key,
        parameter_name=API_KEY_HEADER,
        allowed_hosts=[host],
    )

    request_adapter = DefaultRequestAdapter(
        authentication_provider=auth_provider,
        http_client=http_client,
    )
    request_adapter.base_url = base_url

    return PrdbClient(request_adapter)


def create_anonymous_client(
    *,
    base_url: str = DEFAULT_BASE_URL,
    http_client: Optional["httpx.AsyncClient"] = None,
) -> PrdbClient:
    """Create a client without credentials.

    Only ``GET /health`` is reachable this way; every other endpoint answers
    401. Provided so health probes do not need an API key.
    """
    request_adapter = DefaultRequestAdapter(
        authentication_provider=AnonymousAuthenticationProvider(),
        http_client=http_client,
    )
    request_adapter.base_url = base_url

    return PrdbClient(request_adapter)
