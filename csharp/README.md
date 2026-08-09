# Prdb.Sdk (C#)

C# client for the [prdb Public API](https://apidocs.prdb.net/).

## Install

```bash
dotnet add package Prdb.Sdk
```

Targets .NET 8.0, so it runs on .NET 8 and later.

## Usage

```csharp
using Prdb.Sdk;

var client = PrdbClientFactory.Create("...");

// GET /videos
var page = await client.Videos.GetAsync();
foreach (var video in page?.Items ?? [])
{
    Console.WriteLine(video.Title);
}

// GET /videos/{id}
var single = await client.Videos[videoId].GetAsync();

// Query parameters are typed, including the closed-set ones.
var pageTwo = await client.Videos.GetAsync(config =>
{
    config.QueryParameters.Page = 2;
    config.QueryParameters.PageSize = 50;
    config.QueryParameters.Search = "...";
});
```

The request builders mirror the API's URL structure, so `GET /videos/{id}/filehashes`
is `client.Videos[videoId].Filehashes.GetAsync()`.

## Authentication

`PrdbClientFactory.Create` sends the key in the `X-Api-Key` header, and keeps it
on the API host: a redirect to a different origin throws
`CrossOriginRedirectException` rather than handing your credential to whoever
answers there. Redirects that stay on the same origin are followed normally.

`baseUrl` must use `https`, so the key is never sent in cleartext.

`GET /health` is the only endpoint that works without a key; use
`PrdbClientFactory.CreateAnonymous()` for health probes. That one has no
credential to protect, so it accepts a plain `http` base URL.

## Dependency injection

In an application with a service container, register the client instead of
building one by hand:

```csharp
using Prdb.Sdk;

services.AddPrdbClient(options =>
{
    options.ApiKey = configuration["Prdb:ApiKey"];
});
```

`PrdbClient` can then be injected anywhere. Its connections are managed by
`IHttpClientFactory`, so handler lifetime and pooling work the way the rest of
an ASP.NET application expects — a client built by hand and held as a singleton
never picks up a DNS change, and one built per call exhausts sockets.

`AddPrdbClient` returns the `IHttpClientBuilder` for the underlying named
client, which is where an application attaches its own pipeline:

```csharp
services.AddPrdbClient(options =>
{
    options.ApiKey = configuration["Prdb:ApiKey"];
    options.Retry = PrdbRetryOptions.Disabled;   // see below
})
.AddStandardResilienceHandler();
```

Anything added to that builder runs *inside* the SDK's middleware, so a
resilience handler there sees the individual HTTP attempts.

Leaving `ApiKey` unset registers an anonymous client. An empty one is rejected,
because that is a configuration value that failed to resolve rather than a
deliberate choice. Every other setting is checked at registration too, so a bad
base URL stops startup instead of the first request.

### Settings that change while the application runs

The overload above reads the options once, at registration. If your API key or
base URL lives somewhere a user can edit — a database row, a reloading
configuration source — take the overload that also gets the `IServiceProvider`.
It runs on every resolution, and the client is transient, so each injected
client uses the current values:

```csharp
services.AddPrdbClient((serviceProvider, options) =>
{
    var settings = serviceProvider.GetRequiredService<ISettingsSnapshot>();
    options.ApiKey = settings.PrdbApiKey;
    options.BaseUrl = settings.PrdbApiUrl;
    options.Retry = PrdbRetryOptions.Disabled;
})
.AddStandardResilienceHandler();
```

Settings that are not known at registration cannot be validated there, so a bad
base URL or an empty key throws when a client is resolved rather than at
startup. Resolve one while starting up if you want the failure there.

## Options

```csharp
var client = PrdbClientFactory.Create(
    apiKey: "...",
    baseUrl: "https://api.prdb.net",     // override for a staging deployment
    transport: myHandler,                // proxies, pooling, your own pipeline
    retry: PrdbRetryOptions.Disabled,    // see below
    timeout: TimeSpan.FromSeconds(30));  // per request, default 100 seconds
```

`transport` is the innermost `HttpMessageHandler`. The SDK's middleware is
layered on top of it, so the redirect rule above applies to it too.

**A transport must not follow redirects itself.** One that does would follow a
redirect off the API host before the SDK's rule could refuse it, and nothing
below strips `X-Api-Key`. So the SDK checks, and refuses to build a client on a
transport whose primary handler has `AllowAutoRedirect` set:

```csharp
var transport = new SocketsHttpHandler { AllowAutoRedirect = false };
var client = PrdbClientFactory.Create("...", transport: transport);
```

`KiotaClientFactory.GetDefaultHttpMessageHandler()` produces a suitable handler
too. For a handler that comes from `IHttpClientFactory`, configure it where it
is registered:

```csharp
services.AddHttpClient("prdb")
    .ConfigurePrimaryHttpMessageHandler(
        () => new SocketsHttpHandler { AllowAutoRedirect = false });
```

The SDK neither disposes nor modifies a transport you supply. Both matter when
it comes from `IHttpMessageHandlerFactory.CreateHandler`, where handlers are
pooled and shared across the process — and where a `SocketsHttpHandler` refuses
to be reconfigured at all once it has served its first request.

### Retrying

By default the SDK retries a `429`, `503` or `504` up to three times, honouring
`Retry-After`.

Turn that off if your application already retries prdb calls:

```csharp
var client = PrdbClientFactory.Create("...", retry: PrdbRetryOptions.Disabled);
```

Otherwise the two policies multiply — one logical call becomes up to *n×m*
requests against an API that rate limits, and an outer circuit breaker never
sees a stable failure to open on. The built-in policy also retries writes, so an
application that must not repeat one should own the retry itself.

To keep it but change it:

```csharp
var client = PrdbClientFactory.Create("...", retry: new PrdbRetryOptions
{
    MaxRetries = 5,
    Delay = TimeSpan.FromSeconds(1),
});
```

**Retrying costs you the error body.** Kiota's retry handler throws its own
`AggregateException` of bare `ApiException`s once the attempts are spent,
instead of handing the last response on, so the error mapping never runs:

```
503, retrying enabled   AggregateException of ApiException, no body
503, retrying disabled  ProblemDetails, detail: "fail-closed"
```

That applies to a refusal that *persists* — one the API repeats until the
attempts run out, which is exactly the case where `403` explains that there is
no API plan, or `503` that rate limiting is unavailable and the API is
fail-closed. A retry that succeeds is unaffected.

So an application that wants to log *why* prdb refused should disable the SDK's
retry and own the retrying itself, with a policy that returns the final response
rather than throwing — `AddStandardResilienceHandler` does. This is Kiota's
behaviour in .NET only; the Python, TypeScript and Go SDKs return the last
response and keep the typed error.

## Reading the response status

A typed call returns the deserialised body, which is all you need until an
operation answers with more than one success status. `POST
/downloaded-from-indexers` is the one that does: **201** when it created the
entry, **200** when an equivalent one already existed and is being returned
unchanged. The bodies are the same shape, so the status is the only thing that
tells the two apart.

Pass a `ResponseStatusOption` to read it:

```csharp
using System.Net;

var status = new ResponseStatusOption();

var entry = await client.DownloadedFromIndexers.PostAsync(
    body,
    config => config.Options.Add(status));

if (status.StatusCode == HttpStatusCode.OK)
{
    // An equivalent entry already existed; entry is the one the API has.
}
```

Kiota's own `NativeResponseHandler` cannot serve this: it surfaces the raw
`HttpResponseMessage` but suppresses deserialisation while doing so, so the
typed result comes back null. The option is the other half — the call returns
its model as usual, and the status is on the option afterwards.

Use one instance per call. It is written when the response arrives, so sharing
one across concurrent calls means whichever finishes last wins.

The status recorded is the one the result was built from: after a redirect the
SDK followed, and after the last retry, whether that retrying is the SDK's own
or your resilience handler inside the pipeline. A call that throws records too,
so a `ProblemDetails` caught from a `403` still has its status alongside. It
stays null when no response was reached at all — a failed connection, a
timeout, or a refused cross-origin redirect.

## Uploading an image

`POST /video-user-images` takes a `MultipartBody`:

```csharp
using Microsoft.Kiota.Abstractions;

using var file = File.OpenRead("preview.jpg");

var body = new MultipartBody();
body.AddOrReplacePart("File", "image/jpeg", file, "preview.jpg");
body.AddOrReplacePart("PreviewImageType", "text/plain", "Single");
body.AddOrReplacePart("VideoId", "text/plain", videoId.ToString());

var result = await client.VideoUserImages.PostAsync(body);
```

**Do not set `RequestAdapter` on the body.** The property is public and its
documentation says serialisation needs it, which makes the endpoint look
uncallable from outside the SDK — the adapter behind `PrdbClient` is
`protected`, so there is no way to reach it. There is no need to: the request
adapter fills the property in while sending. A test in this repository pins that
down.

## Reading the rate limit

Every metered response carries the rate limit it was counted against, so you can
pace off the answers you are already getting instead of spending a request on
`GET /rate-limit` to ask.

```csharp
var limits = new RateLimitOption();

var sites = await client.Sites.GetAsync(config => config.Options.Add(limits));

if (limits.Hour is { Remaining: < 50 } hour)
{
    // Slow down; hour.ResetInSeconds until a slot frees up.
}
```

`Hour` and `Month` are each a `RateLimitWindow` with `Limit`, `Remaining` and
`ResetInSeconds`, or null.

`ResetInSeconds` is the wait until the oldest request leaves the sliding window
and frees **one** slot — not a timestamp, and not the time until the whole
window resets. It is the same quantity `resetsInSeconds` carries on
`GET /rate-limit`.

Null is an answer rather than a gap. A response the API did not meter — `401`,
`403`, `503`, and `GET /rate-limit` itself — carries no headers at all, and a
`429` carries only the window that refused the request, so exactly one of the
two being set is normal. A call that throws records too, so the reading is
there for a caller that catches the error.

## Reading response headers

The rate limit above is the typed reading of six of them. For anything else —
`ETag`, `Retry-After` on a `429` — the raw headers are reachable per request
through `HeadersInspectionHandlerOption`:

```csharp
using Microsoft.Kiota.Http.HttpClientLibrary.Middleware.Options;

var inspection = new HeadersInspectionHandlerOption
{
    InspectResponseHeaders = true,
};

var page = await client.WantedVideos.Changes.GetAsync(config =>
{
    config.QueryParameters.Since = DateTimeOffset.UtcNow.AddDays(-1);
    config.Options.Add(inspection);
});

var date = inspection.ResponseHeaders["Date"];
```

It populates on a `304` too, so the `ETag` from a conditional `GET /sites` is
readable on both legs of the round trip.

## Generated code

Everything under `src/Prdb.Sdk/Generated/` is produced by Kiota from
`spec/openapi.json` in the repository root and is overwritten on every
regeneration. Do not edit it — see the [root README](../README.md#regenerating).
