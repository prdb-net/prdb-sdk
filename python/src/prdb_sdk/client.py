"""Client construction for the prdb Public API."""

from __future__ import annotations

import copy
from dataclasses import dataclass
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
from kiota_abstractions.request_option import RequestOption
from kiota_bundle.default_request_adapter import DefaultRequestAdapter
from kiota_http.kiota_client_factory import KiotaClientFactory
from kiota_http.middleware import BaseMiddleware, RetryHandler
from kiota_http.middleware.options import RedirectHandlerOption, RetryHandlerOption

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


class ResponseStatusOption(RequestOption):
    """Per-request option reporting which status code the API answered with.

    A generated method returns the deserialised body and nothing else, which is
    a problem when an operation answers with more than one success status.
    ``POST /downloaded-from-indexers`` is the one that does: ``201`` when it
    created the entry, ``200`` when an equivalent one already existed and is
    being returned unchanged. The bodies are the same shape, so the status is
    the only thing that tells the two apart.

    Kiota's own way of reaching the response, ``NativeResponseHandler``,
    suppresses deserialisation while it does so -- you get the raw response or
    the typed model, never both. This option is the other half: the call
    returns its model as usual, and the status is here afterwards::

        from kiota_abstractions.base_request_configuration import RequestConfiguration

        status = ResponseStatusOption()
        entry = await client.downloaded_from_indexers.post(
            body, request_configuration=RequestConfiguration(options=[status])
        )
        if status.status_code == 200:
            ...  # an equivalent entry already existed and was returned unchanged

    Use one instance per call: it is written when the response arrives, so
    sharing one across concurrent calls means whichever finishes last wins.

    The status recorded is the one of the response the result was built from --
    after any redirect the SDK followed, and after the last retry. A call that
    raises records too, so the ``status_code`` is set for a caller that catches
    an :class:`APIError`.

    Attributes:
        status_code: The status the API answered with, or ``None`` until the
            call has produced a response -- and for good if none was reached at
            all, as with a connection failure, a timeout, or a redirect refused
            by :class:`CrossOriginRedirectError`.
    """

    #: Key this option travels under, unique to the SDK.
    RESPONSE_STATUS_KEY = "prdb.response_status"

    def __init__(self) -> None:
        self.status_code: Optional[int] = None

    @staticmethod
    def get_key() -> str:
        return ResponseStatusOption.RESPONSE_STATUS_KEY


class _ResponseStatusHandler(BaseMiddleware):
    """Records the response status into the option a request carries.

    Sits at the outer end of the SDK's pipeline, above the retry and redirect
    handlers, so what it records is the response the caller's result is built
    from rather than an attempt on the way there.
    """

    async def send(
        self, request: httpx.Request, transport: httpx.AsyncBaseTransport
    ) -> httpx.Response:
        # Read before sending: the innermost middleware strips the options off
        # the request on its way to the transport, so afterwards there is
        # nothing left to look them up in.
        options = getattr(request, "options", None)
        option = options.get(ResponseStatusOption.get_key()) if options else None

        response = await super().send(request, transport)

        if option is not None:
            option.status_code = response.status_code

        return response


@dataclass(frozen=True)
class RetryOptions:
    """How the SDK retries a request the API refused with 429, 503 or 504.

    Retry belongs to whoever owns the calling application's resilience story.
    An application that already retries prdb calls itself should pass
    :meth:`disabled`, otherwise the two policies multiply: one logical call
    becomes up to ``n×m`` requests against an API that rate limits, and the
    outer circuit breaker never sees a stable failure to open on.

    The built-in policy retries idempotent and non-idempotent requests alike,
    so an application that must not repeat a write should own the retry itself.

    Attributes:
        max_retries: How often a refused request is retried. At most 10. Zero
            leaves the retry handler out of the pipeline entirely.
        delay: Seconds to wait before a retry, unless the response carries a
            ``Retry-After`` header, which always wins. At most 180.
    """

    max_retries: int = RetryHandlerOption.DEFAULT_MAX_RETRIES
    delay: float = RetryHandlerOption.DEFAULT_DELAY

    def __post_init__(self) -> None:
        if not 0 <= self.max_retries <= RetryHandlerOption.MAX_MAX_RETRIES:
            raise ValueError(
                f"max_retries must be between 0 and "
                f"{RetryHandlerOption.MAX_MAX_RETRIES}, got {self.max_retries}"
            )
        if not 0 <= self.delay <= RetryHandlerOption.MAX_DELAY:
            raise ValueError(
                f"delay must be between 0 and {RetryHandlerOption.MAX_DELAY} "
                f"seconds, got {self.delay}"
            )

    @classmethod
    def disabled(cls) -> "RetryOptions":
        """No retrying at all: a 429 or 503 reaches the caller as the API sent it."""
        return cls(max_retries=0)


def create_client(
    api_key: str,
    *,
    base_url: str = DEFAULT_BASE_URL,
    http_client: Optional[httpx.AsyncClient] = None,
    retry: Optional[RetryOptions] = None,
) -> PrdbClient:
    """Create a client authenticated with an API key.

    Args:
        api_key: The API key, sent in the ``X-Api-Key`` header on every request.
        base_url: Override the API root. Useful for a staging deployment. Must
            use ``https``, so the key never travels in cleartext.
        http_client: Supply your own ``httpx.AsyncClient`` to control timeouts,
            proxies or connection limits. One is created for you when omitted.
            The SDK does not modify the client you pass: it copies it and
            installs its middleware on the copy, so your client keeps behaving
            the way you configured it. The copy shares your transport, so your
            connection pool is the one used -- and closing your client closes
            the connections this one sends through.
        retry: How the SDK retries a refused request. Defaults to Kiota's
            policy — three attempts, honouring ``Retry-After``. Pass
            :meth:`RetryOptions.disabled` if your application already retries
            prdb calls itself.

    Returns:
        A client whose request builders mirror the API's URL structure, so
        ``GET /videos/{id}`` is ``client.videos.by_id(video_id).get()``.

    Raises:
        ValueError: If ``api_key`` is empty, or ``base_url`` is not an
            absolute ``https`` URL.
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

    return _build_client(auth_provider, base_url, http_client, retry)


def create_anonymous_client(
    *,
    base_url: str = DEFAULT_BASE_URL,
    http_client: Optional[httpx.AsyncClient] = None,
    retry: Optional[RetryOptions] = None,
) -> PrdbClient:
    """Create a client without credentials.

    Only ``GET /health`` is reachable this way; every other endpoint answers
    401. Provided so health probes do not need an API key.

    With no key to protect, ``base_url`` may use plain ``http``.

    Raises:
        ValueError: If ``base_url`` is not an absolute URL.
    """
    _resolve_host(base_url, require_https=False)

    return _build_client(
        AnonymousAuthenticationProvider(), base_url, http_client, retry
    )


def _build_client(
    auth_provider: AuthenticationProvider,
    base_url: str,
    http_client: Optional[httpx.AsyncClient],
    retry: Optional[RetryOptions],
) -> PrdbClient:
    request_adapter = DefaultRequestAdapter(
        authentication_provider=auth_provider,
        http_client=_build_http_client(http_client, retry),
    )
    request_adapter.base_url = base_url

    return PrdbClient(request_adapter)


def _build_http_client(
    http_client: Optional[httpx.AsyncClient],
    retry: Optional[RetryOptions],
) -> httpx.AsyncClient:
    """Build the client the request adapter sends through.

    A client handed straight to the request adapter carries no middleware at
    all, which loses redirect handling, retries and Kiota's parameter name
    decoding. Routing both paths through this function keeps a caller-supplied
    client behaving like the one we build ourselves.
    """
    options: dict[str, object] = {
        RedirectHandlerOption.get_key(): RedirectHandlerOption(
            scrub_sensitive_headers=_refuse_cross_origin_redirect,
        ),
    }

    if retry is not None and retry.max_retries > 0:
        options[RetryHandlerOption.get_key()] = RetryHandlerOption(
            delay=retry.delay,
            max_retries=retry.max_retries,
        )

    middleware = KiotaClientFactory.get_default_middleware(options)  # type: ignore[arg-type]

    if retry is not None and retry.max_retries == 0:
        # Removed rather than configured with zero attempts, so "no retrying"
        # means the handler is not in the pipeline at all and cannot be
        # re-enabled by a per-request option.
        middleware = [
            handler for handler in middleware if not isinstance(handler, RetryHandler)
        ]

    # First in the list is outermost, which puts it above the retry and
    # redirect handlers: the status it records is the one the caller's result
    # was built from, not that of an attempt on the way there.
    middleware = [_ResponseStatusHandler(), *middleware]

    if http_client is None:
        return KiotaClientFactory.create_with_custom_middleware(middleware=middleware)

    return _load_middleware_onto_a_copy(http_client, middleware)


def _load_middleware_onto_a_copy(
    http_client: httpx.AsyncClient,
    middleware: list[BaseMiddleware],
) -> httpx.AsyncClient:
    """Install the pipeline on a copy of the caller's client, not on theirs.

    Kiota loads middleware by replacing a client's transport, in place. Doing
    that to a client the SDK was merely lent reconfigures an object the caller
    still uses: every other request their application makes through it would
    run prdb's middleware, including the cross-origin rule below, which would
    refuse redirects that have nothing to do with prdb. Each call wraps the
    transport again, too, so a client shared across several SDK clients would
    accumulate a pipeline per client built from it.

    So the pipeline goes onto a shallow copy. It keeps the caller's timeouts,
    headers, auth and event hooks, and it shares their transport, so their
    connection pool, TLS settings and proxies are the ones actually used --
    only the transport reference on the copy is replaced. Their client object
    is left exactly as it was.

    The copy shares the caller's transport, so it also shares its lifetime:
    closing their client closes the connections this one sends through.
    """
    ours: httpx.AsyncClient = copy.copy(http_client)

    # Ours to decide, now that the client is ours. httpx follows redirects above
    # the transport, which is where Kiota's middleware lives, so a redirect httpx
    # followed itself is one the rule below would never see.
    ours.follow_redirects = False

    return KiotaClientFactory.create_with_custom_middleware(
        middleware=middleware,
        client=ours,
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
