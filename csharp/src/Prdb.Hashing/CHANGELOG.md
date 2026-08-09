# Changelog — Prdb.Hashing

This package is versioned and released separately from the four SDKs, because it
is not generated from the OpenAPI document and does not change when the API
does. It releases from a `hashing/v*` tag; the SDKs release from `v*`.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**A change to a hash value is a breaking change**, whatever it does to the API
surface. Every stored hash a user has computed with an earlier version stops
matching, and the comparison is silent about it — files simply go unidentified.

## [Unreleased]

### Added

- Initial release. `OsHash` and `PerceptualHash` compute the values the prdb
  Public API identifies files by, matching what Stash produces bit for bit, as
  specified in [`docs/video-hashing.md`](../../../docs/video-hashing.md).

  ```csharp
  string? osHash = OsHash.Compute(path);

  var result = await new VideoPerceptualHasher().ComputeAsync(path);
  if (result.IsComputed)
      Console.WriteLine(result.Hash);
  ```

  `VideoPerceptualHasher` shells out to ffmpeg and ffprobe; `OsHash` needs
  neither. Failures come back as a `PerceptualHashOutcome` rather than an
  exception, because on a real library a truncated download or an unseekable
  container is routine and a caller working through a backlog has to carry on.

- `PerceptualHashDistance` compares perceptual hashes by Hamming distance, with
  `DefaultThreshold` at the 8-of-64 bits Stash uses. Comparing them for equality
  makes a perceptual hash into a worse `osHash`.

- `FileHashes` converts between this package's lowercase output and the
  uppercase form the API stores. The API validates case-insensitively, so
  lookups work either way, but a local store usually compares bytes — and there
  a mirrored uppercase hash never matches a locally computed one, silently.

- Public test vectors at the image and montage levels, generated from published
  formulas rather than shipped as binary fixtures, so an implementation in any
  language can check itself against the same numbers.
