using System.Net;
using System.Text;
using System.Text.Json.Nodes;
using Microsoft.Kiota.Abstractions;
using Prdb.Sdk.Generated.Models;
using Xunit;

namespace Prdb.Sdk.Tests;

public class RatingsTests
{
    private const string Origin = "https://api.example.test";
    private static readonly Guid Target = Guid.Parse("11111111-1111-4111-8111-111111111111");
    // Synthetic wire responses shared with the other three SDK contract tests.
    private static JsonNode Fixture() => JsonNode.Parse(File.ReadAllText(
        Path.Combine(AppContext.BaseDirectory, "ratings.json")))!;

    [Theory]
    [InlineData(true)]
    [InlineData(false)]
    public async Task RatingOperations_PreserveBodiesHeadersStatusesAndNulls(bool actor)
    {
        var fixture = Fixture();
        var resource = actor ? "actors" : "videos";
        (HttpMethod Method, string Suffix, int Status, string? Payload)[] exchanges = [
            (HttpMethod.Get, "/rating-summary", 200, "emptySummary"),
            (HttpMethod.Get, "/rating-summary", 200, "summary"),
            (HttpMethod.Get, "/rating", 200, "noRating"),
            (HttpMethod.Put, "/rating", 200, "deletedReceipt"),
            (HttpMethod.Put, "/rating", 202, "receipt"),
            (HttpMethod.Post, "/rating/review", 202, "receipt"),
            (HttpMethod.Delete, "/rating/review", 204, null),
            (HttpMethod.Delete, "/rating", 204, null),
        ];
        var calls = 0;
        using var handler = new Handler(async request =>
        {
            var expected = exchanges[calls++];
            Assert.Equal(expected.Method, request.Method);
            Assert.Equal($"/{resource}/{Target}{expected.Suffix}", request.RequestUri!.AbsolutePath);
            Assert.Equal("test-key", Assert.Single(request.Headers.GetValues("X-Api-Key")));
            if (request.Method == HttpMethod.Put || request.Method == HttpMethod.Post)
            {
                var body = JsonNode.Parse(await request.Content!.ReadAsStringAsync())!;
                if (calls == 4)
                {
                    Assert.Equal(4, body["stars"]!.GetValue<int>());
                    Assert.Null(body["reviewText"]);
                    Assert.False(request.Headers.Contains("Idempotency-Key"));
                }
                else
                {
                    Assert.Equal("synthetic-submission-key", Assert.Single(request.Headers.GetValues("Idempotency-Key")));
                    Assert.True(JsonNode.DeepEquals(JsonNode.Parse(request.Method == HttpMethod.Put
                        ? """{"stars":4,"reviewText":"Carefully made."}"""
                        : """{"text":"Carefully made."}"""), body));
                }
            }
            return Response(request, expected.Status, expected.Payload is null ? null : fixture[expected.Payload]);
        });
        var client = PrdbClientFactory.Create("test-key", Origin, handler);
        var a = client.Actors[Target];
        var v = client.Videos[Target];
        var summary = actor ? await a.RatingSummary.GetAsync() : await v.RatingSummary.GetAsync();
        Assert.Equal(0, summary!.RatingCount);
        Assert.Equal(0, summary.ReviewCount);
        Assert.Null(summary.AverageRating);
        summary = actor ? await a.RatingSummary.GetAsync() : await v.RatingSummary.GetAsync();
        Assert.Equal(3.75, summary!.AverageRating);
        var own = actor ? await a.Rating.GetAsync() : await v.Rating.GetAsync();
        Assert.Null(own!.Rating);
        var body = new SetRatingRequest { Stars = 4 };
        var receipt = actor ? await a.Rating.PutAsync(body) : await v.Rating.PutAsync(body);
        Assert.Null(receipt!.RatingId);
        Assert.Null(receipt.ReviewId);
        Assert.Null(receipt.ReviewState);
        var status = new ResponseStatusOption();
        void Configure(RequestConfiguration<DefaultQueryParameters> config)
        {
            config.Headers.Add("Idempotency-Key", "synthetic-submission-key");
            config.Options.Add(status);
        }
        body.ReviewText = "Carefully made.";
        receipt = actor ? await a.Rating.PutAsync(body, Configure) : await v.Rating.PutAsync(body, Configure);
        Assert.Equal(HttpStatusCode.Accepted, status.StatusCode);
        Assert.Equal(Guid.Parse(fixture["ratingId"]!.GetValue<string>()), receipt!.RatingId);
        Assert.Equal("Pending", receipt.ReviewState);
        var review = new SubmitRatingReviewRequest { Text = "Carefully made." };
        receipt = actor ? await a.Rating.Review.PostAsync(review, Configure) : await v.Rating.Review.PostAsync(review, Configure);
        Assert.Equal(HttpStatusCode.Accepted, status.StatusCode);
        Assert.Equal(Guid.Parse(fixture["reviewId"]!.GetValue<string>()), receipt!.ReviewId);
        if (actor) await a.Rating.Review.DeleteAsync(Configure); else await v.Rating.Review.DeleteAsync(Configure);
        Assert.Equal(HttpStatusCode.NoContent, status.StatusCode);
        if (actor) await a.Rating.DeleteAsync(Configure); else await v.Rating.DeleteAsync(Configure);
        Assert.Equal(HttpStatusCode.NoContent, status.StatusCode);
        Assert.Equal(exchanges.Length, calls);
    }

    [Theory]
    [InlineData(OwnReviewState.None)]
    [InlineData(OwnReviewState.Published)]
    [InlineData(OwnReviewState.Pending)]
    [InlineData(OwnReviewState.Rejected)]
    [InlineData(OwnReviewState.Hidden)]
    public async Task OwnReview_PreservesSafeStateAndNullablePublication(OwnReviewState state)
    {
        var fixture = Fixture();
        fixture["own"]!["rating"]!["review"]!["state"] = state.ToString();
        using var handler = new Handler(request => Task.FromResult(Response(request, 200, fixture["own"])));
        var client = PrdbClientFactory.Create("test-key", Origin, handler);
        var rating = (await client.Actors[Target].Rating.GetAsync())!.Rating!;
        Assert.Equal(Guid.Parse(fixture["ratingId"]!.GetValue<string>()), rating.Id);
        Assert.Equal(RatingTargetType.Actor, rating.TargetType);
        Assert.NotEqual(rating.CreatedAtUtc, rating.UpdatedAtUtc);
        Assert.Equal("Carefully made.", rating.Review!.Text);
        Assert.Equal(state, rating.Review.State);
        Assert.Null(rating.Review.PublishedAtUtc);
    }

    [Fact]
    public async Task Mine_PreservesAllFiltersAndOpaqueCursor()
    {
        var fixture = Fixture();
        var calls = 0;
        using var handler = new Handler(request =>
        {
            Assert.Equal("/ratings/mine", request.RequestUri!.AbsolutePath);
            Assert.Equal("test-key", Assert.Single(request.Headers.GetValues("X-Api-Key")));
            var query = request.RequestUri.Query.TrimStart('?').Split('&').ToDictionary(
                part => Uri.UnescapeDataString(part.Split('=', 2)[0]),
                part => Uri.UnescapeDataString(part.Split('=', 2)[1]));
            var expected = fixture["filters"]!.AsObject().ToDictionary(pair => pair.Key, pair => pair.Value!.GetValue<string>());
            if (calls > 0) expected.Add("cursor", fixture["page"]!["nextCursor"]!.GetValue<string>());
            foreach (var key in new[] { "fromUtc", "toUtc" })
            {
                Assert.Equal(DateTimeOffset.Parse(expected[key]), DateTimeOffset.Parse(query[key]));
                query.Remove(key); expected.Remove(key);
            }
            Assert.Equal(expected.OrderBy(pair => pair.Key), query.OrderBy(pair => pair.Key));
            return Task.FromResult(Response(request, 200, fixture[calls++ == 0 ? "page" : "lastPage"]));
        });
        var client = PrdbClientFactory.Create("test-key", Origin, handler);
        string? cursor = null;
        void Configure(RequestConfiguration<Generated.Ratings.Mine.MineRequestBuilder.MineRequestBuilderGetQueryParameters> config)
        {
            var q = config.QueryParameters;
            q.Search = "Example actor"; q.Type = RatingTargetType.Actor; q.Stars = 4;
            q.FromUtc = DateTimeOffset.Parse("2026-11-01T00:00:00Z");
            q.ToUtc = DateTimeOffset.Parse("2026-12-01T00:00:00Z");
            q.HasText = true; q.ReviewState = OwnReviewState.Pending;
            q.SortBy = RatingSortBy.Stars; q.SortDirection = Generated.Ratings.Mine.GetSortDirectionQueryParameterType.Desc;
            q.PageSize = 2; q.Cursor = cursor;
        }
        var page = await client.Ratings.Mine.GetAsync(Configure);
        Assert.True(page!.HasMore);
        Assert.Equal(OwnReviewState.Pending, page.Items![0].Review!.State);
        Assert.Null(page.Items[1].Review);
        cursor = page.NextCursor;
        var last = await client.Ratings.Mine.GetAsync(Configure);
        Assert.Empty(last!.Items!);
        Assert.False(last.HasMore);
        Assert.Null(last.NextCursor);
        Assert.Equal(2, calls);
    }

    public static IEnumerable<object[]> ErrorCases =>
        from actor in new[] { true, false }
        from code in new[] { 400, 401, 403, 404, 409, 429, 503 }
        select new object[] { actor, code };

    [Theory]
    [MemberData(nameof(ErrorCases))]
    public async Task ReviewErrors_PreserveTypedProblemStatusAndRetryAfter(bool actor, int code)
    {
        var fixture = Fixture();
        using var handler = new Handler(request =>
        {
            var response = Response(request, code, fixture["problems"]![code.ToString()]);
            response.Headers.Add("Retry-After", "300");
            return Task.FromResult(response);
        });
        var client = PrdbClientFactory.Create("test-key", Origin, handler, PrdbRetryOptions.Disabled);
        var status = new ResponseStatusOption();
        var body = new SubmitRatingReviewRequest { Text = "Carefully made." };
        var problem = await Assert.ThrowsAsync<ProblemDetails>(() => actor
            ? client.Actors[Target].Rating.Review.PostAsync(body, config => config.Options.Add(status))
            : client.Videos[Target].Rating.Review.PostAsync(body, config => config.Options.Add(status)));
        Assert.Equal(code, problem.Status);
        Assert.Equal((HttpStatusCode)code, status.StatusCode);
        if (code == 429) Assert.Equal("300", Assert.Single(problem.ResponseHeaders!["Retry-After"]));
    }

    private static HttpResponseMessage Response(HttpRequestMessage request, int code, JsonNode? payload) => new((HttpStatusCode)code)
    {
        RequestMessage = request,
        Content = payload is null ? null : new StringContent(payload.ToJsonString(), Encoding.UTF8, "application/json"),
    };

    private sealed class Handler(Func<HttpRequestMessage, Task<HttpResponseMessage>> respond) : HttpMessageHandler
    {
        protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken) => respond(request);
    }
}
