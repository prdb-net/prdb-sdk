namespace Prdb.Hashing;

/// <summary>
/// A straight (non-premultiplied) 8-bit RGBA image buffer.
/// <para>
/// This package has no image library, and the perceptual hash has to reproduce Go's
/// <c>image.NRGBA</c> byte layout anyway to stay bit-compatible, so the buffer is
/// modelled on it directly: four bytes per pixel in R, G, B, A order, rows laid out top
/// to bottom with a stride of <c>Width * 4</c>.
/// </para>
/// </summary>
public sealed class PixelImage
{
    /// <summary>Bytes per pixel: four, for R, G, B and A.</summary>
    public const int BytesPerPixel = 4;

    /// <summary>Creates a fully transparent image of the given size.</summary>
    public PixelImage(int width, int height)
    {
        if (width <= 0 || height <= 0)
            throw new ArgumentOutOfRangeException(nameof(width), "A pixel image needs a positive width and height.");

        Width = width;
        Height = height;
        Pixels = new byte[width * height * BytesPerPixel];
    }

    /// <summary>Width in pixels.</summary>
    public int Width { get; }

    /// <summary>Height in pixels.</summary>
    public int Height { get; }

    /// <summary>Bytes per row.</summary>
    public int Stride => Width * BytesPerPixel;

    /// <summary>The raw buffer, four bytes per pixel in R, G, B, A order.</summary>
    public byte[] Pixels { get; }

    /// <summary>Byte offset of the pixel at (<paramref name="x"/>, <paramref name="y"/>).</summary>
    public int OffsetOf(int x, int y) => (y * Stride) + (x * BytesPerPixel);

    /// <summary>
    /// Copies <paramref name="source"/> onto this image with its top-left corner at
    /// (<paramref name="x"/>, <paramref name="y"/>), the operation Stash performs with
    /// <c>imaging.Paste</c> when it assembles the frame montage.
    /// </summary>
    public void Paste(PixelImage source, int x, int y)
    {
        if (source is null)
            throw new ArgumentNullException(nameof(source));

        if (x < 0 || y < 0 || x + source.Width > Width || y + source.Height > Height)
            throw new ArgumentOutOfRangeException(nameof(source), "The pasted image does not fit at that position.");

        for (var row = 0; row < source.Height; row++)
        {
            Array.Copy(
                source.Pixels,
                source.OffsetOf(0, row),
                Pixels,
                OffsetOf(x, y + row),
                source.Stride);
        }
    }
}
