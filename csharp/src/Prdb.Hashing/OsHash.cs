using System.Buffers.Binary;

namespace Prdb.Hashing;

/// <summary>
/// The OpenSubtitles hash (OSHash) for a file, as the prdb Public API's <c>osHash</c>
/// field carries it. Specified in <c>docs/video-hashing.md</c>.
/// <para>
/// It reads 64 KiB from each end of the file, which makes it cheap on large files and
/// stable under renaming — but it changes completely when the file is re-encoded, which
/// is what the perceptual hash is for.
/// </para>
/// </summary>
public static class OsHash
{
    private const int BlockSize = 65536; // 64 KiB

    /// <summary>
    /// The smallest file that has an OSHash. Anything below this is too short to supply
    /// the two blocks the algorithm reads.
    /// </summary>
    public const long MinimumFileSize = BlockSize * 2;

    /// <summary>
    /// Returns the OSHash for <paramref name="filePath"/> as 16 lowercase hex characters,
    /// or <c>null</c> if the file does not exist or is smaller than
    /// <see cref="MinimumFileSize"/>.
    /// </summary>
    /// <exception cref="IOException">The file could not be read.</exception>
    /// <exception cref="UnauthorizedAccessException">The file could not be opened.</exception>
    public static string? Compute(string filePath)
    {
        var info = new FileInfo(filePath);
        if (!info.Exists || info.Length < MinimumFileSize)
            return null;

        var hash = (ulong)info.Length;
        var buffer = new byte[BlockSize];

        using var stream = File.OpenRead(filePath);

        stream.ReadExactly(buffer);
        Accumulate(ref hash, buffer);

        stream.Seek(-BlockSize, SeekOrigin.End);
        stream.ReadExactly(buffer);
        Accumulate(ref hash, buffer);

        // Lowercase hex is the canonical form; see FileHashes for the conversion the API
        // boundary needs.
        return hash.ToString("x016");
    }

    /// <summary>
    /// Like <see cref="Compute"/>, but reports a file that cannot be read right now
    /// instead of throwing. Returns <c>false</c> when the file is locked by another
    /// process or unreadable; <paramref name="hash"/> then carries no meaning.
    /// <para>
    /// A file being written or moved is a normal state on a host that downloads around
    /// the clock, and it is not the same answer as "this file has no hash". A caller that
    /// cannot tell the two apart either abandons the whole run over one busy file, or
    /// treats the missing hash as a content change and resets bookkeeping that was
    /// correct.
    /// </para>
    /// </summary>
    public static bool TryCompute(string filePath, out string? hash)
    {
        try
        {
            hash = Compute(filePath);
            return true;
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
        {
            hash = null;
            return false;
        }
    }

    private static void Accumulate(ref ulong hash, byte[] buffer)
    {
        for (var i = 0; i < buffer.Length; i += 8)
            hash += BinaryPrimitives.ReadUInt64LittleEndian(buffer.AsSpan(i, 8));
    }
}
