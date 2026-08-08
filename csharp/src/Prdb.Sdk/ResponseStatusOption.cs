using System.Net;
using Microsoft.Kiota.Abstractions;
using Microsoft.Kiota.Http.HttpClientLibrary.Extensions;

namespace Prdb.Sdk;

/// <summary>
/// Per-request option that reports which status code the API answered a typed call with.
/// </summary>
/// <remarks>
/// A generated method returns the deserialised body and nothing else, which is a problem when
/// an operation answers with more than one success status. <c>POST /downloaded-from-indexers</c>
/// is the one that does: <c>201</c> when it created the entry, <c>200</c> when an equivalent one
/// already existed and is being returned unchanged. The bodies are the same shape, so the status
/// is the only thing that tells the two apart.
/// <para>
/// Kiota's own way of reaching the response is <c>NativeResponseHandler</c>, which suppresses
/// deserialisation while it does so — you get the raw response or the typed model, never both.
/// This option is the other half: the typed call returns as usual, and the status is here
/// afterwards.
/// </para>
/// <example>
/// <code>
/// var status = new ResponseStatusOption();
///
/// var entry = await client.DownloadedFromIndexers.PostAsync(
///     body,
///     config => config.Options.Add(status));
///
/// if (status.StatusCode == HttpStatusCode.OK)
/// {
///     // An equivalent entry already existed and was returned unchanged.
/// }
/// </code>
/// </example>
/// <para>
/// One instance per call: it is written when the response arrives, so sharing one across
/// concurrent calls means whichever finishes last wins. Reading it before the call returns is
/// meaningless for the same reason.
/// </para>
/// <para>
/// The status recorded is the one of the response the result was built from — after any
/// redirect the SDK followed, and after the last retry, whether the retrying is the SDK's own or
/// an application's inside the pipeline. A call that throws still records: a
/// <see cref="Generated.Models.ProblemDetails"/> from a <c>403</c> arrives with
/// <see cref="StatusCode"/> set.
/// </para>
/// </remarks>
public sealed class ResponseStatusOption : IRequestOption
{
    /// <summary>
    /// The status code the API answered with, or <see langword="null"/> until the call the
    /// option was passed to has produced a response.
    /// </summary>
    /// <remarks>
    /// Stays <see langword="null"/> when no response was reached at all — a connection that
    /// failed, a timeout, or a redirect refused by
    /// <see cref="CrossOriginRedirectException"/>.
    /// </remarks>
    public HttpStatusCode? StatusCode { get; internal set; }
}

/// <summary>
/// Records the response status into the <see cref="ResponseStatusOption"/> a call carries.
/// </summary>
/// <remarks>
/// Sits at the outer end of the SDK's pipeline, above the retry and redirect handlers, so what
/// it sees is the response the caller's result is built from rather than an attempt on the way
/// there.
/// </remarks>
internal sealed class ResponseStatusHandler : DelegatingHandler
{
    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request,
        CancellationToken cancellationToken)
    {
        var response = await base.SendAsync(request, cancellationToken).ConfigureAwait(false);

        if (request.GetRequestOption<ResponseStatusOption>() is { } option)
        {
            option.StatusCode = response.StatusCode;
        }

        return response;
    }
}
