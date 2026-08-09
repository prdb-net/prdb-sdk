using Xunit;

namespace Prdb.Hashing.Tests;

public class BmpImageReaderTests
{
    [Fact]
    public void Read_ReturnsRowsTopDownFromABottomUpBitmap()
    {
        // BMP stores rows bottom-up by default, so the first row in the file is the
        // bottom of the image. Getting this backwards flips every frame and silently
        // changes the hash.
        var bmp = BuildBmp(2, 2, topDown: false,
        [
            // bottom row first, samples are BGR
            [0, 0, 255, 0, 255, 0],
            [255, 0, 0, 255, 255, 255],
        ]);

        var image = BmpImageReader.Read(bmp);

        Assert.Equal(2, image.Width);
        Assert.Equal(2, image.Height);

        // Top-left of the image is the first pixel of the last row in the file: blue.
        Assert.Equal(new byte[] { 0, 0, 255, 255 }, PixelAt(image, 0, 0));
        Assert.Equal(new byte[] { 255, 255, 255, 255 }, PixelAt(image, 1, 0));

        // Bottom-left is the first pixel of the first row in the file: red.
        Assert.Equal(new byte[] { 255, 0, 0, 255 }, PixelAt(image, 0, 1));
        Assert.Equal(new byte[] { 0, 255, 0, 255 }, PixelAt(image, 1, 1));
    }

    [Fact]
    public void Read_HandlesTopDownBitmaps()
    {
        var bmp = BuildBmp(2, 2, topDown: true,
        [
            [0, 0, 255, 0, 255, 0],
            [255, 0, 0, 255, 255, 255],
        ]);

        var image = BmpImageReader.Read(bmp);

        Assert.Equal(new byte[] { 255, 0, 0, 255 }, PixelAt(image, 0, 0));
        Assert.Equal(new byte[] { 0, 0, 255, 255 }, PixelAt(image, 0, 1));
    }

    [Fact]
    public void Read_SkipsRowPadding()
    {
        // A 3-pixel row is 9 bytes, padded to 12. Reading the padding as pixel data
        // would shift every row after the first.
        var bmp = BuildBmp(3, 2, topDown: true,
        [
            [1, 2, 3, 4, 5, 6, 7, 8, 9],
            [10, 11, 12, 13, 14, 15, 16, 17, 18],
        ]);

        var image = BmpImageReader.Read(bmp);

        // Samples are BGR, so the first pixel of the second row reads back reversed.
        Assert.Equal(new byte[] { 12, 11, 10, 255 }, PixelAt(image, 0, 1));
    }

    [Fact]
    public void Read_ForcesAlphaOpaque()
    {
        var bmp = BuildBmp(1, 1, topDown: true, [[10, 20, 30]]);

        // The resampler skips premultiplication because alpha is always 255. A frame that
        // arrived transparent would quietly break that assumption.
        Assert.Equal(255, BmpImageReader.Read(bmp).Pixels[3]);
    }

    [Theory]
    [InlineData(new byte[] { 0x00, 0x01, 0x02, 0x03 })]
    [InlineData(new byte[] { })]
    public void Read_RejectsSomethingThatIsNotABmp(byte[] data)
        => Assert.Throws<InvalidDataException>(() => BmpImageReader.Read(data));

    [Fact]
    public void Read_RejectsAFrameShorterThanItsHeaderClaims()
    {
        var bmp = BuildBmp(4, 4, topDown: true, BuildRows(4, 4));

        Assert.Throws<InvalidDataException>(() => BmpImageReader.Read(bmp.AsSpan(0, bmp.Length - 8)));
    }

    private static byte[][] BuildRows(int width, int height)
    {
        var rows = new byte[height][];
        for (var y = 0; y < height; y++)
        {
            rows[y] = new byte[width * 3];
            for (var i = 0; i < rows[y].Length; i++)
                rows[y][i] = (byte)((y * width) + i);
        }

        return rows;
    }

    private static byte[] PixelAt(PixelImage image, int x, int y)
        => image.Pixels.AsSpan(image.OffsetOf(x, y), PixelImage.BytesPerPixel).ToArray();

    /// <summary>A 24-bit BMP in the shape ffmpeg's bmp encoder emits.</summary>
    private static byte[] BuildBmp(int width, int height, bool topDown, byte[][] rows)
    {
        var rowStride = ((width * 3) + 3) & ~3;
        var buffer = new byte[54 + (rowStride * height)];

        buffer[0] = (byte)'B';
        buffer[1] = (byte)'M';
        BitConverter.GetBytes(buffer.Length).CopyTo(buffer, 2);
        BitConverter.GetBytes(54).CopyTo(buffer, 10);
        BitConverter.GetBytes(40).CopyTo(buffer, 14);
        BitConverter.GetBytes(width).CopyTo(buffer, 18);
        BitConverter.GetBytes(topDown ? -height : height).CopyTo(buffer, 22);
        BitConverter.GetBytes((short)1).CopyTo(buffer, 26);
        BitConverter.GetBytes((short)24).CopyTo(buffer, 28);
        BitConverter.GetBytes(0).CopyTo(buffer, 30);

        for (var y = 0; y < height; y++)
            rows[y].CopyTo(buffer, 54 + (y * rowStride));

        return buffer;
    }
}
