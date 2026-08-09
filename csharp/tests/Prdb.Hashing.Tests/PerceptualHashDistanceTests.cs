using Xunit;

namespace Prdb.Hashing.Tests;

public class PerceptualHashDistanceTests
{
    [Theory]
    [InlineData(0UL, 0UL, 0)]
    [InlineData(0UL, 1UL, 1)]
    [InlineData(0UL, 3UL, 2)]
    [InlineData(0UL, ulong.MaxValue, 64)]
    [InlineData(0xFFFFFFFF00000000UL, 0x00000000FFFFFFFFUL, 64)]
    public void Between_CountsDifferingBits(ulong left, ulong right, int expected)
        => Assert.Equal(expected, PerceptualHashDistance.Between(left, right));

    [Fact]
    public void Between_IsSymmetric()
        => Assert.Equal(
            PerceptualHashDistance.Between(0x0123456789abcdefUL, 0xfedcba9876543210UL),
            PerceptualHashDistance.Between(0xfedcba9876543210UL, 0x0123456789abcdefUL));

    [Fact]
    public void Between_InHexForm_MatchesTheNumericForm()
        => Assert.Equal(4, PerceptualHashDistance.Between("0000000000000000", "000000000000000f"));

    [Fact]
    public void Between_InHexForm_IgnoresCase()
        => Assert.Equal(0, PerceptualHashDistance.Between("ABCDEF0123456789", "abcdef0123456789"));

    [Theory]
    [InlineData(null, "0000000000000000")]
    [InlineData("0000000000000000", "nonsense")]
    [InlineData("short", "0000000000000000")]
    public void Between_InHexForm_ReturnsNullForAnUnusableValue(string? left, string? right)
    {
        // Not zero, and not the maximum: a caller that cannot parse a hash must be able
        // to tell that apart from a hash that genuinely matches or genuinely does not.
        Assert.Null(PerceptualHashDistance.Between(left, right));
    }

    [Theory]
    [InlineData("0123456789abcdef", 0x0123456789abcdefUL)]
    [InlineData("FFFFFFFFFFFFFFFF", ulong.MaxValue)]
    [InlineData("  0123456789ABCDEF  ", 0x0123456789abcdefUL)]
    public void TryParse_AcceptsBothCasesAndTrims(string input, ulong expected)
    {
        Assert.True(PerceptualHashDistance.TryParse(input, out var value));
        Assert.Equal(expected, value);
    }

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("   ")]
    [InlineData("0123456789abcde")]   // 15 characters
    [InlineData("0123456789abcdef0")] // 17 characters
    [InlineData("0123456789abcdeg")]  // not hex
    public void TryParse_RejectsAnythingThatIsNotA64BitHexHash(string? input)
    {
        // A short or malformed value must not be silently zero-extended: 0 is a real hash
        // and would match every dark or blank video within the threshold.
        Assert.False(PerceptualHashDistance.TryParse(input, out var value));
        Assert.Equal(0UL, value);
    }

    [Fact]
    public void DefaultThreshold_IsTheOneStashUses()
    {
        // Changing this changes which files a caller treats as duplicates, so it is
        // pinned rather than left as an implementation detail.
        Assert.Equal(8, PerceptualHashDistance.DefaultThreshold);
    }
}
