using System.Net;
using System.Text;
using System.Text.Json.Nodes;
using Prdb.Sdk.Generated;
using Prdb.Sdk.Generated.Models;
using Xunit;

namespace Prdb.Sdk.Tests;

public sealed class PreviewEnrichmentTests
{
    private static JsonNode Fixture() => JsonNode.Parse(File.ReadAllText(Path.Combine(AppContext.BaseDirectory, "preview-enrichment.json")))!;
    private static readonly Guid VideoId = Guid.Parse((string)Fixture()["detail"]!["id"]!);

    [Fact]
    public async Task DetailKeepsTrueAndReadsAnAbsentFieldAsUnknown()
    {
        var fixture = Fixture(); var bodies = new Queue<JsonNode>([fixture["detail"]!, fixture["detailFromOlderServer"]!]);
        using var handler = new Handler(request =>
        {
            Assert.Equal($"/videos/{VideoId}", request.RequestUri!.AbsolutePath);
            return (200, bodies.Dequeue());
        });
        var client = PrdbClientFactory.Create("test-key", "https://api.example.test", handler);
        var current = (await client.Videos[VideoId].GetAsync())!;
        var older = (await client.Videos[VideoId].GetAsync())!;
        Assert.True(current.PreviewEnrichmentEligible);
        Assert.Null(older.PreviewEnrichmentEligible);
    }

    [Fact]
    public async Task BatchKeepsTrueFalseAndAbsentApart()
    {
        var fixture = Fixture();
        using var handler = new Handler(request =>
        {
            Assert.Equal("/videos/batch", request.RequestUri!.AbsolutePath);
            Assert.Equal(HttpMethod.Post, request.Method);
            return (200, fixture["batch"]!);
        });
        var client = PrdbClientFactory.Create("test-key", "https://api.example.test", handler);
        var videos = (await client.Videos.Batch.PostAsync(new GetVideosByIdsRequest { Ids = [VideoId] }))!;
        Assert.Equal([true, false, null], videos.Select(v => v.PreviewEnrichmentEligible));
    }

    [Fact]
    public async Task FeedCarriesUpsertsTombstonesAndFlipsAcrossCursorPages()
    {
        var fixture = Fixture(); var index = 0; var queries = new List<string>();
        using var handler = new Handler(request =>
        {
            Assert.Equal("/videos/changes", request.RequestUri!.AbsolutePath);
            queries.Add(request.RequestUri.Query);
            return (200, fixture["pages"]![index++]!);
        });
        var client = PrdbClientFactory.Create("test-key", "https://api.example.test", handler);
        var first = (await client.Videos.Changes.GetAsync(c => { c.QueryParameters.Since = DateTimeOffset.MinValue; c.QueryParameters.PageSize = 2; }))!;
        Assert.True(first.HasMore);
        Assert.Equal([true, false], first.Items!.Select(i => i.Video!.PreviewEnrichmentEligible));
        var second = (await client.Videos.Changes.GetAsync(c =>
        { c.QueryParameters.Since = first.NextCursor!.UpdatedAtUtc; c.QueryParameters.SinceId = first.NextCursor.Id; c.QueryParameters.PageSize = 2; }))!;
        var tombstone = Assert.Single(second.Items!);
        Assert.Equal("deleted", tombstone.EventType);
        Assert.True(tombstone.Video!.IsDeleted);
        Assert.False(tombstone.Video.PreviewEnrichmentEligible);
        Assert.Contains($"SinceId={first.NextCursor!.Id}", queries[1]);
        var following = (await client.Videos.Changes.GetAsync(c => c.QueryParameters.Since = second.ServerTimeUtc))!;
        var flipped = Assert.Single(following.Items!).Video!;
        Assert.Equal(first.Items![0].Video!.Id, flipped.Id);
        Assert.False(flipped.PreviewEnrichmentEligible);
        Assert.Equal(3, index);
    }

    public static TheoryData<int, string> DeclaredErrors => new() { { 404, "notFound" }, { 403, "forbidden" }, { 400, "invalidCursor" } };

    [Theory]
    [MemberData(nameof(DeclaredErrors))]
    public async Task DeclaredErrorsStayTypedProblems(int status, string body)
    {
        using var handler = new Handler(_ => (status, Fixture()[body]!));
        var client = PrdbClientFactory.Create("test-key", "https://api.example.test", handler);
        Func<PrdbClient, Task> call = status switch
        {
            404 => c => c.Videos[VideoId].GetAsync(),
            403 => c => c.Videos.Batch.PostAsync(new GetVideosByIdsRequest { Ids = [VideoId] }),
            _ => c => c.Videos.Changes.GetAsync(),
        };
        var problem = await Assert.ThrowsAsync<ProblemDetails>(() => call(client));
        Assert.Equal(status, problem.Status);
    }

    private sealed class Handler(Func<HttpRequestMessage, (int Status, JsonNode Body)> respond) : HttpMessageHandler
    {
        protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken token)
        {
            Assert.Equal("test-key", Assert.Single(request.Headers.GetValues("X-Api-Key")));
            var result = respond(request);
            return Task.FromResult(new HttpResponseMessage((HttpStatusCode)result.Status)
            { RequestMessage = request, Content = new StringContent(result.Body.ToJsonString(), Encoding.UTF8, "application/json") });
        }
    }
}
