using System.Security.Cryptography;
using System.Text.Json;

namespace Prdb.Hashing.Tests;

/// <summary>
/// Reads <c>docs/video-hashing-vectors.json</c>, the published form of the vectors in
/// <c>docs/video-hashing.md</c>. The file is copied next to the test assembly at build
/// time, so the tests assert against exactly what is published rather than a transcription
/// that could drift from it.
/// </summary>
public static class TestVectors
{
    public const string FileName = "video-hashing-vectors.json";

    private static readonly JsonDocument Document = Load();

    public static string Sha256Hex(byte[] data)
        => Convert.ToHexString(SHA256.HashData(data)).ToLowerInvariant();

    /// <summary>kind, param, width, height, pixelsSha256, pHash</summary>
    public static IEnumerable<object[]> Level1() =>
        Document.RootElement.GetProperty("level1").EnumerateArray().Select(v => new object[]
        {
            v.GetProperty("image").GetString()!,
            v.GetProperty("param").GetInt32(),
            v.GetProperty("width").GetInt32(),
            v.GetProperty("height").GetInt32(),
            v.GetProperty("pixelsSha256").GetString()!,
            v.GetProperty("pHash").GetString()!,
        });

    /// <summary>kind, tileWidth, tileHeight, montageWidth, montageHeight, montageSha256, pHash</summary>
    public static IEnumerable<object[]> Level2() =>
        Document.RootElement.GetProperty("level2").EnumerateArray().Select(v => new object[]
        {
            v.GetProperty("frames").GetString()!,
            v.GetProperty("tileWidth").GetInt32(),
            v.GetProperty("tileHeight").GetInt32(),
            v.GetProperty("montageWidth").GetInt32(),
            v.GetProperty("montageHeight").GetInt32(),
            v.GetProperty("montageSha256").GetString()!,
            v.GetProperty("pHash").GetString()!,
        });

    /// <summary>file, lavfiSource, contentSha256, pHash</summary>
    public static IEnumerable<(string File, string Source, string ContentSha256, string PHash)> Level3() =>
        Document.RootElement.GetProperty("level3").EnumerateArray().Select(v => (
            v.GetProperty("file").GetString()!,
            v.GetProperty("lavfiSource").GetString()!,
            v.GetProperty("contentSha256").GetString()!,
            v.GetProperty("pHash").GetString()!));

    /// <summary>
    /// The montage a level 2 row describes. The checker generator takes the tile index as
    /// its square size rather than as a seed, floored at 1, so that no two tiles are alike.
    /// </summary>
    public static PixelImage BuildMontage(string kind, int tileWidth, int tileHeight)
    {
        var frames = Enumerable
            .Range(0, FrameMontage.FrameCount)
            .Select(i => ProceduralImages.Create(kind, kind == "checker" ? Math.Max(i, 1) : i, tileWidth, tileHeight))
            .ToList();

        return FrameMontage.Combine(frames);
    }

    private static JsonDocument Load()
    {
        var path = Path.Combine(AppContext.BaseDirectory, FileName);

        if (!File.Exists(path))
            throw new FileNotFoundException(
                $"{FileName} was not copied next to the test assembly. It is the published " +
                "vector file and the tests cannot run without it.", path);

        return JsonDocument.Parse(File.ReadAllText(path));
    }
}
