using System.Net;
using System.Text;
using System.Text.Json.Nodes;
using Prdb.Sdk.Generated.Models;
using Xunit;

namespace Prdb.Sdk.Tests;

public class ActorMergeTests
{
    private const string Origin = "https://api.example.test";
    private static JsonNode Fixture() => JsonNode.Parse(File.ReadAllText(
        Path.Combine(AppContext.BaseDirectory, "actor-merge.json")))!;

    [Theory]
    [InlineData(false)]
    [InlineData(true)]
    public async Task RetainedDetailAndBatch_PreserveCanonicalIdentity(bool omitMapping)
    {
        var fixture = Fixture();
        var source = Guid.Parse(fixture["sourceId"]!.GetValue<string>());
        var target = Guid.Parse(fixture["targetId"]!.GetValue<string>());
        var requests = 0;
        using var handler = new Handler(async request =>
        {
            requests++;
            if (request.RequestUri!.AbsolutePath == "/actors/batch")
            {
                Assert.Equal(HttpMethod.Post, request.Method);
                var body = JsonNode.Parse(await request.Content!.ReadAsStringAsync())!;
                Assert.Equal(new[] { source, target }, body["ids"]!.AsArray()
                    .Select(id => Guid.Parse(id!.GetValue<string>())));
                return fixture["batch"]!;
            }
            Assert.Equal($"/actors/{source}", request.RequestUri.AbsolutePath);
            if (omitMapping) fixture["detail"]!.AsObject().Remove("requestedIds");
            return fixture["detail"]!;
        });
        var client = PrdbClientFactory.Create("test-key", Origin, handler);
        var status = new ResponseStatusOption();
        var detail = await client.Actors[source].GetAsync(config => config.Options.Add(status));
        Assert.Equal(HttpStatusCode.OK, status.StatusCode);
        Assert.Equal(target, detail!.Id);
        Assert.Null(detail.RequestedIds);
        var batch = await client.Actors.Batch.PostAsync(new GetActorsByIdsRequest { Ids = [source, target] });
        var canonical = Assert.Single(batch!);
        Assert.Equal(target, canonical.Id);
        Assert.Equal(new Guid?[] { source, target }, canonical.RequestedIds);
        Assert.Equal(2, requests);
    }

    [Theory]
    [InlineData(false)]
    [InlineData(true)]
    public async Task MergeFeeds_PreserveSourceTombstonesAndNullableTargets(bool favorite)
    {
        var fixture = Fixture();
        var path = favorite ? "/favorite-actors/changes" : "/actors/changes";
        using var handler = new Handler(request =>
        {
            Assert.Equal(path, request.RequestUri!.AbsolutePath);
            Assert.Contains("Since=", request.RequestUri.Query);
            return Task.FromResult(fixture[favorite ? "favoriteActorChanges" : "actorChanges"]!);
        });
        var client = PrdbClientFactory.Create("test-key", Origin, handler);
        List<(string? Event, Guid? Id, bool? Deleted, Guid? Target)> rows;
        Guid? cursor;
        if (favorite)
        {
            var page = await client.FavoriteActors.Changes.GetAsync(config =>
                config.QueryParameters.Since = DateTimeOffset.MinValue);
            rows = page!.Items!.Select(item => (item.EventType, item.FavoriteActor!.Id,
                item.FavoriteActor.IsDeleted, item.FavoriteActor.MergedIntoActorId)).ToList();
            cursor = page.NextCursor!.Id;
        }
        else
        {
            var page = await client.Actors.Changes.GetAsync(config =>
                config.QueryParameters.Since = DateTimeOffset.MinValue);
            rows = page!.Items!.Select(item => (item.EventType, item.Actor!.Id,
                item.Actor.IsDeleted, item.Actor.MergedIntoActorId)).ToList();
            cursor = page.NextCursor!.Id;
        }
        Assert.Equal(new[] { "deleted", "updated", "deleted" }, rows.Select(row => row.Event));
        Assert.Equal(Guid.Parse(fixture["sourceId"]!.GetValue<string>()), rows[0].Id);
        Assert.True(rows[0].Deleted);
        var target = Guid.Parse(fixture["targetId"]!.GetValue<string>());
        Assert.Equal(target, rows[0].Target);
        Assert.Equal(target, rows[1].Id);
        Assert.False(rows[1].Deleted);
        Assert.Null(rows[1].Target); // Omitted property.
        Assert.True(rows[2].Deleted);
        Assert.Null(rows[2].Target); // Explicit null.
        Assert.Equal(Guid.Parse(fixture["ordinaryId"]!.GetValue<string>()), cursor);
    }

    private sealed class Handler(Func<HttpRequestMessage, Task<JsonNode>> respond) : HttpMessageHandler
    {
        protected override async Task<HttpResponseMessage> SendAsync(
            HttpRequestMessage request, CancellationToken cancellationToken) =>
            new(HttpStatusCode.OK)
            {
                RequestMessage = request,
                Content = new StringContent((await respond(request)).ToJsonString(), Encoding.UTF8, "application/json"),
            };
    }
}
