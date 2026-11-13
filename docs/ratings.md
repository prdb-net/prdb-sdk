# Ratings

Version 0.26.0 adds 13 authenticated operations for Actor/Video ratings.
Aggregates are live and separate from catalogue detail, list, batch, search and
change-feed payloads. `ratingCount` counts current votes, `averageRating` is
their arithmetic average, and `reviewCount` counts only published review texts.
An unrated target returns zero counts and a null average.

All operations require the existing API key and API-enabled subscription. The
responses use `Cache-Control: no-store`. No other account's review text, public
review listing, community feed or rating delta feed is exposed.

## Request builders

The Actor and Video resources expose the same six operations; the seventh path
lists the authenticated account's current collection.

| HTTP operation | Python suffix | TypeScript suffix | Go suffix | C# suffix |
|---|---|---|---|---|
| GET rating-summary | `.rating_summary.get()` | `.ratingSummary.get()` | `.RatingSummary().Get(ctx, nil)` | `.RatingSummary.GetAsync()` |
| GET rating | `.rating.get()` | `.rating.get()` | `.Rating().Get(ctx, nil)` | `.Rating.GetAsync()` |
| PUT rating | `.rating.put(body, config)` | `.rating.put(body, config)` | `.Rating().Put(ctx, body, config)` | `.Rating.PutAsync(body, configure)` |
| POST rating/review | `.rating.review.post(body, config)` | `.rating.review.post(body, config)` | `.Rating().Review().Post(ctx, body, config)` | `.Rating.Review.PostAsync(body, configure)` |
| DELETE rating/review | `.rating.review.delete()` | `.rating.review.delete()` | `.Rating().Review().Delete(ctx, nil)` | `.Rating.Review.DeleteAsync()` |
| DELETE rating | `.rating.delete()` | `.rating.delete()` | `.Rating().Delete(ctx, nil)` | `.Rating.DeleteAsync()` |

Append a suffix to one of these resource builders:

| Language | Actor | Video |
|---|---|---|
| Python | `client.actors.by_actor_id(actor_id)` | `client.videos.by_id(video_id)` |
| TypeScript | `client.actors.byActorId(actorId)` | `client.videos.byId(videoId)` |
| Go | `client.Actors().ByActorId(actorID)` | `client.Videos().ById(videoID)` |
| C# | `client.Actors[actorId]` | `client.Videos[videoId]` |

The new `actorId` path parameters change Kiota's Actor item name. Existing
Python `by_id`, TypeScript `byId` and Go `ById` Actor calls must use the names
above, including detail and account calls. The concrete generated builder
changes from `ActorsItemRequestBuilder` to `ActorItemRequestBuilder`; update
explicit type annotations/imports. C# item access and all Video access retain
their existing names.

## Stars, text and idempotency

`SetRatingRequest` takes whole `stars` from 1 to 5. Omit `reviewText` to change
only stars. Optional text is immutable public plain text, 1–2,000 characters,
without links. `SubmitRatingReviewRequest` takes `text` and requires an existing
rating. To replace a text, delete the review first, then submit a new one.
Deleting just the review preserves stars; deleting the rating removes both.
Both deletions return bodyless `204` and are safe to repeat.

Every text submission requires an `Idempotency-Key` header, including PUT with
`reviewText`. Generated methods accept this through their normal request
configuration headers. Reuse the same key and identical payload after an
uncertain submission. Changing the payload with that key returns `409`. A
replay cannot reset later stars or resurrect deleted text. After deletion, a
new submission needs a new key, even for identical text. Keys belong to the
account across API keys and website sessions.

Clean text returns `200` with `reviewState: "Published"`; held text returns
`202` with `reviewState: "Pending"`. Use the existing per-request
`ResponseStatusOption` to distinguish these statuses while retaining the typed
`RatingWriteResponse`. Its `ratingId`, `reviewId` and `reviewState` are nullable:
a replay receipt may describe a later deletion or moderation outcome, and is
not proof of current public visibility.

## Own ratings and nullable fields

`OwnRatingResponse.rating` is null when the account has no current rating.
`OwnRatingItem.review` is null when it has no text; a present review includes
only the account's own text and safe state (`None`, `Published`, `Pending`,
`Rejected`, `Hidden`). `publishedAtUtc` is nullable. Original `createdAtUtc`
and later `updatedAtUtc` are distinct. No internal moderation reasons are
returned.

Python, Go and C# retain null object fields as `None`, `nil` and `null`.
TypeScript's pinned Kiota JSON runtime materializes a null object as `{}`;
check the required identity field, `response?.rating?.id == null` or
`rating.review?.id == null`, to detect absence. Nullable scalar values can
be `undefined`; use a nullish check for the average, receipt fields and cursor.
Do not infer a pending review or a zero rating from absent values.

## Collection and pagination

Read the collection with Python `client.ratings.mine.get(config)`, TypeScript
`client.ratings.mine.get(config)`, or C# `client.Ratings.Mine.GetAsync(configure)`.
Their typed query configurations support `search`, `type` (Actor/Video),
`stars`, `fromUtc` (inclusive), `toUtc` (exclusive), `hasText`, `reviewState`,
`sortBy` (Date/Stars), `sortDirection` (asc/desc), `pageSize` and `cursor`.
Python uses snake_case for multiword parameter names.

For Go, build a query with `net/url.Values`, encode it with `Encode()`, and use
`client.Ratings().Mine().WithUrl(baseURL + "/ratings/mine?" + query.Encode()).Get(ctx, nil)`.
The pinned runtime panics on typed date query parameters, even when unset;
the raw-URL builder retains typed responses and errors. Use the client's base
origin and encode cursor values rather than concatenating them unescaped.

The default page size is 20; the maximum is 100. Preserve every filter, sort
option and page size when sending `nextCursor` as `cursor`. Cursors bind to
the account and complete query; changing either returns `400`. Stop when
`hasMore` is false and `nextCursor` is null. Refresh a star-sorted collection
after a mutation. This collection contains current ratings, not a history of
star changes.

## Errors and retries

All new builders map `400`, `401`, `403`, `404`, `409`, `429` and `503` to
typed `ProblemDetails`. A `429` carries `Retry-After` seconds alongside existing
public-budget headers. Configure the existing retry options when the calling
application owns retries, and preserve the text submission's key and payload.
Writes may return `503` while rollout or enforcement is unavailable; reads are
available independently of the write gate. Client generation does not enable
server write gates.

The synthetic [shared fixture](../tests/fixtures/ratings.json) is exercised by
all four SDK test suites, including all 13 operations, owner states, nullable
fields, idempotency headers, paging, typed refusals and `Retry-After`.
