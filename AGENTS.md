# Repository Guidelines

Open-source SDKs for the prdb Public API in Python, TypeScript, Go and C#.
All four are generated with [Kiota](https://learn.microsoft.com/openapi/kiota/)
from one OpenAPI document, and the generated code is committed.

The repository also holds one package that is **not** an SDK and not generated:
`Prdb.Hashing`, which computes the `osHash` and `pHash` values the API
identifies files by. It has its own rules — see *The hashing package* below.

## Language

**Everything in this repository is in English** — code, comments, documentation,
commit messages, branch names, PR titles and descriptions, CI job names, test
names, and anything visible to SDK users. No exceptions.

## The one hard rule

**Never hand-edit anything under a `generated/` directory.** It is overwritten
by `scripts/generate.sh` and your change will vanish without warning.

| Language | Generated | Hand-written |
|---|---|---|
| Python | `python/src/prdb_sdk/generated/` | `python/src/prdb_sdk/{__init__,client}.py` |
| TypeScript | `typescript/src/generated/` | `typescript/src/index.ts` |
| Go | `go/generated/` | `go/client.go` |
| C# | `csharp/src/Prdb.Sdk/Generated/` | `csharp/src/Prdb.Sdk/PrdbClientFactory.cs` |

If generated output is wrong, the cause is upstream. Fix it in the spec (the
`prdb` repository, `src/prdb.PublicApi`) or in the pinned generator version —
never by patching the output here.

## Layout

```
spec/openapi.json        pinned copy of the published API document
docs/video-hashing.md    normative osHash and pHash specification
scripts/config.sh        spec URL, pinned Kiota version, shared coordinates
scripts/update-spec.sh   refresh the spec from apidocs.prdb.net
scripts/generate.sh      regenerate all four SDKs
python/ typescript/ go/ csharp/
```

## Where the spec comes from

<https://apidocs.prdb.net/openapi/openapi.json> — public, no auth. The path is
not guessable: the docs UI fetches `/configuration.json` to discover it, and
`/openapi.json` returns 404. `api.prdb.net` never serves the document, because
the API only maps its OpenAPI endpoint in the Development environment.

`apidocs` deploys from prdb's default branch only. While an API change is still
unmerged, take the spec from the `openapi:` job artifact
(`artifacts/public-api.json`) instead.

**The document is OpenAPI 3.0 on purpose.** Nullability is spelled
`nullable: true`, and a nullable `$ref` is `allOf: [{$ref}]` alongside it. Do
not treat that as stale and do not ask prdb to publish 3.1: both 3.1 spellings
break generators. `oneOf: [null, $ref]` becomes a composed wrapper type, and
sibling keywords next to a `$ref` are intersected under JSON Schema 2020-12, so
`{"$ref": X, "type": ["null","object"]}` still rejects `null`. 3.0's `allOf`
plus `nullable` has one meaning that every generator implements. See prdb #20
and #21, and prdb commit `992a2e9`.

## Regenerating

```bash
scripts/update-spec.sh   # then
scripts/generate.sh
```

Commit `spec/openapi.json` and the regenerated `generated/` directories
**together** — CI re-runs the generation and fails on any drift, so a spec
committed without its output (or vice versa) breaks the build.

Bumping `KIOTA_VERSION` in `scripts/config.sh` rewrites every SDK. Do it in its
own commit, so the diff is reviewable as a generator change rather than being
mixed into an API change.

## Keep the four wrappers parallel

Each language has a small hand-written wrapper that wires up API-key
authentication and the base URL. They are deliberately the same shape:

- a constructor taking the API key, with optional base URL and transport
- an anonymous variant, because `GET /health` is the only endpoint that works
  without a key
- a redirect to a different origin refused rather than followed, so the key
  cannot travel off the API host
- validation that rejects an empty key, a non-absolute base URL, and — for the
  authenticated constructor only — a base URL that is not `https`
- a per-request option reporting the response status, because a typed call
  otherwise cannot tell 201 from 200 on `POST /downloaded-from-indexers`. It is
  recorded at the outer end of the pipeline, above the retry and redirect
  handlers, so it is the status the caller's result was built from. Go does it
  with a `RoundTripper` instead of Kiota middleware, so that a caller-supplied
  `*http.Client` is covered too

Adding a capability to one wrapper means adding it to all four. A user who
learns one SDK should recognise the others.

## The redirect rule is ours to enforce

The API key travels in `X-Api-Key`, a custom header. Every layer underneath
strips only `Authorization` (and sometimes `Cookie`) when a redirect leaves the
origin — Kiota's redirect handlers in all four languages, `net/http`, `httpx`,
`fetch` and `HttpClient` alike. A custom header is carried straight through.

So each wrapper installs its own rule, and each has a test that drives a real
redirect to a second host and asserts the key did not arrive. If you touch
client construction, run those tests: this is the one place where a plausible
refactor silently gives the credential away.

The corollary is that a caller-supplied transport must still run through our
middleware. Python, TypeScript and C# take the innermost transport and build the
pipeline around it; Go copies the client and sets `CheckRedirect`, because its
Kiota middleware lives in the `Transport` the caller owns.

None of the four reconfigure what the caller owns. Go copies the client, Python
copies it and installs the pipeline on the copy, TypeScript wraps the supplied
`fetch`, and C# checks the transport rather than correcting it: a handler from
`IHttpMessageHandlerFactory` is pooled and shared, and a `SocketsHttpHandler`
refuses property writes once it has served a request, so turning
`AllowAutoRedirect` off for the caller both reconfigures someone else's
transport and throws on the second client built from the same handler. Reading
the property is legal at any time. Do not turn that check back into a fix.

## Verifying a change

Run the check for whatever you touched; CI runs all of them.

```bash
cd python     && pip install -e '.[dev]' && python -m pytest
cd typescript && npm install && npm run typecheck && npm test
cd go         && go build ./... && go vet ./... && go test ./...
cd csharp     && dotnet build Prdb.Sdk.slnx -c Release && dotnet test Prdb.Sdk.slnx
```

The C# tests target `net8.0` and `net10.0`. With only one runtime installed,
add `-f net10.0` (or whichever you have) to `dotnet test`.

Examples in a README are code. When you change one, compile it — a snippet that
does not build is a bug report waiting to happen.

## The hashing package

`csharp/src/Prdb.Hashing/` computes the `osHash` and `pHash` values the API
identifies files by. It is hand-written, has no package dependencies, and shells
out to ffmpeg. C# only for now, by decision — a port to the other three is not
planned.

**`docs/video-hashing.md` is the specification; this package is one
implementation of it.** When the two disagree, the document is right. It is
normative because the values have to be comparable with Stash's and with every
other client's: two 64-bit perceptual hashes from different methods sit about 32
bits apart whether or not they describe the same video.

That makes `PerceptualHashReferenceTests` unlike other tests. Its expectations
are not in the test file at all: it reads `docs/video-hashing-vectors.json`, the
published vectors, which were produced by the Go reference chain. A failure
means these hashes stopped matching the rest of the ecosystem. **Do not update
the vector file to match new output** — find what changed in the arithmetic
instead. Editing it is editing the specification.

Level 3 is the one exception worth knowing. Those vectors are pinned to the
ffmpeg build named in the file, because which frame a seek lands on depends on
the build; a different ffmpeg may legitimately disagree there while levels 1 and
2 still pass. Compare ffmpeg versions before suspecting the code.

The code deliberately reproduces the reference's mistakes: the resampler is not
ordinary bilinear interpolation, the "median" is not a median, the DC
coefficient is kept, and the DCT divisors are copied rather than recomputed
because two runtimes need not agree on the last bit of a cosine. Each of those
has a comment saying so. A cleanup that fixes any of them changes every hash the
package produces.

The ffmpeg command line is part of the specification, not an implementation
detail: which frame a seek lands on depends on the argument order. It is pinned
by tests that need no ffmpeg installed, so a change to it fails in CI rather
than on a developer machine.

## Versioning

The four SDK packages share one version number, set per language in
`python/pyproject.toml`, `typescript/package.json` and
`csharp/src/Prdb.Sdk/Prdb.Sdk.csproj`. Go takes its version from the git tag.
Keep them in step; `scripts/check-version.sh` enforces it.

`Prdb.Hashing` is **exempt** and carries its own version. It is not generated
from the spec and does not change when the API does, so it releases from its own
tag (`hashing/v0.1.0`, via `release-hashing.yml`) rather than from `v*`. Do not
add it to `check-version.sh`: that would force a version bump on a package
nothing changed in.

## Solution files

C# uses the modern `Prdb.Sdk.slnx` format only. Do not create or commit legacy
`*.sln` files.
