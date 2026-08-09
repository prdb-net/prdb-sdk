using System.Buffers.Binary;
using Xunit;

namespace Prdb.Hashing.Tests;

public class OsHashTests : IDisposable
{
    private readonly string _directory =
        Path.Combine(Path.GetTempPath(), $"prdb-oshash-{Guid.NewGuid():N}");

    public OsHashTests() => Directory.CreateDirectory(_directory);

    public void Dispose()
    {
        if (Directory.Exists(_directory))
            Directory.Delete(_directory, recursive: true);

        GC.SuppressFinalize(this);
    }

    [Fact]
    public void Compute_SumsTheFileSizeAndBothEndBlocks()
    {
        // A file of exactly two blocks, all zero except one uint64 in each block. The
        // expected value is then computable by hand, which is what makes this a check on
        // the algorithm rather than on itself.
        const long size = 131072;
        var bytes = new byte[size];
        BinaryPrimitives.WriteUInt64LittleEndian(bytes.AsSpan(0), 0x1111111111111111);
        BinaryPrimitives.WriteUInt64LittleEndian(bytes.AsSpan(65536), 0x2222222222222222);

        var path = Write("two-blocks.bin", bytes);

        var expected = unchecked((ulong)size + 0x1111111111111111 + 0x2222222222222222);
        Assert.Equal(expected.ToString("x016"), OsHash.Compute(path));
    }

    [Fact]
    public void Compute_ReadsTheLastBlockFromTheEndNotTheSecondBlock()
    {
        // A file larger than two blocks, with a marker in the middle that must NOT be
        // read and one at the very end that must be. Reading sequentially instead of
        // seeking to the end gives a different, plausible-looking answer.
        var bytes = new byte[65536 * 4];
        BinaryPrimitives.WriteUInt64LittleEndian(bytes.AsSpan(65536), 0xAAAAAAAAAAAAAAAA);
        BinaryPrimitives.WriteUInt64LittleEndian(bytes.AsSpan(bytes.Length - 8), 0x0000000000000005);

        var path = Write("four-blocks.bin", bytes);

        var expected = unchecked((ulong)bytes.Length + 0x0000000000000005);
        Assert.Equal(expected.ToString("x016"), OsHash.Compute(path));
    }

    [Fact]
    public void Compute_WrapsOnOverflowRatherThanThrowing()
    {
        var bytes = new byte[131072];
        BinaryPrimitives.WriteUInt64LittleEndian(bytes.AsSpan(0), ulong.MaxValue);

        var path = Write("overflow.bin", bytes);

        // 131072 + (2^64 - 1) wraps to 131071.
        Assert.Equal((131071UL).ToString("x016"), OsHash.Compute(path));
    }

    [Theory]
    [InlineData(0)]
    [InlineData(1)]
    [InlineData(131071)]
    public void Compute_ReturnsNullForAFileTooShortToHash(int size)
    {
        // Not zero and not an exception: a short file genuinely has no OSHash, and
        // padding it to produce one would invent a value nobody else would compute.
        var path = Write($"short-{size}.bin", new byte[size]);

        Assert.Null(OsHash.Compute(path));
    }

    [Fact]
    public void Compute_ReturnsNullForAMissingFile()
        => Assert.Null(OsHash.Compute(Path.Combine(_directory, "absent.bin")));

    [Fact]
    public void Compute_IsAlways16LowercaseHexCharacters()
    {
        // A value that needs fewer digits must still be padded: the API stores char(16),
        // and an unpadded hash never matches.
        var bytes = new byte[131072];
        var path = Write("zeroes.bin", bytes);

        Assert.Equal("0000000000020000", OsHash.Compute(path));
    }

    [Fact]
    public void TryCompute_ReportsSuccessForANormalFile()
    {
        var path = Write("normal.bin", new byte[131072]);

        Assert.True(OsHash.TryCompute(path, out var hash));
        Assert.NotNull(hash);
    }

    [Fact]
    public void TryCompute_ReportsSuccessWithANullHashForAShortFile()
    {
        // "Readable, but too short" and "could not be read" are different answers, and a
        // caller that conflates them resets bookkeeping that was correct.
        var path = Write("tiny.bin", new byte[10]);

        Assert.True(OsHash.TryCompute(path, out var hash));
        Assert.Null(hash);
    }

    private string Write(string name, byte[] content)
    {
        var path = Path.Combine(_directory, name);
        File.WriteAllBytes(path, content);
        return path;
    }
}
