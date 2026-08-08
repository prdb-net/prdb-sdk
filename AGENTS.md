# Repository Guidelines

Open-source SDKs for the prdb Public API in Python, TypeScript, Go and C#.
All four are generated with [Kiota](https://learn.microsoft.com/openapi/kiota/)
from one OpenAPI document, and the generated code is committed.

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

## Versioning

The four packages share one version number, set per language in
`python/pyproject.toml`, `typescript/package.json` and
`csharp/src/Prdb.Sdk/Prdb.Sdk.csproj`. Go takes its version from the git tag.
Keep them in step.

## Solution files

C# uses the modern `Prdb.Sdk.slnx` format only. Do not create or commit legacy
`*.sln` files.
