# Contributing

Bug reports and pull requests are welcome.

Everything in this repository is in English — code, comments, documentation,
commit messages, branch names and PR descriptions. No exceptions.

## The one hard rule

**Never hand-edit anything under a `generated/` directory.** It is overwritten
by `scripts/generate.sh`, and your change will vanish without warning on the
next run.

| Language | Generated | Hand-written |
|---|---|---|
| Python | `python/src/prdb_sdk/generated/` | `python/src/prdb_sdk/{__init__,client}.py` |
| TypeScript | `typescript/src/generated/` | `typescript/src/index.ts` |
| Go | `go/generated/` | `go/client.go` |
| C# | `csharp/src/Prdb.Sdk/Generated/` | `csharp/src/Prdb.Sdk/PrdbClientFactory.cs` |

If the generated output is wrong, the cause is upstream — the API's OpenAPI
document, or the pinned generator version. Open an issue saying which you think
it is and we will trace it. The API lives in a private repository, so you cannot
file it there yourself; we relay it.

## Reporting a bug

Tell us which SDK and which version, and include the request you made. Three
kinds of bug end up in different places, and guessing wrong costs a round trip:

- **Wrong types or missing properties in a client** — almost always the spec.
  Say which property, and which language you noticed it in.
- **Wrong behaviour in a wrapper** — authentication, base URLs, redirects,
  error handling. That is our code, in one of the four files above.
- **Wrong data from the API** — belongs upstream. Report it here anyway if you
  are not sure; we would rather route it than have you drop it.

## Setting up

You only need the toolchain for the language you are touching. CI runs all four.

```bash
cd python     && pip install -e '.[dev]'   # Python 3.10+
cd typescript && npm install               # Node 20+
cd go         && go build ./...            # Go 1.23+
cd csharp     && dotnet restore            # .NET 10 SDK
```

The C# library targets `net8.0`, but the test project also targets `net10.0`,
so building the solution needs the .NET 10 SDK. It builds the `net8.0` target
too; you only need the .NET 8 *runtime* if you want to run the tests on it.

Regenerating additionally installs Kiota as a global .NET tool, pinned in
`scripts/config.sh`. `scripts/generate.sh` does that for you and refuses to run
against a version other than the pinned one.

## Running the tests

```bash
cd python     && python -m pytest
cd typescript && npm run typecheck && npm test
cd go         && go vet ./... && go test ./...
cd csharp     && dotnet test Prdb.Sdk.slnx
```

The tests cover the hand-written wrappers, not the generated code — that is the
generator's output, and CI checks it a different way (see below).

The C# tests run on both target frameworks, so plain `dotnet test` needs the
.NET 8 and .NET 10 runtimes. With only one installed, pick it explicitly:
`dotnet test Prdb.Sdk.slnx -f net10.0`.

## Changing the wrappers

The four wrappers are deliberately the same shape: an API-key constructor, an
anonymous one, the same validation, the same redirect rule. **Adding a
capability to one means adding it to all four**, so that someone who learns one
SDK recognises the others.

One area deserves particular care. The API key travels in `X-Api-Key`, a custom
header, and every HTTP layer underneath strips only `Authorization` (sometimes
`Cookie`) when a redirect leaves the origin — Kiota's redirect handlers,
`net/http`, `httpx`, `fetch` and `HttpClient` alike. A custom header rides
straight through. Each wrapper therefore refuses cross-origin redirects itself,
and each has a test that drives a real redirect to a second host and asserts the
key did not arrive.

If you touch client construction, run those tests. This is the one place in the
repository where a perfectly reasonable-looking refactor silently gives the
user's credential away.

## Regenerating

The spec is pinned at `spec/openapi.json` and the generated code is committed
next to it. The two are always updated together.

```bash
scripts/update-spec.sh   # refresh spec/openapi.json from apidocs.prdb.net
scripts/generate.sh      # regenerate all four SDKs
```

Commit the spec and the regenerated directories in the same commit. CI re-runs
the generation and fails on any difference, so a spec committed without its
output — or the reverse — breaks the build.

Bumping `KIOTA_VERSION` in `scripts/config.sh` rewrites every SDK. Do that in
its own commit, so the diff reads as a generator change rather than hiding
inside an API change.

## Commits and pull requests

Commit subjects follow [Conventional Commits](https://www.conventionalcommits.org/):
`feat:`, `fix:`, `chore:`, `docs:`. Keep the subject under about 72 characters
and write it in the imperative.

Explain *why* in the body. A commit that says what the diff already shows is a
wasted opportunity; the interesting part is the reasoning that is no longer
visible once the code is in place.

Examples in a README are code. When you change one, compile it — a snippet that
does not build is a bug report waiting to happen.

## Releasing

For maintainers. Publishing to PyPI, npm and NuGet is not automated yet.

The four packages share one version number, set in `python/pyproject.toml`,
`typescript/package.json` and `csharp/src/Prdb.Sdk/Prdb.Sdk.csproj`. Keep them
in step, and add the release section to `CHANGELOG.md` in the same commit.

Go is the exception: it takes its version from a git tag, and because the module
lives in a subdirectory its tags carry that prefix — `go/v0.1.0`, not `v0.1.0`.
A tag without the prefix will not be found by `go get`.

## License

By contributing you agree that your contribution is licensed under the MIT
License, the same as the rest of the repository.
