using System.Net;
using System.Text;
using Microsoft.Kiota.Abstractions;
using Xunit;

namespace Prdb.Sdk.Tests;

/// <summary>
/// Tests for what the wrapper does to the HTTP pipeline it builds: retrying, the request
/// deadline, who owns a caller-supplied transport, and who is allowed to follow a redirect.
/// </summary>
/// <remarks>
/// The credential tests live in <see cref="PrdbClientFactoryTests"/>. These are about the
/// pipeline being the shape the README promises, because every one of these properties is
/// invisible from a typed call and would otherwise only surface in production.
/// </remarks>
public class PrdbClientPipelineTests
{
    private const string ApiOrigin = "https://api.example.test";

    /// <summary>Kiota's retry handler is in the default pipeline, so this is the status quo.</summary>
    [Fact]
    public async Task Create_RetriesARefusedRequest_ByDefault()
    {
        var recorder = new Recorder(RefuseOnce());
        var client = PrdbClientFactory.Create(
            "secret-key",
            ApiOrigin,
            recorder,
            retry: Immediate);

        var result = await client.Health.GetAsync();

        Assert.NotNull(result);
        Assert.Equal(2, recorder.Requests.Count);
    }

    /// <summary>
    /// The opt-out an application with its own retry policy needs.
    /// </summary>
    /// <remarks>
    /// Without it, the SDK's retry sits outside the application's and the two multiply: one
    /// logical call becomes several requests against an API that rate limits, and the outer
    /// circuit breaker never sees a stable failure.
    /// </remarks>
    [Fact]
    public async Task Create_DoesNotRetry_WhenRetryIsDisabled()
    {
        var recorder = new Recorder(AlwaysRefuse);
        var client = PrdbClientFactory.Create(
            "secret-key",
            ApiOrigin,
            recorder,
            retry: PrdbRetryOptions.Disabled);

        await Assert.ThrowsAsync<ApiException>(() => client.Health.GetAsync());

        Assert.Single(recorder.Requests);
    }

    [Fact]
    public void Create_RejectsRetriesAboveTheSupportedMaximum()
    {
        var error = Assert.Throws<ArgumentException>(() => PrdbClientFactory.Create(
            "secret-key",
            ApiOrigin,
            retry: new PrdbRetryOptions { MaxRetries = PrdbRetryOptions.MaxAllowedRetries + 1 }));

        Assert.Contains(nameof(PrdbRetryOptions.MaxRetries), error.Message, StringComparison.Ordinal);
    }

    [Fact]
    public void Create_RejectsANegativeRetryDelay()
    {
        Assert.Throws<ArgumentException>(() => PrdbClientFactory.Create(
            "secret-key",
            ApiOrigin,
            retry: new PrdbRetryOptions { Delay = TimeSpan.FromSeconds(-1) }));
    }

    /// <summary>
    /// The timeout is not reachable through <c>transport</c>: it lives on the HttpClient the
    /// factory builds, which is deliberately never exposed. Hence its own parameter.
    /// </summary>
    [Fact]
    public void BuildHttpClient_AppliesTheRequestedTimeout()
    {
        using var transport = new Recorder();

        using var withDefault = PrdbClientFactory.BuildHttpClient(transport, null, null);
        using var withCustom = PrdbClientFactory.BuildHttpClient(
            transport, null, TimeSpan.FromSeconds(5));

        Assert.Equal(PrdbClientFactory.DefaultTimeout, withDefault.Timeout);
        Assert.Equal(TimeSpan.FromSeconds(5), withCustom.Timeout);
    }

    [Fact]
    public void Create_RejectsANonPositiveTimeout()
    {
        Assert.Throws<ArgumentException>(() => PrdbClientFactory.Create(
            "secret-key",
            ApiOrigin,
            timeout: TimeSpan.Zero));
    }

    /// <summary>
    /// The ownership contract for a caller-supplied transport, pinned down.
    /// </summary>
    /// <remarks>
    /// The natural way to hand the SDK an application's pipeline is
    /// <c>IHttpMessageHandlerFactory.CreateHandler</c>, and those handlers are pooled and
    /// shared. Disposing one would break every other caller in the process, so the SDK must
    /// never dispose what it did not create.
    /// </remarks>
    [Fact]
    public async Task BuildHttpClient_DoesNotDisposeACallerSuppliedTransport()
    {
        using var transport = new Recorder();

        PrdbClientFactory.BuildHttpClient(transport, null, null).Dispose();

        // Still serving: if the client had owned the transport, this would throw.
        using var probe = new HttpClient(transport, disposeHandler: false);
        var response = await probe.GetAsync($"{ApiOrigin}/health");

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
    }

    /// <summary>
    /// A transport that follows redirects itself would step over the cross-origin refusal:
    /// our handler never sees the redirect, and nothing below strips <c>X-Api-Key</c>.
    /// </summary>
    /// <remarks>
    /// Kiota's own default transport disables redirect following; a plain
    /// <see cref="SocketsHttpHandler"/> or <see cref="HttpClientHandler"/> does not, and a
    /// handler chain from <c>IHttpMessageHandlerFactory</c> ends in one of those.
    /// </remarks>
    [Theory]
    [InlineData(false)]
    [InlineData(true)]
    public void Create_StopsACallerSuppliedTransportFromFollowingRedirects(bool behindADelegatingHandler)
    {
        var primary = new SocketsHttpHandler { AllowAutoRedirect = true };
        HttpMessageHandler transport = behindADelegatingHandler
            ? new PassThroughHandler { InnerHandler = primary }
            : primary;

        using (transport)
        {
            PrdbClientFactory.Create("secret-key", ApiOrigin, transport);

            Assert.False(primary.AllowAutoRedirect);
        }
    }

    /// <summary>Retrying with no delay, so a test does not wait out the real backoff.</summary>
    private static PrdbRetryOptions Immediate => new() { MaxRetries = 1, Delay = TimeSpan.Zero };

    private static Func<HttpRequestMessage, HttpResponseMessage> RefuseOnce()
    {
        var served = 0;
        return request => served++ == 0 ? Unavailable(request) : Healthy(request);
    }

    private static HttpResponseMessage AlwaysRefuse(HttpRequestMessage request) =>
        Unavailable(request);

    private static HttpResponseMessage Unavailable(HttpRequestMessage request) =>
        new(HttpStatusCode.ServiceUnavailable) { RequestMessage = request };

    private static HttpResponseMessage Healthy(HttpRequestMessage request) =>
        new(HttpStatusCode.OK)
        {
            RequestMessage = request,
            Content = new StringContent(
                """{"status":"healthy","timestamp":"2026-08-07T12:00:00Z"}""",
                Encoding.UTF8,
                "application/json"),
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

    /// <summary>Stands in for the delegating handlers an application adds to its own pipeline.</summary>
    private sealed class PassThroughHandler : DelegatingHandler;
}
