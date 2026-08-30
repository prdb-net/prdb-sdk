namespace Prdb.Sdk;

/// <summary>
/// Settings for a <see cref="Generated.PrdbClient"/> registered through dependency injection.
/// </summary>
/// <seealso cref="PrdbServiceCollectionExtensions.AddPrdbClient(Microsoft.Extensions.DependencyInjection.IServiceCollection, System.Action{PrdbClientOptions})"/>
public sealed class PrdbClientOptions
{
    /// <summary>
    /// The API key, sent in the <c>X-Api-Key</c> header on every request. Leave it unset to
    /// register an anonymous client, which reaches only <c>GET /health</c>.
    /// </summary>
    public string? ApiKey { get; set; }

    /// <summary>
    /// The API root. Useful for a staging deployment. Must use <c>https</c> whenever
    /// <see cref="ApiKey"/> is set, so the key is never sent in cleartext — except for a
    /// loopback address (<c>localhost</c>, <c>127.0.0.1</c> or <c>[::1]</c>), where plain
    /// <c>http</c> is accepted because the request never leaves the machine.
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
