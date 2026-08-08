# @prdb/sdk (TypeScript)

TypeScript client for the [prdb Public API](https://apidocs.prdb.net/).

## Install

```bash
npm install @prdb/sdk
```

Requires Node 20 or newer. The package is ESM-only and ships type declarations.

## Usage

```ts
import { createClient } from "@prdb/sdk";

const client = createClient({ apiKey: "..." });

// GET /videos
const page = await client.videos.get();
for (const video of page?.items ?? []) {
  console.log(video.title);
}

// GET /videos/{id}
const video = await client.videos.byId(videoId).get();

// Query parameters are typed, including the closed-set ones.
const pageTwo = await client.videos.get({
  queryParameters: { page: 2, pageSize: 50, search: "..." },
});
```

The request builders mirror the API's URL structure, so `GET /videos/{id}/filehashes`
is `client.videos.byId(videoId).filehashes.get()`.

## Authentication

`createClient` sends the key in the `X-Api-Key` header, and keeps it on the API
host: a redirect to a different origin throws `CrossOriginRedirectError` rather
than handing your credential to whoever answers there. Redirects that stay on
the same origin are followed normally.

`baseUrl` must use `https`, so the key is never sent in cleartext.

`GET /health` is the only endpoint that works without a key; use
`createAnonymousClient()` for health probes. That one has no credential to
protect, so it accepts a plain `http` base URL.

## Options

```ts
import { RETRY_DISABLED, createClient } from "@prdb/sdk";

const client = createClient({
  apiKey: "...",
  baseUrl: "https://api.prdb.net", // override for a staging deployment
  customFetch: myFetch,            // control timeouts, proxies, agents
  retry: RETRY_DISABLED,           // see below
});
```

`customFetch` is wrapped in the SDK's middleware, so the redirect rule above
applies to it too.

### Retrying

By default the SDK retries a `429`, `503` or `504` up to three times, honouring
`Retry-After`.

Turn that off if your application already retries prdb calls:

```ts
const client = createClient({ apiKey: "...", retry: RETRY_DISABLED });
```

Otherwise the two policies multiply — one logical call becomes up to *n×m*
requests against an API that rate limits, and an outer circuit breaker never
sees a stable failure to open on. The built-in policy also retries writes, so an
application that must not repeat one should own the retry itself.

To keep it but change it:

```ts
const client = createClient({
  apiKey: "...",
  retry: { maxRetries: 5, delay: 1 },
});
```

## Generated code

Everything under `src/generated/` is produced by Kiota from `spec/openapi.json`
in the repository root and is overwritten on every regeneration. Do not edit it
— see the [root README](../README.md#regenerating).
