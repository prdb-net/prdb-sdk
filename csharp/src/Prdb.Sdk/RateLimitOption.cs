using System.Globalization;
using System.Net.Http.Headers;
using Microsoft.Kiota.Abstractions;

namespace Prdb.Sdk;

/// <summary>
/// One rate-limiting window, as the API reported it on a response.
/// </summary>
/// <param name="Limit">How many requests the window allows in total.</param>
/// <param name="Remaining">How many of them are left.</param>
/// <param name="ResetInSeconds">
/// Seconds until the oldest request leaves the sliding window and frees one slot — not a
/// timestamp, and not the time until the whole window resets. The same quantity
/// <c>resetsInSeconds</c> carries on <c>GET /rate-limit</c>.
/// </param>
public sealed record RateLimitWindow(int Limit, int Remaining, int ResetInSeconds);

/// <summary>
/// Per-request option reporting the rate-limit state the API sent back.
/// </summary>
/// <remarks>
/// Every metered response carries its rate-limit headers, so a client can pace itself off the
/// answers it is already getting instead of spending a request on <c>GET /rate-limit</c> to ask.
/// <para>
/// Kiota can surface response headers through its own headers-inspection option, but as raw
/// multi-valued strings that a caller has to find, pick apart and parse. This option is the
/// typed form.
/// </para>
/// <example>
/// <code>
/// var limits = new RateLimitOption();
///
/// var sites = await client.Sites.GetAsync(config => config.Options.Add(limits));
///
/// if (limits.Hour is { Remaining: &lt; 50 } hour)
/// {
///     // Slow down; hour.ResetInSeconds until a slot frees up.
/// }
/// </code>
/// </example>
/// <para>
/// One instance per call: it is written when the response arrives, so sharing one across
/// concurrent calls means whichever finishes last wins.
/// </para>
/// </remarks>
public sealed class RateLimitOption : IRequestOption
{
    /// <summary>
    /// The hourly window, or <see langword="null"/> if the response carried no hourly headers.
    /// </summary>
    public RateLimitWindow? Hour { get; internal set; }

    /// <summary>
    /// The monthly window, or <see langword="null"/> if the response carried no monthly headers.
    /// </summary>
    /// <remarks>
    /// Both are <see langword="null"/> for a response the API did not meter — <c>401</c>,
    /// <c>403</c>, <c>503</c> and <c>GET /rate-limit</c> itself — and for a call that never
    /// reached a response. A <c>429</c> carries only the window that refused it, so exactly one
    /// of the two being set is normal rather than a partial reading.
    /// </remarks>
    public RateLimitWindow? Month { get; internal set; }

    /// <summary>
    /// Reads one window's three headers, or <see langword="null"/> if they are not all there.
    /// </summary>
    /// <remarks>
    /// Deliberately lenient: rate-limit headers are metadata about a call that has already
    /// succeeded, so a missing or malformed one reports "no reading" rather than failing the
    /// call the caller actually made.
    /// </remarks>
    internal static RateLimitWindow? Read(HttpResponseHeaders headers, string window)
    {
        var values = new int[3];
        var names = new[] { "Limit", "Remaining", "Reset" };

        for (var i = 0; i < names.Length; i++)
        {
            if (!headers.TryGetValues($"X-RateLimit-{names[i]}-{window}", out var raw))
            {
                return null;
            }

            var first = raw.FirstOrDefault();
            if (!int.TryParse(
                    first,
                    NumberStyles.Integer,
                    CultureInfo.InvariantCulture,
                    out values[i]))
            {
                return null;
            }
        }

        return new RateLimitWindow(values[0], values[1], values[2]);
    }
}
