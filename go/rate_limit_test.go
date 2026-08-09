package prdb

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"

	abs "github.com/microsoft/kiota-abstractions-go"

	"github.com/prdb-net/prdb-sdk/go/generated"
	"github.com/prdb-net/prdb-sdk/go/generated/models"
	"github.com/prdb-net/prdb-sdk/go/generated/sites"
)

const sitesBody = `{"items":[],"page":1,"pageSize":20,"totalCount":7}`

var rateLimitHeaders = map[string]string{
	"X-RateLimit-Limit-Hour":      "1000",
	"X-RateLimit-Remaining-Hour":  "993",
	"X-RateLimit-Reset-Hour":      "2471",
	"X-RateLimit-Limit-Month":     "50000",
	"X-RateLimit-Remaining-Month": "48120",
	"X-RateLimit-Reset-Month":     "1904322",
}

func sitesHandler(status int, headers map[string]string) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		for name, value := range headers {
			w.Header().Set(name, value)
		}
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(status)
		_, _ = w.Write([]byte(sitesBody))
	}
}

// sitesTLSServer answers over TLS, so its client can be handed to NewClient.
// That drives the caller-supplied *http.Client path -- the one where Kiota's own
// headers-inspection option reads nothing, because it is a middleware and a
// supplied client owns the Transport those live in.
func sitesTLSServer(t *testing.T, status int, headers map[string]string) *httptest.Server {
	t.Helper()

	server := httptest.NewTLSServer(sitesHandler(status, headers))
	t.Cleanup(server.Close)

	return server
}

// sitesServer answers over plain HTTP, for the client the SDK builds itself.
func sitesServer(t *testing.T, status int, headers map[string]string) *httptest.Server {
	t.Helper()

	server := httptest.NewServer(sitesHandler(status, headers))
	t.Cleanup(server.Close)

	return server
}

func listSites(
	client *generated.PrdbClient,
	limits *RateLimitOption,
) (models.ListSitesResponseable, error) {
	return client.Sites().Get(
		context.Background(),
		&abs.RequestConfiguration[sites.SitesRequestBuilderGetQueryParameters]{
			Options: []abs.RequestOption{limits},
		},
	)
}

func assertWindow(t *testing.T, got *RateLimitWindow, want RateLimitWindow, which string) {
	t.Helper()

	if got == nil {
		t.Fatalf("%s window = nil, want %+v", which, want)
	}
	if *got != want {
		t.Errorf("%s window = %+v, want %+v", which, *got, want)
	}
}

// The point of the option: pace off the response you already have.
//
// Note that this drives the caller-supplied *http.Client path -- server.Client()
// -- which is the one where Kiota's own headers-inspection option reads nothing
// at all, because that option is a middleware and a supplied client owns the
// Transport its middleware would live in.
func TestRateLimitOptionReportsBothWindows(t *testing.T) {
	server := sitesTLSServer(t, http.StatusOK, rateLimitHeaders)

	client, err := NewClient("secret-key", Options{
		BaseURL:    server.URL,
		HTTPClient: server.Client(),
	})
	if err != nil {
		t.Fatalf("NewClient: %v", err)
	}

	limits := NewRateLimitOption()

	page, err := listSites(client, limits)
	if err != nil {
		t.Fatalf("Get: %v", err)
	}

	if page == nil || page.GetTotalCount() == nil || *page.GetTotalCount() != 7 {
		t.Errorf("the typed result did not survive: %+v", page)
	}

	assertWindow(t, limits.Hour, RateLimitWindow{Limit: 1000, Remaining: 993, ResetInSeconds: 2471}, "hourly")
	assertWindow(t, limits.Month, RateLimitWindow{Limit: 50000, Remaining: 48120, ResetInSeconds: 1904322}, "monthly")
}

// A 429 carries only the window that refused it, so exactly one window being set
// is normal rather than a partial reading. A refusal is also exactly when a
// caller wants the reading, so it records on the error path too.
func TestRateLimitOptionReportsOnlyTheRefusingWindow(t *testing.T) {
	hourlyOnly := map[string]string{"Retry-After": "2471"}
	for name, value := range rateLimitHeaders {
		if len(name) > 5 && name[len(name)-5:] == "-Hour" {
			hourlyOnly[name] = value
		}
	}

	server := sitesServer(t, http.StatusTooManyRequests, hourlyOnly)

	client, err := NewAnonymousClient(Options{
		BaseURL: server.URL,
		Retry:   RetryDisabled(),
	})
	if err != nil {
		t.Fatalf("NewAnonymousClient: %v", err)
	}

	limits := NewRateLimitOption()

	if _, err := listSites(client, limits); err == nil {
		t.Fatal("Get succeeded, want a refusal")
	}

	assertWindow(t, limits.Hour, RateLimitWindow{Limit: 1000, Remaining: 993, ResetInSeconds: 2471}, "hourly")
	if limits.Month != nil {
		t.Errorf("monthly window = %+v, want nil", *limits.Month)
	}
}

// 401, 403, 503 and GET /rate-limit carry no headers at all. "Not metered" is an
// answer, so it reads as nil rather than as a zeroed window.
func TestRateLimitOptionReportsNothingForAnUnmeteredResponse(t *testing.T) {
	server := sitesTLSServer(t, http.StatusOK, nil)

	client, err := NewClient("secret-key", Options{
		BaseURL:    server.URL,
		HTTPClient: server.Client(),
	})
	if err != nil {
		t.Fatalf("NewClient: %v", err)
	}

	limits := NewRateLimitOption()

	if _, err := listSites(client, limits); err != nil {
		t.Fatalf("Get: %v", err)
	}

	if limits.Hour != nil || limits.Month != nil {
		t.Errorf("windows = %+v / %+v, want nil / nil", limits.Hour, limits.Month)
	}
}

// Metadata about a call that already worked must not be able to break it. The
// windows are read independently, so one unreadable header does not cost the
// other.
func TestRateLimitOptionSurvivesAMalformedHeader(t *testing.T) {
	malformed := map[string]string{}
	for name, value := range rateLimitHeaders {
		malformed[name] = value
	}
	malformed["X-RateLimit-Remaining-Hour"] = "12abc"

	server := sitesTLSServer(t, http.StatusOK, malformed)

	client, err := NewClient("secret-key", Options{
		BaseURL:    server.URL,
		HTTPClient: server.Client(),
	})
	if err != nil {
		t.Fatalf("NewClient: %v", err)
	}

	limits := NewRateLimitOption()

	page, err := listSites(client, limits)
	if err != nil {
		t.Fatalf("Get: %v", err)
	}

	if page == nil {
		t.Fatal("the call lost its result over a header")
	}
	if limits.Hour != nil {
		t.Errorf("hourly window = %+v, want nil", *limits.Hour)
	}
	assertWindow(t, limits.Month, RateLimitWindow{Limit: 50000, Remaining: 48120, ResetInSeconds: 1904322}, "monthly")
}

// The recorder wraps the whole middleware pipeline, so a retried request reports
// the attempt that succeeded rather than the refusal before it.
func TestRateLimitOptionReportsTheLastAttempt(t *testing.T) {
	served := 0
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		served++
		if served == 1 {
			w.WriteHeader(http.StatusServiceUnavailable)
			return
		}
		for name, value := range rateLimitHeaders {
			w.Header().Set(name, value)
		}
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(sitesBody))
	}))
	t.Cleanup(server.Close)

	client, err := NewAnonymousClient(Options{
		BaseURL: server.URL,
		Retry:   &RetryOptions{MaxRetries: 1},
	})
	if err != nil {
		t.Fatalf("NewAnonymousClient: %v", err)
	}

	limits := NewRateLimitOption()

	if _, err := listSites(client, limits); err != nil {
		t.Fatalf("Get: %v", err)
	}

	if served != 2 {
		t.Fatalf("served %d requests, want 2", served)
	}
	assertWindow(t, limits.Hour, RateLimitWindow{Limit: 1000, Remaining: 993, ResetInSeconds: 2471}, "hourly")
}

// The transport is in every client, so a call without the option must be
// unaffected.
func TestRateLimitOptionIsOptional(t *testing.T) {
	server := sitesTLSServer(t, http.StatusOK, rateLimitHeaders)

	client, err := NewClient("secret-key", Options{
		BaseURL:    server.URL,
		HTTPClient: server.Client(),
	})
	if err != nil {
		t.Fatalf("NewClient: %v", err)
	}

	if _, err := client.Sites().Get(context.Background(), nil); err != nil {
		t.Fatalf("Get: %v", err)
	}
}
