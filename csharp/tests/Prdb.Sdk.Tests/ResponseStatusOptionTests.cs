using System.Net;
using System.Text;
using Prdb.Sdk.Generated.Models;
using Xunit;

namespace Prdb.Sdk.Tests;

/// <summary>
/// Tests for <see cref="ResponseStatusOption"/>: a typed call that also reports which status
/// the API answered with.
/// </summary>
public class ResponseStatusOptionTests
{
    private const string ApiOrigin = "https://api.example.test";

    /// <summary>
    /// Both halves at once, which is what Kiota's <c>NativeResponseHandler</c> cannot do: it
    /// surfaces the raw response but suppresses deserialisation, so the typed result comes back
    /// null.
    /// </summary>
    [Fact]
    public async Task Get_ReportsTheSuccessStatus_AlongsideTheTypedResult()
    {
        var client = NewClient(new Recorder());
        var option = new ResponseStatusOption();

        var health = await client.Health.GetAsync(config => config.Options.Add(option));

        Assert.Equal("healthy", health?.Status);
        Assert.Equal(HttpStatusCode.OK, option.StatusCode);
    }

    /// <summary>
    /// The status is the one the result was built from, so a retried request reports the
    /// attempt that succeeded rather than the refusal before it.
    /// </summary>
    /// <remarks>
    /// Which is only true because the handler sits above the retry handler. An application's
    /// own resilience pipeline is further in still — <c>AddPrdbClient</c> attaches it inside
    /// the SDK's middleware — so this covers that case too.
    /// </remarks>
    [Fact]
    public async Task Get_ReportsTheLastAttempt_WhenARefusalIsRetried()
    {
        var recorder = new Recorder(RefuseOnceThenSucceed());
        var client = NewClient(recorder, new PrdbRetryOptions { MaxRetries = 1, Delay = TimeSpan.Zero });
        var option = new ResponseStatusOption();

        await client.Health.GetAsync(config => config.Options.Add(option));

        Assert.Equal(2, recorder.Requests.Count);
        Assert.Equal(HttpStatusCode.OK, option.StatusCode);
    }

    /// <summary>Likewise for a redirect the SDK followed: the destination answered, not the 307.</summary>
    [Fact]
    public async Task Get_ReportsTheStatusAfterASameOriginRedirect()
    {
        var client = NewClient(new Recorder(RedirectWithinTheApi));
        var option = new ResponseStatusOption();

        await client.Health.GetAsync(config => config.Options.Add(option));

        Assert.Equal(HttpStatusCode.OK, option.StatusCode);
    }

    /// <summary>
    /// A refusal records too. The call throws its <see cref="ProblemDetails"/> as always, and
    /// the status is there for a caller that catches it.
    /// </summary>
    [Fact]
    public async Task Get_ReportsTheStatus_WhenTheApiRefuses()
    {
        var client = NewClient(new Recorder(Forbidden), PrdbRetryOptions.Disabled);
        var option = new ResponseStatusOption();

        await Assert.ThrowsAsync<ProblemDetails>(
            () => client.UserIdentity.GetAsync(config => config.Options.Add(option)));

        Assert.Equal(HttpStatusCode.Forbidden, option.StatusCode);
    }

    /// <summary>
    /// Nothing was reached, so there is no status to report — rather than a stale or invented
    /// one.
    /// </summary>
    [Fact]
    public async Task Get_ReportsNoStatus_WhenACrossOriginRedirectIsRefused()
    {
        var client = NewClient(new Recorder(RedirectAwayFromTheApi));
        var option = new ResponseStatusOption();

        await Assert.ThrowsAsync<CrossOriginRedirectException>(
            () => client.Health.GetAsync(config => config.Options.Add(option)));

        Assert.Null(option.StatusCode);
    }

    /// <summary>The handler is in every pipeline, so a call without the option must be unaffected.</summary>
    [Fact]
    public async Task Get_Succeeds_WithoutTheOption()
    {
        var client = NewClient(new Recorder());

        Assert.NotNull(await client.Health.GetAsync());
    }

    private static Generated.PrdbClient NewClient(
        HttpMessageHandler transport,
        PrdbRetryOptions? retry = null) =>
        PrdbClientFactory.Create("secret-key", ApiOrigin, transport, retry);

    private static Func<HttpRequestMessage, HttpResponseMessage> RefuseOnceThenSucceed()
    {
        var served = 0;
        return request => served++ == 0
            ? new HttpResponseMessage(HttpStatusCode.ServiceUnavailable) { RequestMessage = request }
            : Healthy(request);
    }

    private static HttpResponseMessage RedirectWithinTheApi(HttpRequestMessage request) =>
        request.RequestUri!.AbsolutePath == "/health"
            ? Redirect(request, $"{ApiOrigin}/healthz")
            : Healthy(request);

    private static HttpResponseMessage RedirectAwayFromTheApi(HttpRequestMessage request) =>
        request.RequestUri!.Host == "api.example.test"
            ? Redirect(request, "https://elsewhere.example.test/health")
            : Healthy(request);

    private static HttpResponseMessage Redirect(HttpRequestMessage request, string location)
    {
        var response = new HttpResponseMessage(HttpStatusCode.TemporaryRedirect)
        {
            // Kiota's redirect handler builds the follow-up request from this.
            RequestMessage = request,
        };
        response.Headers.Location = new Uri(location);
        return response;
    }

    private static HttpResponseMessage Healthy(HttpRequestMessage request) =>
        Json(request, HttpStatusCode.OK, """{"status":"healthy","timestamp":"2026-08-07T12:00:00Z"}""");

    private static HttpResponseMessage Forbidden(HttpRequestMessage request) =>
        Json(
            request,
            HttpStatusCode.Forbidden,
            """{"title":"Forbidden","status":403,"detail":"no api plan"}""",
            "application/problem+json");

    private static HttpResponseMessage Json(
        HttpRequestMessage request,
        HttpStatusCode status,
        string body,
        string contentType = "application/json") =>
        new(status)
        {
            RequestMessage = request,
            Content = new StringContent(body, Encoding.UTF8, contentType),
        };

    /// <summary>Innermost handler: records every request, then answers it.</summary>
    private sealed class Recorder(Func<HttpRequestMessage, HttpResponseMessage>? handler = null)
        : HttpMessageHandler
    {
        private readonly Func<HttpRequestMessage, HttpResponseMessage> _handler =
            handler ?? Healthy;

        public List<Uri> Requests { get; } = [];

        protected override Task<HttpResponseMessage> SendAsync(
            HttpRequestMessage request,
            CancellationToken cancellationToken)
        {
            Requests.Add(request.RequestUri!);

            return Task.FromResult(_handler(request));
        }
    }
}
