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

`create_client` sends the key in the `X-Api-Key` header and binds it to the API
host, so a redirect elsewhere cannot carry the credential off-site.

`GET /health` is the only endpoint that works without a key; use
`create_anonymous_client()` for health probes.

## Options

```python
client = create_client(
    api_key="...",
    base_url="https://api.prdb.net",   # override for a staging deployment
    http_client=my_httpx_async_client, # control timeouts, proxies, retries
)
```

## Generated code

Everything under `prdb_sdk/generated/` is produced by Kiota from
`spec/openapi.json` in the repository root and is overwritten on every
regeneration. Do not edit it — see the [root README](../README.md#regenerating).
