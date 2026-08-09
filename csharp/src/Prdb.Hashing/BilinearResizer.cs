namespace Prdb.Hashing;

/// <summary>
/// Port of <c>github.com/nfnt/resize</c>'s bilinear path, the resampler
/// <c>goimagehash.PerceptionHash</c> uses and therefore the one Stash's video pHash
/// depends on. See step 3 of <c>docs/video-hashing.md</c>.
/// <para>
/// <b>This is not a general-purpose resizer.</b> It is a transcription, kept public only
/// so that an implementation in another language can be checked against it one stage at a
/// time. "Bilinear" here is not the usual four-neighbour interpolation: nfnt scales the
/// triangle filter's support by the downscale factor, so shrinking 800x450 to 64x64
/// averages over a 26-tap window per axis. It also runs two passes that each write a
/// transposed intermediate, and it accumulates in int32 with int16 fixed-point weights.
/// Every one of those choices moves individual hash bits, so the arithmetic and its
/// truncation are reproduced as-is.
/// </para>
/// <para>
/// nfnt dispatches on the concrete Go image type: an <c>image.NRGBA</c> input takes a
/// path that premultiplies by alpha first. Only fully opaque images are ever hashed here
/// (the montage is completely covered by its tiles), and premultiplying by an alpha of
/// 255 is the identity, so the two paths coincide and only one is implemented.
/// </para>
/// </summary>
public static class BilinearResizer
{
    // nfnt's package-level blur factor, and the tap count its Bilinear kernel reports.
    private const double Blur = 1.0;
    private const int Taps = 2;

    /// <summary>
    /// Resizes <paramref name="image"/> to the given size, reproducing nfnt's arithmetic
    /// exactly. Returns the input unchanged when it is already that size.
    /// </summary>
    public static PixelImage Resize(PixelImage image, int width, int height)
    {
        if (image is null)
            throw new ArgumentNullException(nameof(image));

        if (width <= 0 || height <= 0)
            throw new ArgumentOutOfRangeException(nameof(width), "The target size must be positive.");

        var scaleX = (double)image.Width / width;
        var scaleY = (double)image.Height / height;

        // nfnt returns the input untouched when nothing would change. Kept because it is
        // observable: the caller would otherwise re-quantise pixels through the filter.
        if (image.Width == width && image.Height == height)
            return image;

        // Pass one filters horizontally and writes a transposed intermediate, so `temp`
        // is (input height) wide and (target width) tall.
        var temp = new PixelImage(image.Height, width);
        var (coefficients, offsets, filterLength) = CreateWeights(temp.Height, scaleX);
        ResizePass(image, temp, coefficients, offsets, filterLength);

        // Pass two filters the transposed image the same way, which undoes the transpose.
        var result = new PixelImage(width, height);
        (coefficients, offsets, filterLength) = CreateWeights(result.Height, scaleY);
        ResizePass(temp, result, coefficients, offsets, filterLength);

        return result;
    }

    /// <summary>
    /// Port of nfnt's <c>createWeights8</c>: fixed-point filter weights scaled by 256,
    /// plus the first source index each output sample reads from.
    /// </summary>
    private static (short[] Coefficients, int[] Offsets, int FilterLength) CreateWeights(int outputLength, double scale)
    {
        var filterLength = Taps * (int)Math.Max(Math.Ceiling(Blur * scale), 1);
        var filterFactor = Math.Min(1.0 / (Blur * scale), 1);

        var coefficients = new short[outputLength * filterLength];
        var offsets = new int[outputLength];

        for (var y = 0; y < outputLength; y++)
        {
            var interpolated = (scale * (y + 0.5)) - 0.5;
            offsets[y] = (int)interpolated - (filterLength / 2) + 1;
            interpolated -= offsets[y];

            for (var i = 0; i < filterLength; i++)
            {
                var position = (interpolated - i) * filterFactor;
                coefficients[(y * filterLength) + i] = (short)(Triangle(position) * 256);
            }
        }

        return (coefficients, offsets, filterLength);
    }

    /// <summary>nfnt's <c>linear</c> kernel.</summary>
    private static double Triangle(double value)
    {
        value = Math.Abs(value);
        return value <= 1 ? 1 - value : 0;
    }

    /// <summary>
    /// Port of nfnt's <c>resizeRGBA</c>. Reads rows of <paramref name="source"/> and
    /// writes <paramref name="destination"/> transposed, which is why one of these per
    /// axis produces an upright result.
    /// </summary>
    private static void ResizePass(
        PixelImage source,
        PixelImage destination,
        short[] coefficients,
        int[] offsets,
        int filterLength)
    {
        var maxX = source.Width - 1;

        for (var x = 0; x < destination.Width; x++)
        {
            var rowStart = x * source.Stride;

            for (var y = 0; y < destination.Height; y++)
            {
                var r = 0;
                var g = 0;
                var b = 0;
                var a = 0;
                var sum = 0;

                var start = offsets[y];
                var coefficientIndex = y * filterLength;

                for (var i = 0; i < filterLength; i++)
                {
                    int coefficient = coefficients[coefficientIndex + i];
                    if (coefficient == 0)
                        continue;

                    // nfnt clamps reads to the edge pixel, relying on unsigned wraparound
                    // to fold negative indices into the same branch. Spelled out here.
                    var sampleIndex = start + i;
                    sampleIndex = sampleIndex switch
                    {
                        _ when sampleIndex >= maxX => maxX * PixelImage.BytesPerPixel,
                        _ when sampleIndex < 0 => 0,
                        _ => sampleIndex * PixelImage.BytesPerPixel,
                    };

                    r += coefficient * source.Pixels[rowStart + sampleIndex + 0];
                    g += coefficient * source.Pixels[rowStart + sampleIndex + 1];
                    b += coefficient * source.Pixels[rowStart + sampleIndex + 2];
                    a += coefficient * source.Pixels[rowStart + sampleIndex + 3];
                    sum += coefficient;
                }

                var target = (y * destination.Stride) + (x * PixelImage.BytesPerPixel);
                if (sum == 0)
                {
                    // Cannot happen for the triangle kernel, which always keeps at least
                    // one non-zero tap, but a divide by zero would be a silent corruption.
                    continue;
                }

                destination.Pixels[target + 0] = ClampToByte(r / sum);
                destination.Pixels[target + 1] = ClampToByte(g / sum);
                destination.Pixels[target + 2] = ClampToByte(b / sum);
                destination.Pixels[target + 3] = ClampToByte(a / sum);
            }
        }
    }

    private static byte ClampToByte(int value) => value switch
    {
        < 0 => 0,
        > 255 => 255,
        _ => (byte)value,
    };
}
