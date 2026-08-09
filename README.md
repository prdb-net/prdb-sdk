# prdb SDKs

Official client libraries for the [prdb Public API](https://apidocs.prdb.net/),
in Python, TypeScript, Go and C#.

All four are generated with [Kiota](https://learn.microsoft.com/openapi/kiota/)
from the API's own OpenAPI document, so every language exposes the same 49
operations with the same shapes. The generated code is committed, so you can
read it here on GitHub and build the SDKs without installing a generator.

| Language | Package | Directory |
|---|---|---|
| Python | `prdb-sdk` | [`python/`](python/) |
| TypeScript | `@prdb/sdk` | [`typescript/`](typescript/) |
| Go | `github.com/prdb-net/prdb-sdk/go` | [`go/`](go/) |
| C# | `Prdb.Sdk` | [`csharp/`](csharp/) |

## Authentication

Every endpoint except `GET /health` requires an API key, sent in the
`X-Api-Key` header. All four SDKs keep the key on the API host: a redirect to a
different origin is refused rather than followed, so your credential is never
handed to whoever answers there. They also require an `https` base URL, so it is
never sent in cleartext.

Neither the HTTP stacks nor Kiota do this for us — they strip only
`Authorization` across origins, and `X-Api-Key` is a custom header. It is the
wrappers' own rule, and each SDK has a test for it.

Requests are rate limited per key. `GET /rate-limit` reports the remaining
budget, and a `429` response carries a `Retry-After` header.

## Quickstart

The request builders mirror the API's URL structure, so `GET /videos/{id}` reads
the same way in all four languages.

**Python**

```python
from prdb_sdk import create_client

client = create_client(api_key="...")
page = await client.videos.get()
video = await client.videos.by_id(video_id).get()
```

**TypeScript**

```ts
import { createClient } from "@prdb/sdk";

const client = createClient({ apiKey: "..." });
const page = await client.videos.get();
const video = await client.videos.byId(videoId).get();
```

**Go**

```go
client, err := prdb.NewClient("...")
if err != nil {
    return err
}
page, err := client.Videos().Get(ctx, nil)
video, err := client.Videos().ById(videoID).Get(ctx, nil)
```

**C#**

```csharp
var client = PrdbClientFactory.Create("...");
var page = await client.Videos.GetAsync();
var video = await client.Videos[videoId].GetAsync();
```

Each directory has its own README with installation instructions and the
details for that language.

## What the API offers

Videos, actors and sites with their metadata; the scene pre-database; file
hashes for videos and indexers; user-submitted preview images; and the per-user
lists built on top of all of it — favourite actors and sites, wanted videos,
and downloads recorded from indexers.

Endpoints named `/{resource}/changes` are delta feeds. They return the current
state of rows changed since a cursor, including soft-deleted rows as tombstones,
rather than a full history of every mutation — which makes them the right tool
for keeping a local copy in sync.

Full reference: <https://apidocs.prdb.net/>

## Video hashing

Several endpoints identify a file by its `osHash` and `pHash` rather than by its
name. Both are defined in [`docs/video-hashing.md`](docs/video-hashing.md),
which is normative and detailed enough to implement from — including public test
vectors, because "compatible with everyone else's hashes" is otherwise just a
claim.

The values are only comparable if everyone computes them the same way: two
64-bit perceptual hashes from different methods sit about 32 bits apart whether
or not they describe the same video. They match what
[Stash](https://github.com/stashapp/stash) computes, bit for bit.

For C# there is a package that implements it —
[`Prdb.Hashing`](csharp/src/Prdb.Hashing/), separate from the SDK because it
starts processes and needs ffmpeg:

```csharp
string? osHash = OsHash.Compute(path);
var result = await new VideoPerceptualHasher().ComputeAsync(path);
```

The other three languages have no such package yet. The specification is the
contract, not the C# code, so an implementation that agrees with the test
vectors is correct whatever it shares.

## Regenerating

The spec is pinned at [`spec/openapi.json`](spec/openapi.json) and the generated
code is committed alongside it. The two are always updated together.

```bash
scripts/update-spec.sh   # refresh spec/openapi.json from apidocs.prdb.net
scripts/generate.sh      # regenerate all four SDKs
```

`scripts/generate.sh` only rewrites the `generated/` directories. The
hand-written wrapper next to each one — the few dozen lines that wire up
authentication and the base URL — is never touched.

The Kiota version is pinned in [`scripts/config.sh`](scripts/config.sh). CI
re-runs the generation and fails if the result differs from what is committed,
so the checked-in code cannot silently drift from the spec.

## Contributing

Bug reports and pull requests are welcome — see
[CONTRIBUTING.md](CONTRIBUTING.md) for how to set up, run the tests and report
a bug against the right layer.

Two things worth knowing before you start: the `generated/` directories are not
editable by hand, because the next run overwrites them, and everything in this
repository is in English, including commit messages.

Released changes are listed in [CHANGELOG.md](CHANGELOG.md).

## License

MIT — see [LICENSE](LICENSE).
