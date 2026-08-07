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

## Options

```csharp
var client = PrdbClientFactory.Create(
    apiKey: "...",
    baseUrl: "https://api.prdb.net", // override for a staging deployment
    transport: myHandler);           // control timeouts, proxies, pooling
```

`transport` is the innermost `HttpMessageHandler`. The SDK's middleware is
layered on top of it, so the redirect rule above applies to it too.

## Generated code

Everything under `src/Prdb.Sdk/Generated/` is produced by Kiota from
`spec/openapi.json` in the repository root and is overwritten on every
regeneration. Do not edit it — see the [root README](../README.md#regenerating).
