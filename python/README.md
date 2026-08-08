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

## Generated code

Everything under `prdb_sdk/generated/` is produced by Kiota from
`spec/openapi.json` in the repository root and is overwritten on every
regeneration. Do not edit it — see the [root README](../README.md#regenerating).
