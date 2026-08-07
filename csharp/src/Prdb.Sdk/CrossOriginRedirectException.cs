namespace Prdb.Sdk;

/// <summary>
/// Thrown when the API redirects to a different origin.
/// </summary>
/// <remarks>
/// Following such a redirect would hand the API key to whoever answers at the new
/// location, so the SDK refuses it. Redirects that stay on the same origin are
/// followed normally.
/// </remarks>
public sealed class CrossOriginRedirectException : Exception
{
    /// <summary>Creates the exception for a refused redirect.</summary>
    /// <param name="originalUri">Where the request that got redirected was sent.</param>
    /// <param name="newUri">Where the redirect pointed.</param>
    public CrossOriginRedirectException(Uri originalUri, Uri newUri)
        : base($"Refusing to follow a redirect from {originalUri.Host} to {newUri.Host}; "
               + "the API key is bound to the first host.")
    {
        OriginalUri = originalUri;
        NewUri = newUri;
    }

    /// <summary>Where the request that got redirected was sent.</summary>
    public Uri OriginalUri { get; }

    /// <summary>Where the redirect pointed.</summary>
    public Uri NewUri { get; }
}
