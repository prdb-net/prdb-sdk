using Microsoft.Kiota.Abstractions.Authentication;
using Microsoft.Kiota.Bundle;
using Microsoft.Kiota.Http.HttpClientLibrary;
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
    /// Creates a client authenticated with an API key.
    /// </summary>
    /// <param name="apiKey">The API key, sent in the <c>X-Api-Key</c> header on every request.</param>
    /// <param name="baseUrl">
    /// Override the API root. Useful for a staging deployment. Must use <c>https</c>,
    /// so the key is never sent in cleartext.
    /// </param>
    /// <param name="transport">
    /// Supply your own innermost <see cref="HttpMessageHandler"/> to control timeouts,
    /// proxies or connection pooling. The SDK's middleware is layered on top of it either
    /// way, so the redirect rule below always applies.
    /// </param>
    /// <exception cref="ArgumentException">
    /// <paramref name="apiKey"/> is empty, or <paramref name="baseUrl"/> is not an
    /// absolute <c>https</c> URL.
    /// </exception>
    public static PrdbClient Create(
        string apiKey,
        string baseUrl = DefaultBaseUrl,
        HttpMessageHandler? transport = null)
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

        return Build(authProvider, baseUrl, transport);
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
    /// <paramref name="baseUrl"/> is not an absolute URL.
    /// </exception>
    public static PrdbClient CreateAnonymous(
        string baseUrl = DefaultBaseUrl,
        HttpMessageHandler? transport = null)
    {
        HostOf(baseUrl, nameof(baseUrl), requireHttps: false);

        return Build(new AnonymousAuthenticationProvider(), baseUrl, transport);
    }

    private static PrdbClient Build(
        IAuthenticationProvider authProvider,
        string baseUrl,
        HttpMessageHandler? transport)
    {
        var handlers = KiotaClientFactory.CreateDefaultHandlers([RedirectOption()]);
        var httpClient = KiotaClientFactory.Create(handlers, transport);

        var adapter = new DefaultRequestAdapter(authProvider, httpClient: httpClient)
        {
            BaseUrl = baseUrl,
        };

        return new PrdbClient(adapter);
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
