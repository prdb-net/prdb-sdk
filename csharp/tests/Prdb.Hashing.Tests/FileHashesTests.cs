using Xunit;

namespace Prdb.Hashing.Tests;

public class FileHashesTests
{
    [Theory]
    [InlineData("ABCDEF0123456789", "abcdef0123456789")]
    [InlineData("  ABCDEF0123456789  ", "abcdef0123456789")]
    [InlineData("abcdef0123456789", "abcdef0123456789")]
    public void Normalize_LowercasesAndTrims(string input, string expected)
        => Assert.Equal(expected, FileHashes.Normalize(input));

    [Fact]
    public void Normalize_PassesNullThrough()
    {
        // An absent hash is a normal state — a file below the OSHash minimum, or one
        // whose perceptual hash has not been computed yet — and must not become "".
        Assert.Null(FileHashes.Normalize(null));
    }

    [Theory]
    [InlineData("abcdef0123456789", "ABCDEF0123456789")]
    [InlineData("  abcdef0123456789  ", "ABCDEF0123456789")]
    public void ForPrdbLookup_UppercasesAndTrims(string input, string expected)
        => Assert.Equal(expected, FileHashes.ForPrdbLookup(input));

    [Fact]
    public void RoundTrip_ThroughBothFormsIsStable()
    {
        // The pair has to be an identity on a locally computed hash, or a mirror slowly
        // fills with values that no longer match the files they describe.
        const string local = "0123456789abcdef";

        Assert.Equal(local, FileHashes.Normalize(FileHashes.ForPrdbLookup(local)));
    }
}
