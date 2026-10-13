using System.Net;
using System.Text;
using System.Text.Json.Nodes;
using Prdb.Sdk.Generated.Models;
using Xunit;

namespace Prdb.Sdk.Tests;

public sealed class ReleaseAssociationTests
{
    private static JsonNode Fixture() => JsonNode.Parse(File.ReadAllText(Path.Combine(AppContext.BaseDirectory, "release-associations.json")))!;
    [Fact]
    public async Task BaselineEmptyAndFollowUpPagesPreserveCursorStatesAndCorrection()
    {
        var fixture = Fixture(); var index = 0;
        using var handler = new Handler(request =>
        {
            Assert.Equal("/video-release-associations/changes", request.RequestUri!.AbsolutePath);
            Assert.Contains("Since=", request.RequestUri.Query);
            Assert.Equal("test-key", Assert.Single(request.Headers.GetValues("X-Api-Key")));
            return (200, fixture["pages"]![index++]!);
        });
        var client = PrdbClientFactory.Create("test-key", "https://api.example.test", handler);
        var baseline = (await client.VideoReleaseAssociations.Changes.GetAsync(c => c.QueryParameters.Since = DateTimeOffset.MinValue))!;
        Assert.Equal(4, baseline.Items!.Count);
        Assert.True(baseline.Items[0].VideoReleaseAssociation!.IsConfirmed);
        Assert.False(baseline.Items[1].VideoReleaseAssociation!.IsConfirmed);
        Assert.False(baseline.Items[2].VideoReleaseAssociation!.SourceAvailable);
        Assert.True(baseline.Items[3].VideoReleaseAssociation!.IsDeleted);
        Assert.Equal(VideoReleaseAssociationDto_providerKey.Nzbcache, baseline.Items[0].VideoReleaseAssociation!.ProviderKey);
        var empty = (await client.VideoReleaseAssociations.Changes.GetAsync(c =>
        { c.QueryParameters.Since = baseline.NextCursor!.UpdatedAtUtc; c.QueryParameters.SinceId = baseline.NextCursor.Id; }))!;
        Assert.Empty(empty.Items!); Assert.NotNull(empty.NextCursor); Assert.Equal(baseline.NextCursor!.Id, empty.NextCursor!.Id);
        var following = (await client.VideoReleaseAssociations.Changes.GetAsync(c => c.QueryParameters.Since = empty.ServerTimeUtc))!;
        var changed = Assert.Single(following.Items!);
        Assert.Equal(VideoReleaseAssociationChangeDto_eventType.Updated, changed.EventType);
        Assert.Equal(baseline.Items[0].VideoReleaseAssociation!.Id, changed.VideoReleaseAssociation!.Id);
        Assert.NotEqual(baseline.Items[0].VideoReleaseAssociation!.VideoId, changed.VideoReleaseAssociation.VideoId);
        Assert.Equal(3, index);
    }
    [Fact]
    public async Task InvalidCursorHasTypedValidationProblem()
    {
        using var handler = new Handler(_ => (400, Fixture()["invalidCursor"]!));
        var client = PrdbClientFactory.Create("test-key", "https://api.example.test", handler);
        var problem = await Assert.ThrowsAsync<ValidationProblemDetails>(() => client.VideoReleaseAssociations.Changes.GetAsync());
        Assert.Equal(400, problem.Status); Assert.NotNull(problem.Errors);
    }
    private sealed class Handler(Func<HttpRequestMessage, (int Status, JsonNode Body)> respond) : HttpMessageHandler
    {
        protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken token)
        {
            var result = respond(request);
            return Task.FromResult(new HttpResponseMessage((HttpStatusCode)result.Status)
            { RequestMessage = request, Content = new StringContent(result.Body.ToJsonString(), Encoding.UTF8, "application/json") });
        }
    }
}
