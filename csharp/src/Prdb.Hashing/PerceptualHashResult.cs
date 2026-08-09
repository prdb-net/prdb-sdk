namespace Prdb.Hashing;

/// <summary>Why a video did or did not produce a perceptual hash.</summary>
public enum PerceptualHashOutcome
{
    /// <summary>A hash was computed.</summary>
    Computed = 0,

    /// <summary>The file does not exist.</summary>
    SourceMissing = 1,

    /// <summary>ffprobe reported no usable duration, so the sample points are unknown.</summary>
    ProbeFailed = 2,

    /// <summary>ffmpeg could not produce one of the 25 frames, even with accurate seek.</summary>
    FrameCaptureFailed = 3,

    /// <summary>A frame came back as something other than a BMP this reader handles.</summary>
    FrameDecodeFailed = 4,

    /// <summary>ffprobe or ffmpeg exceeded its timeout.</summary>
    TimedOut = 5,
}

/// <summary>
/// The outcome of hashing one video.
/// <para>
/// A failure is reported rather than thrown, because on a real library it is a routine
/// event — a truncated download, a file that is not really a video, a container ffmpeg
/// cannot seek — and a caller working through a backlog needs to record it against that
/// file and carry on.
/// </para>
/// </summary>
/// <param name="Outcome">Why the hash was or was not produced.</param>
/// <param name="Hash">The 16 lowercase hex characters, when <paramref name="Outcome"/> is
/// <see cref="PerceptualHashOutcome.Computed"/>; otherwise null.</param>
/// <param name="Error">A short description of the failure, when there was one.</param>
/// <param name="UsedAccurateSeek">Whether ffmpeg fell back to accurate seek. Informational:
/// the value is correct either way, but the file took much longer than usual.</param>
public sealed record PerceptualHashResult(
    PerceptualHashOutcome Outcome,
    string? Hash = null,
    string? Error = null,
    bool UsedAccurateSeek = false)
{
    /// <summary>Whether <see cref="Hash"/> carries a value.</summary>
    public bool IsComputed => Outcome == PerceptualHashOutcome.Computed;
}
