# Changelog

All four SDKs share this file and one version number, because they are
generated from the same OpenAPI document and released together.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Entries describe what changed for someone *using* an SDK. A regeneration that
moves a thousand lines but no API surface is not worth an entry; a property that
changed type is, whichever language it landed in.

## [Unreleased]

## [0.1.1] - 2026-08-07

No functional change. The four packages are identical to 0.1.0 apart from
their version number.

Released to exercise the automated publishing path end to end. The npm package
in 0.1.0 was published by hand, because npm will only accept a trusted
publisher for a package that already exists, so the workflow's npm job had
never actually run.

First release.

### Added

- Python, TypeScript, Go and C# clients for the prdb Public API, covering all
  49 operations. Generated with Kiota 1.34.1 from
  <https://apidocs.prdb.net/openapi/openapi.json>.
- An API-key constructor per language (`create_client`, `createClient`,
  `NewClient`, `PrdbClientFactory.Create`), sending the key in the `X-Api-Key`
  header.
- An anonymous constructor per language, because `GET /health` is the only
  endpoint reachable without a key.
- A redirect that leaves the API's origin is refused rather than followed, so
  the key cannot travel off-site. The HTTP stacks strip only `Authorization`
  across origins, and `X-Api-Key` is a custom header, so each wrapper enforces
  this itself.
- The authenticated constructors require an `https` base URL, so the key is
  never sent in cleartext. The anonymous ones still accept `http`.
