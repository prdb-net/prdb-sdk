namespace Prdb.Hashing;

/// <summary>
/// Port of <c>goimagehash/transforms</c>'s static DCT, the unscaled DCT-II by the
/// Byeong Gi Lee recursion that the perceptual hash calls. See step 5 of
/// <c>docs/video-hashing.md</c>.
/// <para>
/// The cosine divisors are copied from goimagehash's precomputed tables rather than
/// recomputed with <see cref="Math.Cos"/>. Two runtimes are not required to agree on the
/// last bit of a cosine, and a divisor that differs by one ulp can move a coefficient
/// across the threshold and flip a hash bit. Copying the tables removes the question.
/// </para>
/// <para>
/// Public so that a port to another language can be checked one stage at a time; it is
/// not a general-purpose DCT, and no normalisation factor is applied.
/// </para>
/// </summary>
public static class FastDct
{
    /// <summary>
    /// Port of <c>DCT2DFast64</c>: a row transform across all 64 rows, then a column
    /// transform over the first 8 columns only, returning the top-left 8x8 block
    /// flattened row-major. The remaining columns cannot influence that block, which is
    /// why goimagehash skips them.
    /// </summary>
    /// <param name="pixels">4096 greyscale values, row-major. Modified in place.</param>
    /// <returns>64 coefficients, with the DC coefficient at index 0.</returns>
    public static double[] Transform64(double[] pixels)
    {
        if (pixels is null)
            throw new ArgumentNullException(nameof(pixels));

        if (pixels.Length != 64 * 64)
            throw new ArgumentException("The perceptual hash DCT expects a 64x64 pixel buffer.", nameof(pixels));

        for (var row = 0; row < 64; row++)
            Forward64(pixels.AsSpan(row * 64, 64));

        var flattened = new double[64];
        var column = new double[64];

        for (var i = 0; i < 8; i++)
        {
            for (var j = 0; j < 64; j++)
                column[j] = pixels[(64 * j) + i];

            Forward64(column);

            for (var j = 0; j < 8; j++)
                flattened[(8 * j) + i] = column[j];
        }

        return flattened;
    }

    private static void Forward64(Span<double> input)
    {
        Span<double> temp = stackalloc double[64];
        for (var i = 0; i < 32; i++)
        {
            double x = input[i], y = input[63 - i];
            temp[i] = x + y;
            temp[i + 32] = (x - y) / Dct64[i];
        }

        Forward32(temp[..32]);
        Forward32(temp[32..]);

        for (var i = 0; i < 31; i++)
        {
            input[(i * 2) + 0] = temp[i];
            input[(i * 2) + 1] = temp[i + 32] + temp[i + 33];
        }

        input[62] = temp[31];
        input[63] = temp[63];
    }

    private static void Forward32(Span<double> input)
    {
        Span<double> temp = stackalloc double[32];
        for (var i = 0; i < 16; i++)
        {
            double x = input[i], y = input[31 - i];
            temp[i] = x + y;
            temp[i + 16] = (x - y) / Dct32[i];
        }

        Forward16(temp[..16]);
        Forward16(temp[16..]);

        for (var i = 0; i < 15; i++)
        {
            input[(i * 2) + 0] = temp[i];
            input[(i * 2) + 1] = temp[i + 16] + temp[i + 17];
        }

        input[30] = temp[15];
        input[31] = temp[31];
    }

    private static void Forward16(Span<double> input)
    {
        Span<double> temp = stackalloc double[16];
        for (var i = 0; i < 8; i++)
        {
            double x = input[i], y = input[15 - i];
            temp[i] = x + y;
            temp[i + 8] = (x - y) / Dct16[i];
        }

        Forward8(temp[..8]);
        Forward8(temp[8..]);

        for (var i = 0; i < 7; i++)
        {
            input[(i * 2) + 0] = temp[i];
            input[(i * 2) + 1] = temp[i + 8] + temp[i + 9];
        }

        input[14] = temp[7];
        input[15] = temp[15];
    }

    private static void Forward8(Span<double> input)
    {
        Span<double> a = stackalloc double[4];
        Span<double> b = stackalloc double[4];

        double x0 = input[0], y0 = input[7];
        double x1 = input[1], y1 = input[6];
        double x2 = input[2], y2 = input[5];
        double x3 = input[3], y3 = input[4];

        a[0] = x0 + y0;
        a[1] = x1 + y1;
        a[2] = x2 + y2;
        a[3] = x3 + y3;
        b[0] = (x0 - y0) / 1.9615705608064609;
        b[1] = (x1 - y1) / 1.6629392246050907;
        b[2] = (x2 - y2) / 1.1111404660392046;
        b[3] = (x3 - y3) / 0.3901806440322566;

        Forward4(a);
        Forward4(b);

        input[0] = a[0];
        input[1] = b[0] + b[1];
        input[2] = a[1];
        input[3] = b[1] + b[2];
        input[4] = a[2];
        input[5] = b[2] + b[3];
        input[6] = a[3];
        input[7] = b[3];
    }

    private static void Forward4(Span<double> input)
    {
        double x0 = input[0], y0 = input[3];
        double x1 = input[1], y1 = input[2];

        var t0 = x0 + y0;
        var t1 = x1 + y1;
        var t2 = (x0 - y0) / 1.8477590650225735;
        var t3 = (x1 - y1) / 0.7653668647301797;

        double x = t0, y = t1;
        t0 += t1;
        t1 = (x - y) / 1.4142135623730951;

        x = t2;
        y = t3;
        t2 += t3;
        t3 = (x - y) / 1.4142135623730951;

        input[0] = t0;
        input[1] = t2 + t3;
        input[2] = t1;
        input[3] = t3;
    }

    private static readonly double[] Dct64 =
    [
        1.9993976373924083, 1.9945809133573804, 1.9849590691974202, 1.9705552847778824,
        1.9514042600770571, 1.9275521315908797, 1.8990563611860733, 1.8659855976694777,
        1.8284195114070614, 1.7864486023910306, 1.7401739822174227, 1.6897071304994142,
        1.6351696263031674, 1.5766928552532127, 1.5144176930129691, 1.448494165902934,
        1.3790810894741339, 1.3063456859075537, 1.2304631811612539, 1.151616382835691,
        1.0699952397741948, 0.9857963844595683, 0.8992226593092132, 0.8104826280099796,
        0.7197900730699766, 0.627363480797783, 0.5334255149497968, 0.43820248031373954,
        0.3419237775206027, 0.24482135039843256, 0.1471291271993349, 0.049082457045824535,
    ];

    private static readonly double[] Dct32 =
    [
        1.9975909124103448, 1.978353019929562, 1.9400625063890882, 1.8830881303660416,
        1.8079785862468867, 1.7154572200005442, 1.6064150629612899, 1.4819022507099182,
        1.3431179096940369, 1.191398608984867, 1.0282054883864435, 0.8551101868605644,
        0.6737797067844401, 0.48596035980652796, 0.2934609489107235, 0.09813534865483627,
    ];

    private static readonly double[] Dct16 =
    [
        1.9903694533443936, 1.9138806714644176, 1.76384252869671, 1.546020906725474,
        1.2687865683272912, 0.9427934736519956, 0.5805693545089246, 0.19603428065912154,
    ];
}
