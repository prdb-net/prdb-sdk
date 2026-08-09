using Xunit;

namespace Prdb.Hashing.Tests;

/// <summary>
/// The level 3 vectors: a video file to a hash, which adds ffmpeg's frame selection to
/// everything the other levels cover.
/// <para>
/// Skipped where ffmpeg is absent, which includes CI. Unlike levels 1 and 2 these are also
/// pinned to an ffmpeg build — the one named in the vector file — so a different build may
/// legitimately disagree here while the arithmetic still matches. A failure is a reason to
/// compare ffmpeg versions before suspecting the code.
/// </para>
/// </summary>
public sealed class Level3VectorTests : IDisposable
{
    private readonly string _directory =
        Path.Combine(Path.GetTempPath(), $"prdb-phash-l3-{Guid.NewGuid():N}");

    public Level3VectorTests() => Directory.CreateDirectory(_directory);

    public void Dispose()
    {
        if (Directory.Exists(_directory))
            Directory.Delete(_directory, recursive: true);
    }

    [FfmpegFact]
    public async Task VideoFiles_MatchTheSpecification()
    {
        foreach (var (file, source, contentSha256, expected) in TestVectors.Level3())
        {
            var path = Path.Combine(_directory, file);
            await RenderAsync(path, source);

            // The +bitexact flags in the documented command are what make this digest
            // reproducible at all: without them Matroska writes a random segment UID, so
            // the same command produces a different file every run.
            Assert.Equal(contentSha256, TestVectors.Sha256Hex(await File.ReadAllBytesAsync(path)));

            var result = await new VideoPerceptualHasher().ComputeAsync(path);

            Assert.True(result.IsComputed, $"{file}: {result.Outcome} {result.Error}");
            Assert.Equal(expected, result.Hash);
        }
    }

    /// <summary>The generation command from the specification, argument for argument.</summary>
    private static async Task RenderAsync(string path, string source)
    {
        var result = await new ProcessRunner().RunAsync(
            new ProcessRequest("ffmpeg",
            [
                "-y", "-loglevel", "error",
                "-f", "lavfi", "-i", source,
                "-c:v", "ffv1", "-level", "3", "-pix_fmt", "yuv420p",
                "-fflags", "+bitexact", "-flags:v", "+bitexact",
                path,
            ]),
            TimeSpan.FromMinutes(2),
            CancellationToken.None);

        if (result.ExitCode != 0)
            throw new InvalidOperationException($"ffmpeg failed to render the fixture: {result.StandardError}");
    }
}
