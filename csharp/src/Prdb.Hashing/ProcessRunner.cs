using System.Diagnostics;

namespace Prdb.Hashing;

/// <summary>
/// An ffmpeg or ffprobe invocation. Set <see cref="CaptureBinaryOutput"/> when the tool
/// writes image bytes to stdout, which cannot survive being decoded as text.
/// </summary>
internal sealed record ProcessRequest(
    string FileName,
    IReadOnlyList<string> Arguments,
    bool CaptureBinaryOutput = false);

internal sealed record ProcessResult(
    int? ExitCode,
    string StandardOutput,
    string StandardError,
    bool TimedOut,
    byte[]? BinaryOutput = null);

/// <summary>
/// The seam that lets the hasher be tested without ffmpeg installed. Internal: which
/// process is started, and with which arguments, is fixed by the specification and is not
/// something a caller may substitute.
/// </summary>
internal interface IProcessRunner
{
    Task<ProcessResult> RunAsync(ProcessRequest request, TimeSpan timeout, CancellationToken ct);
}

internal sealed class ProcessRunner : IProcessRunner
{
    public async Task<ProcessResult> RunAsync(ProcessRequest request, TimeSpan timeout, CancellationToken ct)
    {
        using var process = new Process();
        process.StartInfo = new ProcessStartInfo
        {
            FileName = request.FileName,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true,
        };

        foreach (var argument in request.Arguments)
            process.StartInfo.ArgumentList.Add(argument);

        try
        {
            process.Start();
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
            // A missing ffmpeg lands here, and it is the most likely setup mistake.
            return new ProcessResult(null, string.Empty, ex.Message, false);
        }

        // Binary output has to bypass the StreamReader entirely: it decodes bytes as
        // text, and any byte sequence that is not valid in the console encoding comes
        // back as replacement characters, which silently corrupts an image.
        Task<string>? stdoutTask = null;
        Task<byte[]>? stdoutBytesTask = null;
        if (request.CaptureBinaryOutput)
            stdoutBytesTask = ReadAllBytesAsync(process);
        else
            stdoutTask = process.StandardOutput.ReadToEndAsync(CancellationToken.None);

        var stderrTask = process.StandardError.ReadToEndAsync(CancellationToken.None);
        var exitTask = process.WaitForExitAsync(CancellationToken.None);
        var timedOut = false;

        var outputTask = (Task?)stdoutTask ?? stdoutBytesTask!;

        try
        {
            await exitTask.WaitAsync(timeout, ct).ConfigureAwait(false);
        }
        catch (TimeoutException)
        {
            timedOut = true;
            TryKillProcessTree(process);
        }
        catch (OperationCanceledException)
        {
            TryKillProcessTree(process);
            await DrainAfterTerminationAsync(exitTask, outputTask, stderrTask).ConfigureAwait(false);
            throw;
        }

        await DrainAfterTerminationAsync(exitTask, outputTask, stderrTask).ConfigureAwait(false);

        return new ProcessResult(
            process.HasExited ? process.ExitCode : null,
            stdoutTask is { IsCompletedSuccessfully: true } ? stdoutTask.Result : string.Empty,
            stderrTask.IsCompletedSuccessfully ? stderrTask.Result : string.Empty,
            timedOut,
            stdoutBytesTask is { IsCompletedSuccessfully: true } ? stdoutBytesTask.Result : null);
    }

    private static async Task<byte[]> ReadAllBytesAsync(Process process)
    {
        using var buffer = new MemoryStream();
        await process.StandardOutput.BaseStream.CopyToAsync(buffer, CancellationToken.None).ConfigureAwait(false);
        return buffer.ToArray();
    }

    private static void TryKillProcessTree(Process process)
    {
        try
        {
            if (!process.HasExited)
                process.Kill(entireProcessTree: true);
        }
        catch (InvalidOperationException)
        {
            // Already gone between the check and the kill.
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
            // Nothing useful to do: the caller is already reporting a failure.
        }
    }

    /// <summary>
    /// Waits for the pipes to close after the process has been asked to stop, so the
    /// handles are not left open. Bounded, because a killed process with a surviving
    /// grandchild can hold the pipe indefinitely.
    /// </summary>
    private static async Task DrainAfterTerminationAsync(Task exitTask, Task outputTask, Task<string> stderrTask)
    {
        try
        {
            await Task.WhenAll(exitTask, outputTask, stderrTask)
                .WaitAsync(TimeSpan.FromSeconds(10))
                .ConfigureAwait(false);
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
            // The result is reported from whatever completed; a drain failure is not
            // itself an outcome the caller can act on.
        }
    }
}
