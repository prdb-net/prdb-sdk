using Microsoft.Kiota.Abstractions;
using Microsoft.Kiota.Abstractions.Authentication;

namespace Prdb.Sdk;

/// <summary>
/// Puts the API key in the <c>X-Api-Key</c> header of requests to the API host, and leaves
/// every other request alone.
/// </summary>
/// <remarks>
/// Kiota's own <see cref="ApiKeyAuthenticationProvider"/> does exactly this, except that it
/// refuses any scheme but <c>https</c> — a loopback address included, where the request never
/// reaches a wire the key could be read off. Rather than let that refusal surface on the first
/// call to a local server, the wrapper carries the same logic with the loopback exemption
/// <see cref="PrdbClientFactory.IsLoopback"/> describes.
/// <para>
/// The host binding is Kiota's, unchanged: <see cref="AllowedHostsValidator"/> holds the base
/// URL's host, and a request to anywhere else is returned unauthenticated rather than rejected,
/// so the key cannot be attached to a URL built for another host.
/// </para>
/// </remarks>
internal sealed class ApiKeyHeaderAuthenticationProvider : IAuthenticationProvider
{
    private readonly string apiKey;
    private readonly AllowedHostsValidator validator;

    /// <param name="apiKey">The key to send.</param>
    /// <param name="allowedHost">The only host it may be sent to.</param>
    internal ApiKeyHeaderAuthenticationProvider(string apiKey, string allowedHost)
    {
        this.apiKey = apiKey;
        validator = new AllowedHostsValidator([allowedHost]);
    }

    /// <exception cref="InvalidOperationException">
    /// The request would carry the key over plain <c>http</c> to somewhere other than a loopback
    /// address. Construction rejects such a base URL, so this covers a URL that became insecure
    /// afterwards rather than anything a caller can reach directly.
    /// </exception>
    public Task AuthenticateRequestAsync(
        RequestInformation request,
        Dictionary<string, object>? additionalAuthenticationContext = null,
        CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(request);

        if (!validator.IsUrlHostValid(request.URI))
        {
            return Task.CompletedTask;
        }

        if (request.URI.Scheme != Uri.UriSchemeHttps && !PrdbClientFactory.IsLoopback(request.URI))
        {
            throw new InvalidOperationException(
                $"Refusing to send the API key to '{request.URI}': plain http is accepted only "
                + "for a loopback address.");
        }

        request.Headers.Add(PrdbClientFactory.ApiKeyHeader, apiKey);

        return Task.CompletedTask;
    }
}
