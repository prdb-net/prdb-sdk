using System.Net;
using System.Text;
using System.Text.Json.Nodes;
using Microsoft.Kiota.Abstractions;
using Prdb.Sdk.Generated.Models;
using Xunit;

namespace Prdb.Sdk.Tests;

public sealed class ReleaseResolutionTests
{
    private static JsonNode Fixture() => JsonNode.Parse(File.ReadAllText(Path.Combine(AppContext.BaseDirectory,"release-resolution.json")))!;
    private static ResolveReleasesRequest Body(JsonNode fixture) => new()
    {
        Releases = fixture["request"]!["releases"]!.AsArray().Select(x => new ResolveReleaseInput
        {
            Ref = x!["ref"]!.GetValue<string>(), Title = x["title"]!.GetValue<string>(),
            SizeBytes = x["sizeBytes"]?.GetValue<long>(),
            PostedAtUtc = x["postedAtUtc"] is { } posted ? DateTimeOffset.Parse(posted.GetValue<string>()) : null,
            Source = x["source"] is not { } source ? null : new ResolveReleaseSource
            {
                Kind = Enum.Parse<ReleaseSourceKind>(source["kind"]!.GetValue<string>(),true),
                Origin = source["origin"]!.GetValue<string>(), EntryId = source["entryId"]!.GetValue<string>()
            }
        }).ToList()
    };

    [Fact]
    public async Task TypedConsumerPreservesMixedRefsSelectsActorsSkipsOwnedAndRechecksWithoutChangingInput()
    {
        var fixture = Fixture(); var calls = 0;
        using var handler = new Handler(async request =>
        {
            Assert.Equal(HttpMethod.Post,request.Method); Assert.Equal("/releases/resolve",request.RequestUri!.AbsolutePath);
            Assert.Equal("test-key",Assert.Single(request.Headers.GetValues("X-Api-Key")));
            var body = JsonNode.Parse(await request.Content!.ReadAsStringAsync())!;
            if (calls++ == 0)
            {
                Assert.Equal(4294967296,body["releases"]![0]!["sizeBytes"]!.GetValue<long>());
                Assert.Equal(TimeSpan.Zero,DateTimeOffset.Parse(body["releases"]![0]!["postedAtUtc"]!.GetValue<string>()).Offset);
                Assert.Equal("nzbcache",body["releases"]![1]!["source"]!["kind"]!.GetValue<string>());
                return (200,fixture["response"]!);
            }
            Assert.Single(body["releases"]!.AsArray());
            Assert.Equal("Synthetic.New.Knowledge",body["releases"]![0]!["title"]!.GetValue<string>());
            return (200,fixture["recheck"]!);
        });
        var client = PrdbClientFactory.Create("test-key","https://api.example.test",handler,retry: PrdbRetryOptions.Disabled);
        var request = Body(fixture); var limits = new RateLimitOption();
        var result = (await client.Releases.Resolve.PostAsync(request,c => c.Options.Add(limits)))!;
        var rows = result.Results!;
        Assert.Equal(request.Releases!.Select(x => x.Ref),rows.Select(x => x.Ref));
        Assert.Equal(ReleaseResolutionStatus.RetryLater,rows[2].Status);
        Assert.Equal(ReleaseResolutionStatus.Invalid,rows[3].Status); Assert.Null(rows[3].RecheckAfterUtc);
        Assert.Equal(ReleaseResolutionReason.UnsupportedPack,rows[4].ReasonCode);
        Assert.Empty(rows[5].VideoIds!); Assert.Single(rows[5].Candidates!);
        Assert.Null(rows[1].Videos![0].ReleaseDate);
        Assert.Null(rows[2].SourceState!.LastSuccessfulSyncAtUtc);
        Assert.Equal(995,limits.Hour!.Remaining);
        var owned = Guid.Parse(fixture["ids"]!["classic"]!.GetValue<string>());
        var selectedActor = Guid.Parse(fixture["ids"]!["actor"]!.GetValue<string>());
        var targets = rows.Where(x => x.AutomationEligible == true).SelectMany(x => x.Videos!)
            .Where(x => x.VideoId != owned && x.ActorIds!.Contains(selectedActor)).Select(x => x.VideoId).Distinct().ToArray();
        Assert.Equal(Guid.Parse(fixture["ids"]!["creator"]!.GetValue<string>()),Assert.Single(targets));
        Assert.True(rows[2].RecheckAfterUtc > result.EvaluatedAtUtc);
        var pending = request.Releases!.Single(x => x.Ref == "pending");
        var rechecked = (await client.Releases.Resolve.PostAsync(new() { Releases = [pending] }))!;
        var updated = Assert.Single(rechecked.Results!);
        Assert.Equal(ReleaseResolutionStatus.Resolved,updated.Status);
        Assert.NotEqual(rows.Last().ResolutionVersion,updated.ResolutionVersion);
        Assert.Equal(2,calls);
    }

    [Theory]
    [InlineData(400,typeof(ValidationProblemDetails))]
    [InlineData(401,typeof(RateLimitProblemResponse))]
    [InlineData(403,typeof(RateLimitProblemResponse))]
    [InlineData(413,typeof(ProblemDetails))]
    [InlineData(415,typeof(ProblemDetails))]
    [InlineData(429,typeof(RateLimitProblemResponse))]
    [InlineData(500,typeof(ProblemDetails))]
    [InlineData(503,typeof(RateLimitProblemResponse))]
    public async Task AllDeclaredRefusalsAreTypedAndRetainRetryHeaders(int code,Type expected)
    {
        var fixture = Fixture();
        using var handler = new Handler(_ => Task.FromResult((code,fixture["problems"]![code.ToString()]!)));
        var client = PrdbClientFactory.Create("test-key","https://api.example.test",handler,retry: PrdbRetryOptions.Disabled);
        var error = await Record.ExceptionAsync(() => client.Releases.Resolve.PostAsync(Body(fixture)));
        Assert.IsType(expected,error);
        var problem = (ApiException)error!; Assert.Equal(code,problem.ResponseStatusCode);
        if (code is 429 or 503) Assert.Equal("300",Assert.Single(problem.ResponseHeaders!["Retry-After"]));
    }
    private sealed class Handler(Func<HttpRequestMessage,Task<(int Status,JsonNode Body)>> respond) : HttpMessageHandler
    {
        protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request,CancellationToken token)
        {
            var result = await respond(request);
            var response = new HttpResponseMessage((HttpStatusCode)result.Status)
            { RequestMessage = request,Content = new StringContent(result.Body.ToJsonString(),Encoding.UTF8,"application/json") };
            response.Headers.Add("X-RateLimit-Limit-Hour","1000"); response.Headers.Add("X-RateLimit-Remaining-Hour","995");
            response.Headers.Add("X-RateLimit-Reset-Hour","60");
            if (result.Status is 429 or 503) response.Headers.Add("Retry-After","300");
            return response;
        }
    }
}
