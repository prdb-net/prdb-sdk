using Microsoft.Kiota.Abstractions.Authentication;
using Microsoft.Kiota.Bundle;
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
    /// <param name="baseUrl">Override the API root. Useful for a staging deployment.</param>
    /// <param name="httpClient">
    /// Supply your own <see cref="HttpClient"/> to control timeouts, proxies or retries.
    /// One is created for you when omitted.
    /// </param>
    /// <exception cref="ArgumentException">
    /// <paramref name="apiKey"/> is empty, or <paramref name="baseUrl"/> is not an absolute URL.
    /// </exception>
    public static PrdbClient Create(
        string apiKey,
        string baseUrl = DefaultBaseUrl,
        HttpClient? httpClient = null)
    {
        if (string.IsNullOrWhiteSpace(apiKey))
        {
            throw new ArgumentException("API key must not be empty.", nameof(apiKey));
        }

        var host = HostOf(baseUrl, nameof(baseUrl));

        // Restricting the key to the API host means a redirect to somewhere else
        // cannot carry the credential off-site.
        var authProvider = new ApiKeyAuthenticationProvider(
            apiKey,
            ApiKeyHeader,
            ApiKeyAuthenticationProvider.KeyLocation.Header,
            host);

        return Build(authProvider, baseUrl, httpClient);
    }

    /// <summary>
    /// Creates a client without credentials.
    /// </summary>
    /// <remarks>
    /// Only <c>GET /health</c> is reachable this way; every other endpoint answers 401.
    /// Provided so health probes do not need an API key.
    /// </remarks>
    public static PrdbClient CreateAnonymous(
        string baseUrl = DefaultBaseUrl,
        HttpClient? httpClient = null)
    {
        HostOf(baseUrl, nameof(baseUrl));

        return Build(new AnonymousAuthenticationProvider(), baseUrl, httpClient);
    }

    private static PrdbClient Build(
        IAuthenticationProvider authProvider,
        string baseUrl,
        HttpClient? httpClient)
    {
        var adapter = httpClient is null
            ? new DefaultRequestAdapter(authProvider)
            : new DefaultRequestAdapter(authProvider, httpClient: httpClient);

        adapter.BaseUrl = baseUrl;

        return new PrdbClient(adapter);
    }

    private static string HostOf(string baseUrl, string paramName)
    {
        if (!Uri.TryCreate(baseUrl, UriKind.Absolute, out var uri) || string.IsNullOrEmpty(uri.Host))
        {
            throw new ArgumentException($"Base URL must be an absolute URL, got '{baseUrl}'.", paramName);
        }

        return uri.Host;
    }
}
