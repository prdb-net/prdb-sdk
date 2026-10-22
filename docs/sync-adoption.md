# Baseline and Identification freshness adoption

Version 0.22.0 adds both operations in Python, TypeScript, Go and C#. The four
SDKs are generated from the same published OpenAPI document; existing callers
can keep their current routes. All existing runtime minimums remain unchanged.

## Video baseline

Use the generated `videos.baseline` request builder (C#: `Videos.Baseline`,
Go: `Videos().Baseline()`) with `createdFrom`, `createdBefore`, `pageSize` and,
on subsequent requests, the opaque `cursor`. The generated query serializers
emit PascalCase parameter names from the published spec; the API accepts them.
Use timezone-aware UTC date values. **Go exception:** the pinned Kiota runtime
panics on typed date query parameters; newer versions inspected also drop the
dates. Use `WithUrl` with `net/url.Values` for this operation instead of setting
`CreatedFrom`/`CreatedBefore` on its typed query configuration. The generated
response and 413 error types still apply. This exact pattern is compiled and
exercised by `go/sync_contracts_test.go`:

```go
query := url.Values{
    "CreatedFrom": {from.Format(time.RFC3339)},
    "CreatedBefore": {before.Format(time.RFC3339)},
    "PageSize": {"1000"},
    "Cursor": {cursor},
}
baselineURL := baseURL + "/videos/baseline?" + query.Encode()
page, err := client.Videos().Baseline().WithUrl(baselineURL).Get(ctx, nil)
```

Create a fresh `WithUrl` builder for each call; the Go runtime consumes its raw
URL state during request construction. Use the same trusted API base URL as the authenticated client, and retain the
normal cursor/checkpoint rules below. The creation window is half-open and at
most 90 days. Page size defaults to and cannot exceed 1000; byte/row caps can
produce shorter pages. Keep the creation range fixed throughout the scan.

Persist each full document page, range, `changesSince`, `nextCursor` and an
explicit baseline/catch-up/live phase in one local transaction. Resume the last
committed checkpoint after failure or a lost response. `hasMore=false` ends
the baseline. A typed `BaselineDocumentTooLargeResponse` on 413 contains
`videoId`, `nextCursor` and `changesSince`: fetch that detail through the normal
route, persist it and the continuation together, then resume. Reconcile a 404
through the feed rather than silently losing the exceptional ID.

After the baseline, start Video changes at `changesSince` inclusively, with no
`sinceId`. Persist nested feed cursors with each page; on an empty page advance
using the server's safe `serverTimeUtc`, without moving backwards. Apply only
newer revisions, retain tombstone revisions against late page replays, and
follow merge survivors. Keep live rows in the chosen creation range. When
replacing a local inventory, prune missing IDs only after the whole inventory
has completed. This is a mutable scan plus catch-up, not an immutable snapshot;
it inherits the existing feed's settle-delay and writer timestamp assumptions.

## Identification reuse

Set `includeFreshness=true` on ordinary Identify. Persist each answer with its
optional `freshnessToken`, `freshnessExpiresAtUtc` and the complete original
tuple: filename, filesize and all supplied MD5/OS/pHash evidence. Missing proofs
are normal. Deduplicate only identical complete tuples, not filenames alone.

Call the generated `videos.identify.validate` builder with those tuples and
proofs, up to 200 per request. Refs preserve correlation and may change; results
preserve order. Switch on the typed status:

- `unchanged`: reuse the retained Identification answer with its original
  confidence. This does not refresh Video details or strengthen identity.
- `identified`: replace the answer and proof atomically with `result`.
- `reidentify`: run ordinary Identify when ready. This is the no-fallback
  outcome when the request sets `reidentify=false`.

By default, invalid/missing/expired/wrong-account/evicted proofs are identified
again in one bounded batch. Validation does not extend expiry. `includeVideoDetails`
applies only to replacement results; use Video changes for ongoing detail
freshness. Never rely on proof validity across account or tuple changes.

The wire sends `result:null` for `unchanged` and `reidentify`. Python, Go and C#
preserve a null reference; the pinned TypeScript Kiota runtime materializes an
empty object for a null model reference. **Always branch on `status` and only
read `result` for `identified`**, in every language.

Older servers can omit proof fields and return 404 for validation. Keep the
ordinary Identify path for those cases. Missing fields must not become an
assertion of freshness. These are additive capabilities, not mandatory changes
for existing consumers.

## Budget and validation

Every baseline page, Identify call and validation call costs one ordinary hourly
and monthly request unit; validation is not free. Detail escapes and catch-up
calls cost additional units. All keys and MCP activity share the account's
rolling one-hour/31-day budget. Observe both windows. Reset seconds concern the
oldest single unit, not a complete refill. `/rate-limit` is quota-exempt and can
return a five-second cached snapshot.

The shared `tests/fixtures/sync-contracts.json` fixture is exercised through the
real generated serializers and request builders in all four languages. Tests
cover scope/cursor encoding, full documents and watermark, typed 413 recovery,
opt-in and 64-bit tuple sizes, all three statuses, nullable results and legacy
proof omission. The generated directories must never be edited by hand.
