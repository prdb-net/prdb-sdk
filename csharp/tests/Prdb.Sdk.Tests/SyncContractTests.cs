using System.Net;
using System.Text;
using System.Text.Json.Nodes;
using Prdb.Sdk.Generated.Models;
using Xunit;

namespace Prdb.Sdk.Tests;

public sealed class SyncContractTests
{
    private static JsonNode Fixture() => JsonNode.Parse(File.ReadAllText(Path.Combine(AppContext.BaseDirectory, "sync-contracts.json")))!;

    [Fact]
    public async Task BaselinePreservesScopeDocumentsAndTypedOversizedContinuation()
    {
        var fixture = Fixture(); var status = 200;
        using var handler = new Handler(request =>
        {
            Assert.Equal("/videos/baseline", request.RequestUri!.AbsolutePath);
            var query = Uri.UnescapeDataString(request.RequestUri.Query);
            Assert.Contains("Cursor=opaque+/=", query); Assert.Contains("PageSize=1000", query);
            Assert.Contains("CreatedFrom=2026-10-01", query);
            return Task.FromResult((status, fixture[status == 200 ? "baseline" : "oversized"]!));
        });
        var client = PrdbClientFactory.Create("test-key", "https://api.example.test", handler, retry: PrdbRetryOptions.Disabled);
        Task<VideoBaselineResponse?> Read() => client.Videos.Baseline.GetAsync(c =>
        {
            c.QueryParameters.CreatedFrom = DateTimeOffset.Parse("2026-10-01T00:00:00Z");
            c.QueryParameters.CreatedBefore = DateTimeOffset.Parse("2026-10-22T00:00:00Z");
            c.QueryParameters.PageSize = 1000; c.QueryParameters.Cursor = "opaque+/=";
        });
        var page = (await Read())!;
        Assert.Equal("Full document", Assert.Single(page.Items!).Description);
        Assert.True(page.HasMore); Assert.Equal("opaque+/=", page.NextCursor);
        Assert.Equal(DateTimeOffset.Parse("2026-10-22T10:00:00Z"), page.ChangesSince);
        status = 413;
        var error = await Assert.ThrowsAsync<BaselineDocumentTooLargeResponse>(() => Read());
        Assert.Equal(Guid.Parse(fixture["oversized"]!["videoId"]!.GetValue<string>()), error.VideoId);
        Assert.Equal("after-large", error.NextCursor); Assert.Equal(page.ChangesSince, error.ChangesSince);
    }

    [Fact]
    public async Task FreshnessPreservesTupleMixedNullableResultsAndLegacyOmissions()
    {
        var fixture = Fixture(); var legacy = false;
        using var handler = new Handler(async request =>
        {
            var body = JsonNode.Parse(await request.Content!.ReadAsStringAsync())!;
            if (request.RequestUri!.AbsolutePath == "/videos/identify")
            {
                Assert.True(body["includeFreshness"]!.GetValue<bool>());
                return (200, fixture[legacy ? "legacy" : "identify"]!);
            }
            Assert.Equal("/videos/identify/validate", request.RequestUri.AbsolutePath);
            Assert.False(body["reidentify"]!.GetValue<bool>());
            Assert.Equal(4294967296, body["files"]![0]!["filesize"]!.GetValue<long>());
            Assert.Equal(new string('a',32), body["files"]![0]!["md5"]!.GetValue<string>());
            Assert.Equal("proof", body["files"]![0]!["freshnessToken"]!.GetValue<string>());
            return (200, fixture["validation"]!);
        });
        var client = PrdbClientFactory.Create("test-key", "https://api.example.test", handler);
        var file = new IdentifyVideoFileDto { Ref = "r1", Filename = "Synthetic.mp4", Filesize = 4294967296, Md5 = new string('a',32) };
        var request = new IdentifyVideosRequest { Files = [file], IncludeFreshness = true };
        var result = (await client.Videos.Identify.PostAsync(request))!;
        Assert.Equal("proof", result.Results![0].FreshnessToken); Assert.NotNull(result.Results[0].FreshnessExpiresAtUtc);
        file.FreshnessToken = result.Results[0].FreshnessToken;
        var mixed = (await client.Videos.Identify.Validate.PostAsync(new() { Files = [file], Reidentify = false }))!;
        Assert.Equal(new[] { "r1", "r2", "r3" }, mixed.Results!.Select(x => x.Ref));
        Assert.Equal(new[] { "unchanged", "identified", "reidentify" }, mixed.Results!.Select(x => x.Status.ToString()!.ToLowerInvariant()));
        Assert.Null(mixed.Results[0].Result); Assert.Null(mixed.Results[2].Result);
        Assert.Equal("replacement", mixed.Results[1].Result!.FreshnessToken);
        legacy = true;
        var old = (await client.Videos.Identify.PostAsync(request))!;
        Assert.Null(old.Results![0].FreshnessToken); Assert.Null(old.Results[0].FreshnessExpiresAtUtc);
    }

    private sealed class Handler(Func<HttpRequestMessage,Task<(int Status,JsonNode Body)>> respond) : HttpMessageHandler
    {
        protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken token)
        {
            var result = await respond(request);
            return new HttpResponseMessage((HttpStatusCode)result.Status)
            { RequestMessage = request, Content = new StringContent(result.Body.ToJsonString(), Encoding.UTF8, "application/json") };
        }
    }
}
