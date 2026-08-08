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
	"strings"
	"time"

	abs "github.com/microsoft/kiota-abstractions-go"
	auth "github.com/microsoft/kiota-abstractions-go/authentication"
	bundle "github.com/microsoft/kiota-bundle-go"
	khttp "github.com/microsoft/kiota-http-go"

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
	//
	// Kiota's middleware lives in the Transport, which a supplied client owns,
	// so the SDK's pipeline -- Retry included -- does not apply to it. Setting
	// both HTTPClient and Retry is an error rather than a silent no-op.
	HTTPClient *nethttp.Client

	// Retry configures how the SDK retries a request the API refused with 429,
	// 503 or 504. Nil keeps Kiota's policy: three attempts, honouring
	// Retry-After.
	Retry *RetryOptions
}

// RetryOptions describes the SDK's retry policy.
//
// Retry belongs to whoever owns the calling application's resilience story. An
// application that already retries prdb calls itself should pass
// RetryDisabled, otherwise the two policies multiply: one logical call becomes
// up to n*m requests against an API that rate limits, and the outer circuit
// breaker never sees a stable failure to open on.
//
// The built-in policy retries idempotent and non-idempotent requests alike, so
// an application that must not repeat a write should own the retry itself.
type RetryOptions struct {
	// MaxRetries is how often a refused request is retried, at most 10. Zero
	// leaves the retry handler out of the pipeline entirely.
	MaxRetries int

	// Delay is how long to wait before a retry, unless the response carries a
	// Retry-After header, which always wins. At most 180 seconds. Rounded down
	// to whole seconds, which is the granularity the handler works in. Zero
	// means Kiota's default of three seconds.
	Delay time.Duration
}

// RetryDisabled turns retrying off: a 429 or 503 reaches the caller as the API
// sent it.
func RetryDisabled() *RetryOptions {
	return &RetryOptions{MaxRetries: 0}
}

const (
	maxAllowedRetries = 10
	maxAllowedDelay   = 180 * time.Second
)

func (o *RetryOptions) validate() error {
	if o.MaxRetries < 0 || o.MaxRetries > maxAllowedRetries {
		return fmt.Errorf(
			"prdb: retry MaxRetries must be between 0 and %d, got %d",
			maxAllowedRetries, o.MaxRetries)
	}
	if o.Delay < 0 || o.Delay > maxAllowedDelay {
		return fmt.Errorf(
			"prdb: retry Delay must be between 0 and %s, got %s", maxAllowedDelay, o.Delay)
	}
	return nil
}

// NewClient creates a client authenticated with an API key, which is sent in
// the X-Api-Key header on every request.
//
// It returns an error if apiKey is empty, or opts.BaseURL is not an absolute
// https URL. The https requirement keeps the key out of cleartext; it also
// matches Kiota's own refusal to attach a key over plain http, but fails here
// at construction rather than on the first request.
func NewClient(apiKey string, opts ...Options) (*generated.PrdbClient, error) {
	if apiKey == "" {
		return nil, errors.New("prdb: api key must not be empty")
	}

	options := firstOrZero(opts)
	baseURL, host, err := resolveBaseURL(options.BaseURL, true)
	if err != nil {
		return nil, err
	}

	// Restricting the key to the API host means Kiota will not attach it to a
	// URL it builds for another host. It says nothing about redirects, which
	// happen a layer below; buildClient handles those.
	authProvider, err := auth.NewApiKeyAuthenticationProviderWithValidHosts(
		apiKey,
		APIKeyHeader,
		auth.HEADER_KEYLOCATION,
		[]string{host},
	)
	if err != nil {
		return nil, fmt.Errorf("prdb: building authentication provider: %w", err)
	}

	return buildClient(authProvider, baseURL, options)
}

// NewAnonymousClient creates a client without credentials.
//
// Only GET /health is reachable this way; every other endpoint answers 401.
// Provided so health probes do not need an API key.
//
// With no credential to protect, opts.BaseURL may use plain http.
func NewAnonymousClient(opts ...Options) (*generated.PrdbClient, error) {
	options := firstOrZero(opts)
	baseURL, _, err := resolveBaseURL(options.BaseURL, false)
	if err != nil {
		return nil, err
	}

	return buildClient(&auth.AnonymousAuthenticationProvider{}, baseURL, options)
}

func buildClient(
	authProvider auth.AuthenticationProvider,
	baseURL string,
	options Options,
) (*generated.PrdbClient, error) {
	if options.Retry != nil {
		if err := options.Retry.validate(); err != nil {
			return nil, err
		}
		if options.HTTPClient != nil {
			return nil, errors.New(
				"prdb: Retry has no effect on a supplied HTTPClient, because Kiota's " +
					"middleware lives in the Transport that client owns; configure " +
					"retrying on that client instead, or leave HTTPClient nil")
		}
	}

	httpClient := options.HTTPClient
	if httpClient == nil {
		var err error
		httpClient, err = newHTTPClient(options.Retry)
		if err != nil {
			return nil, err
		}
	} else {
		// A caller-supplied client does not run Kiota's middleware, so apply the
		// same-host redirect rule through net/http instead. Copied rather than
		// mutated: the caller's client is theirs, not ours.
		//
		// Applied even over a CheckRedirect they set themselves. Theirs may well
		// follow a redirect off the API host, and nothing below strips X-Api-Key,
		// so leaving it in charge would hand the credential to whoever answered.
		// Ours runs first and refuses; anything it allows is then theirs to judge.
		clone := *httpClient
		clone.CheckRedirect = refuseCrossHostRedirectThen(httpClient.CheckRedirect)
		httpClient = &clone
	}

	adapter, err := bundle.NewDefaultRequestAdapterWithParseNodeFactoryAndSerializationWriterFactoryAndHttpClient(
		authProvider, nil, nil, httpClient)
	if err != nil {
		return nil, fmt.Errorf("prdb: building request adapter: %w", err)
	}

	adapter.SetBaseUrl(baseURL)

	return generated.NewPrdbClient(adapter), nil
}

// newHTTPClient builds Kiota's default client with one change: a redirect to a
// different host is refused instead of followed.
//
// This is not belt and braces. The API key travels in a custom header, and
// neither net/http nor Kiota's redirect handler strips it across hosts — both
// only drop Authorization — so a redirect off api.prdb.net would hand the
// credential to whoever answered. Same-host redirects are still followed.
func newHTTPClient(retry *RetryOptions) (*nethttp.Client, error) {
	requestOptions := []abs.RequestOption{
		&khttp.RedirectHandlerOptions{
			MaxRedirects:   defaultMaxRedirects,
			ShouldRedirect: sameHostOnly,
		},
	}

	if retry != nil && retry.MaxRetries > 0 {
		requestOptions = append(requestOptions, &khttp.RetryHandlerOptions{
			MaxRetries:   retry.MaxRetries,
			DelaySeconds: int(retry.Delay.Seconds()),
			ShouldRetry: func(_ time.Duration, _ int, _ *nethttp.Request, _ *nethttp.Response) bool {
				return true
			},
		})
	}

	middlewares, err := khttp.GetDefaultMiddlewaresWithOptions(requestOptions...)
	if err != nil {
		return nil, fmt.Errorf("prdb: building http middleware: %w", err)
	}

	if retry != nil && retry.MaxRetries == 0 {
		// Removed rather than configured with zero attempts, so "no retrying"
		// means the handler is not in the pipeline at all and cannot be
		// re-enabled by a per-request option.
		middlewares = withoutRetryHandler(middlewares)
	}

	return khttp.GetDefaultClient(middlewares...), nil
}

func withoutRetryHandler(middlewares []khttp.Middleware) []khttp.Middleware {
	kept := make([]khttp.Middleware, 0, len(middlewares))
	for _, middleware := range middlewares {
		if _, isRetry := middleware.(*khttp.RetryHandler); !isRetry {
			kept = append(kept, middleware)
		}
	}
	return kept
}

const defaultMaxRedirects = 5

// refuseCrossHostRedirectThen refuses a redirect that leaves the API host, and
// otherwise defers to the caller's own policy.
func refuseCrossHostRedirectThen(
	next func(req *nethttp.Request, via []*nethttp.Request) error,
) func(req *nethttp.Request, via []*nethttp.Request) error {
	return func(req *nethttp.Request, via []*nethttp.Request) error {
		if err := refuseCrossHostRedirect(req, via); err != nil {
			return err
		}
		if next != nil {
			return next(req, via)
		}
		return nil
	}
}

// refuseCrossHostRedirect is the net/http equivalent of sameHostOnly, for the
// path where a caller supplies their own client.
func refuseCrossHostRedirect(req *nethttp.Request, via []*nethttp.Request) error {
	if len(via) == 0 {
		return nil
	}
	if len(via) >= defaultMaxRedirects {
		return fmt.Errorf("prdb: stopped after %d redirects", defaultMaxRedirects)
	}
	if !strings.EqualFold(req.URL.Host, via[0].URL.Host) {
		return fmt.Errorf(
			"prdb: refusing to follow a redirect from %s to %s; the api key is bound to the first host",
			via[0].URL.Host, req.URL.Host)
	}
	return nil
}

func sameHostOnly(req *nethttp.Request, res *nethttp.Response) bool {
	if res == nil || req == nil {
		return false
	}

	status := res.StatusCode
	if status != nethttp.StatusMovedPermanently &&
		status != nethttp.StatusFound &&
		status != nethttp.StatusSeeOther &&
		status != nethttp.StatusTemporaryRedirect &&
		status != nethttp.StatusPermanentRedirect {
		return false
	}

	location := res.Header.Get("Location")
	if location == "" {
		return false
	}

	target, err := url.Parse(location)
	if err != nil {
		return false
	}
	if !target.IsAbs() {
		// A relative Location stays on the current host.
		return true
	}

	return strings.EqualFold(target.Host, req.URL.Host)
}

func resolveBaseURL(baseURL string, requireHTTPS bool) (resolved string, host string, err error) {
	if baseURL == "" {
		baseURL = DefaultBaseURL
	}

	parsed, parseErr := url.Parse(baseURL)
	if parseErr != nil || !parsed.IsAbs() || parsed.Host == "" ||
		(parsed.Scheme != "http" && parsed.Scheme != "https") {
		return "", "", fmt.Errorf("prdb: base URL must be an absolute URL, got %q", baseURL)
	}

	if requireHTTPS && parsed.Scheme != "https" {
		return "", "", fmt.Errorf(
			"prdb: base URL must use https so the api key is not sent in cleartext, got %q", baseURL)
	}

	return baseURL, parsed.Hostname(), nil
}

func firstOrZero(opts []Options) Options {
	if len(opts) == 0 {
		return Options{}
	}
	return opts[0]
}
