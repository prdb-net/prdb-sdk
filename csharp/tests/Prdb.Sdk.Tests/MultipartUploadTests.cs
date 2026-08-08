using System.Net;
using System.Text;
using Microsoft.Kiota.Abstractions;
using Xunit;

namespace Prdb.Sdk.Tests;

/// <summary>
/// Tests that <c>POST /video-user-images</c> is callable the way the README documents it.
/// </summary>
/// <remarks>
/// <see cref="MultipartBody"/> exposes a <c>RequestAdapter</c> property that its serialisation
/// needs, and a consumer has no way to supply one: the adapter behind
/// <see cref="Generated.PrdbClient"/> is <c>protected</c> on <c>BaseRequestBuilder</c>. Which
/// makes the endpoint read as uncallable from outside the SDK, though it is not — the request
/// adapter fills the property in while sending. Asserted here so the README's example stays
/// true, and so a Kiota upgrade that changed it would fail the build rather than the caller.
/// </remarks>
public class MultipartUploadTests
{
    private const string ApiOrigin = "https://api.example.test";

    [Fact]
    public async Task Post_UploadsMultipartFormData_WithoutTheCallerSettingTheRequestAdapter()
    {
        var recorder = new Recorder();
        var client = PrdbClientFactory.Create("secret-key", ApiOrigin, recorder);

        var body = new MultipartBody();
        body.AddOrReplacePart("File", "image/jpeg", new MemoryStream([0xFF, 0xD8, 0xFF, 0xD9]), "preview.jpg");
        body.AddOrReplacePart("PreviewImageType", "text/plain", "Single");

        // The precondition, asserted rather than assumed: nothing set this, and nothing outside
        // the SDK could have.
        Assert.Null(body.RequestAdapter);

        var result = await client.VideoUserImages.PostAsync(body);

        Assert.NotNull(result);
        Assert.StartsWith("multipart/form-data", recorder.ContentType, StringComparison.Ordinal);
        Assert.Contains("boundary=", recorder.ContentType, StringComparison.Ordinal);
        Assert.Contains("name=\"File\"", recorder.Body, StringComparison.Ordinal);
        Assert.Contains("filename=\"preview.jpg\"", recorder.Body, StringComparison.Ordinal);
        Assert.Contains("Single", recorder.Body, StringComparison.Ordinal);
    }

    /// <summary>Innermost handler: keeps the request body, then answers it.</summary>
    private sealed class Recorder : HttpMessageHandler
    {
        public string ContentType { get; private set; } = "";

        public string Body { get; private set; } = "";

        protected override async Task<HttpResponseMessage> SendAsync(
            HttpRequestMessage request,
            CancellationToken cancellationToken)
        {
            if (request.Content is { } content)
            {
                ContentType = content.Headers.ContentType?.ToString() ?? "";
                Body = await content.ReadAsStringAsync(cancellationToken);
            }

            return new HttpResponseMessage(HttpStatusCode.Created)
            {
                RequestMessage = request,
                Content = new StringContent(
                    """{"id":"00000000-0000-0000-0000-000000000100"}""",
                    Encoding.UTF8,
                    "application/json"),
            };
        }
    }
}
