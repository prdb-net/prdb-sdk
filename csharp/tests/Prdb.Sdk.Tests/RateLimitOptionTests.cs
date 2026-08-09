using System.Net;
using System.Text;
using Prdb.Sdk.Generated.Models;
using Xunit;

namespace Prdb.Sdk.Tests;

/// <summary>
/// Tests for <see cref="RateLimitOption"/>: a typed call that also reports the rate-limit state
/// the API sent back.
/// </summary>
/// <remarks>
/// Every metered response carries the headers, so a client can pace itself off the answers it is
/// already getting rather than spending a request on <c>GET /rate-limit</c> to ask. Kiota can
/// surface them, but only as raw multi-valued strings.
/// </remarks>
public class RateLimitOptionTests
{
    private const string ApiOrigin = "https://api.example.test";

    private static readonly (string Name, string Value)[] RateLimitHeaders =
    [
        ("X-RateLimit-Limit-Hour", "1000"),
        ("X-RateLimit-Remaining-Hour", "993"),
        ("X-RateLimit-Reset-Hour", "2471"),
        ("X-RateLimit-Limit-Month", "50000"),
        ("X-RateLimit-Remaining-Month", "48120"),
        ("X-RateLimit-Reset-Month", "1904322"),
    ];

    /// <summary>The reading arrives with the typed model, not instead of it.</summary>
    [Fact]
    public async Task Get_ReportsBothWindows_AlongsideTheTypedResult()
    {
        var client = NewClient(new Recorder(request => Sites(request, HttpStatusCode.OK, RateLimitHeaders)));
        var limits = new RateLimitOption();

        var page = await client.Sites.GetAsync(config => config.Options.Add(limits));

        Assert.Equal(7, page?.TotalCount);
        Assert.Equal(new RateLimitWindow(1000, 993, 2471), limits.Hour);
        Assert.Equal(new RateLimitWindow(50000, 48120, 1904322), limits.Month);
    }

    /// <summary>
    /// A <c>429</c> carries only the window that refused it, so exactly one window being set is
    /// normal rather than a partial reading. A refusal is also exactly when a caller wants it.
    /// </summary>
    [Fact]
    public async Task Get_ReportsOnlyTheWindow_ThatRefusedTheRequest()
    {
        var hourlyOnly = RateLimitHeaders
            .Where(header => header.Name.EndsWith("-Hour", StringComparison.Ordinal))
            .Append(("Retry-After", "2471"))
            .ToArray();

        var client = NewClient(
            new Recorder(request => Sites(request, HttpStatusCode.TooManyRequests, hourlyOnly)),
            PrdbRetryOptions.Disabled);
        var limits = new RateLimitOption();

        await Assert.ThrowsAsync<ProblemDetails>(
            () => client.Sites.GetAsync(config => config.Options.Add(limits)));

        Assert.Equal(new RateLimitWindow(1000, 993, 2471), limits.Hour);
        Assert.Null(limits.Month);
    }

    /// <summary>
    /// <c>401</c>, <c>403</c>, <c>503</c> and <c>GET /rate-limit</c> carry no headers at all.
    /// "Not metered" is an answer, so it reads as null rather than as a zeroed window.
    /// </summary>
    [Fact]
    public async Task Get_ReportsNoRateLimit_ForAnUnmeteredResponse()
    {
        var client = NewClient(new Recorder(request => Sites(request, HttpStatusCode.OK, [])));
        var limits = new RateLimitOption();

        await client.Sites.GetAsync(config => config.Options.Add(limits));

        Assert.Null(limits.Hour);
        Assert.Null(limits.Month);
    }

    /// <summary>
    /// Metadata about a call that already worked must not be able to break it. Note that the
    /// windows are read independently, so one unreadable header does not cost the other.
    /// </summary>
    [Fact]
    public async Task Get_SurvivesAMalformedHeader_WithoutFailingTheCall()
    {
        var malformed = RateLimitHeaders
            .Select(header => header.Name == "X-RateLimit-Remaining-Hour"
                ? (header.Name, Value: "12abc")
                : header)
            .ToArray();

        var client = NewClient(new Recorder(request => Sites(request, HttpStatusCode.OK, malformed)));
        var limits = new RateLimitOption();

        var page = await client.Sites.GetAsync(config => config.Options.Add(limits));

        Assert.Equal(7, page?.TotalCount);
        Assert.Null(limits.Hour);
        Assert.Equal(new RateLimitWindow(50000, 48120, 1904322), limits.Month);
    }

    /// <summary>The reading is of the response the result was built from, not of an attempt.</summary>
    [Fact]
    public async Task Get_ReportsTheLastAttempt_WhenARefusalIsRetried()
    {
        var served = 0;
        var client = NewClient(
            new Recorder(request => served++ == 0
                ? Sites(request, HttpStatusCode.ServiceUnavailable, [])
                : Sites(request, HttpStatusCode.OK, RateLimitHeaders)),
            new PrdbRetryOptions { MaxRetries = 1, Delay = TimeSpan.Zero });
        var limits = new RateLimitOption();

        await client.Sites.GetAsync(config => config.Options.Add(limits));

        Assert.Equal(new RateLimitWindow(1000, 993, 2471), limits.Hour);
    }

    /// <summary>The handler is in every pipeline, so a call without the option must be unaffected.</summary>
    [Fact]
    public async Task Get_Succeeds_WithoutTheOption()
    {
        var client = NewClient(new Recorder(request => Sites(request, HttpStatusCode.OK, RateLimitHeaders)));

        Assert.NotNull(await client.Sites.GetAsync());
    }

    private static Generated.PrdbClient NewClient(
        HttpMessageHandler transport,
        PrdbRetryOptions? retry = null) =>
        PrdbClientFactory.Create("secret-key", ApiOrigin, transport, retry);

    private static HttpResponseMessage Sites(
        HttpRequestMessage request,
        HttpStatusCode status,
        (string Name, string Value)[] headers)
    {
        var body = status == HttpStatusCode.TooManyRequests
            ? """{"title":"Too Many Requests","status":429}"""
            : """{"items":[],"page":1,"pageSize":20,"totalCount":7}""";

        var response = new HttpResponseMessage(status)
        {
            RequestMessage = request,
            Content = new StringContent(body, Encoding.UTF8, "application/json"),
        };

        foreach (var (name, value) in headers)
        {
            response.Headers.TryAddWithoutValidation(name, value);
        }

        return response;
    }

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
