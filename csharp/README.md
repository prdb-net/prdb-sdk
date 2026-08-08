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
layered on top of it, so the redirect rule above applies to it too — and
redirect following is turned off on the handler itself, since otherwise it
would follow a redirect before the SDK's rule could refuse it.

The SDK never disposes a transport you supply. That matters when it comes from
`IHttpMessageHandlerFactory.CreateHandler`, where handlers are pooled and shared
across the process.

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

## Reading response headers

A typed call returns the deserialised body, but the response headers are
reachable per request through `HeadersInspectionHandlerOption`:

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

Useful for the rate limit headers, `ETag`, and `Retry-After` on a `429`.

## Generated code

Everything under `src/Prdb.Sdk/Generated/` is produced by Kiota from
`spec/openapi.json` in the repository root and is overwritten on every
regeneration. Do not edit it — see the [root README](../README.md#regenerating).
