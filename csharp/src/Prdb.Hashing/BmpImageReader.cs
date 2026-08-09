using System.Buffers.Binary;

namespace Prdb.Hashing;

/// <summary>
/// Reads the uncompressed BMP frames ffmpeg writes for the perceptual hash.
/// <para>
/// Deliberately narrow: this decodes what ffmpeg's <c>bmp</c> encoder produces and
/// nothing else. A general BMP reader would have to handle palettes, run-length
/// compression and colour profiles, none of which can appear here, and every extra
/// branch is one more way to mis-read a frame into a wrong hash.
/// </para>
/// </summary>
public static class BmpImageReader
{
    private const int FileHeaderSize = 14;

    /// <summary>Decodes a BMP frame into a fully opaque RGBA image.</summary>
    /// <exception cref="InvalidDataException">The data is not a BMP this reader handles.</exception>
    public static PixelImage Read(ReadOnlySpan<byte> data)
    {
        if (data.Length < FileHeaderSize + 40)
            throw new InvalidDataException("The BMP frame is too short to contain a header.");

        if (data[0] != (byte)'B' || data[1] != (byte)'M')
            throw new InvalidDataException("The frame is not a BMP: the 'BM' signature is missing.");

        var pixelOffset = BinaryPrimitives.ReadInt32LittleEndian(data[10..]);
        var headerSize = BinaryPrimitives.ReadInt32LittleEndian(data[14..]);

        // 40 is BITMAPINFOHEADER; 108 and 124 are the V4/V5 headers, which only add
        // colour-space fields after the geometry this reader uses.
        if (headerSize is not (40 or 108 or 124))
            throw new InvalidDataException($"Unsupported BMP header size {headerSize}.");

        var width = BinaryPrimitives.ReadInt32LittleEndian(data[18..]);
        var rawHeight = BinaryPrimitives.ReadInt32LittleEndian(data[22..]);
        var bitsPerPixel = BinaryPrimitives.ReadInt16LittleEndian(data[28..]);
        var compression = BinaryPrimitives.ReadInt32LittleEndian(data[30..]);

        if (bitsPerPixel is not (24 or 32))
            throw new InvalidDataException($"Unsupported BMP colour depth {bitsPerPixel}.");

        // 0 is BI_RGB. 3 is BI_BITFIELDS, which ffmpeg only emits for 32-bit output with
        // the standard BGRA masks, so it is read the same way.
        if (compression is not (0 or 3))
            throw new InvalidDataException($"Unsupported BMP compression {compression}.");

        if (width <= 0)
            throw new InvalidDataException($"Invalid BMP width {width}.");

        // A negative height means the rows are stored top-down instead of the usual
        // bottom-up order.
        var topDown = rawHeight < 0;
        var height = Math.Abs(rawHeight);
        if (height == 0)
            throw new InvalidDataException("Invalid BMP height 0.");

        var bytesPerSample = bitsPerPixel / 8;
        var rowStride = ((width * bytesPerSample) + 3) & ~3; // rows are padded to 4 bytes
        var required = pixelOffset + (rowStride * height);
        if (pixelOffset < FileHeaderSize || data.Length < required)
            throw new InvalidDataException("The BMP frame is shorter than its header claims.");

        var image = new PixelImage(width, height);

        for (var y = 0; y < height; y++)
        {
            var sourceRow = topDown ? y : height - 1 - y;
            var source = data.Slice(pixelOffset + (sourceRow * rowStride), rowStride);

            for (var x = 0; x < width; x++)
            {
                var sample = source[(x * bytesPerSample)..];
                var target = image.OffsetOf(x, y);

                // BMP stores samples as BGR(A). Alpha is forced opaque rather than read:
                // ffmpeg emits bgr24 for video frames, and the montage and resampler both
                // rely on every pixel being opaque.
                image.Pixels[target + 0] = sample[2];
                image.Pixels[target + 1] = sample[1];
                image.Pixels[target + 2] = sample[0];
                image.Pixels[target + 3] = 255;
            }
        }

        return image;
    }
}
