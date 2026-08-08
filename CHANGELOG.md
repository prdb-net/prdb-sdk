# Changelog

All four SDKs share this file and one version number, because they are
generated from the same OpenAPI document and released together.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Entries describe what changed for someone *using* an SDK. A regeneration that
moves a thousand lines but no API surface is not worth an entry; a property that
changed type is, whichever language it landed in.

## [Unreleased]

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
