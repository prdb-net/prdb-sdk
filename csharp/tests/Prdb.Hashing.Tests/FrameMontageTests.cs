using Xunit;

namespace Prdb.Hashing.Tests;

public class FrameMontageTests
{
    [Fact]
    public void Combine_PlacesFramesLeftToRightThenTopToBottom()
    {
        // Each frame is a flat block whose channels carry its index, so a misplaced tile
        // is visible as the wrong value at a known coordinate.
        var frames = Enumerable
            .Range(0, FrameMontage.FrameCount)
            .Select(i => ProceduralImages.Flat(4, 3, (byte)i))
            .ToList();

        var montage = FrameMontage.Combine(frames);

        Assert.Equal(4 * FrameMontage.Columns, montage.Width);
        Assert.Equal(3 * FrameMontage.Rows, montage.Height);

        for (var index = 0; index < FrameMontage.FrameCount; index++)
        {
            var x = 4 * (index % FrameMontage.Columns);
            var y = 3 * (index / FrameMontage.Columns);
            Assert.Equal((byte)index, montage.Pixels[montage.OffsetOf(x, y)]);
        }
    }

    [Fact]
    public void Combine_LeavesNoUncoveredCanvas()
    {
        var frames = Enumerable
            .Range(0, FrameMontage.FrameCount)
            .Select(_ => ProceduralImages.Flat(4, 3, 200))
            .ToList();

        var montage = FrameMontage.Combine(frames);

        // Every pixel opaque means the tiles tile the canvas exactly. The resampler port
        // assumes this: it skips alpha premultiplication because alpha is always 255.
        for (var i = PixelImage.BytesPerPixel - 1; i < montage.Pixels.Length; i += PixelImage.BytesPerPixel)
            Assert.Equal(255, montage.Pixels[i]);
    }

    [Fact]
    public void Combine_RejectsWrongFrameCount()
    {
        var frames = Enumerable.Range(0, 24).Select(_ => ProceduralImages.Flat(4, 3, 1)).ToList();

        var exception = Assert.Throws<ArgumentException>(() => FrameMontage.Combine(frames));
        Assert.Contains("exactly 25 frames", exception.Message);
    }

    [Fact]
    public void Combine_RejectsFramesOfDifferentSizes()
    {
        // ffmpeg's scale filter makes this impossible in practice, so a mismatch means
        // the filter was ignored — which must not quietly become a different hash.
        var frames = Enumerable
            .Range(0, FrameMontage.FrameCount)
            .Select(i => ProceduralImages.Flat(i == 7 ? 5 : 4, 3, 1))
            .ToList();

        var exception = Assert.Throws<ArgumentException>(() => FrameMontage.Combine(frames));
        Assert.Contains("same dimensions", exception.Message);
    }
}
