using Xunit;

namespace Prdb.Hashing.Tests;

/// <summary>
/// Drives the real ffmpeg binary end to end: seek, scale, BMP encode, decode, montage,
/// hash. The stubbed tests pin the arguments; only this one proves the bytes that come
/// back are actually decodable into the frames the hash expects.
/// <para>
/// It cannot assert a specific hash — that is the level 3 test vector, which needs an
/// ffmpeg version attached to it and does not exist yet. What it can assert is that the
/// chain runs, is reproducible, and distinguishes different content.
/// </para>
/// <para>
/// Skipped where ffmpeg is absent, which includes the CI image.
/// </para>
/// </summary>
public sealed class VideoPerceptualHasherEndToEndTests : IAsyncLifetime
{
    private readonly string _directory =
        Path.Combine(Path.GetTempPath(), $"prdb-phash-e2e-{Guid.NewGuid():N}");

    private string _videoPath = string.Empty;

    public async Task InitializeAsync()
    {
        if (!FfmpegProbe.IsAvailable.Value)
            return;

        Directory.CreateDirectory(_directory);
        _videoPath = Path.Combine(_directory, "sample.mp4");

        // A deterministic synthetic clip: testsrc2 renders a moving pattern, so the 25
        // sample points genuinely differ from each other.
        await RenderAsync(_videoPath, "testsrc2=size=640x360:rate=10:duration=20");
    }

    public Task DisposeAsync()
    {
        if (Directory.Exists(_directory))
            Directory.Delete(_directory, recursive: true);

        return Task.CompletedTask;
    }

    [FfmpegFact]
    public async Task ComputeAsync_HashesARealVideo()
    {
        var result = await new VideoPerceptualHasher().ComputeAsync(_videoPath);

        Assert.True(result.IsComputed, result.Error);
        Assert.Matches("^[0-9a-f]{16}$", result.Hash!);

        // A hash of zero would mean every DCT coefficient landed on the same side of the
        // threshold, which for a moving test pattern means the frames never decoded.
        Assert.NotEqual("0000000000000000", result.Hash);
    }

    [FfmpegFact]
    public async Task ComputeAsync_IsReproducibleForTheSameFile()
    {
        var first = await new VideoPerceptualHasher().ComputeAsync(_videoPath);
        var second = await new VideoPerceptualHasher().ComputeAsync(_videoPath);

        Assert.Equal(first.Hash, second.Hash);
    }

    [FfmpegFact]
    public async Task ComputeAsync_DiffersForDifferentContent()
    {
        var otherPath = Path.Combine(_directory, "other.mp4");
        await RenderAsync(otherPath, "smptebars=size=640x360:rate=10:duration=20");

        var first = await new VideoPerceptualHasher().ComputeAsync(_videoPath);
        var second = await new VideoPerceptualHasher().ComputeAsync(otherPath);

        Assert.NotEqual(first.Hash, second.Hash);
    }

    [FfmpegFact]
    public async Task ComputeAsync_WithAMissingFfmpeg_ReportsProbeFailedRatherThanThrowing()
    {
        // The most likely setup mistake. It has to arrive as a result, because a caller
        // working through a backlog needs to record it against the file and carry on.
        var hasher = new VideoPerceptualHasher(new VideoHashingOptions
        {
            FfmpegPath = Path.Combine(_directory, "no-such-ffmpeg"),
        });

        var result = await hasher.ComputeAsync(_videoPath);

        Assert.Equal(PerceptualHashOutcome.ProbeFailed, result.Outcome);
    }

    private static async Task RenderAsync(string path, string source)
    {
        var result = await new ProcessRunner().RunAsync(
            new ProcessRequest("ffmpeg",
            [
                "-y", "-loglevel", "error",
                "-f", "lavfi", "-i", source,
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                path,
            ]),
            TimeSpan.FromMinutes(2),
            CancellationToken.None);

        if (result.ExitCode != 0)
            throw new InvalidOperationException($"ffmpeg failed to render the fixture: {result.StandardError}");
    }
}
