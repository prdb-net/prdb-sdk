# Prdb.Hashing

Computes the `osHash` and `pHash` values that the
[prdb Public API](https://apidocs.prdb.net/) identifies video files by — the same
values [Stash](https://github.com/stashapp/stash) computes, bit for bit.

Separate from the `Prdb.Sdk` package on purpose: this one starts processes and
needs ffmpeg, which an HTTP client has no business doing. Use them together or
either alone.

## Install

```bash
dotnet add package Prdb.Hashing
```

The perceptual hash shells out to **ffmpeg and ffprobe**, which have to be on
`PATH` or configured explicitly. OSHash does not need them.

## Use

```csharp
using Prdb.Hashing;

// OSHash: cheap, exact, and null for a file under 128 KiB.
string? osHash = OsHash.Compute("/media/scene.mkv");

// Perceptual hash: decodes 25 frames, so it belongs in a background queue.
var hasher = new VideoPerceptualHasher();
var result = await hasher.ComputeAsync("/media/scene.mkv");

if (result.IsComputed)
    Console.WriteLine(result.Hash);      // 16 lowercase hex characters
else
    Console.WriteLine(result.Outcome);   // ProbeFailed, FrameCaptureFailed, TimedOut, ...
```

Point it at a specific ffmpeg, and give it longer on slow storage:

```csharp
var hasher = new VideoPerceptualHasher(new VideoHashingOptions
{
    FfmpegPath = "/opt/ffmpeg/bin/ffmpeg",   // ffprobe is found next to it
    FrameTimeout = TimeSpan.FromMinutes(5),
});
```

Compare two perceptual hashes by Hamming distance, never for equality:

```csharp
int? distance = PerceptualHashDistance.Between(left, right);

if (distance <= PerceptualHashDistance.DefaultThreshold)   // 8 of 64 bits, as Stash uses
    // ... the same content in a different encode
```

## Two things worth knowing

**Failures are returned, not thrown.** On a real library, a truncated download
or a container ffmpeg cannot seek is routine. A caller working through a backlog
needs to record the outcome against that file and carry on, so only cancellation
propagates.

**Casing differs across the API boundary.** This package produces lowercase hex;
the API normalises to uppercase on write. Its validation is case-insensitive, so
lookups work either way — but a local store usually compares bytes, and there a
mirrored uppercase hash never matches a locally computed one. The miss is
silent. `FileHashes.Normalize` and `FileHashes.ForPrdbLookup` convert in each
direction.

## Compatibility

The method is specified in
[`docs/video-hashing.md`](https://github.com/prdb-net/prdb-sdk/blob/main/docs/video-hashing.md),
in enough detail to reimplement from, with public test vectors. This package is
a transcription of it and reproduces the reference's quirks deliberately — a
perceptual hash that does not match what everyone else computes is worth very
little.

## License

MIT — see [LICENSE](https://github.com/prdb-net/prdb-sdk/blob/main/LICENSE).
