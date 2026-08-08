using Microsoft.Extensions.DependencyInjection;
using Microsoft.Kiota.Http.HttpClientLibrary;
using Prdb.Sdk.Generated;

namespace Prdb.Sdk;

/// <summary>
/// Registers a <see cref="PrdbClient"/> in an application's service container.
/// </summary>
public static class PrdbServiceCollectionExtensions
{
    /// <summary>Name of the <see cref="HttpClient"/> registration the SDK uses.</summary>
    public const string HttpClientName = "Prdb.Sdk";

    /// <summary>
    /// Registers <see cref="PrdbClient"/> so it can be injected, with its connections managed
    /// by <c>IHttpClientFactory</c>.
    /// </summary>
    /// <remarks>
    /// This is the recommended way to use the SDK in an application that already has a service
    /// container. Handler lifetime and connection pooling are then managed the way the rest of
    /// the application expects, rather than by a client the SDK holds forever — which is what a
    /// hand-built <see cref="PrdbClientFactory.Create"/> singleton comes down to, stale DNS
    /// included.
    /// <para>
    /// The returned builder is the application's hook for the transport: anything added to it
    /// runs <em>inside</em> the SDK's middleware, so a resilience handler added here sees the
    /// individual HTTP attempts. Pair that with
    /// <c>options.Retry = PrdbRetryOptions.Disabled</c>, otherwise the SDK's own retry sits
    /// outside the application's and the two multiply.
    /// </para>
    /// <example>
    /// <code>
    /// services.AddPrdbClient(options =>
    /// {
    ///     options.ApiKey = configuration["Prdb:ApiKey"];
    ///     options.Retry = PrdbRetryOptions.Disabled;
    /// })
    /// .AddStandardResilienceHandler();
    /// </code>
    /// </example>
    /// <para>
    /// The client is registered as transient, which is what makes handler rotation work: each
    /// resolution asks the factory for the current handler chain. Resolving one is cheap.
    /// </para>
    /// <para>
    /// The settings are read once, here. An application whose API key or base URL can change
    /// while it runs wants the
    /// <see cref="AddPrdbClient(IServiceCollection, Action{IServiceProvider, PrdbClientOptions})"/>
    /// overload instead.
    /// </para>
    /// </remarks>
    /// <param name="services">The container to register into.</param>
    /// <param name="configure">Sets the API key, and optionally the base URL, retry policy and timeout.</param>
    /// <returns>
    /// The <see cref="IHttpClientBuilder"/> for the underlying named client, so the caller can
    /// attach their own message handlers.
    /// </returns>
    /// <exception cref="ArgumentException">
    /// The configured base URL is not absolute, is not <c>https</c> while an API key is set, or
    /// the retry or timeout settings are out of range. Thrown at registration, so a
    /// misconfiguration fails at startup rather than on the first request.
    /// </exception>
    public static IHttpClientBuilder AddPrdbClient(
        this IServiceCollection services,
        Action<PrdbClientOptions> configure)
    {
        ArgumentNullException.ThrowIfNull(services);
        ArgumentNullException.ThrowIfNull(configure);

        var options = new PrdbClientOptions();
        configure(options);

        // Built once against a throwaway transport purely to validate: every argument check in
        // the factory runs here, at registration time, instead of on the first injected use.
        using (var probe = KiotaClientFactory.GetDefaultHttpMessageHandler())
        {
            CreateClient(options, probe);
        }

        return Register(services, _ => options);
    }

    /// <summary>
    /// Registers <see cref="PrdbClient"/> with its settings read afresh on every resolution,
    /// for an application whose API key or base URL can change while it runs.
    /// </summary>
    /// <remarks>
    /// The client is transient, so <paramref name="configure"/> runs once per injected client,
    /// with the container available to read the current values from. An application that stores
    /// its credentials in a database or reloads them from configuration needs this; one that
    /// reads them from configuration at startup does not, and should prefer the
    /// <see cref="AddPrdbClient(IServiceCollection, Action{PrdbClientOptions})"/> overload,
    /// which validates them while the application is still starting.
    /// <example>
    /// <code>
    /// services.AddPrdbClient((serviceProvider, options) =>
    /// {
    ///     var settings = serviceProvider.GetRequiredService&lt;ISettingsSnapshot&gt;();
    ///     options.ApiKey = settings.PrdbApiKey;
    ///     options.BaseUrl = settings.PrdbApiUrl;
    ///     options.Retry = PrdbRetryOptions.Disabled;
    /// })
    /// .AddStandardResilienceHandler();
    /// </code>
    /// </example>
    /// <para>
    /// Settings that cannot be known at registration cannot be validated there either, so a bad
    /// base URL or an empty API key surfaces as an <see cref="ArgumentException"/> when a client
    /// is resolved. Resolve one during startup if you want the failure there.
    /// </para>
    /// </remarks>
    /// <param name="services">The container to register into.</param>
    /// <param name="configure">
    /// Sets the API key, and optionally the base URL, retry policy and timeout, from the
    /// services available at resolution time.
    /// </param>
    /// <returns>
    /// The <see cref="IHttpClientBuilder"/> for the underlying named client, so the caller can
    /// attach their own message handlers.
    /// </returns>
    public static IHttpClientBuilder AddPrdbClient(
        this IServiceCollection services,
        Action<IServiceProvider, PrdbClientOptions> configure)
    {
        ArgumentNullException.ThrowIfNull(services);
        ArgumentNullException.ThrowIfNull(configure);

        return Register(services, serviceProvider =>
        {
            var options = new PrdbClientOptions();
            configure(serviceProvider, options);

            return options;
        });
    }

    private static IHttpClientBuilder Register(
        IServiceCollection services,
        Func<IServiceProvider, PrdbClientOptions> resolveOptions)
    {
        var builder = services.AddHttpClient(HttpClientName)
            // IHttpClientFactory's own default primary handler follows redirects, which the SDK
            // refuses to build on: it would step over the cross-origin rule before it ever ran.
            // Kiota's does not redirect, so this is also the handler that makes the
            // registration work at all.
            .ConfigurePrimaryHttpMessageHandler(() => KiotaClientFactory.GetDefaultHttpMessageHandler());

        services.AddTransient(serviceProvider =>
        {
            var transport = serviceProvider
                .GetRequiredService<IHttpMessageHandlerFactory>()
                .CreateHandler(HttpClientName);

            return CreateClient(resolveOptions(serviceProvider), transport);
        });

        return builder;
    }

    // Only an unset key registers an anonymous client. An empty one is a misconfiguration --
    // most likely a missing configuration value -- and has to fail rather than quietly produce
    // a client that answers 401 on everything but the health probe.
    private static PrdbClient CreateClient(PrdbClientOptions options, HttpMessageHandler transport) =>
        options.ApiKey is null
            ? PrdbClientFactory.CreateAnonymous(options.BaseUrl, transport, options.Retry, options.Timeout)
            : PrdbClientFactory.Create(options.ApiKey, options.BaseUrl, transport, options.Retry, options.Timeout);
}
