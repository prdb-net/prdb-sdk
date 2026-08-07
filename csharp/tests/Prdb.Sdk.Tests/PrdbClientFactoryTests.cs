using System.Net;
using System.Text;
using Xunit;

namespace Prdb.Sdk.Tests;

/// <summary>
/// Tests for the hand-written client wrapper.
/// </summary>
/// <remarks>
/// The generated code is not tested here; it is Kiota's output and is covered by
/// the drift check in CI. What is worth testing is the wrapper's own promises:
/// where the API key goes, and where it must not go.
/// <para>
/// Requests are served by a recording <see cref="HttpMessageHandler"/> rather than
/// a real socket, so no TLS certificates are needed and every test stays in-process.
/// </para>
/// </remarks>
public class PrdbClientFactoryTests
{
    private const string ApiOrigin = "https://api.example.test";
    private const string OtherOrigin = "https://elsewhere.example.test";

    [Fact]
    public async Task Create_SendsTheApiKeyHeader()
    {
        var recorder = new Recorder();
        var client = PrdbClientFactory.Create("secret-key", ApiOrigin, recorder);

        await client.Health.GetAsync();

        Assert.Equal("secret-key", recorder.Requests[0].ApiKey);
    }

    [Fact]
    public async Task CreateAnonymous_SendsNoApiKey()
    {
        var recorder = new Recorder();
        var client = PrdbClientFactory.CreateAnonymous(ApiOrigin, recorder);

        await client.Health.GetAsync();

        Assert.Null(recorder.Requests[0].ApiKey);
    }

    /// <summary>
    /// The guarantee the README makes, pinned down.
    /// </summary>
    /// <remarks>
    /// Kiota's default scrubbing drops only <c>Authorization</c>, so without the
    /// wrapper's own rule the key would travel to whoever answers at the redirect
    /// target.
    /// </remarks>
    [Fact]
    public async Task Create_RefusesACrossOriginRedirect_WithoutLeakingTheKey()
    {
        var recorder = new Recorder(RedirectAwayFromTheApi);
        var client = PrdbClientFactory.Create("secret-key", ApiOrigin, recorder);

        await Assert.ThrowsAsync<CrossOriginRedirectException>(
            () => client.Health.GetAsync());

        Assert.Empty(recorder.KeysSentTo("elsewhere.example.test"));
    }

    /// <summary>Refusing cross-origin redirects must not refuse ordinary ones.</summary>
    [Fact]
    public async Task Create_FollowsASameOriginRedirect()
    {
        var recorder = new Recorder(RedirectWithinTheApi);
        var client = PrdbClientFactory.Create("secret-key", ApiOrigin, recorder);

        var result = await client.Health.GetAsync();

        Assert.NotNull(result);
        Assert.Equal(
            ["/health", "/healthz"],
            recorder.Requests.Select(request => request.Uri.AbsolutePath));
        Assert.Equal(
            ["secret-key", "secret-key"],
            recorder.KeysSentTo("api.example.test"));
    }

    [Fact]
    public void Create_RejectsAnEmptyApiKey()
    {
        Assert.Throws<ArgumentException>(() => PrdbClientFactory.Create(""));
    }

    [Theory]
    [InlineData("api.prdb.net")]
    [InlineData("/videos")]
    [InlineData("not a url")]
    [InlineData("")]
    public void Create_RejectsARelativeBaseUrl(string baseUrl)
    {
        Assert.Throws<ArgumentException>(() => PrdbClientFactory.Create("secret-key", baseUrl));
    }

    /// <summary>
    /// An API key must not travel in cleartext. The Go SDK's Kiota provider refuses
    /// this outright; the others do not, so the wrapper enforces it to keep the four
    /// SDKs behaving alike. A staging deployment therefore has to terminate TLS.
    /// </summary>
    [Fact]
    public void Create_RejectsAPlaintextBaseUrl()
    {
        var error = Assert.Throws<ArgumentException>(
            () => PrdbClientFactory.Create("secret-key", "http://localhost:8080"));

        Assert.Contains("https", error.Message, StringComparison.Ordinal);
    }

    /// <summary>With no credential to protect, plain HTTP is the caller's business.</summary>
    [Fact]
    public void CreateAnonymous_AllowsAPlaintextBaseUrl()
    {
        Assert.NotNull(PrdbClientFactory.CreateAnonymous("http://localhost:8080"));
    }

    [Fact]
    public void DefaultBaseUrl_IsProduction()
    {
        Assert.StartsWith("https://", PrdbClientFactory.DefaultBaseUrl, StringComparison.Ordinal);
    }

    private static HttpResponseMessage RedirectAwayFromTheApi(HttpRequestMessage request) =>
        request.RequestUri!.Host == "api.example.test"
            ? Redirect(request, $"{OtherOrigin}/health")
            : Healthy(request);

    private static HttpResponseMessage RedirectWithinTheApi(HttpRequestMessage request) =>
        request.RequestUri!.AbsolutePath == "/health"
            ? Redirect(request, $"{ApiOrigin}/healthz")
            : Healthy(request);

    private static HttpResponseMessage Redirect(HttpRequestMessage request, string location)
    {
        var response = new HttpResponseMessage(HttpStatusCode.TemporaryRedirect)
        {
            // Kiota's redirect handler builds the follow-up request from this;
            // a real handler sets it, so the fake has to as well.
            RequestMessage = request,
        };
        response.Headers.Location = new Uri(location);
        return response;
    }

    private static HttpResponseMessage Healthy(HttpRequestMessage request) =>
        new(HttpStatusCode.OK)
        {
            RequestMessage = request,
            Content = new StringContent(
                """{"status":"healthy","timestamp":"2026-08-07T12:00:00Z"}""",
                Encoding.UTF8,
                "application/json"),
        };

    private sealed record SeenRequest(Uri Uri, string? ApiKey);

    /// <summary>Innermost handler: records every request, then answers it.</summary>
    private sealed class Recorder(Func<HttpRequestMessage, HttpResponseMessage>? handler = null)
        : HttpMessageHandler
    {
        private readonly Func<HttpRequestMessage, HttpResponseMessage> _handler =
            handler ?? Healthy;

        public List<SeenRequest> Requests { get; } = [];

        public IEnumerable<string> KeysSentTo(string host) =>
            Requests
                .Where(request => request.Uri.Host == host && request.ApiKey is not null)
                .Select(request => request.ApiKey!);

        protected override Task<HttpResponseMessage> SendAsync(
            HttpRequestMessage request,
            CancellationToken cancellationToken)
        {
            var apiKey = request.Headers.TryGetValues(PrdbClientFactory.ApiKeyHeader, out var values)
                ? string.Join(",", values)
                : null;

            Requests.Add(new SeenRequest(request.RequestUri!, apiKey));

            return Task.FromResult(_handler(request));
        }
    }
}
