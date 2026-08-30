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
            () => PrdbClientFactory.Create("secret-key", "http://api.example.test:8080"));

        Assert.Contains("https", error.Message, StringComparison.Ordinal);
    }

    /// <summary>
    /// A request to a loopback address never reaches a wire the key could be read off,
    /// so the cleartext rule has nothing to protect there. Without this, testing against
    /// a local stand-in for the API would need a certificate for a server that only ever
    /// answers itself.
    /// </summary>
    [Theory]
    [InlineData("http://localhost:8080")]
    [InlineData("http://LOCALHOST:8080")]
    [InlineData("http://127.0.0.1:8080")]
    [InlineData("http://[::1]:8080")]
    public void Create_AllowsAPlaintextLoopbackBaseUrl(string baseUrl)
    {
        Assert.NotNull(PrdbClientFactory.Create("secret-key", baseUrl));
    }

    /// <summary>
    /// The exemption is for the three names browsers treat as a secure context, not for
    /// everything <see cref="Uri.IsLoopback"/> accepts: the rest of <c>127.0.0.0/8</c> stays
    /// out, so all four SDKs accept the same base URLs.
    /// </summary>
    [Theory]
    [InlineData("http://127.0.0.2:8080")]
    [InlineData("http://localhost.example.test:8080")]
    [InlineData("http://127.0.0.1.example.test:8080")]
    public void Create_RejectsAPlaintextBaseUrlThatIsMerelyLoopbackAdjacent(string baseUrl)
    {
        Assert.Throws<ArgumentException>(() => PrdbClientFactory.Create("secret-key", baseUrl));
    }

    /// <summary>
    /// Construction succeeding is only half of it: Kiota's authentication provider gets its
    /// own say on the scheme, so the key has to be shown actually arriving over plain http.
    /// </summary>
    [Fact]
    public async Task Create_SendsTheApiKeyOverPlaintextLoopback()
    {
        var recorder = new Recorder();
        var client = PrdbClientFactory.Create("secret-key", "http://127.0.0.1:8080", recorder);

        await client.Health.GetAsync();

        Assert.Equal("secret-key", recorder.Requests[0].ApiKey);
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
