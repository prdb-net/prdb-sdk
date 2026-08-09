namespace Prdb.Hashing;

/// <summary>
/// Assembles the 5x5 frame collage that the perceptual hash is computed over, matching
/// Stash's <c>combineImages</c>. See step 2 of <c>docs/video-hashing.md</c>.
/// <para>
/// Hashing a collage rather than a single frame is what makes the value describe the
/// whole video: one frame would collide across every scene with a similar composition,
/// and would land on a title card or a black frame often enough to be useless.
/// </para>
/// </summary>
public static class FrameMontage
{
    /// <summary>Columns in the grid.</summary>
    public const int Columns = 5;

    /// <summary>Rows in the grid.</summary>
    public const int Rows = 5;

    /// <summary>Frames the montage is built from: 25.</summary>
    public const int FrameCount = Columns * Rows;

    /// <summary>
    /// Pastes the frames into the grid left to right, top to bottom, in sample order.
    /// </summary>
    public static PixelImage Combine(IReadOnlyList<PixelImage> frames)
    {
        if (frames is null)
            throw new ArgumentNullException(nameof(frames));

        if (frames.Count != FrameCount)
            throw new ArgumentException($"The montage needs exactly {FrameCount} frames, got {frames.Count}.", nameof(frames));

        var width = frames[0].Width;
        var height = frames[0].Height;

        // Stash sizes the grid from the first frame and pastes the rest at fixed offsets.
        // A frame of a different size would land misaligned and leave uncovered canvas in
        // the hash, so it is rejected here rather than quietly changing the result.
        for (var i = 1; i < frames.Count; i++)
        {
            if (frames[i].Width != width || frames[i].Height != height)
                throw new ArgumentException("All montage frames must have the same dimensions.", nameof(frames));
        }

        var montage = new PixelImage(width * Columns, height * Rows);
        for (var index = 0; index < frames.Count; index++)
        {
            var x = width * (index % Columns);
            var y = height * (index / Columns);
            montage.Paste(frames[index], x, y);
        }

        return montage;
    }
}
