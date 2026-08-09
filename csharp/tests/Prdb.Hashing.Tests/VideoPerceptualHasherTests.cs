using Xunit;

namespace Prdb.Hashing.Tests;

/// <summary>
/// Pins the ffmpeg invocation and the failure reporting without needing ffmpeg installed.
/// The command line is the part of the specification that a library cannot enforce, so it
/// is asserted here argument by argument.
/// </summary>
public class VideoPerceptualHasherTests
{
    [Fact]
    public void SampleTimestamps_SpanTheMiddleNinetyPercent()
    {
        var timestamps = VideoPerceptualHasher.SampleTimestamps(1000).ToList();

        Assert.Equal(25, timestamps.Count);

        // Stash offsets by 5% at each end and spreads the rest evenly, without a
        // half-step. The first sample therefore sits exactly on the 5% mark.
        Assert.Equal(50, timestamps[0], 9);
        Assert.Equal(86, timestamps[1], 9);
        Assert.Equal(914, timestamps[24], 9);

        // The last sample stays a full step short of the 95% mark, so nothing is ever
        // sampled from the final 8.6% of the runtime.
        Assert.True(timestamps[^1] < 950);
    }

    [Fact]
    public void SampleTimestamps_AreStrictlyIncreasing()
    {
        var timestamps = VideoPerceptualHasher.SampleTimestamps(3600).ToList();

        Assert.Equal(timestamps.OrderBy(t => t), timestamps);
        Assert.Equal(timestamps.Distinct().Count(), timestamps.Count);
    }

    [Theory]
    [InlineData(61.72835, "61.72835")]
    [InlineData(0.5, "0.5")]
    [InlineData(120, "120")]
    public void FormatSeconds_UsesAnInvariantDecimalPoint(double seconds, string expected)
    {
        // A comma here would make ffmpeg seek to zero and every hash would describe the
        // opening frames instead of the film.
        Assert.Equal(expected, VideoPerceptualHasher.FormatSeconds(seconds));
    }

    [Fact]
    public async Task ComputeAsync_WithMissingFile_ReportsSourceMissing()
    {
        var result = await CreateHasher(new StubProcessRunner()).ComputeAsync("/does/not/exist.mp4");

        Assert.Equal(PerceptualHashOutcome.SourceMissing, result.Outcome);
        Assert.Null(result.Hash);
        Assert.False(result.IsComputed);
    }

    [Fact]
    public async Task ComputeAsync_WhenProbeReturnsNoDuration_ReportsProbeFailed()
    {
        using var file = new TempFile();
        var runner = new StubProcessRunner { ProbeOutput = "{\"format\":{}}" };

        var result = await CreateHasher(runner).ComputeAsync(file.Path);

        Assert.Equal(PerceptualHashOutcome.ProbeFailed, result.Outcome);
    }

    [Fact]
    public async Task ComputeAsync_UsesStashesFfmpegArgumentsForEveryFrame()
    {
        using var file = new TempFile();
        var runner = new StubProcessRunner { FrameBuilder = () => SyntheticBmp(160, 90) };
        var options = new VideoHashingOptions { FfmpegPath = Path.Combine("/opt", "bin", "ffmpeg") };

        var result = await new VideoPerceptualHasher(options, runner).ComputeAsync(file.Path);

        Assert.True(result.IsComputed);
        Assert.Equal(25, runner.FfmpegInvocations.Count);

        var first = runner.FfmpegInvocations[0];
        Assert.Equal(Path.Combine("/opt", "bin", "ffmpeg"), first.FileName);
        Assert.True(first.CaptureBinaryOutput);

        var arguments = first.Arguments.ToArray();
        AssertContainsInOrder(arguments, "-ss", "5", "-i", file.Path);
        AssertContainsInOrder(arguments, "-vf", "scale=160:-2", "-c:v", "bmp", "-f", "rawvideo", "-");

        // Seeking before the input is the fast path; it must come ahead of -i.
        Assert.True(Array.IndexOf(arguments, "-ss") < Array.IndexOf(arguments, "-i"));

        // ffprobe is derived from the ffmpeg path so a bundled binary is found next to it.
        var probe = Assert.Single(runner.ProbeInvocations);
        Assert.Equal(Path.Combine("/opt", "bin", "ffprobe"), probe.FileName);
    }

    [Fact]
    public async Task ComputeAsync_UsesAnExplicitFfprobePathWhenGiven()
    {
        using var file = new TempFile();
        var runner = new StubProcessRunner { FrameBuilder = () => SyntheticBmp(160, 90) };
        var options = new VideoHashingOptions
        {
            FfmpegPath = "ffmpeg",
            FfprobePath = Path.Combine("/elsewhere", "ffprobe"),
        };

        await new VideoPerceptualHasher(options, runner).ComputeAsync(file.Path);

        Assert.Equal(Path.Combine("/elsewhere", "ffprobe"), Assert.Single(runner.ProbeInvocations).FileName);
    }

    [Fact]
    public async Task ComputeAsync_WhenFastSeekFails_RetriesWithAccurateSeekAndKeepsIt()
    {
        using var file = new TempFile();
        var runner = new StubProcessRunner
        {
            FrameBuilder = () => SyntheticBmp(160, 90),
            FailFirstFfmpegCall = true,
        };

        var result = await CreateHasher(runner).ComputeAsync(file.Path);

        Assert.True(result.IsComputed);
        Assert.True(result.UsedAccurateSeek);

        // 25 frames plus the one failed fast-seek attempt.
        Assert.Equal(26, runner.FfmpegInvocations.Count);

        // The retry and every frame after it seek after the input, which is accurate but
        // slow. Stash switches once rather than retrying each frame.
        var retry = runner.FfmpegInvocations[1].Arguments.ToArray();
        Assert.True(Array.IndexOf(retry, "-ss") > Array.IndexOf(retry, "-i"));

        var last = runner.FfmpegInvocations[^1].Arguments.ToArray();
        Assert.True(Array.IndexOf(last, "-ss") > Array.IndexOf(last, "-i"));
    }

    [Fact]
    public async Task ComputeAsync_WithoutAFallback_DoesNotReportAccurateSeek()
    {
        using var file = new TempFile();
        var runner = new StubProcessRunner { FrameBuilder = () => SyntheticBmp(160, 90) };

        var result = await CreateHasher(runner).ComputeAsync(file.Path);

        Assert.False(result.UsedAccurateSeek);
    }

    [Fact]
    public async Task ComputeAsync_WhenAFrameCannotBeDecoded_ReportsFrameDecodeFailed()
    {
        using var file = new TempFile();
        var runner = new StubProcessRunner { FrameBuilder = () => [0x00, 0x01, 0x02, 0x03] };

        var result = await CreateHasher(runner).ComputeAsync(file.Path);

        Assert.Equal(PerceptualHashOutcome.FrameDecodeFailed, result.Outcome);
    }

    [Fact]
    public async Task ComputeAsync_WhenFfmpegKeepsFailing_ReportsFrameCaptureFailed()
    {
        using var file = new TempFile();
        var runner = new StubProcessRunner { FrameBuilder = () => [] };

        var result = await CreateHasher(runner).ComputeAsync(file.Path);

        Assert.Equal(PerceptualHashOutcome.FrameCaptureFailed, result.Outcome);
        Assert.Null(result.Hash);
    }

    [Fact]
    public async Task ComputeAsync_WhenFfmpegTimesOut_ReportsTimedOut()
    {
        using var file = new TempFile();
        var runner = new StubProcessRunner { TimeOutFfmpeg = true };

        var result = await CreateHasher(runner).ComputeAsync(file.Path);

        // Distinct from a capture failure: a timeout is worth retrying later, a broken
        // file is not.
        Assert.Equal(PerceptualHashOutcome.TimedOut, result.Outcome);
    }

    [Fact]
    public void Constructor_RejectsAnEmptyFfmpegPath()
        => Assert.Throws<ArgumentException>(() =>
            new VideoPerceptualHasher(new VideoHashingOptions { FfmpegPath = "  " }));

    [Fact]
    public async Task ComputeAsync_IgnoresOptionsMutatedAfterConstruction()
    {
        using var file = new TempFile();
        var runner = new StubProcessRunner { FrameBuilder = () => SyntheticBmp(160, 90) };
        var options = new VideoHashingOptions { FfmpegPath = "ffmpeg" };
        var hasher = new VideoPerceptualHasher(options, runner);

        options.FfmpegPath = "somewhere-else";
        await hasher.ComputeAsync(file.Path);

        Assert.Equal("ffmpeg", runner.FfmpegInvocations[0].FileName);
    }

    private static VideoPerceptualHasher CreateHasher(IProcessRunner runner) =>
        new(new VideoHashingOptions(), runner);

    private static void AssertContainsInOrder(string[] actual, params string[] expected)
    {
        var index = 0;
        foreach (var value in expected)
        {
            index = Array.IndexOf(actual, value, index);
            Assert.True(index >= 0, $"'{value}' is missing or out of order in: {string.Join(' ', actual)}");
            index++;
        }
    }

    /// <summary>A minimal 24-bit bottom-up BMP, the shape ffmpeg's bmp encoder emits.</summary>
    internal static byte[] SyntheticBmp(int width, int height)
    {
        var rowStride = ((width * 3) + 3) & ~3;
        var pixelDataSize = rowStride * height;
        var buffer = new byte[54 + pixelDataSize];

        buffer[0] = (byte)'B';
        buffer[1] = (byte)'M';
        BitConverter.GetBytes(buffer.Length).CopyTo(buffer, 2);
        BitConverter.GetBytes(54).CopyTo(buffer, 10);
        BitConverter.GetBytes(40).CopyTo(buffer, 14);
        BitConverter.GetBytes(width).CopyTo(buffer, 18);
        BitConverter.GetBytes(height).CopyTo(buffer, 22);
        BitConverter.GetBytes((short)1).CopyTo(buffer, 26);
        BitConverter.GetBytes((short)24).CopyTo(buffer, 28);
        BitConverter.GetBytes(0).CopyTo(buffer, 30);

        for (var i = 0; i < pixelDataSize; i++)
            buffer[54 + i] = (byte)(i % 251);

        return buffer;
    }

    private sealed class TempFile : IDisposable
    {
        public TempFile() => Path = System.IO.Path.GetTempFileName();

        public string Path { get; }

        public void Dispose() => File.Delete(Path);
    }

    internal sealed record RecordedInvocation(string FileName, IReadOnlyList<string> Arguments, bool CaptureBinaryOutput);

    internal sealed class StubProcessRunner : IProcessRunner
    {
        public string ProbeOutput { get; set; } = "{\"format\":{\"duration\":\"100.0\"}}";

        public Func<byte[]>? FrameBuilder { get; set; }

        public bool FailFirstFfmpegCall { get; set; }

        public bool TimeOutFfmpeg { get; set; }

        public List<RecordedInvocation> ProbeInvocations { get; } = [];

        public List<RecordedInvocation> FfmpegInvocations { get; } = [];

        public Task<ProcessResult> RunAsync(ProcessRequest request, TimeSpan timeout, CancellationToken ct)
        {
            var recorded = new RecordedInvocation(request.FileName, request.Arguments, request.CaptureBinaryOutput);

            // The hasher derives the ffprobe path from the ffmpeg one, so the file name is
            // what tells the two apart — which also keeps that derivation under test.
            if (request.FileName.Contains("ffprobe", StringComparison.Ordinal))
            {
                ProbeInvocations.Add(recorded);
                return Task.FromResult(new ProcessResult(0, ProbeOutput, string.Empty, false));
            }

            FfmpegInvocations.Add(recorded);

            if (TimeOutFfmpeg)
                return Task.FromResult(new ProcessResult(null, string.Empty, string.Empty, true));

            if (FailFirstFfmpegCall && FfmpegInvocations.Count == 1)
                return Task.FromResult(new ProcessResult(1, string.Empty, "seek failed", false));

            var frame = FrameBuilder?.Invoke() ?? [];
            var exitCode = frame.Length == 0 ? 1 : 0;

            return Task.FromResult(new ProcessResult(exitCode, string.Empty, string.Empty, false, frame));
        }
    }
}
