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

`createClient` sends the key in the `X-Api-Key` header and binds it to the API
host, so a redirect elsewhere cannot carry the credential off-site.

`GET /health` is the only endpoint that works without a key; use
`createAnonymousClient()` for health probes.

## Options

```ts
const client = createClient({
  apiKey: "...",
  baseUrl: "https://api.prdb.net", // override for a staging deployment
  httpClient: myHttpClient,        // control timeouts, proxies, retries
});
```

## Generated code

Everything under `src/generated/` is produced by Kiota from `spec/openapi.json`
in the repository root and is overwritten on every regeneration. Do not edit it
— see the [root README](../README.md#regenerating).
