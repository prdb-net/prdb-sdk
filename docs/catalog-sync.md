# Catalogue synchronization

SDK version 0.16.0 adds `GET /videos/changes` (`GetVideoChanges`) and
`GET /sites/changes` (`GetSiteChanges`). Both require an API key.

| Language | Videos | Sites |
|---|---|---|
| Python | `client.videos.changes.get(...)` | `client.sites.changes.get(...)` |
| TypeScript | `client.videos.changes.get(...)` | `client.sites.changes.get(...)` |
| Go | `client.Videos().Changes().Get(ctx, config)` | `client.Sites().Changes().Get(ctx, config)` |
| C# | `client.Videos.Changes.GetAsync(...)` | `client.Sites.Changes.GetAsync(...)` |

## Starting and continuing a feed

Keep a separate cursor for each feed. For a full baseline, send
`Since=0001-01-01T00:00:00Z` and omit `SinceId`. `Since` is required by the
API even though the generated query-parameter types allow it to be omitted.
`PageSize` defaults to 100 and accepts values from 1 through 1000.

Each page contains `items`, `pageSize`, `hasMore`, `serverTimeUtc` and a
nullable `nextCursor`. Rows are ordered by `updatedAtUtc`, then UUID.

1. Apply every item to your local catalogue. Upsert `created` and `updated`
   items; remove `deleted` items. These are current states, not an event log,
   so several edits between polls can appear as one item.
2. For a nonempty page, pass both `nextCursor.updatedAtUtc` and
   `nextCursor.id` back as `Since` and `SinceId`. Preserve the timestamp's
   precision and the UUID; dropping the UUID can repeat rows sharing a timestamp.
3. Commit the cursor only after the items are applied successfully. Make
   application idempotent so a retried page is safe.
4. Continue immediately while `hasMore` is true. Keep the last returned cursor
   when pausing after a nonempty final page.
5. When a page is empty, persist `serverTimeUtc` as `Since` and clear `SinceId`.
   An empty page has no row cursor; the server clock supplies the next lower bound.

Use UTC timestamps. In TypeScript, construct the baseline with the full ISO
string above: the numeric `Date` constructor treats years 0 through 99 specially.

## Payloads and deletions

Each video item wraps its payload in `video`, including its current site,
network, actors, images, pre-names, description and quality overview. Each
site item wraps current site, network and link content in `site`. Changes to
nested catalogue content advance the owning row's timestamp.

Deletion items retain the payload UUID, `isDeleted` and `deletedAtUtc` while
content fields are null or empty. A video deleted by a merge also carries
`mergedIntoId`, the surviving video's UUID. Treat deletion items as removals;
do not replace a cached detail with their empty content.

Tombstones are currently retained indefinitely, with a guaranteed minimum of
90 days. If a future retention window is introduced and your cursor is older
than that window, rebuild the baseline to avoid missing deletions.

These feeds do not add canonical Site artwork. Sites still expose no logo or
profile image; [issue #35](https://github.com/prdb-net/prdb-sdk/issues/35)
tracks the API extension needed for that capability.
