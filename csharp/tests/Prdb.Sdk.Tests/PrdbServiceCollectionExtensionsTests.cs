using System.Net;
using System.Text;
using Microsoft.Extensions.DependencyInjection;
using Prdb.Sdk.Generated;
using Xunit;

namespace Prdb.Sdk.Tests;

/// <summary>
/// Tests for the dependency injection registration.
/// </summary>
/// <remarks>
/// What matters here is that the client's connections are managed by
/// <c>IHttpClientFactory</c> rather than by a handler the SDK holds forever, and that routing
/// construction through the factory does not quietly weaken the redirect rule.
/// </remarks>
public class PrdbServiceCollectionExtensionsTests
{
    private const string ApiOrigin = "https://api.example.test";

    [Fact]
    public async Task AddPrdbClient_ResolvesAClientThatSendsTheApiKey()
    {
        var recorder = new Recorder();
        var services = new ServiceCollection();

        services.AddPrdbClient(options =>
        {
            options.ApiKey = "secret-key";
            options.BaseUrl = ApiOrigin;
        })
        .ConfigurePrimaryHttpMessageHandler(() => recorder);

        using var provider = services.BuildServiceProvider();
        await provider.GetRequiredService<PrdbClient>().Health.GetAsync();

        Assert.Equal("secret-key", Assert.Single(recorder.ApiKeys));
    }

    /// <summary>
    /// Anything the application adds to the returned builder has to end up inside the SDK's
    /// middleware — that is what makes the builder the right place for a resilience handler.
    /// </summary>
    [Fact]
    public async Task AddPrdbClient_RunsHandlersAddedToTheBuilder()
    {
        var recorder = new Recorder();
        var counter = new CountingHandler();
        var services = new ServiceCollection();

        services.AddPrdbClient(options =>
        {
            options.ApiKey = "secret-key";
            options.BaseUrl = ApiOrigin;
        })
        .AddHttpMessageHandler(() => counter)
        .ConfigurePrimaryHttpMessageHandler(() => recorder);

        using var provider = services.BuildServiceProvider();
        await provider.GetRequiredService<PrdbClient>().Health.GetAsync();

        Assert.Equal(1, counter.Seen);
    }

    /// <summary>
    /// <c>IHttpClientFactory</c>'s own default primary handler follows redirects, which would
    /// step over the cross-origin refusal before it ever runs. The registration replaces it.
    /// </summary>
    [Fact]
    public void AddPrdbClient_UsesAPrimaryHandlerThatDoesNotFollowRedirects()
    {
        var services = new ServiceCollection();
        services.AddPrdbClient(options => options.ApiKey = "secret-key");

        using var provider = services.BuildServiceProvider();
        var handler = provider
            .GetRequiredService<IHttpMessageHandlerFactory>()
            .CreateHandler(PrdbServiceCollectionExtensions.HttpClientName);

        Assert.False(AllowsAutoRedirect(handler));
    }

    /// <summary>
    /// Transient, so every resolution asks the factory for the current handler chain. A
    /// singleton would pin one handler for the lifetime of the process and never see a DNS
    /// change, which is the problem the registration exists to solve.
    /// </summary>
    [Fact]
    public void AddPrdbClient_RegistersTheClientAsTransient()
    {
        var services = new ServiceCollection();
        services.AddPrdbClient(options => options.ApiKey = "secret-key");

        using var provider = services.BuildServiceProvider();

        Assert.NotSame(
            provider.GetRequiredService<PrdbClient>(),
            provider.GetRequiredService<PrdbClient>());
    }

    /// <summary>A misconfiguration should stop startup, not the first request hours later.</summary>
    [Fact]
    public void AddPrdbClient_RejectsAPlaintextBaseUrl_AtRegistration()
    {
        var services = new ServiceCollection();

        var error = Assert.Throws<ArgumentException>(() => services.AddPrdbClient(options =>
        {
            options.ApiKey = "secret-key";
            options.BaseUrl = "http://localhost:8080";
        }));

        Assert.Contains("https", error.Message, StringComparison.Ordinal);
    }

    /// <summary>
    /// An unset key is a deliberate anonymous client; an empty one is a configuration value
    /// that failed to resolve, and must not silently become a client that only reaches /health.
    /// </summary>
    [Fact]
    public void AddPrdbClient_RejectsAnEmptyApiKey_ButAllowsAnUnsetOne()
    {
        Assert.Throws<ArgumentException>(
            () => new ServiceCollection().AddPrdbClient(options => options.ApiKey = ""));

        var anonymous = new ServiceCollection();
        anonymous.AddPrdbClient(options => options.BaseUrl = ApiOrigin);

        using var provider = anonymous.BuildServiceProvider();
        Assert.NotNull(provider.GetRequiredService<PrdbClient>());
    }

    private static bool AllowsAutoRedirect(HttpMessageHandler handler)
    {
        for (var current = handler; current is not null;)
        {
            switch (current)
            {
                case SocketsHttpHandler sockets:
                    return sockets.AllowAutoRedirect;

                case HttpClientHandler client:
                    return client.AllowAutoRedirect;

                case DelegatingHandler delegating:
                    current = delegating.InnerHandler;
                    continue;

                default:
                    return false;
            }
        }

        return false;
    }

    private sealed class CountingHandler : DelegatingHandler
    {
        public int Seen { get; private set; }

        protected override Task<HttpResponseMessage> SendAsync(
            HttpRequestMessage request,
            CancellationToken cancellationToken)
        {
            Seen++;

            return base.SendAsync(request, cancellationToken);
        }
    }

    private sealed class Recorder : HttpMessageHandler
    {
        public List<string> ApiKeys { get; } = [];

        protected override Task<HttpResponseMessage> SendAsync(
            HttpRequestMessage request,
            CancellationToken cancellationToken)
        {
            if (request.Headers.TryGetValues(PrdbClientFactory.ApiKeyHeader, out var values))
            {
                ApiKeys.Add(string.Join(",", values));
            }

            return Task.FromResult(new HttpResponseMessage(HttpStatusCode.OK)
            {
                RequestMessage = request,
                Content = new StringContent(
                    """{"status":"healthy","timestamp":"2026-08-07T12:00:00Z"}""",
                    Encoding.UTF8,
                    "application/json"),
            });
        }
    }
}
