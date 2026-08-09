# @prdb/sdk (TypeScript)

TypeScript client for the [prdb Public API](https://apidocs.prdb.net/).

## Install

```bash
npm install @prdb/sdk
```

Requires Node 22 or newer. The package is ESM-only and ships type declarations.

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

## Reading the response status

A typed call returns the deserialised body, which is all you need until an
operation answers with more than one success status. `POST
/downloaded-from-indexers` is the one that does: **201** when it created the
entry, **200** when an equivalent one already existed and is being returned
unchanged. The bodies are the same shape, so the status is the only thing that
tells the two apart.

Pass a `ResponseStatusOption` to read it:

```ts
import { ResponseStatusOption } from "@prdb/sdk";

const status = new ResponseStatusOption();

const entry = await client.downloadedFromIndexers.post(body, {
  options: [status],
});

if (status.statusCode === 200) {
  // An equivalent entry already existed; entry is the one the API has.
}
```

Kiota's own native response handler cannot serve this: it surfaces the raw
`Response` but suppresses deserialisation while doing so, so the typed result
comes back `undefined`. The option is the other half — the call returns its
model as usual, and the status is on the option afterwards.

## Reading the rate limit

Every metered response carries the rate limit it was counted against, so you can
pace off the answers you are already getting instead of spending a request on
`GET /rate-limit` to ask.

```ts
import { RateLimitOption } from "@prdb/sdk";

const limits = new RateLimitOption();

const sites = await client.sites.get({ options: [limits] });

if (limits.hour && limits.hour.remaining < 50) {
  // Slow down; limits.hour.resetInSeconds until a slot frees up.
}
```

`hour` and `month` are each a `RateLimitWindow` with `limit`, `remaining` and
`resetInSeconds`, or `undefined`.

`resetInSeconds` is the wait until the oldest request leaves the sliding window
and frees **one** slot — not a timestamp, and not the time until the whole
window resets. It is the same quantity `resetsInSeconds` carries on
`GET /rate-limit`.

`undefined` is an answer rather than a gap. A response the API did not meter —
`401`, `403`, `503`, and `GET /rate-limit` itself — carries no headers at all,
and a `429` carries only the window that refused the request, so exactly one of
the two being set is normal. A rejected call records too, so the reading is
there for a caller that catches the error.

Kiota can also surface response headers itself, through
`HeadersInspectionOptions`, as raw multi-valued strings. This option is the
typed reading of the six that matter.

Use one instance per call. It is written when the response arrives, so sharing
one across concurrent calls means whichever finishes last wins.

The status recorded is the one the result was built from: after a redirect the
SDK followed, and after the last retry. A call that rejects records too, so an
error caught from a `403` still has its status alongside. It stays `undefined`
when no response was reached at all — a failed connection, a timeout, or a
refused cross-origin redirect.

## Generated code

Everything under `src/generated/` is produced by Kiota from `spec/openapi.json`
in the repository root and is overwritten on every regeneration. Do not edit it
— see the [root README](../README.md#regenerating).
