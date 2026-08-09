using System.Diagnostics.CodeAnalysis;

namespace Prdb.Hashing;

/// <summary>
/// Casing conversion at the prdb API boundary.
/// <para>
/// This package computes hashes as lowercase hex, while the API normalises <c>osHash</c>
/// and <c>pHash</c> to uppercase on write. Its validation is case-insensitive, so a
/// lookup works either way — but a local store usually compares bytes (SQLite's default
/// <c>BINARY</c> collation, for instance), and there a mirrored uppercase hash never
/// matches a locally computed one. The miss is silent: the file simply stays
/// unidentified.
/// </para>
/// <para>
/// Convert every hash crossing the boundary rather than taking it as it arrives, so that
/// no comparison on either side depends on a collation setting.
/// </para>
/// </summary>
public static class FileHashes
{
    /// <summary>
    /// The local storage form: lowercase hex, matching what <see cref="OsHash"/> and
    /// <see cref="PerceptualHash"/> produce. Apply this to every hash read from the API
    /// before writing it to a local table.
    /// </summary>
    [return: NotNullIfNotNull(nameof(value))]
    public static string? Normalize(string? value)
        => value is null ? null : value.Trim().ToLowerInvariant();

    /// <summary>
    /// The form the API stores. Used when a hash is sent as a lookup key, so the match on
    /// their side is byte-for-byte rather than a favour granted by the server's
    /// collation.
    /// </summary>
    public static string ForPrdbLookup(string value)
    {
        if (value is null)
            throw new ArgumentNullException(nameof(value));

        return value.Trim().ToUpperInvariant();
    }
}
