# Changelog

All four SDKs share this file and one version number, because they are
generated from the same OpenAPI document and released together.

`Prdb.Hashing` is not one of them and is versioned separately; its changes are
in [`csharp/src/Prdb.Hashing/CHANGELOG.md`](csharp/src/Prdb.Hashing/CHANGELOG.md).

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Entries describe what changed for someone *using* an SDK. A regeneration that
moves a thousand lines but no API surface is not worth an entry; a property that
changed type is, whichever language it landed in.

## [Unreleased]

### Documented

- **What every API model represents and what nearly every property means.** The
  API now publishes the XML documentation that already accompanied its source
  models, taking the generated SDKs from 15 documented properties to 310. In
  particular, `VideoDetailImageDto.cdnPath` and
  `VideoDetailActorImageDto.cdnPath` are complete absolute URLs ready to request
  as-is, despite their names, and the image collections in a video detail now
  document their stable ordering. This regeneration changes documentation only:
  no field, type, method, operation, or status code changed.

## [0.6.1] - 2026-08-09

A regeneration that changes no type, field, method or status code. Both entries
below are doc comments, in all four languages, so upgrading changes what your
editor tells you and nothing else.

### Documented

- **What an integer enum's values mean, at all 42 use sites instead of 29.** An
  enum reaches the SDK as a plain `int`, so the schema description — `Known
  values: Sabnzbd (0), Nzbget (1), Filesystem (2), Other (3), Ordeno (4).` — is
  the only place a caller learns what `4` stands for. Kiota picks that up
  through a bare `$ref` but not through the `allOf: [$ref]` plus `nullable`
  wrapper a nullable property gets, so 13 properties said `The fulfillmentByApp
  property` and nothing else. `FulfillmentApp` gained `Ordeno = 4` in 0.5.0 and
  not one of its five use sites mentioned it. `BirthdayType`, `VideoQuality`,
  `FulfillmentApp` and `IdentifyMatchKind` are the enums affected.

- **That a `pHash` is only comparable if it was computed the one right way**, on
  the five endpoints that accept one and the two `filenames` routes underneath
  them. A value from any other procedure is not wrong in a way the value itself
  reveals: `POST /videos/identify` skips that rung silently, the two lookups
  match nothing, and the submission paths store it where it can never be
  matched. The procedure is specified in
  [`docs/video-hashing.md`](docs/video-hashing.md), and `Prdb.Hashing`
  implements it for .NET.

## [0.6.0] - 2026-08-09

Two things the 0.5.0 regeneration surfaced but could not fix, because neither
lives in generated code. Both are about the API telling you something the typed
layer was dropping on the floor.

### Added

- **A typed call can now report the rate limit it was counted against.** Every
  metered response carries the six `X-RateLimit-*` headers, so a client can pace
  itself off the answers it is already getting rather than spending a request on
  `GET /rate-limit` to ask. `RateLimitOption` (C#, Python, TypeScript) and
  `prdb.NewRateLimitOption()` (Go) follow `ResponseStatusOption`: the call
  returns its model as usual, and the reading is on the option afterwards.

  ```python
  limits = RateLimitOption()

  sites = await client.sites.get(
      request_configuration=RequestConfiguration(options=[limits])
  )

  if limits.hour and limits.hour.remaining < 50:
      ...  # slow down; limits.hour.reset_in_seconds until a slot frees up
  ```

  `hour` and `month` are each a window of `limit`, `remaining` and
  `reset_in_seconds`, or absent. Absent is an answer rather than a gap: `401`,
  `403`, `503` and `GET /rate-limit` itself are not metered and carry no
  headers, and a `429` carries only the window that refused the request, so
  exactly one of the two being set is normal. A refused call records too. A
  malformed header reports "no reading" rather than failing a call that
  otherwise succeeded.

  **Go callers who supply their own `*http.Client` should prefer this over
  Kiota's `HeadersInspectionOptions`**, which reads nothing at all on that path
  — silently. Kiota's is a middleware, and middleware lives in the `Transport`
  that a supplied client owns; this option is a `RoundTripper` on the client the
  SDK sends through, so it works either way. Measured, not assumed.

### Fixed

- **C#: a `304 Not Modified` no longer arrives as an exception.** `GET /sites`
  answers `304` when you send back the `ETag` it gave you — the request working,
  not failing. Python, TypeScript and Go all return null from that call, but the
  C# request adapter treats any unmapped non-2xx status as a failure and raised
  `ApiException`, so conditional requests were the one thing in this SDK that
  needed a `try`/`catch` around the *successful* path. C# now returns null like
  the other three:

  ```csharp
  var status = new ResponseStatusOption();

  var sites = await client.Sites.GetAsync(config =>
  {
      config.Headers.Add("If-None-Match", etag);
      config.Options.Add(status);
  });

  if (status.StatusCode == HttpStatusCode.NotModified) { /* keep your copy */ }
  ```

  Kiota generates no handling for a declared 3xx in any of the four languages,
  so what each SDK did with a `304` was its adapter's fallback rather than
  anything generated. That is now pinned by a test in all four, so a generator
  upgrade that moved any of them has to fail the build rather than the caller.

  This is the one place the SDK reshapes a response: C# presents the `304` to
  the adapter as a `204`, after the real status has been recorded and with the
  headers left intact. `ResponseStatusOption` still reports `304`, and remains
  how you tell "not modified" from "no rows" — null alone cannot. The
  substitution is visible only to Kiota's `NativeResponseHandler`, which sits
  above it.

### Documented

- **Conditional requests, in all four READMEs**, including how to read the
  `ETag` in the first place — and the API-side wrinkle that a request served
  from the shared read-only cache comes back `200` with a body even when your
  validator still matches, because that cache does not vary by `If-None-Match`.
- **How to read response headers, in the three READMEs that did not say.** Kiota
  ships a headers-inspection option and every wrapper here already installs it,
  so response headers have been reachable *alongside* the typed model all along —
  the C# README was alone in mentioning it.

  This corrects 0.5.0's release notes, which claimed the opposite: that reaching
  response headers cost you the deserialised model. It does not, on the `200` or
  on the `304`. Only the C# `304` throw was real, and it is fixed above.

## [0.5.0] - 2026-08-08

Three new endpoints from one API change. Everything here is additive: no
existing call site changes, and nothing was renamed, retyped or removed.

### Added

- **`POST /videos/identify`** — hand the API a batch of video files and let it
  match them against the catalogue server-side. Matching a file name to a site
  happens here and nowhere else; sites carry no alias names a client could match
  against itself. Each result reports how it was matched (`matchKind`: os hash,
  perceptual hash, file name, release name, or site) and how sure the API is
  (`confidence`, from none through exact, plus ambiguous). Ask for
  `includeVideoDetails` and the full `VideoDetailDto` comes back with the match
  instead of just an id.

  ```python
  result = await client.videos.identify.post(request)
  ```

- **`POST /wanted-videos/fulfillments`** — mark wanted videos as fulfilled in
  one request instead of one call each. Each item reports its own outcome
  (`Updated`, `Unchanged`, `NotWanted`, `NotFound`), so a partial success is
  readable rather than an all-or-nothing failure.

  ```python
  result = await client.wanted_videos.fulfillments.post(request)
  ```

- **`POST /videos/filehash-submissions`** — submit hash-to-video assignments
  from a client. Submissions are stored apart from the aggregated hash set and
  change no read result, so this is a write-only path: it is deliberately not
  the inverse of `GET /videos/{id}/filehashes`. Each item says whether it was
  `Recorded`, `Updated`, `Conflicted`, or whether the video was not found, and
  carries the source of the assignment (`UserConfirmed` or `ClientDetected`).

  ```python
  result = await client.videos.filehash_submissions.post(request)
  ```

  It sits next to `filehashes` on the `videos` builder — `filehashes` reads the
  aggregated set, `filehashSubmissions` writes a submission. Naming follows the
  route, as everywhere else in these SDKs.

- **`SiteSummaryDto` now carries `createdAtUtc` and `updatedAtUtc`**, so a
  cached copy of the site list can be reconciled without refetching each site.

### Changed

- **`GET /sites` accepts `pageSize` up to 1000**, up from 100. The whole site
  list fits in one request at that size.
- **`FulfillmentApp` gained a fifth member, `Ordeno` (`4`).** The four existing
  members keep their numbers. Note that the API document spells its integer
  enums as a bare list of numbers with the member names in the description, so
  none of them are generated as named types in any of the four SDKs —
  `fulfillmentByApp` is an `int`, and `4` is now a value it can carry.

### Known limitations

- **`GET /sites` answers `304 Not Modified` when you send back the `ETag` it
  gave you, and the four SDKs surface that differently.** Python and TypeScript
  return `None`/`undefined` from the typed call, with `ResponseStatusOption`
  reporting `304`. **C# throws `ApiException`** instead — Kiota generates no
  handling for a 3xx response, and its C# adapter treats anything outside 2xx
  with no registered error factory as a failure. So in C# the conditional
  request works, but only through a `try`/`catch`. Tracked separately.

  Reading the `ETag` off the `200` in the first place needs Kiota's native
  response handler, which returns the raw response *instead of* the deserialised
  model, in every language. A typed way to reach response headers is separate
  work and is tracked with the rate-limit headers below.

- **The API now returns six rate-limit headers**
  (`X-RateLimit-{Limit,Remaining,Reset}-{Hour,Month}`) on every metered
  response. `Reset` is a number of seconds until a slot frees up, not a
  timestamp. They pass through untouched but have no typed representation in any
  SDK yet.

## [0.4.0] - 2026-08-08

Shaped by porganizer's third adoption review, which ran against 0.3.0. Neither
finding blocked the migration; one of them cost a workaround.

### Added

- **A typed call can now report which status the API answered with.** `POST
  /downloaded-from-indexers` answers `201` when it created the entry and `200`
  when an equivalent one already existed, and that distinction is behaviour, not
  logging — the 200 path means adopting what the API already has. A generated
  method returns the deserialised body alone, and Kiota's `NativeResponseHandler`
  surfaces the raw response only by suppressing deserialisation, so the typed
  model and the status were mutually exclusive: reading the status meant keeping
  that one call on a raw HTTP client, outside the SDK's typed layer. Pass a
  per-request option instead and get both:

  ```csharp
  var status = new ResponseStatusOption();
  var entry = await client.DownloadedFromIndexers.PostAsync(
      body, config => config.Options.Add(status));

  if (status.StatusCode == HttpStatusCode.OK) { /* it already existed */ }
  ```

  `ResponseStatusOption` (C#, Python, TypeScript) and
  `prdb.NewResponseStatusOption()` (Go). The status recorded is the one the
  result was built from — after a followed redirect and after the last retry,
  the SDK's own or an application's inside the pipeline — and a call that fails
  records too, so a `403`'s `ProblemDetails` arrives with its status alongside.

### Changed

- **C#: how to upload an image, and that `MultipartBody.RequestAdapter` is not
  yours to set.** `POST /video-user-images` takes a `MultipartBody` whose public
  `RequestAdapter` property is documented as needed for serialisation — and a
  consumer cannot obtain one, because the adapter behind `PrdbClient` is
  `protected` on `BaseRequestBuilder`. The endpoint therefore reads as
  uncallable from outside the SDK, which it is not: the request adapter fills the
  property in while sending. The C# README now shows the call, and a test pins
  the behaviour down so a Kiota upgrade that changed it would fail the build
  rather than the caller.
- **TypeScript: the README said Node 20 where `package.json` has required 22
  since 0.2.0.**

## [0.3.1] - 2026-08-08

A Python fix. The other three packages are identical to 0.3.0 apart from their
version number, because the four are released together.

### Fixed

- **Python: a caller-supplied `httpx.AsyncClient` is no longer modified.** The
  SDK installed its middleware the way Kiota does — by replacing the client's
  transport in place — which reconfigured an object the application goes on
  using. Every unrelated request through that client then ran prdb's
  middleware, including the cross-origin redirect rule, so a redirect that had
  nothing to do with prdb was refused with a `CrossOriginRedirectError`. Each
  call wrapped the transport again, so a client shared across several SDK
  clients accumulated one pipeline per client built from it. The middleware now
  goes onto a shallow copy: it keeps the caller's timeouts, headers, auth and
  event hooks, and shares their transport, so their connection pool, TLS
  settings and proxies are still the ones used — but their client object is
  left exactly as it was. This is the same stance the C# wrapper took in 0.3.0,
  from the other end: neither SDK reconfigures what the caller owns.

## [0.3.0] - 2026-08-08

Shaped by porganizer's second adoption review, which ran against the published
0.2.0 package. Both findings are C#, and both were blockers: between them they
ruled out every way of pointing the SDK at an application's own connection pool.

### Added

- **C#: `AddPrdbClient` can read its settings on every resolution.** The
  existing overload captures the options at registration, which freezes the API
  key and base URL for the lifetime of the process — so an application that
  keeps its prdb credentials in a database, and lets a user edit them, kept
  sending the old key until it was restarted. The new overload also receives the
  `IServiceProvider` and runs per resolution:

  ```csharp
  services.AddPrdbClient((serviceProvider, options) =>
  {
      options.ApiKey = serviceProvider.GetRequiredService<ISettingsSnapshot>().PrdbApiKey;
  });
  ```

  The client is transient, so each injected client gets the current values. The
  registration-time overload is unchanged and remains the right default: it
  validates while the application is still starting, which the dynamic one
  cannot.

### Changed

- **BREAKING — C#: a `transport` that follows redirects is now refused, not
  corrected.** 0.2.0 closed the redirect leak by turning `AllowAutoRedirect`
  off on the supplied handler. That write is not the SDK's to make: a
  `SocketsHttpHandler` rejects every property write once it has served a
  request, and a handler from `IHttpMessageHandlerFactory` is pooled for the
  whole handler lifetime — so the first client built from a pooled handler
  worked and every later one threw `InvalidOperationException`, and even the
  first one reconfigured a transport shared with the rest of the process. The
  SDK now reads the property instead, and throws an `ArgumentException` naming
  it when the transport would follow redirects. Pass a handler with
  `AllowAutoRedirect = false`, or `KiotaClientFactory.GetDefaultHttpMessageHandler()`;
  `AddPrdbClient` already installs one and is unaffected.
- **C#: the README now documents that retrying costs you the error body.** Once
  Kiota's .NET retry handler has spent its attempts it throws an
  `AggregateException` of bare `ApiException`s rather than passing the last
  response on, so the error mapping never runs and the `ProblemDetails` that
  0.2.0 added is lost — in precisely the cases it was added for, a refusal the
  API repeats. Disabling the SDK's retry keeps the typed error. Behaviour is
  unchanged; only the documentation is new. The Python, TypeScript and Go
  handlers return the last response and are not affected.

## [0.2.0] - 2026-08-08

The first release with a breaking change, and the first shaped by someone
integrating the SDK rather than by us: porganizer's adoption review
([porganizer#12]) produced both the contract changes below and the retry
control. Reading actor changes needs a code change; nothing else does.

[porganizer#12]: https://gitlab.com/porganizer/porganizer/-/issues/12

### Changed

- **BREAKING — the actor change feed now matches the other six.** `GET
  /actors/changes` was the odd one out on three axes at once, which forced a
  generic change-feed reader to special-case actors forever. The query
  parameter `sinceUtc` is now `since`; the flat `nextCursorUtc` and
  `nextCursorId` are one nested `nextCursor` object, like every other feed; and
  the discriminator on a change is `eventType`, not `changeType`. Code that
  reads actor changes has to be updated. Everything else is unaffected
  (prdb#24).

### Added

- **403, 429 and 503 now deserialise into `ProblemDetails`.** The API returns
  all three on any authenticated endpoint — no API plan, quota spent, and rate
  limit enforcement unavailable respectively — but declared none of them, so
  the generated error mapping could not parse the body and a caller got a bare
  transport exception with a status code and nothing else. All three are now
  declared on all 48 authenticated operations, so the `detail` explaining *why*
  the request was refused reaches the caller. `429` also documents its
  `Retry-After` header (prdb#23).
- **Every change feed response carries `serverTimeUtc`.** An empty page used to
  leave a caller with no cursor to persist, so incremental syncs either
  re-read from the same point forever or invented a timestamp from the client
  clock or the HTTP `Date` header. `serverTimeUtc` is the server's own clock
  read when the page was produced, and is safe to store as the next `since`
  (prdb#25).

- **Retrying is now configurable, and can be turned off.** All four SDKs install
  Kiota's retry handler, which retries `429`, `503` and `504` honouring
  `Retry-After`. An application that already retries prdb calls had no way to
  opt out, so the two policies multiplied: one logical call became up to *n×m*
  requests against an API that rate limits, and an outer circuit breaker never
  saw a stable failure to open on. Pass `PrdbRetryOptions.Disabled` (C#),
  `RetryOptions.disabled()` (Python), `RETRY_DISABLED` (TypeScript) or
  `prdb.RetryDisabled()` (Go), or supply your own attempt count and delay.
  In Go, `Retry` and `HTTPClient` are mutually exclusive and setting both is an
  error, because Kiota's middleware lives in the `Transport` a supplied client
  owns.
- **C#: `services.AddPrdbClient(...)`**, which wires the client through
  `IHttpClientFactory` so handler lifetime and connection pooling are managed
  the way the rest of an ASP.NET application expects. It returns the
  `IHttpClientBuilder`, so an application can attach its own resilience
  handler — that runs inside the SDK's middleware, seeing the individual HTTP
  attempts. Configuration is validated at registration, so a bad base URL stops
  startup rather than the first request.
- **C#: a `timeout` parameter on `Create` and `CreateAnonymous`.** The request
  deadline lives on the `HttpClient` the factory builds, which is deliberately
  never exposed, so it could not be reached through `transport` at all — the
  README claimed otherwise. It now has its own parameter, defaulting to the
  same 100 seconds as before.

### Fixed

- **C#: a caller-supplied `transport` could follow a cross-origin redirect
  before the SDK refused it, leaking the API key.** Kiota's own transport
  disables redirect following, but a plain `SocketsHttpHandler` or
  `HttpClientHandler` does not, and neither does the handler chain from
  `IHttpMessageHandlerFactory`. Such a transport followed the redirect itself,
  so the SDK's rule never ran and `X-Api-Key` reached the other origin.
  Redirect following is now turned off on a supplied transport, and the DI
  registration installs a primary handler that does not redirect.
- **Go: a caller-supplied `*http.Client` with its own `CheckRedirect` could
  follow a cross-origin redirect, leaking the API key.** The wrapper installed
  its rule only when `CheckRedirect` was unset. It is now always installed and
  runs first; a caller's policy still runs afterwards and can refuse more, but
  cannot re-enable a redirect off the API host.
- **C#: the SDK no longer lets its `HttpClient` own a caller-supplied
  transport.** Disposing the client would have disposed the transport with it,
  which matters because a handler from `IHttpMessageHandlerFactory` is pooled
  and shared across the process. Backed by a test.

### Changed

- **TypeScript: the minimum supported Node version is now 22.** Node 20 reached
  end of life in April 2026, and continuing to advertise support for a release
  line that no longer receives security fixes would be misleading. Nothing in
  the SDK requires 22; installing on 20 warns rather than fails, and the code
  still runs. Consider it a statement about what is tested and supported.

## [0.1.1] - 2026-08-07

No functional change. The four packages are identical to 0.1.0 apart from
their version number.

Released to exercise the automated publishing path end to end. The npm package
in 0.1.0 was published by hand, because npm will only accept a trusted
publisher for a package that already exists, so the workflow's npm job had
never actually run.

First release.

### Added

- Python, TypeScript, Go and C# clients for the prdb Public API, covering all
  49 operations. Generated with Kiota 1.34.1 from
  <https://apidocs.prdb.net/openapi/openapi.json>.
- An API-key constructor per language (`create_client`, `createClient`,
  `NewClient`, `PrdbClientFactory.Create`), sending the key in the `X-Api-Key`
  header.
- An anonymous constructor per language, because `GET /health` is the only
  endpoint reachable without a key.
- A redirect that leaves the API's origin is refused rather than followed, so
  the key cannot travel off-site. The HTTP stacks strip only `Authorization`
  across origins, and `X-Api-Key` is a custom header, so each wrapper enforces
  this itself.
- The authenticated constructors require an `https` base URL, so the key is
  never sent in cleartext. The anonymous ones still accept `http`.
