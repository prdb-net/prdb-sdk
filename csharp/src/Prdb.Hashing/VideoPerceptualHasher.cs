using System.Globalization;
using System.Text.Json;

namespace Prdb.Hashing;

/// <summary>
/// Computes a video's perceptual hash the way Stash does: 25 frames sampled across the
/// middle 90% of the runtime, scaled to 160 pixels wide, assembled into a 5x5 montage and
/// hashed with <see cref="PerceptualHash"/>. Specified in <c>docs/video-hashing.md</c>.
/// <para>
/// The ffmpeg invocation is deliberately identical to Stash's, down to the <c>scale</c>
/// filter's <c>-2</c> height and the seek before the input. Which frame ffmpeg lands on
/// depends on those arguments, and a different frame is a different hash.
/// </para>
/// <para>
/// This decodes 25 frames per file, so it is far too slow to sit in the path of a file
/// being imported — it belongs in a background queue that works through a backlog at its
/// own pace. The type is stateless and safe to use concurrently, but each call is
/// CPU- and disk-heavy enough that running many at once is usually counterproductive.
/// </para>
/// </summary>
public sealed class VideoPerceptualHasher
{
    private const int FrameWidth = 160;

    private readonly IProcessRunner _processRunner;
    private readonly string _ffmpegPath;
    private readonly string _ffprobePath;
    private readonly TimeSpan _ffprobeTimeout;
    private readonly TimeSpan _frameTimeout;

    /// <summary>Uses ffmpeg and ffprobe from <c>PATH</c> with the default timeouts.</summary>
    public VideoPerceptualHasher()
        : this(new VideoHashingOptions())
    {
    }

    /// <summary>Uses the binaries and timeouts from <paramref name="options"/>.</summary>
    public VideoPerceptualHasher(VideoHashingOptions options)
        : this(options, new ProcessRunner())
    {
    }

    internal VideoPerceptualHasher(VideoHashingOptions options, IProcessRunner processRunner)
    {
        if (options is null)
            throw new ArgumentNullException(nameof(options));

        if (string.IsNullOrWhiteSpace(options.FfmpegPath))
            throw new ArgumentException("An ffmpeg path is required.", nameof(options));

        _processRunner = processRunner;

        // Copied rather than held, so that mutating the options afterwards cannot change
        // what a call in flight does.
        _ffmpegPath = options.FfmpegPath;
        _ffprobePath = string.IsNullOrWhiteSpace(options.FfprobePath)
            ? DeriveFfprobePath(options.FfmpegPath)
            : options.FfprobePath!;
        _ffprobeTimeout = options.FfprobeTimeout;
        _frameTimeout = options.FrameTimeout;
    }

    /// <summary>
    /// Hashes the video at <paramref name="videoPath"/>. Failures are reported in the
    /// result rather than thrown; only cancellation propagates.
    /// </summary>
    public async Task<PerceptualHashResult> ComputeAsync(string videoPath, CancellationToken ct = default)
    {
        if (!File.Exists(videoPath))
            return new PerceptualHashResult(PerceptualHashOutcome.SourceMissing, Error: "Source video does not exist.");

        var duration = await ProbeDurationAsync(videoPath, ct).ConfigureAwait(false);
        if (duration is null or <= 0)
            return new PerceptualHashResult(PerceptualHashOutcome.ProbeFailed, Error: "ffprobe returned no usable duration.");

        var frames = new List<PixelImage>(FrameMontage.FrameCount);

        // Stash starts with fast seek and, on the first failure, switches to accurate seek
        // for every remaining frame rather than retrying each one. Containers with broken
        // indexes fail the fast path consistently, so switching once is cheaper.
        var accurateSeek = false;

        foreach (var timestamp in SampleTimestamps(duration.Value))
        {
            var capture = await CaptureFrameAsync(videoPath, timestamp, accurateSeek, ct).ConfigureAwait(false);

            if (!capture.Succeeded && !accurateSeek)
            {
                accurateSeek = true;
                capture = await CaptureFrameAsync(videoPath, timestamp, accurateSeek, ct).ConfigureAwait(false);
            }

            if (!capture.Succeeded)
            {
                return capture.TimedOut
                    ? new PerceptualHashResult(PerceptualHashOutcome.TimedOut, Error: capture.Error, UsedAccurateSeek: accurateSeek)
                    : new PerceptualHashResult(PerceptualHashOutcome.FrameCaptureFailed, Error: capture.Error, UsedAccurateSeek: accurateSeek);
            }

            try
            {
                frames.Add(BmpImageReader.Read(capture.Data!));
            }
            catch (InvalidDataException ex)
            {
                return new PerceptualHashResult(PerceptualHashOutcome.FrameDecodeFailed, Error: ex.Message, UsedAccurateSeek: accurateSeek);
            }
        }

        try
        {
            return new PerceptualHashResult(
                PerceptualHashOutcome.Computed,
                PerceptualHash.ComputeHex(FrameMontage.Combine(frames)),
                UsedAccurateSeek: accurateSeek);
        }
        catch (ArgumentException ex)
        {
            // Frames of differing sizes, which would mean ffmpeg ignored the scale filter.
            return new PerceptualHashResult(PerceptualHashOutcome.FrameDecodeFailed, Error: ex.Message, UsedAccurateSeek: accurateSeek);
        }
    }

    /// <summary>
    /// The sample points, offset by 5% at each end so intros and end cards do not
    /// dominate the hash, then spread evenly across the remaining 90%.
    /// <para>
    /// Public because it is part of the specification and therefore worth checking
    /// directly.
    /// </para>
    /// </summary>
    public static IEnumerable<double> SampleTimestamps(double duration)
    {
        var offset = 0.05 * duration;
        var step = 0.9 * duration / FrameMontage.FrameCount;

        for (var i = 0; i < FrameMontage.FrameCount; i++)
            yield return offset + (i * step);
    }

    private async Task<FrameCapture> CaptureFrameAsync(
        string videoPath,
        double timestamp,
        bool accurateSeek,
        CancellationToken ct)
    {
        var arguments = new List<string> { "-loglevel", "error", "-y" };

        // Seeking before the input is the fast path: ffmpeg jumps to the nearest keyframe
        // rather than decoding up to the timestamp. After the input it is exact but slow.
        if (!accurateSeek)
        {
            arguments.Add("-ss");
            arguments.Add(FormatSeconds(timestamp));
        }

        arguments.Add("-i");
        arguments.Add(videoPath);

        if (accurateSeek)
        {
            arguments.Add("-ss");
            arguments.Add(FormatSeconds(timestamp));
        }

        arguments.AddRange([
            "-frames:v", "1",
            "-vf", $"scale={FrameWidth}:-2",
            "-c:v", "bmp",
            "-f", "rawvideo",
            "-",
        ]);

        var result = await _processRunner
            .RunAsync(new ProcessRequest(_ffmpegPath, arguments, CaptureBinaryOutput: true), _frameTimeout, ct)
            .ConfigureAwait(false);

        if (result.TimedOut)
            return new FrameCapture(false, null, true, "ffmpeg timed out capturing a frame.");

        if (result.ExitCode != 0 || result.BinaryOutput is null or { Length: 0 })
            return new FrameCapture(false, null, false, LimitError(result.StandardError) ?? "ffmpeg produced no frame.");

        return new FrameCapture(true, result.BinaryOutput, false, null);
    }

    private async Task<double?> ProbeDurationAsync(string videoPath, CancellationToken ct)
    {
        var result = await _processRunner.RunAsync(
                new ProcessRequest(
                    _ffprobePath,
                    ["-v", "quiet", "-print_format", "json", "-show_entries", "format=duration", videoPath]),
                _ffprobeTimeout,
                ct)
            .ConfigureAwait(false);

        if (result.TimedOut || result.ExitCode != 0)
            return null;

        try
        {
            using var document = JsonDocument.Parse(result.StandardOutput);
            if (!document.RootElement.TryGetProperty("format", out var format) ||
                !format.TryGetProperty("duration", out var durationElement))
                return null;

            return durationElement.ValueKind switch
            {
                JsonValueKind.Number => durationElement.GetDouble(),
                JsonValueKind.String when double.TryParse(
                    durationElement.GetString(),
                    NumberStyles.Float,
                    CultureInfo.InvariantCulture,
                    out var parsed) => parsed,
                _ => null,
            };
        }
        catch (JsonException)
        {
            return null;
        }
    }

    /// <summary>
    /// Matches Go's <c>fmt.Sprint</c> for a float64: the shortest representation that
    /// round-trips. Invariant culture is not optional — a comma as the decimal separator
    /// would make ffmpeg seek to the wrong place, or to zero.
    /// </summary>
    internal static string FormatSeconds(double seconds) =>
        seconds.ToString("R", CultureInfo.InvariantCulture);

    private static string DeriveFfprobePath(string ffmpegPath)
    {
        var directory = Path.GetDirectoryName(ffmpegPath);
        var extension = Path.GetExtension(ffmpegPath);
        var probeName = string.IsNullOrEmpty(extension) ? "ffprobe" : $"ffprobe{extension}";
        return string.IsNullOrEmpty(directory) ? probeName : Path.Combine(directory, probeName);
    }

    private static string? LimitError(string? error) =>
        string.IsNullOrWhiteSpace(error) ? null : error[..Math.Min(error!.Length, 2000)];

    private sealed record FrameCapture(bool Succeeded, byte[]? Data, bool TimedOut, string? Error);
}
