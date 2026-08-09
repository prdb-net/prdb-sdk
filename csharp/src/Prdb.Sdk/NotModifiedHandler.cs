using System.Net;

namespace Prdb.Sdk;

/// <summary>
/// Presents a <c>304 Not Modified</c> to the request adapter as a bodyless success, so a
/// conditional request does not reach the caller as an exception.
/// </summary>
/// <remarks>
/// <c>GET /sites</c> answers <c>304</c> when the caller sends back the <c>ETag</c> it was given.
/// That is the request working, not failing — but Kiota generates no handling for a 3xx response
/// in any language, and only the C# request adapter treats an unmapped non-2xx status as a
/// failure, raising <c>ApiException</c>. Python, TypeScript and Go all return null from the same
/// call, so without this C# would be the one SDK where using an <c>ETag</c> meant wrapping the
/// normal path in <c>try</c>/<c>catch</c>.
/// <para>
/// The status is rewritten to <see cref="HttpStatusCode.NoContent"/> rather than the response
/// being replaced, so the headers — the <c>ETag</c> above all — survive untouched. This handler
/// is the outermost one in the pipeline, which means every other handler, and anything an
/// application attached through <c>AddPrdbClient</c>, has already seen the true <c>304</c>. In
/// particular <see cref="ResponseMetadataHandler"/> runs inside it, so
/// <see cref="ResponseStatusOption"/> still reports <c>304</c> and remains the way to tell "not
/// modified" apart from "nothing to return".
/// </para>
/// <para>
/// The one place the rewrite is visible is Kiota's <c>NativeResponseHandler</c>, which receives
/// the response from the adapter, above this handler, and therefore sees <c>204</c>. That is the
/// price of the adapter having no notion of a non-error 3xx; <c>204</c> is at least honest about
/// there being no body.
/// </para>
/// </remarks>
internal sealed class NotModifiedHandler : DelegatingHandler
{
    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request,
        CancellationToken cancellationToken)
    {
        var response = await base.SendAsync(request, cancellationToken).ConfigureAwait(false);

        if (response.StatusCode == HttpStatusCode.NotModified)
        {
            response.StatusCode = HttpStatusCode.NoContent;
        }

        return response;
    }
}
