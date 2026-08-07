// Package prdb provides a Go client for the prdb Public API.
//
// The request builders mirror the API's URL structure, so GET /videos/{id} is
// client.Videos().ById(videoID).Get(ctx, nil).
//
//	client, err := prdb.NewClient("your-api-key")
//	if err != nil {
//	    return err
//	}
//	page, err := client.Videos().Get(context.Background(), nil)
//
// Everything under the generated package is produced by Kiota from
// spec/openapi.json and is overwritten on every regeneration. Do not edit it.
package prdb

import (
	"errors"
	"fmt"
	nethttp "net/http"
	"net/url"

	auth "github.com/microsoft/kiota-abstractions-go/authentication"
	bundle "github.com/microsoft/kiota-bundle-go"

	"github.com/prdb-net/prdb-sdk/go/generated"
)

const (
	// APIKeyHeader is the header the API expects the key in.
	APIKeyHeader = "X-Api-Key"

	// DefaultBaseURL is the production base URL, also the default baked into
	// the generated client.
	DefaultBaseURL = "https://api.prdb.net"
)

// Options tunes client construction. The zero value is valid.
type Options struct {
	// BaseURL overrides the API root. Useful for a staging deployment.
	// Defaults to DefaultBaseURL.
	BaseURL string

	// HTTPClient supplies your own client to control timeouts, proxies or
	// retries. One is created for you when nil.
	HTTPClient *nethttp.Client
}

// NewClient creates a client authenticated with an API key, which is sent in
// the X-Api-Key header on every request.
//
// It returns an error if apiKey is empty or opts.BaseURL is not absolute.
func NewClient(apiKey string, opts ...Options) (*generated.PrdbClient, error) {
	if apiKey == "" {
		return nil, errors.New("prdb: api key must not be empty")
	}

	options := firstOrZero(opts)
	baseURL, host, err := resolveBaseURL(options.BaseURL)
	if err != nil {
		return nil, err
	}

	// Restricting the key to the API host means a redirect to somewhere else
	// cannot carry the credential off-site.
	authProvider, err := auth.NewApiKeyAuthenticationProviderWithValidHosts(
		apiKey,
		APIKeyHeader,
		auth.HEADER_KEYLOCATION,
		[]string{host},
	)
	if err != nil {
		return nil, fmt.Errorf("prdb: building authentication provider: %w", err)
	}

	return buildClient(authProvider, baseURL, options.HTTPClient)
}

// NewAnonymousClient creates a client without credentials.
//
// Only GET /health is reachable this way; every other endpoint answers 401.
// Provided so health probes do not need an API key.
func NewAnonymousClient(opts ...Options) (*generated.PrdbClient, error) {
	options := firstOrZero(opts)
	baseURL, _, err := resolveBaseURL(options.BaseURL)
	if err != nil {
		return nil, err
	}

	return buildClient(&auth.AnonymousAuthenticationProvider{}, baseURL, options.HTTPClient)
}

func buildClient(
	authProvider auth.AuthenticationProvider,
	baseURL string,
	httpClient *nethttp.Client,
) (*generated.PrdbClient, error) {
	var adapter *bundle.DefaultRequestAdapter
	var err error

	if httpClient == nil {
		adapter, err = bundle.NewDefaultRequestAdapter(authProvider)
	} else {
		adapter, err = bundle.NewDefaultRequestAdapterWithParseNodeFactoryAndSerializationWriterFactoryAndHttpClient(
			authProvider, nil, nil, httpClient)
	}
	if err != nil {
		return nil, fmt.Errorf("prdb: building request adapter: %w", err)
	}

	adapter.SetBaseUrl(baseURL)

	return generated.NewPrdbClient(adapter), nil
}

func resolveBaseURL(baseURL string) (resolved string, host string, err error) {
	if baseURL == "" {
		baseURL = DefaultBaseURL
	}

	parsed, parseErr := url.Parse(baseURL)
	if parseErr != nil || !parsed.IsAbs() || parsed.Host == "" {
		return "", "", fmt.Errorf("prdb: base URL must be an absolute URL, got %q", baseURL)
	}

	return baseURL, parsed.Hostname(), nil
}

func firstOrZero(opts []Options) Options {
	if len(opts) == 0 {
		return Options{}
	}
	return opts[0]
}
