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

from prdb_sdk import (
    API_KEY_HEADER,
    DEFAULT_BASE_URL,
    CrossOriginRedirectError,
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
