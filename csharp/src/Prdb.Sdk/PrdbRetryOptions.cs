namespace Prdb.Sdk;

/// <summary>
/// How the SDK retries a request the API refused with <c>429</c>, <c>503</c> or <c>504</c>.
/// </summary>
/// <remarks>
/// Retry belongs to whoever owns the calling application's resilience story. An application
/// that already retries prdb calls itself should pass <see cref="Disabled"/>, otherwise the
/// two policies multiply: one logical call becomes up to <c>n×m</c> requests against an API
/// that rate limits, and the outer circuit breaker never sees a stable failure to open on.
/// <para>
/// The built-in policy retries idempotent and non-idempotent requests alike, so an
/// application that must not repeat a write should own the retry itself.
/// </para>
/// </remarks>
public sealed record PrdbRetryOptions
{
    /// <summary>Largest value <see cref="MaxRetries"/> accepts.</summary>
    public const int MaxAllowedRetries = 10;

    /// <summary>Largest value <see cref="Delay"/> accepts.</summary>
    public static readonly TimeSpan MaxAllowedDelay = TimeSpan.FromSeconds(180);

    /// <summary>
    /// No retrying at all: the retry handler is left out of the pipeline entirely, so a
    /// <c>429</c> or <c>503</c> reaches the caller as the first response the API gave.
    /// </summary>
    public static PrdbRetryOptions Disabled { get; } = new() { MaxRetries = 0 };

    /// <summary>
    /// How often a refused request is retried. Defaults to 3, at most
    /// <see cref="MaxAllowedRetries"/>. Zero disables retrying, like <see cref="Disabled"/>.
    /// </summary>
    public int MaxRetries { get; init; } = 3;

    /// <summary>
    /// How long to wait before a retry, unless the response carries a <c>Retry-After</c>
    /// header, which always wins. Defaults to 3 seconds, at most <see cref="MaxAllowedDelay"/>.
    /// </summary>
    public TimeSpan Delay { get; init; } = TimeSpan.FromSeconds(3);

    /// <summary>Rejects values the underlying handler would refuse later, at its own construction.</summary>
    /// <exception cref="ArgumentException">A value is negative or above its documented maximum.</exception>
    internal void Validate(string paramName)
    {
        if (MaxRetries < 0 || MaxRetries > MaxAllowedRetries)
        {
            throw new ArgumentException(
                $"{nameof(MaxRetries)} must be between 0 and {MaxAllowedRetries}, got {MaxRetries}.",
                paramName);
        }

        if (Delay < TimeSpan.Zero || Delay > MaxAllowedDelay)
        {
            throw new ArgumentException(
                $"{nameof(Delay)} must be between zero and {MaxAllowedDelay.TotalSeconds} seconds, got {Delay}.",
                paramName);
        }
    }
}
