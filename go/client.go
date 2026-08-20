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
	"strconv"
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

// ResponseStatusOption reports which status code the API answered a typed call
// with.
//
// A generated method returns the deserialised body and nothing else. That is
// not enough when the status itself matters, for example when a conditional
// GET /sites returns 304 with no body.
//
// Pass one per call, in the request configuration's Options:
//
//	status := prdb.NewResponseStatusOption()
//	health, err := client.Health().Get(ctx,
//	    &abstractions.RequestConfiguration[abstractions.DefaultQueryParameters]{
//	        Options: []abstractions.RequestOption{status},
//	    })
//	if err != nil { return err }
//	fmt.Println(health, status.StatusCode)
//
// One instance per call: it is written when the response arrives, so sharing
// one across concurrent calls means whichever finishes last wins.
//
// The status recorded is the one of the response the result was built from --
// after any redirect that was followed, and after the last retry. A call that
// fails records too, so the status is there for a caller that inspects the
// error.
type ResponseStatusOption struct {
	// StatusCode is the status of the last response received, or zero until the
	// call the option was passed to has produced one -- and for good if nothing
	// answered at all, as with a connection failure or a timeout.
	//
	// "Last" matters only when a redirect is refused: a caller-supplied
	// *http.Client follows redirects above the SDK's transport, so the redirect
	// response itself is what was last received. Everywhere else the last
	// response is the one the result was built from.
	StatusCode int
}

// NewResponseStatusOption returns an option ready to be passed to one call.
func NewResponseStatusOption() *ResponseStatusOption {
	return &ResponseStatusOption{}
}

// responseStatusKey is what the request adapter files the option under in the
// request context, and therefore what the metadata transport looks it up by.
var responseStatusKey = abs.RequestOptionKey{Key: "prdb.responseStatus"}

// GetKey identifies the option to Kiota.
func (o *ResponseStatusOption) GetKey() abs.RequestOptionKey {
	return responseStatusKey
}

// RateLimitWindow is one rate-limiting window, as the API reported it on a
// response.
type RateLimitWindow struct {
	// Limit is how many requests the window allows in total.
	Limit int
	// Remaining is how many of them are left.
	Remaining int
	// ResetInSeconds is the number of seconds until the oldest request leaves
	// the sliding window and frees one slot -- not a timestamp, and not the time
	// until the whole window resets. The same quantity resetsInSeconds carries
	// on GET /rate-limit.
	ResetInSeconds int
}

// RateLimitOption reports the rate-limit state the API sent back.
//
// Every metered response carries its rate-limit headers, so a client can pace
// itself off the answers it is already getting instead of spending a request on
// GET /rate-limit to ask.
//
// Kiota can surface response headers through its own headers-inspection option,
// but as raw multi-valued strings that a caller has to find, pick apart and
// parse -- and that option is a Kiota middleware, so it reads nothing at all
// when the caller supplied their own *http.Client. This one is the typed form
// and works on both paths:
//
//	limits := prdb.NewRateLimitOption()
//	sites, err := client.Sites().Get(ctx,
//	    &abstractions.RequestConfiguration[sites.SitesRequestBuilderGetQueryParameters]{
//	        Options: []abstractions.RequestOption{limits},
//	    })
//	if limits.Hour != nil && limits.Hour.Remaining < 50 {
//	    // Slow down; limits.Hour.ResetInSeconds until a slot frees up.
//	}
//
// One instance per call: it is written when the response arrives, so sharing
// one across concurrent calls means whichever finishes last wins.
type RateLimitOption struct {
	// Hour is the hourly window, or nil if the response carried no hourly
	// headers.
	Hour *RateLimitWindow

	// Month is the monthly window, or nil if the response carried no monthly
	// headers.
	//
	// Both are nil for a response the API did not meter -- 401, 403, 503 and
	// GET /rate-limit itself -- and for a call that never reached a response. A
	// 429 carries only the window that refused it, so exactly one of the two
	// being set is normal rather than a partial reading.
	Month *RateLimitWindow
}

// NewRateLimitOption returns an option ready to be passed to one call.
func NewRateLimitOption() *RateLimitOption {
	return &RateLimitOption{}
}

// rateLimitKey is what the request adapter files the option under in the
// request context.
var rateLimitKey = abs.RequestOptionKey{Key: "prdb.rateLimit"}

// GetKey identifies the option to Kiota.
func (o *RateLimitOption) GetKey() abs.RequestOptionKey {
	return rateLimitKey
}

// readRateLimitWindow reads one window's three headers, or nil if they are not
// all there.
//
// Deliberately lenient: rate-limit headers are metadata about a call that has
// already succeeded, so a missing or malformed one reports "no reading" rather
// than failing the call the caller actually made.
func readRateLimitWindow(header nethttp.Header, window string) *RateLimitWindow {
	var values [3]int

	for i, name := range [3]string{"Limit", "Remaining", "Reset"} {
		raw := header.Get("X-RateLimit-" + name + "-" + window)
		if raw == "" {
			return nil
		}

		value, err := strconv.Atoi(strings.TrimSpace(raw))
		if err != nil {
			return nil
		}

		values[i] = value
	}

	return &RateLimitWindow{
		Limit:          values[0],
		Remaining:      values[1],
		ResetInSeconds: values[2],
	}
}

// responseMetadataTransport records response metadata into the options a
// request carries.
//
// A RoundTripper rather than a Kiota middleware, because it has to work on both
// paths: Kiota's middleware lives in the Transport, which a caller-supplied
// client owns and the SDK does not touch. Wrapping the transport of the client
// the SDK sends through covers both. That matters for more than tidiness --
// Kiota's own headers-inspection option is a middleware, so it silently reads
// nothing for a caller who supplied their own client, which is exactly the trap
// this avoids.
//
// On the client the SDK builds, that puts it outside the whole middleware
// pipeline, retries and redirects included, so it records the response the
// result was built from. With a caller-supplied client it runs per round trip,
// below net/http's own redirect following, so the last response it sees wins --
// the same one, unless a redirect was refused.
type responseMetadataTransport struct {
	next nethttp.RoundTripper
}

func (t responseMetadataTransport) RoundTrip(req *nethttp.Request) (*nethttp.Response, error) {
	response, err := t.next.RoundTrip(req)

	if response != nil {
		ctx := req.Context()

		if option, ok := ctx.Value(responseStatusKey).(*ResponseStatusOption); ok {
			option.StatusCode = response.StatusCode
		}

		if option, ok := ctx.Value(rateLimitKey).(*RateLimitOption); ok {
			option.Hour = readRateLimitWindow(response.Header, "Hour")
			option.Month = readRateLimitWindow(response.Header, "Month")
		}
	}

	return response, err
}

// recordResponseMetadata wraps a client's transport so the options are filled
// in. The client is ours by this point -- either built here or a copy of the
// caller's -- so replacing its transport is not a write to anything they own.
func recordResponseMetadata(client *nethttp.Client) {
	next := client.Transport
	if next == nil {
		next = nethttp.DefaultTransport
	}

	client.Transport = responseMetadataTransport{next: next}
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
		recordResponseMetadata(httpClient)
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
		recordResponseMetadata(&clone)
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
