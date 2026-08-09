using System.Net;
using System.Text;
using Microsoft.Kiota.Http.HttpClientLibrary.Middleware.Options;
using Xunit;

namespace Prdb.Sdk.Tests;

/// <summary>
/// Tests for the conditional request on <c>GET /sites</c>: sending back the <c>ETag</c> and
/// getting a <c>304</c> must be an ordinary outcome rather than an exception.
/// </summary>
/// <remarks>
/// Kiota generates no handling for a declared 3xx in any language. Python, TypeScript and Go all
/// fall through to "no body, return null"; only the C# request adapter treats an unmapped
/// non-2xx as a failure. Without <see cref="NotModifiedHandler"/>, using an <c>ETag</c> from C#
/// would mean wrapping the normal path in <c>try</c>/<c>catch</c> — which would make the whole
/// point of the <c>ETag</c> rather expensive.
/// </remarks>
public class NotModifiedTests
{
    private const string ApiOrigin = "https://api.example.test";
    private const string Etag = "W/\"abc123\"";

    /// <summary>The whole point: a 304 comes back as null, not as a thrown exception.</summary>
    [Fact]
    public async Task Get_ReturnsNull_WhenTheApiAnswersNotModified()
    {
        var client = NewClient(new Recorder(Conditional));

        var page = await client.Sites.GetAsync(config =>
            config.Headers.Add("If-None-Match", Etag));

        Assert.Null(page);
    }

    /// <summary>
    /// Null alone cannot be told apart from an empty page, so the status is what distinguishes
    /// them — and it must be the real 304, not the 204 the adapter was handed.
    /// </summary>
    [Fact]
    public async Task Get_StillReportsTheRealStatus_WhenNotModified()
    {
        var client = NewClient(new Recorder(Conditional));
        var status = new ResponseStatusOption();

        await client.Sites.GetAsync(config =>
        {
            config.Headers.Add("If-None-Match", Etag);
            config.Options.Add(status);
        });

        Assert.Equal(HttpStatusCode.NotModified, status.StatusCode);
    }

    /// <summary>
    /// The ETag has to survive the rewrite, or the caller cannot make the next conditional
    /// request and the round trip is a dead end.
    /// </summary>
    [Fact]
    public async Task Get_KeepsTheEtag_WhenNotModified()
    {
        var client = NewClient(new Recorder(Conditional));
        var inspection = new HeadersInspectionHandlerOption { InspectResponseHeaders = true };

        await client.Sites.GetAsync(config =>
        {
            config.Headers.Add("If-None-Match", Etag);
            config.Options.Add(inspection);
        });

        Assert.Equal(Etag, Assert.Single(inspection.ResponseHeaders["ETag"]));
    }

    /// <summary>Without the validator the endpoint answers normally, rewrite or no rewrite.</summary>
    [Fact]
    public async Task Get_ReturnsThePage_WhenTheValidatorDoesNotMatch()
    {
        var client = NewClient(new Recorder(Conditional));
        var status = new ResponseStatusOption();

        var page = await client.Sites.GetAsync(config => config.Options.Add(status));

        Assert.Equal(7, page?.TotalCount);
        Assert.Equal(HttpStatusCode.OK, status.StatusCode);
    }

    /// <summary>
    /// The rewrite is narrow: it must not turn a genuine failure into a silent null. A 403 still
    /// throws, with its ProblemDetails intact.
    /// </summary>
    [Fact]
    public async Task Get_StillThrows_OnARealFailure()
    {
        var client = NewClient(new Recorder(Forbidden), PrdbRetryOptions.Disabled);

        await Assert.ThrowsAsync<Generated.Models.ProblemDetails>(
            () => client.Sites.GetAsync());
    }

    private static Generated.PrdbClient NewClient(
        HttpMessageHandler transport,
        PrdbRetryOptions? retry = null) =>
        PrdbClientFactory.Create("secret-key", ApiOrigin, transport, retry);

    private static HttpResponseMessage Conditional(HttpRequestMessage request)
    {
        var sent = request.Headers.TryGetValues("If-None-Match", out var values)
            ? values.FirstOrDefault()
            : null;

        if (sent == Etag)
        {
            var notModified = new HttpResponseMessage(HttpStatusCode.NotModified)
            {
                RequestMessage = request,
            };
            notModified.Headers.TryAddWithoutValidation("ETag", Etag);
            return notModified;
        }

        var response = new HttpResponseMessage(HttpStatusCode.OK)
        {
            RequestMessage = request,
            Content = new StringContent(
                """{"items":[],"page":1,"pageSize":20,"totalCount":7}""",
                Encoding.UTF8,
                "application/json"),
        };
        response.Headers.TryAddWithoutValidation("ETag", Etag);
        return response;
    }

    private static HttpResponseMessage Forbidden(HttpRequestMessage request) =>
        new(HttpStatusCode.Forbidden)
        {
            RequestMessage = request,
            Content = new StringContent(
                """{"title":"Forbidden","status":403,"detail":"no api plan"}""",
                Encoding.UTF8,
                "application/problem+json"),
        };

    /// <summary>Innermost handler: answers every request.</summary>
    private sealed class Recorder(Func<HttpRequestMessage, HttpResponseMessage> handler)
        : HttpMessageHandler
    {
        protected override Task<HttpResponseMessage> SendAsync(
            HttpRequestMessage request,
            CancellationToken cancellationToken) =>
            Task.FromResult(handler(request));
    }
}
