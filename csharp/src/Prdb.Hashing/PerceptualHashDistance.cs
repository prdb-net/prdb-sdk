using System.Globalization;
using System.Numerics;

namespace Prdb.Hashing;

/// <summary>
/// Comparison of perceptual hashes.
/// <para>
/// Perceptual hashes are not compared for equality. Two encodes of the same content
/// produce hashes that differ in a handful of bits, so the question is how far apart they
/// are, measured as the number of differing bits (the Hamming distance). Equality would
/// only ever match content that happened to round identically, which throws away most of
/// the point of having a perceptual hash at all.
/// </para>
/// <para>
/// Note that the prdb Public API currently matches <c>pHash</c> for equality, so a
/// distance comparison is something a client does over its own files.
/// </para>
/// </summary>
public static class PerceptualHashDistance
{
    /// <summary>
    /// Bits that may differ before two hashes are considered different content.
    /// <para>
    /// 8 of 64 is the threshold Stash uses, and staying with it keeps judgements
    /// consistent with the tooling these hashes are compatible with. Raising it costs
    /// precision quickly: at this length, unrelated videos start colliding not far above
    /// this point.
    /// </para>
    /// </summary>
    public const int DefaultThreshold = 8;

    /// <summary>Number of differing bits between two hashes.</summary>
    public static int Between(ulong left, ulong right) => BitOperations.PopCount(left ^ right);

    /// <summary>
    /// Number of differing bits between two hashes in hex form, or <c>null</c> if either
    /// is not a 16-digit hex value.
    /// </summary>
    public static int? Between(string? left, string? right) =>
        TryParse(left, out var l) && TryParse(right, out var r) ? Between(l, r) : null;

    /// <summary>
    /// Parses the 16-digit hex form, in either case, with surrounding whitespace allowed.
    /// </summary>
    public static bool TryParse(string? hash, out ulong value)
    {
        value = 0;

        if (string.IsNullOrWhiteSpace(hash))
            return false;

        var trimmed = hash.Trim();
        return trimmed.Length == 16
            && ulong.TryParse(trimmed, NumberStyles.HexNumber, CultureInfo.InvariantCulture, out value);
    }
}
