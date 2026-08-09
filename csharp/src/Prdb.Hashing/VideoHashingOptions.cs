namespace Prdb.Hashing;

/// <summary>
/// Where the external tools live and how long they may take.
/// <para>
/// Deliberately small. Everything that decides what the hash <i>is</i> — the frame count,
/// the sample points, the scale filter, the seek strategy — is fixed by
/// <c>docs/video-hashing.md</c> and is not configurable: a knob there would produce
/// values that no longer compare with anyone else's.
/// </para>
/// </summary>
public sealed class VideoHashingOptions
{
    /// <summary>
    /// Path to the ffmpeg binary, or just its name to have it found on <c>PATH</c>.
    /// </summary>
    public string FfmpegPath { get; set; } = "ffmpeg";

    /// <summary>
    /// Path to the ffprobe binary. When null, it is derived from
    /// <see cref="FfmpegPath"/> by swapping the file name and keeping the directory and
    /// extension, which is where a normal install puts it.
    /// </summary>
    public string? FfprobePath { get; set; }

    /// <summary>How long ffprobe may take to report the duration.</summary>
    public TimeSpan FfprobeTimeout { get; set; } = TimeSpan.FromSeconds(30);

    /// <summary>
    /// How long ffmpeg may take per frame — not per file. A hash seeks 25 times, and an
    /// accurate seek near the end of a long file decodes everything before it.
    /// </summary>
    public TimeSpan FrameTimeout { get; set; } = TimeSpan.FromMinutes(2);
}
