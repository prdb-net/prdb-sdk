"""Tests for the hand-written client wrapper.

The generated code is not tested here; it is Kiota's output and is covered by
the drift check in CI. What is worth testing is the wrapper's own promises:
where the API key goes, and where it must not go.

Requests are served by an ``httpx.MockTransport`` rather than a real socket, so
no TLS certificates are needed and every test stays in-process.
"""

from __future__ import annotations

import httpx
import pytest
from kiota_abstractions.api_error import APIError
from kiota_abstractions.base_request_configuration import RequestConfiguration

from prdb_sdk import (
    API_KEY_HEADER,
    DEFAULT_BASE_URL,
    CrossOriginRedirectError,
    RateLimitOption,
    RateLimitWindow,
    ResponseStatusOption,
    RetryOptions,
    create_anonymous_client,
    create_client,
)
API_ORIGIN = "https://api.example.test"
OTHER_ORIGIN = "https://elsewhere.example.test"

HEALTH_BODY = {"status": "healthy", "timestamp": "2026-08-07T12:00:00Z"}


class Recorder:
    """Records every request a mock transport sees."""

    def __init__(self) -> None:
        self.requests: list[httpx.Request] = []

    def keys_sent_to(self, host: str) -> list[str]:
        return [
            request.headers[API_KEY_HEADER]
            for request in self.requests
            if request.url.host == host and API_KEY_HEADER in request.headers
        ]

    def client(self, handler, *, follow_redirects: bool = False) -> httpx.AsyncClient:
        def record(request: httpx.Request) -> httpx.Response:
            self.requests.append(request)
            return handler(request)

        return httpx.AsyncClient(
            transport=httpx.MockTransport(record),
            follow_redirects=follow_redirects,
        )


def health(_: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=HEALTH_BODY)


@pytest.fixture
def recorder() -> Recorder:
    return Recorder()


async def test_sends_the_api_key_header(recorder: Recorder) -> None:
    client = create_client(
        "secret-key", base_url=API_ORIGIN, http_client=recorder.client(health)
    )

    await client.health.get()

    assert recorder.requests[0].headers[API_KEY_HEADER] == "secret-key"


async def test_anonymous_client_sends_no_api_key(recorder: Recorder) -> None:
    client = create_anonymous_client(
        base_url=API_ORIGIN, http_client=recorder.client(health)
    )

    await client.health.get()

    assert API_KEY_HEADER not in recorder.requests[0].headers


async def test_cross_origin_redirect_does_not_leak_the_api_key(
    recorder: Recorder,
) -> None:
    """The guarantee the README makes, pinned down.

    Neither httpx nor Kiota strips a custom header across origins — both drop
    only ``Authorization`` — so without the wrapper's own rule the key would
    travel to whoever answers at the redirect target. ``follow_redirects=True``
    is set deliberately: that is the configuration in which it used to leak.
    """

    def redirect_away(request: httpx.Request) -> httpx.Response:
        if request.url.host == "api.example.test":
            return httpx.Response(307, headers={"Location": f"{OTHER_ORIGIN}/health"})
        return httpx.Response(200, json=HEALTH_BODY)

    client = create_client(
        "secret-key",
        base_url=API_ORIGIN,
        http_client=recorder.client(redirect_away, follow_redirects=True),
    )

    with pytest.raises(CrossOriginRedirectError):
        await client.health.get()

    assert recorder.keys_sent_to("elsewhere.example.test") == []


async def test_same_origin_redirect_is_followed(recorder: Recorder) -> None:
    """Refusing cross-origin redirects must not refuse ordinary ones."""

    def redirect_once(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/health":
            return httpx.Response(307, headers={"Location": f"{API_ORIGIN}/healthz"})
        return httpx.Response(200, json=HEALTH_BODY)

    client = create_client(
        "secret-key",
        base_url=API_ORIGIN,
        http_client=recorder.client(redirect_once),
    )

    result = await client.health.get()

    assert result is not None
    assert [request.url.path for request in recorder.requests] == [
        "/health",
        "/healthz",
    ]
    assert recorder.keys_sent_to("api.example.test") == ["secret-key", "secret-key"]


async def test_leaves_the_supplied_client_alone(recorder: Recorder) -> None:
    """The client belongs to the caller; the SDK only borrows it.

    Kiota installs its middleware by replacing a client's transport in place.
    Were the SDK to let it do that to a client it was lent, every unrelated
    request the application made through that client would run prdb's
    middleware -- including the cross-origin rule, which would refuse redirects
    that have nothing to do with prdb.
    """

    def redirect_away(request: httpx.Request) -> httpx.Response:
        if request.url.host == "api.example.test":
            return httpx.Response(307, headers={"Location": f"{OTHER_ORIGIN}/health"})
        return httpx.Response(200, json=HEALTH_BODY)

    caller_client = recorder.client(redirect_away)

    # Twice: installing in place wraps the transport again on every call, so a
    # client reused across several SDK clients would accumulate pipelines.
    create_client("secret-key", base_url=API_ORIGIN, http_client=caller_client)
    create_client("secret-key", base_url=API_ORIGIN, http_client=caller_client)

    # Their own request, through their own client: the SDK's rule must not be
    # in this path, so the redirect comes back as an ordinary 307.
    response = await caller_client.get(f"{API_ORIGIN}/health")

    assert response.status_code == 307


async def test_uses_the_transport_of_the_supplied_client(recorder: Recorder) -> None:
    """The copy shares the caller's transport, so their pool is the one used."""
    client = create_client(
        "secret-key", base_url=API_ORIGIN, http_client=recorder.client(health)
    )

    await client.health.get()

    assert len(recorder.requests) == 1


async def test_retries_a_refused_request_by_default(recorder: Recorder) -> None:
    """Kiota's retry handler is in the default pipeline, so this is the status quo."""

    def refuse_once(request: httpx.Request) -> httpx.Response:
        if len(recorder.requests) == 1:
            return httpx.Response(503)
        return httpx.Response(200, json=HEALTH_BODY)

    client = create_client(
        "secret-key",
        base_url=API_ORIGIN,
        http_client=recorder.client(refuse_once),
        retry=RetryOptions(max_retries=1, delay=0),
    )

    result = await client.health.get()

    assert result is not None
    assert len(recorder.requests) == 2


async def test_does_not_retry_when_retrying_is_disabled(recorder: Recorder) -> None:
    """The opt-out an application with its own retry policy needs.

    Without it the SDK's retry sits outside the application's and the two
    multiply: one logical call becomes several requests against an API that
    rate limits, and the outer circuit breaker never sees a stable failure.
    """
    client = create_client(
        "secret-key",
        base_url=API_ORIGIN,
        http_client=recorder.client(lambda _: httpx.Response(503)),
        retry=RetryOptions.disabled(),
    )

    with pytest.raises(APIError):
        await client.health.get()

    assert len(recorder.requests) == 1


def get_health(client, status: ResponseStatusOption):
    """GET /health, reporting the status it answered with."""
    return client.health.get(
        request_configuration=RequestConfiguration(options=[status]),
    )


async def test_reports_the_success_status_alongside_the_typed_result(
    recorder: Recorder,
) -> None:
    """Keep the typed result while reporting the response status."""
    client = create_client(
        "secret-key",
        base_url=API_ORIGIN,
        http_client=recorder.client(lambda _: httpx.Response(200, json=HEALTH_BODY)),
    )
    status = ResponseStatusOption()

    health = await get_health(client, status)

    assert health is not None
    assert health.status == "healthy"
    assert status.status_code == 200


async def test_reports_the_last_attempt_when_a_refusal_is_retried(
    recorder: Recorder,
) -> None:
    """The handler sits above the retry handler, so the attempt that succeeded wins."""

    def refuse_once(_: httpx.Request) -> httpx.Response:
        if len(recorder.requests) == 1:
            return httpx.Response(503)
        return httpx.Response(200, json=HEALTH_BODY)

    client = create_client(
        "secret-key",
        base_url=API_ORIGIN,
        http_client=recorder.client(refuse_once),
        retry=RetryOptions(max_retries=1, delay=0),
    )
    status = ResponseStatusOption()

    await get_health(client, status)

    assert len(recorder.requests) == 2
    assert status.status_code == 200


async def test_reports_the_status_when_the_api_refuses(recorder: Recorder) -> None:
    """A refusal records too, for a caller that catches the error."""
    client = create_client(
        "secret-key",
        base_url=API_ORIGIN,
        http_client=recorder.client(
            lambda _: httpx.Response(
                403, json={"title": "Forbidden", "status": 403, "detail": "no api plan"}
            )
        ),
        retry=RetryOptions.disabled(),
    )
    status = ResponseStatusOption()

    with pytest.raises(APIError):
        await get_health(client, status)

    assert status.status_code == 403


async def test_reports_no_status_when_no_response_was_reached(
    recorder: Recorder,
) -> None:
    """Nothing answered, so there is no status -- rather than an invented one."""

    def redirect_away(request: httpx.Request) -> httpx.Response:
        if request.url.host == "api.example.test":
            return httpx.Response(307, headers={"Location": f"{OTHER_ORIGIN}/health"})
        return httpx.Response(200, json=HEALTH_BODY)

    client = create_client(
        "secret-key", base_url=API_ORIGIN, http_client=recorder.client(redirect_away)
    )
    status = ResponseStatusOption()

    with pytest.raises(CrossOriginRedirectError):
        await client.health.get(
            request_configuration=RequestConfiguration(options=[status])
        )

    assert status.status_code is None


RATE_LIMIT_HEADERS = {
    "X-RateLimit-Limit-Hour": "1000",
    "X-RateLimit-Remaining-Hour": "993",
    "X-RateLimit-Reset-Hour": "2471",
    "X-RateLimit-Limit-Month": "50000",
    "X-RateLimit-Remaining-Month": "48120",
    "X-RateLimit-Reset-Month": "1904322",
}


def sites_page(recorder: Recorder, *, status_code: int = 200, headers=None, retry=None):
    """A client whose GET /sites answers with the given status and headers."""
    return create_client(
        "secret-key",
        base_url=API_ORIGIN,
        http_client=recorder.client(
            lambda _: httpx.Response(
                status_code, json=SITES_BODY, headers=headers or {}
            )
        ),
        retry=retry,
    )


SITES_BODY = {"items": [], "page": 1, "pageSize": 20, "totalCount": 7}


async def test_reports_both_rate_limit_windows_alongside_the_typed_result(
    recorder: Recorder,
) -> None:
    """The point of the option: pace off the response you already have.

    Kiota can surface the headers, but as raw multi-valued strings. This is the
    typed reading, and it arrives with the model rather than instead of it.
    """
    client = sites_page(recorder, headers=RATE_LIMIT_HEADERS)
    limits = RateLimitOption()

    page = await client.sites.get(
        request_configuration=RequestConfiguration(options=[limits])
    )

    assert page is not None
    assert page.total_count == 7

    assert limits.hour == RateLimitWindow(
        limit=1000, remaining=993, reset_in_seconds=2471
    )
    assert limits.month == RateLimitWindow(
        limit=50000, remaining=48120, reset_in_seconds=1904322
    )


async def test_reports_only_the_window_that_refused_a_request(
    recorder: Recorder,
) -> None:
    """A 429 carries only the window it came from, so one window alone is normal."""
    hourly_only = {
        name: value
        for name, value in RATE_LIMIT_HEADERS.items()
        if name.endswith("-Hour")
    }
    client = sites_page(
        recorder,
        status_code=429,
        headers={**hourly_only, "Retry-After": "2471"},
        retry=RetryOptions.disabled(),
    )
    limits = RateLimitOption()

    with pytest.raises(APIError):
        await client.sites.get(
            request_configuration=RequestConfiguration(options=[limits])
        )

    # A refusal is exactly when a caller wants the reading, so it records too.
    assert limits.hour == RateLimitWindow(
        limit=1000, remaining=993, reset_in_seconds=2471
    )
    assert limits.month is None


async def test_reports_no_rate_limit_for_an_unmetered_response(
    recorder: Recorder,
) -> None:
    """401, 403, 503 and GET /rate-limit carry no headers -- that is an answer."""
    client = sites_page(recorder)
    limits = RateLimitOption()

    await client.sites.get(
        request_configuration=RequestConfiguration(options=[limits])
    )

    assert limits.hour is None
    assert limits.month is None


async def test_a_malformed_rate_limit_header_does_not_fail_the_call(
    recorder: Recorder,
) -> None:
    """Metadata about a call that already worked must not be able to break it."""
    client = sites_page(
        recorder,
        headers={**RATE_LIMIT_HEADERS, "X-RateLimit-Remaining-Hour": "not-a-number"},
    )
    limits = RateLimitOption()

    page = await client.sites.get(
        request_configuration=RequestConfiguration(options=[limits])
    )

    assert page is not None
    assert limits.hour is None
    # The other window is independent, so it still reads.
    assert limits.month == RateLimitWindow(
        limit=50000, remaining=48120, reset_in_seconds=1904322
    )


ETAG = 'W/"abc123"'


def conditional(request: httpx.Request) -> httpx.Response:
    """GET /sites, answering 304 when the caller sends the validator back."""
    if request.headers.get("If-None-Match") == ETAG:
        return httpx.Response(304, headers={"ETag": ETAG})
    return httpx.Response(200, json=SITES_BODY, headers={"ETag": ETAG})


async def test_a_conditional_request_returns_none_rather_than_raising(
    recorder: Recorder,
) -> None:
    """A 304 is the request working, not failing.

    Kiota generates no handling for a declared 3xx in any language, so what each
    SDK does with one is its request adapter's fallback rather than anything
    generated. Python falls through to "no body, return None". Pinned here
    because C# does not -- it raises, and needs a handler in the pipeline to
    match the other three -- so a Kiota upgrade that moved Python the same way
    should fail the build rather than the caller.
    """
    client = create_client(
        "secret-key", base_url=API_ORIGIN, http_client=recorder.client(conditional)
    )
    status = ResponseStatusOption()
    configuration = RequestConfiguration(options=[status])
    configuration.headers.add("If-None-Match", ETAG)

    page = await client.sites.get(request_configuration=configuration)

    assert page is None
    # None alone cannot be told apart from an empty page; the status is what does.
    assert status.status_code == 304


@pytest.mark.parametrize(
    "kwargs",
    [{"max_retries": -1}, {"max_retries": 11}, {"delay": -1.0}, {"delay": 181.0}],
)
def test_rejects_retry_options_out_of_range(kwargs: dict[str, float]) -> None:
    with pytest.raises(ValueError):
        RetryOptions(**kwargs)  # type: ignore[arg-type]


def test_rejects_an_empty_api_key() -> None:
    with pytest.raises(ValueError):
        create_client("")


@pytest.mark.parametrize("base_url", ["api.prdb.net", "/videos", "not a url", ""])
def test_rejects_a_relative_base_url(base_url: str) -> None:
    with pytest.raises(ValueError):
        create_client("secret-key", base_url=base_url)


def test_rejects_a_plaintext_base_url() -> None:
    """An API key must not travel in cleartext.

    The Go SDK's Kiota provider refuses this outright; the Python one does not,
    so the wrapper enforces it to keep the four SDKs behaving alike. A staging
    deployment therefore has to terminate TLS.
    """
    with pytest.raises(ValueError, match="https"):
        create_client("secret-key", base_url="http://localhost:8080")


def test_anonymous_client_allows_plaintext() -> None:
    """With no credential to protect, plain HTTP is the caller's business."""
    assert create_anonymous_client(base_url="http://localhost:8080") is not None


def test_default_base_url_is_production() -> None:
    assert DEFAULT_BASE_URL.startswith("https://")
