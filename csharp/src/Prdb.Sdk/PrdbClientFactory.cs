using Microsoft.Kiota.Abstractions;
using Microsoft.Kiota.Abstractions.Authentication;
using Microsoft.Kiota.Bundle;
using Microsoft.Kiota.Http.HttpClientLibrary;
using Microsoft.Kiota.Http.HttpClientLibrary.Middleware;
using Microsoft.Kiota.Http.HttpClientLibrary.Middleware.Options;
using Prdb.Sdk.Generated;

namespace Prdb.Sdk;

/// <summary>
/// Creates <see cref="PrdbClient"/> instances for the prdb Public API.
/// </summary>
/// <remarks>
/// The request builders mirror the API's URL structure, so <c>GET /videos/{id}</c>
/// is <c>client.Videos[videoId].GetAsync()</c>.
/// <para>
/// Everything under <c>Prdb.Sdk.Generated</c> is produced by Kiota from
/// <c>spec/openapi.json</c> and is overwritten on every regeneration.
/// </para>
/// </remarks>
public static class PrdbClientFactory
{
    /// <summary>Header the API expects the key in.</summary>
    public const string ApiKeyHeader = "X-Api-Key";

    /// <summary>Production base URL, also the default baked into the generated client.</summary>
    public const string DefaultBaseUrl = "https://api.prdb.net";

    /// <summary>
    /// How long a request may take before it is abandoned, unless a caller asks for
    /// something else. Matches <see cref="HttpClient"/>'s own default.
    /// </summary>
    public static readonly TimeSpan DefaultTimeout = TimeSpan.FromSeconds(100);

    /// <summary>
    /// Creates a client authenticated with an API key.
    /// </summary>
    /// <param name="apiKey">The API key, sent in the <c>X-Api-Key</c> header on every request.</param>
    /// <param name="baseUrl">
    /// Override the API root. Useful for a staging deployment. Must use <c>https</c>,
    /// so the key is never sent in cleartext.
    /// </param>
    /// <param name="transport">
    /// Supply your own innermost <see cref="HttpMessageHandler"/> to control proxies or
    /// connection pooling, or to insert your own resilience pipeline. The SDK's middleware is
    /// layered on top of it either way, so the redirect rule below always applies. It must not
    /// follow redirects itself — see <see cref="RequireNoRedirectsBelowUs"/>. The SDK neither
    /// disposes nor modifies a handler you supply.
    /// </param>
    /// <param name="retry">
    /// How the SDK retries a refused request. Defaults to Kiota's policy — three attempts,
    /// honouring <c>Retry-After</c>. Pass <see cref="PrdbRetryOptions.Disabled"/> if your
    /// application already retries prdb calls itself.
    /// </param>
    /// <param name="timeout">
    /// How long a request may take before it is abandoned. Defaults to
    /// <see cref="DefaultTimeout"/>. This cannot be set through <paramref name="transport"/>,
    /// because the deadline lives on the <see cref="HttpClient"/> above it.
    /// </param>
    /// <exception cref="ArgumentException">
    /// <paramref name="apiKey"/> is empty, <paramref name="baseUrl"/> is not an absolute
    /// <c>https</c> URL, <paramref name="transport"/> follows redirects, or
    /// <paramref name="retry"/> or <paramref name="timeout"/> is out of range.
    /// </exception>
    public static PrdbClient Create(
        string apiKey,
        string baseUrl = DefaultBaseUrl,
        HttpMessageHandler? transport = null,
        PrdbRetryOptions? retry = null,
        TimeSpan? timeout = null)
    {
        if (string.IsNullOrWhiteSpace(apiKey))
        {
            throw new ArgumentException("API key must not be empty.", nameof(apiKey));
        }

        var host = HostOf(baseUrl, nameof(baseUrl), requireHttps: true);

        var authProvider = new ApiKeyAuthenticationProvider(
            apiKey,
            ApiKeyHeader,
            ApiKeyAuthenticationProvider.KeyLocation.Header,
            host);

        return Build(authProvider, baseUrl, transport, retry, timeout);
    }

    /// <summary>
    /// Creates a client without credentials.
    /// </summary>
    /// <remarks>
    /// Only <c>GET /health</c> is reachable this way; every other endpoint answers 401.
    /// Provided so health probes do not need an API key.
    /// <para>
    /// With no credential to protect, <paramref name="baseUrl"/> may use plain <c>http</c>.
    /// </para>
    /// </remarks>
    /// <exception cref="ArgumentException">
    /// <paramref name="baseUrl"/> is not an absolute URL, <paramref name="transport"/> follows
    /// redirects, or <paramref name="retry"/> or <paramref name="timeout"/> is out of range.
    /// </exception>
    public static PrdbClient CreateAnonymous(
        string baseUrl = DefaultBaseUrl,
        HttpMessageHandler? transport = null,
        PrdbRetryOptions? retry = null,
        TimeSpan? timeout = null)
    {
        HostOf(baseUrl, nameof(baseUrl), requireHttps: false);

        return Build(new AnonymousAuthenticationProvider(), baseUrl, transport, retry, timeout);
    }

    private static PrdbClient Build(
        IAuthenticationProvider authProvider,
        string baseUrl,
        HttpMessageHandler? transport,
        PrdbRetryOptions? retry,
        TimeSpan? timeout)
    {
        var adapter = new DefaultRequestAdapter(
            authProvider,
            httpClient: BuildHttpClient(transport, retry, timeout))
        {
            BaseUrl = baseUrl,
        };

        return new PrdbClient(adapter);
    }

    /// <summary>
    /// Builds the <see cref="HttpClient"/> the request adapter sends through: the SDK's
    /// middleware pipeline, ending in <paramref name="transport"/> when one was supplied.
    /// </summary>
    internal static HttpClient BuildHttpClient(
        HttpMessageHandler? transport,
        PrdbRetryOptions? retry,
        TimeSpan? timeout)
    {
        retry?.Validate(nameof(retry));

        if (timeout is { } requested && requested <= TimeSpan.Zero && requested != Timeout.InfiniteTimeSpan)
        {
            throw new ArgumentException($"Timeout must be positive, got {requested}.", nameof(timeout));
        }

        var handlers = CreateHandlers(retry);

        HttpClient httpClient;
        if (transport is null)
        {
            httpClient = KiotaClientFactory.Create(handlers, null);
        }
        else
        {
            RequireNoRedirectsBelowUs(transport);

            // Built by hand rather than through KiotaClientFactory.Create, which leaves the
            // HttpClient owning its handler: disposing this client would then dispose the
            // caller's transport too. A handler from IHttpMessageHandlerFactory is pooled and
            // shared, so tearing it down would break every other caller in the process.
            var chain = KiotaClientFactory.ChainHandlersCollectionAndGetFirstLink(transport, [.. handlers]);
            httpClient = new HttpClient(chain!, disposeHandler: false);
        }

        httpClient.Timeout = timeout ?? DefaultTimeout;

        return httpClient;
    }

    /// <summary>
    /// Kiota's default handlers, with the retry handler configured or removed, and the SDK's
    /// own status recorder in front of them.
    /// </summary>
    /// <remarks>
    /// The retry handler is removed rather than configured with zero attempts, so "no retrying"
    /// means the handler is not in the pipeline at all and cannot be re-enabled by a per-request
    /// option.
    /// <para>
    /// <see cref="ResponseStatusHandler"/> goes first, which puts it above the retry and
    /// redirect handlers — and above whatever an application added through
    /// <c>AddPrdbClient</c>, since that runs inside ours. So the status it records is the one of
    /// the response the caller's result was built from, not of an attempt on the way there.
    /// </para>
    /// </remarks>
    private static IList<DelegatingHandler> CreateHandlers(PrdbRetryOptions? retry)
    {
        var options = new List<IRequestOption> { RedirectOption() };

        if (retry is { MaxRetries: > 0 })
        {
            options.Add(new RetryHandlerOption
            {
                MaxRetry = retry.MaxRetries,
                Delay = (int)Math.Ceiling(retry.Delay.TotalSeconds),
            });
        }

        var handlers = KiotaClientFactory.CreateDefaultHandlers([.. options]);

        if (retry is { MaxRetries: 0 })
        {
            for (var i = handlers.Count - 1; i >= 0; i--)
            {
                if (handlers[i] is RetryHandler)
                {
                    handlers.RemoveAt(i);
                }
            }
        }

        handlers.Insert(0, new ResponseStatusHandler());

        return handlers;
    }

    /// <summary>
    /// Refuses a caller-supplied transport that follows redirects itself, so the SDK's
    /// redirect handler is the only thing that decides whether a redirect is followed.
    /// </summary>
    /// <remarks>
    /// A fresh <see cref="SocketsHttpHandler"/> or <see cref="HttpClientHandler"/> follows
    /// redirects on its own — Kiota's default transport is the exception, not the rule. A
    /// transport that follows one itself never lets our handler see it, and neither
    /// <see cref="HttpClient"/> nor the handler below strips a custom header across origins,
    /// so the API key would travel to whoever answered.
    /// <para>
    /// Checked rather than corrected. Writing the property is not ours to do twice over: a
    /// <see cref="SocketsHttpHandler"/> refuses every property write once it has served a
    /// request, and a handler from <c>IHttpMessageHandlerFactory</c> is pooled for the whole
    /// handler lifetime — so correcting it would throw on the second client built from the
    /// same handler, and on the first it would reconfigure a transport shared with every other
    /// consumer of that client name. Reading is legal at any time, and a configuration error
    /// naming the property says more than a leak that never happens.
    /// </para>
    /// <para>
    /// A handler from <c>IHttpMessageHandlerFactory</c> is a chain of delegating handlers, so
    /// the primary one at the end of it is what has to be reached.
    /// </para>
    /// </remarks>
    /// <exception cref="ArgumentException">The transport follows redirects.</exception>
    private static void RequireNoRedirectsBelowUs(HttpMessageHandler transport)
    {
        for (var handler = transport; handler is not null;)
        {
            switch (handler)
            {
                case SocketsHttpHandler { AllowAutoRedirect: true }:
                case HttpClientHandler { AllowAutoRedirect: true }:
                    throw new ArgumentException(
                        "The transport must not follow redirects: set AllowAutoRedirect to "
                        + "false on its primary handler, or build it with "
                        + "KiotaClientFactory.GetDefaultHttpMessageHandler(). A redirect the "
                        + "transport follows itself is one the SDK never sees, and nothing "
                        + $"below strips {ApiKeyHeader}, so the key would reach whoever "
                        + "answered at the other origin.",
                        nameof(transport));

                case DelegatingHandler delegating:
                    handler = delegating.InnerHandler;
                    continue;

                default:
                    // Either a handler that does not redirect, or someone else's handler type.
                    // For the latter there is no portable way to ask; the redirect tests cover
                    // the types we can reach.
                    return;
            }
        }
    }

    /// <summary>
    /// Kiota's default redirect behaviour with one change: a redirect to a different
    /// origin is refused instead of followed.
    /// </summary>
    /// <remarks>
    /// The API key travels in a custom header, and nothing below this point strips it.
    /// Kiota's default scrubbing removes only <c>Authorization</c>, and
    /// <see cref="HttpClient"/>'s own redirect handling does not touch custom headers
    /// either, so a redirect off the API host would hand the credential to whoever
    /// answered. Redirects that stay on the same origin are followed normally.
    /// </remarks>
    private static RedirectHandlerOption RedirectOption() => new()
    {
        ScrubSensitiveHeaders = RefuseCrossOriginRedirect,
    };

    /// <param name="request">The redirect request, already pointing at the new location.</param>
    /// <param name="originalUri">Where the request that got redirected was sent.</param>
    /// <param name="resolver">Kiota's URI resolver; unused here.</param>
    private static void RefuseCrossOriginRedirect(
        HttpRequestMessage request,
        Uri originalUri,
        Func<Uri, Uri?>? resolver)
    {
        var newUri = request.RequestUri;
        if (newUri is null || IsSameOrigin(originalUri, newUri))
        {
            return;
        }

        // Removed before throwing as well, so the key is gone even if a caller
        // catches the exception and reuses the request.
        request.Headers.Remove(ApiKeyHeader);
        request.Headers.Authorization = null;
        request.Headers.Remove("Cookie");

        throw new CrossOriginRedirectException(originalUri, newUri);
    }

    private static bool IsSameOrigin(Uri left, Uri right) =>
        string.Equals(left.Scheme, right.Scheme, StringComparison.OrdinalIgnoreCase)
        && string.Equals(left.Host, right.Host, StringComparison.OrdinalIgnoreCase)
        && left.Port == right.Port;

    private static string HostOf(string baseUrl, string paramName, bool requireHttps)
    {
        if (!Uri.TryCreate(baseUrl, UriKind.Absolute, out var uri)
            || string.IsNullOrEmpty(uri.Host)
            || (uri.Scheme != Uri.UriSchemeHttp && uri.Scheme != Uri.UriSchemeHttps))
        {
            throw new ArgumentException($"Base URL must be an absolute URL, got '{baseUrl}'.", paramName);
        }

        if (requireHttps && uri.Scheme != Uri.UriSchemeHttps)
        {
            throw new ArgumentException(
                $"Base URL must use https so the API key is not sent in cleartext, got '{baseUrl}'.",
                paramName);
        }

        return uri.Host;
    }
}
