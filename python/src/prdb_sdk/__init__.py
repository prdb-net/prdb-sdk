"""Python SDK for the prdb Public API.

The request builders under the returned client mirror the API's URL structure::

    from prdb_sdk import create_client

    client = create_client(api_key="...")
    page = await client.videos.get()
    video = await client.videos.by_id(video_id).get()

Everything under ``prdb_sdk.generated`` is produced by Kiota from
``spec/openapi.json`` and is overwritten on every regeneration. Do not edit it.
"""

from .client import (
    API_KEY_HEADER,
    DEFAULT_BASE_URL,
    CrossOriginRedirectError,
    PrdbClient,
    RateLimitOption,
    RateLimitWindow,
    ResponseStatusOption,
    RetryOptions,
    create_anonymous_client,
    create_client,
)

__all__ = [
    "API_KEY_HEADER",
    "DEFAULT_BASE_URL",
    "CrossOriginRedirectError",
    "PrdbClient",
    "RateLimitOption",
    "RateLimitWindow",
    "ResponseStatusOption",
    "RetryOptions",
    "create_anonymous_client",
    "create_client",
]
