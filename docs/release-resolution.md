# Release metadata resolution

SDK 0.20.0 exposes `POST /releases/resolve`. Use it for release metadata before
acquisition; `/videos/identify` remains the separate file/hash contract.
Submit 1–200 original titles with unique opaque refs and optional complete source
identities, positive byte sizes, UTC posting instants and category hints. JSON is
limited to 1 MiB. One batch consumes one ordinary API request.

The generated builders are `client.releases.resolve.post(body)` in Python and
TypeScript, `client.Releases().Resolve().Post(ctx, body, nil)` in Go and
`client.Releases.Resolve.PostAsync(body)` in C#. The contract tests compile calls
through every authenticated wrapper. Go's wrapper disables Kiota's default gzip
request compression so JSON posts have the same ordinary encoding as the other
SDKs. Caller-owned transports retain their existing configuration.

C# example, with the same types exercised by `ReleaseResolutionTests`:

```csharp
using Prdb.Sdk;
using Prdb.Sdk.Generated.Models;

var client = PrdbClientFactory.Create(apiKey);
var response = await client.Releases.Resolve.PostAsync(new ResolveReleasesRequest
{
    Releases = [new ResolveReleaseInput
    {
        Ref = "r1", Title = originalTitle, SizeBytes = 4_294_967_296,
        PostedAtUtc = DateTimeOffset.Parse("2026-10-13T14:00:00Z")
    }]
});
```

`sizeBytes` is an integer byte count, not a media-file size or an identity proof.
Python, Go and C# preserve signed 64-bit values. TypeScript uses `number`; keep
supplied values within `Number.MAX_SAFE_INTEGER` to avoid rounding unknown large
sizes. Optional values may be omitted rather than invented. UTC posting time is
not the video's release date.

`source` is optional; when supplied it needs `kind` (`newznab` or `nzbcache`),
`origin` (HTTPS base URL without credentials/query/fragment) and `entryId` (opaque
provider key, a UUID for NZBCache). An origin or key alone does not establish
identity. The API never fetches supplied URLs.

Each ordered result echoes its ref. Only `resolved` and `automationEligible`
carry confirmed active `videoIds` and `videos` with Site/Actor IDs. Apply local
ownership, selected sites/actors, quality, rights and availability separately.
Incomplete actor credits do not prove an unlisted actor is absent. `candidates`
are alternatives, never confirmed identities or pack membership. Packs return
`unsupported/unsupportedPack`; the first version supports single videos only.

`candidate`, `ambiguous`, `conflict`, `unmatched` and `retryLater` remain distinct
and are rechecked at the supplied `recheckAfterUtc` with jitter/quota budgets.
Permanent invalid/unsupported inputs have a null recheck. Resolved acquisitions
still pending may be rechecked after 24 hours. The same request can resolve after
new catalogue knowledge without a manual resubmission workflow.
`resolutionVersion` is an opaque equality token, not an ordered timestamp or feed
cursor. Serialize rechecks or reject older in-flight responses using your own
request sequence. Never compare versions lexically to decide which is newer.

Nullable fields stay nullable in the generated clients. In TypeScript, Kiota
represents null dates as `undefined`; use a nullish check. Invalid per-entry
fields remain `invalid` alongside valid neighbours. Uncorrelatable batches use
400; size/media failures use 413/415. Unexpected/system-wide failures use
500/503; 401/403/429/503 retain typed gate problems and quota/Retry-After metadata.
The existing wrapper retry options apply: disable automatic retries if the
application owns the retry schedule.

Release identification writes neither catalogue associations nor user/filehash
contributions. After acquisition, use real file evidence with `/videos/identify`.
A release-derived guess must never become its own independent confirmation via
feedback submissions. No download or new file-hashing implementation is included.

The shared synthetic fixture and all four adapter tests cover mixed results,
int64/UTC hints, nullable dates and gate refusals. The C# consumer test additionally
selects Actor IDs, filters local ownership and rechecks an unchanged pending
input; it preserves typed validation/body-limit/media/server errors and Retry-After.
API SQL precision/load evidence is in
[the upstream report](https://gitlab.com/prdbnet/prdb/-/blob/main/docs/release-resolution-acceptance.md).
