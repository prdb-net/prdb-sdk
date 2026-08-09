# prdb-sdk (Python)

Python client for the [prdb Public API](https://apidocs.prdb.net/).

## Install

```bash
pip install prdb-sdk
```

Requires Python 3.10 or newer. The client is async and uses `httpx` under the
hood, by way of the Kiota bundle.

## Usage

```python
import asyncio
from uuid import UUID

from prdb_sdk import create_client


async def main() -> None:
    client = create_client(api_key="...")

    # GET /videos
    page = await client.videos.get()
    for video in page.items or []:
        print(video.title)

    # GET /videos/{id}
    video = await client.videos.by_id(UUID("...")).get()

    # Query parameters are typed, including the closed-set ones.
    from prdb_sdk.generated.videos.videos_request_builder import VideosRequestBuilder

    config = VideosRequestBuilder.VideosRequestBuilderGetRequestConfiguration(
        query_parameters=VideosRequestBuilder.VideosRequestBuilderGetQueryParameters(
            page=2,
            page_size=50,
            search="...",
        )
    )
    page_two = await client.videos.get(request_configuration=config)


asyncio.run(main())
```

The request builders mirror the API's URL structure, so `GET /videos/{id}/filehashes`
is `client.videos.by_id(video_id).filehashes.get()`.

## Authentication

`create_client` sends the key in the `X-Api-Key` header, and keeps it on the API
host: a redirect to a different origin raises `CrossOriginRedirectError` rather
than handing your credential to whoever answers there. Redirects that stay on
the same origin are followed normally.

`base_url` must use `https`, so the key is never sent in cleartext.

`GET /health` is the only endpoint that works without a key; use
`create_anonymous_client()` for health probes. That one has no credential to
protect, so it accepts a plain `http` base URL.

## Options

```python
from prdb_sdk import RetryOptions, create_client

client = create_client(
    api_key="...",
    base_url="https://api.prdb.net",   # override for a staging deployment
    http_client=my_httpx_async_client, # control timeouts, proxies, connection limits
    retry=RetryOptions.disabled(),     # see below
)
```

A client you pass in is left as it is. The SDK copies it and installs its
middleware on the copy, so the client it sends through behaves like the one
built for you — same redirect rule, same retry handling — while yours keeps
behaving the way you configured it.

The copy shares your transport, so your connection pool, TLS settings and
proxies are the ones actually used. That also ties the lifetimes together:
closing your client closes the connections the SDK sends through.

### Retrying

By default the SDK retries a `429`, `503` or `504` up to three times, honouring
`Retry-After`.

Turn that off if your application already retries prdb calls:

```python
client = create_client("...", retry=RetryOptions.disabled())
```

Otherwise the two policies multiply — one logical call becomes up to *n×m*
requests against an API that rate limits, and an outer circuit breaker never
sees a stable failure to open on. The built-in policy also retries writes, so an
application that must not repeat one should own the retry itself.

To keep it but change it:

```python
client = create_client("...", retry=RetryOptions(max_retries=5, delay=1.0))
```

## Reading the response status

A typed call returns the deserialised body, which is all you need until an
operation answers with more than one success status. `POST
/downloaded-from-indexers` is the one that does: **201** when it created the
entry, **200** when an equivalent one already existed and is being returned
unchanged. The bodies are the same shape, so the status is the only thing that
tells the two apart.

Pass a `ResponseStatusOption` to read it:

```python
from kiota_abstractions.base_request_configuration import RequestConfiguration

from prdb_sdk import ResponseStatusOption

status = ResponseStatusOption()

entry = await client.downloaded_from_indexers.post(
    body, request_configuration=RequestConfiguration(options=[status])
)

if status.status_code == 200:
    ...  # an equivalent entry already existed; entry is the one the API has
```

Kiota's own `NativeResponseHandler` cannot serve this: it surfaces the raw
response but suppresses deserialisation while doing so, so the typed result
comes back `None`. The option is the other half — the call returns its model as
usual, and the status is on the option afterwards.

## Reading the rate limit

Every metered response carries the rate limit it was counted against, so you can
pace off the answers you are already getting instead of spending a request on
`GET /rate-limit` to ask.

```python
from kiota_abstractions.base_request_configuration import RequestConfiguration

from prdb_sdk import RateLimitOption

limits = RateLimitOption()

sites = await client.sites.get(
    request_configuration=RequestConfiguration(options=[limits])
)

if limits.hour and limits.hour.remaining < 50:
    ...  # slow down; limits.hour.reset_in_seconds until a slot frees up
```

`hour` and `month` are each a `RateLimitWindow` with `limit`, `remaining` and
`reset_in_seconds`, or `None`.

`reset_in_seconds` is the wait until the oldest request leaves the sliding
window and frees **one** slot — not a timestamp, and not the time until the
whole window resets. It is the same quantity `resetsInSeconds` carries on
`GET /rate-limit`.

`None` is an answer rather than a gap. A response the API did not meter — `401`,
`403`, `503`, and `GET /rate-limit` itself — carries no headers at all, and a
`429` carries only the window that refused the request, so exactly one of the
two being set is normal. A refusal records too, so the reading is there for a
caller that catches the error.

Kiota can also surface response headers itself, through
`HeadersInspectionHandlerOption`, as raw multi-valued strings. This option is
the typed reading of the six that matter.

## Conditional requests

`GET /sites` returns a weak `ETag` covering the matched rows and the paging,
sorting and search parameters. Send it back as `If-None-Match` and the endpoint
answers **304 Not Modified** with no body while nothing has changed — the whole
site list fits in one request at `page_size=1000`, so this is worth doing.

```python
from kiota_abstractions.base_request_configuration import RequestConfiguration
from kiota_http.middleware.options import HeadersInspectionHandlerOption

from prdb_sdk import ResponseStatusOption

# First call: read the validator off the response.
inspect = HeadersInspectionHandlerOption(inspect_response_headers=True)
sites = await client.sites.get(
    request_configuration=RequestConfiguration(options=[inspect])
)
etag = next(iter(inspect.response_headers.try_get("etag")))

# Later: ask only for what changed.
status = ResponseStatusOption()
configuration = RequestConfiguration(options=[status])
configuration.headers.add("If-None-Match", etag)

sites = await client.sites.get(request_configuration=configuration)

if status.status_code == 304:
    ...  # nothing changed; keep the copy you already have
```

A `304` returns `None` from the typed call rather than raising. `None` alone
does not distinguish "not modified" from "no rows", so pass a
`ResponseStatusOption` when you need to tell them apart.

One wrinkle from the API side: the shared read-only cache does not vary by
`If-None-Match`, so a request that hits it is answered `200` with a body even
when your validator still matches. That is expected rather than an error.

Use one instance per call. It is written when the response arrives, so sharing
one across concurrent calls means whichever finishes last wins.

The status recorded is the one the result was built from: after a redirect the
SDK followed, and after the last retry. A call that raises records too, so an
`APIError` caught from a `403` still has its status alongside. It stays `None`
when no response was reached at all — a failed connection, a timeout, or a
refused cross-origin redirect.

## Generated code

Everything under `prdb_sdk/generated/` is produced by Kiota from
`spec/openapi.json` in the repository root and is overwritten on every
regeneration. Do not edit it — see the [root README](../README.md#regenerating).
