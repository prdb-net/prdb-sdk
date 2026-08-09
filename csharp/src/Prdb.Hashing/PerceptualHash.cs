namespace Prdb.Hashing;

/// <summary>
/// The 64-bit DCT perceptual hash the prdb Public API's <c>pHash</c> field carries — a
/// port of <c>goimagehash.PerceptionHash</c>, which Stash computes over a video's frame
/// montage. Specified in <c>docs/video-hashing.md</c>.
/// <para>
/// The point of this type is interoperability, not perceptual quality: a value that does
/// not match what Stash would produce for the same input is worth very little, so the
/// pipeline reproduces goimagehash's choices even where a cleaner one exists. The
/// notable ones are the resampler (see <see cref="BilinearResizer"/>), the DC coefficient
/// being kept rather than discarded, and the "median" below.
/// </para>
/// <para>
/// This hashes an image. To hash a video, use <see cref="VideoPerceptualHasher"/>, which
/// extracts the frames and assembles the montage first.
/// </para>
/// </summary>
public static class PerceptualHash
{
    private const int HashSize = 64;

    /// <summary>
    /// Returns the hash as the 16 lowercase hex characters the API's <c>pHash</c> field
    /// expects, matching <see cref="OsHash"/>'s formatting.
    /// </summary>
    public static string ComputeHex(PixelImage image) => Compute(image).ToString("x016");

    /// <summary>Returns the hash as a 64-bit value, most significant bit first.</summary>
    public static ulong Compute(PixelImage image)
    {
        if (image is null)
            throw new ArgumentNullException(nameof(image));

        var resized = BilinearResizer.Resize(image, 64, 64);
        var luminance = ToGrayscale(resized);
        var coefficients = FastDct.Transform64(luminance);
        var median = MedianOfPixels(coefficients);

        var hash = 0UL;
        for (var index = 0; index < coefficients.Length; index++)
        {
            if (coefficients[index] > median)
                hash |= 1UL << (HashSize - index - 1);
        }

        return hash;
    }

    /// <summary>
    /// goimagehash's luminosity conversion. It nominally works on 16-bit channels and
    /// divides two of them by 257 and the third by 256, which reads like a typo, but for
    /// 8-bit sources both divisions return the original byte exactly, so the weights can
    /// be applied to the bytes directly without changing a single result.
    /// </summary>
    private static double[] ToGrayscale(PixelImage image)
    {
        var pixels = new double[image.Width * image.Height];

        for (var y = 0; y < image.Height; y++)
        {
            for (var x = 0; x < image.Width; x++)
            {
                var offset = image.OffsetOf(x, y);
                pixels[(y * image.Width) + x] =
                    (0.299 * image.Pixels[offset + 0]) +
                    (0.587 * image.Pixels[offset + 1]) +
                    (0.114 * image.Pixels[offset + 2]);
            }
        }

        return pixels;
    }

    /// <summary>
    /// Port of goimagehash's <c>MedianOfPixels</c>.
    /// <para>
    /// This is not the median. Quickselect leaves everything below position k unsorted,
    /// and for an even-length input the function averages position k with whatever
    /// happens to sit at k-1, which is an arbitrary element of the lower partition rather
    /// than the next-smallest value. The threshold is therefore biased low by an amount
    /// that depends on the pivot sequence. It is reproduced exactly, including the pivot
    /// choice and the swap order, because the hash bits sit on the wrong side of it
    /// otherwise.
    /// </para>
    /// </summary>
    private static double MedianOfPixels(double[] pixels)
    {
        var buffer = (double[])pixels.Clone();
        var length = buffer.Length;
        var position = length / 2;
        return QuickSelectMedian(buffer, 0, length - 1, position);
    }

    private static double QuickSelectMedian(double[] sequence, int low, int high, int k)
    {
        if (low == high)
            return sequence[k];

        while (low < high)
        {
            var pivot = (low / 2) + (high / 2);
            var pivotValue = sequence[pivot];
            var storeIndex = low;

            (sequence[pivot], sequence[high]) = (sequence[high], sequence[pivot]);

            for (var i = low; i < high; i++)
            {
                if (sequence[i] < pivotValue)
                {
                    (sequence[storeIndex], sequence[i]) = (sequence[i], sequence[storeIndex]);
                    storeIndex++;
                }
            }

            (sequence[high], sequence[storeIndex]) = (sequence[storeIndex], sequence[high]);

            if (k <= storeIndex)
                high = storeIndex;
            else
                low = storeIndex + 1;
        }

        if (sequence.Length % 2 == 0)
            return (sequence[k - 1] / 2) + (sequence[k] / 2);

        return sequence[k];
    }
}
