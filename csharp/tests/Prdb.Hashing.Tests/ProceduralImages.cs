using Prdb.Hashing;

namespace Prdb.Hashing.Tests;

/// <summary>
/// Deterministic test images, generated from a formula that the Go reference program
/// implements identically. The formulas are published in <c>docs/video-hashing.md</c>.
/// <para>
/// Sharing a generator rather than a binary fixture keeps the reference values checkable:
/// anyone can regenerate them by running the same formula through goimagehash, and the
/// repository stays free of megabytes of opaque image data.
/// </para>
/// </summary>
public static class ProceduralImages
{
    public static PixelImage Create(string kind, int seed, int width, int height) => kind switch
    {
        "noise" => Noise(seed, width, height),
        "gradient" => Gradient(seed, width, height),
        _ => throw new ArgumentOutOfRangeException(nameof(kind), kind, "Unknown procedural image kind."),
    };

    /// <summary>
    /// Noise from a linear congruential generator: high-frequency content, which is where
    /// a resampler that averages over the wrong window shows up immediately.
    /// </summary>
    public static PixelImage Noise(int seed, int width, int height)
    {
        var image = new PixelImage(width, height);
        var state = unchecked(((uint)seed * 2654435761u) + 12345u);

        byte Next()
        {
            state = unchecked((state * 1664525u) + 1013904223u);
            return (byte)((state >> 16) & 0xFF);
        }

        for (var y = 0; y < height; y++)
        {
            for (var x = 0; x < width; x++)
            {
                var offset = image.OffsetOf(x, y);
                image.Pixels[offset + 0] = Next();
                image.Pixels[offset + 1] = Next();
                image.Pixels[offset + 2] = Next();
                image.Pixels[offset + 3] = 255;
            }
        }

        return image;
    }

    /// <summary>
    /// Smooth low-frequency content, so a bug that only bites on image-like input cannot
    /// hide behind random pixels.
    /// </summary>
    public static PixelImage Gradient(int seed, int width, int height)
    {
        var image = new PixelImage(width, height);

        for (var y = 0; y < height; y++)
        {
            for (var x = 0; x < width; x++)
            {
                var offset = image.OffsetOf(x, y);
                image.Pixels[offset + 0] = (byte)(((x * 255 / width) + (seed * 7)) % 256);
                image.Pixels[offset + 1] = (byte)(((y * 255 / height) + (seed * 13)) % 256);
                image.Pixels[offset + 2] = (byte)(((x * 255 / width) + (y * 255 / height) + (seed * 31)) % 256);
                image.Pixels[offset + 3] = 255;
            }
        }

        return image;
    }

    public static PixelImage Flat(int width, int height, byte value)
    {
        var image = new PixelImage(width, height);

        for (var i = 0; i < image.Pixels.Length; i += PixelImage.BytesPerPixel)
        {
            image.Pixels[i + 0] = value;
            image.Pixels[i + 1] = value;
            image.Pixels[i + 2] = value;
            image.Pixels[i + 3] = 255;
        }

        return image;
    }
}
