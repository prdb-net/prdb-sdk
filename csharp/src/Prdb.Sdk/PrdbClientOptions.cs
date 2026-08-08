namespace Prdb.Sdk;

/// <summary>
/// Settings for a <see cref="Generated.PrdbClient"/> registered through dependency injection.
/// </summary>
/// <seealso cref="PrdbServiceCollectionExtensions.AddPrdbClient"/>
public sealed class PrdbClientOptions
{
    /// <summary>
    /// The API key, sent in the <c>X-Api-Key</c> header on every request. Leave it unset to
    /// register an anonymous client, which reaches only <c>GET /health</c>.
    /// </summary>
    public string? ApiKey { get; set; }

    /// <summary>
    /// The API root. Useful for a staging deployment. Must use <c>https</c> whenever
    /// <see cref="ApiKey"/> is set, so the key is never sent in cleartext.
    /// </summary>
    public string BaseUrl { get; set; } = PrdbClientFactory.DefaultBaseUrl;

    /// <summary>
    /// How the SDK retries a refused request. Defaults to Kiota's policy — three attempts,
    /// honouring <c>Retry-After</c>. Set <see cref="PrdbRetryOptions.Disabled"/> when the
    /// application supplies its own resilience handler on the returned builder, so the two
    /// policies do not multiply.
    /// </summary>
    public PrdbRetryOptions? Retry { get; set; }

    /// <summary>
    /// How long a request may take before it is abandoned. Defaults to
    /// <see cref="PrdbClientFactory.DefaultTimeout"/>.
    /// </summary>
    public TimeSpan? Timeout { get; set; }
}
