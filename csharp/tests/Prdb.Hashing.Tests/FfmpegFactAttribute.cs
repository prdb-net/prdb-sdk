using System.Diagnostics;
using Xunit;

namespace Prdb.Hashing.Tests;

/// <summary>
/// A fact that only runs where an ffmpeg binary is on PATH.
/// <para>
/// The CI image is the plain .NET SDK and has no ffmpeg, so these would fail there for a
/// reason that says nothing about the code. They do run on developer machines, which is
/// where an ffmpeg change would actually show up.
/// </para>
/// </summary>
public sealed class FfmpegFactAttribute : FactAttribute
{
    public FfmpegFactAttribute()
    {
        if (!FfmpegProbe.IsAvailable.Value)
            Skip = "ffmpeg is not installed on this machine.";
    }
}

public static class FfmpegProbe
{
    public static readonly Lazy<bool> IsAvailable = new(() =>
    {
        try
        {
            using var process = Process.Start(new ProcessStartInfo("ffmpeg", "-version")
            {
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true,
            });

            if (process is null)
                return false;

            process.WaitForExit(10_000);
            return process.HasExited && process.ExitCode == 0;
        }
        catch
        {
            return false;
        }
    });
}
