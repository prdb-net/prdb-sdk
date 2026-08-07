package prdb

import (
	"context"
	"crypto/tls"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

// healthServer answers GET /health over TLS and records the request it saw.
//
// TLS rather than plain HTTP because Kiota's API key provider refuses to attach
// a credential to an http:// URL. See TestAPIKeyRequiresHTTPS.
func healthServer(t *testing.T, seen *http.Header) *httptest.Server {
	t.Helper()

	server := httptest.NewTLSServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		*seen = r.Header.Clone()
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"status":"healthy","timestamp":"2026-08-07T12:00:00Z"}`))
	}))
	t.Cleanup(server.Close)

	return server
}

func TestNewClientSendsAPIKeyHeader(t *testing.T) {
	var seen http.Header
	server := healthServer(t, &seen)

	client, err := NewClient("secret-key", Options{
		BaseURL:    server.URL,
		HTTPClient: server.Client(),
	})
	if err != nil {
		t.Fatalf("NewClient: %v", err)
	}

	if _, err := client.Health().Get(context.Background(), nil); err != nil {
		t.Fatalf("Health().Get: %v", err)
	}

	if got := seen.Get(APIKeyHeader); got != "secret-key" {
		t.Errorf("%s = %q, want %q", APIKeyHeader, got, "secret-key")
	}
}

func TestNewAnonymousClientSendsNoAPIKey(t *testing.T) {
	var seen http.Header
	server := healthServer(t, &seen)

	client, err := NewAnonymousClient(Options{
		BaseURL:    server.URL,
		HTTPClient: server.Client(),
	})
	if err != nil {
		t.Fatalf("NewAnonymousClient: %v", err)
	}

	if _, err := client.Health().Get(context.Background(), nil); err != nil {
		t.Fatalf("Health().Get: %v", err)
	}

	if got := seen.Get(APIKeyHeader); got != "" {
		t.Errorf("%s = %q, want it absent", APIKeyHeader, got)
	}
}

// An API key is never attached over plain HTTP. Worth pinning: it means a local
// staging deployment must terminate TLS for an authenticated client to work.
func TestAPIKeyRequiresHTTPS(t *testing.T) {
	var seen http.Header
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		seen = r.Header.Clone()
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"status":"healthy","timestamp":"2026-08-07T12:00:00Z"}`))
	}))
	t.Cleanup(server.Close)

	client, err := NewClient("secret-key", Options{
		BaseURL:    server.URL,
		HTTPClient: server.Client(),
	})
	if err != nil {
		t.Fatalf("NewClient: %v", err)
	}

	_, err = client.Health().Get(context.Background(), nil)
	if err == nil {
		t.Fatal("expected the request over plain HTTP to be refused")
	}
	if seen.Get(APIKeyHeader) != "" {
		t.Error("the api key reached the wire over plain HTTP")
	}
}

// The key is bound to the base URL's host, so a redirect to another host cannot
// carry the credential off-site. Go's http.Client strips Authorization and
// Cookie across hosts by itself, but not a custom header like X-Api-Key, so this
// is the wrapper's own guarantee and worth pinning down.
func TestRedirectToAnotherHostDoesNotLeakTheAPIKey(t *testing.T) {
	var elsewhereSaw http.Header
	elsewhere := httptest.NewTLSServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		elsewhereSaw = r.Header.Clone()
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"status":"healthy","timestamp":"2026-08-07T12:00:00Z"}`))
	}))
	t.Cleanup(elsewhere.Close)

	origin := httptest.NewTLSServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		http.Redirect(w, r, elsewhere.URL+"/health", http.StatusTemporaryRedirect)
	}))
	t.Cleanup(origin.Close)

	// One client that trusts both test certificates.
	httpClient := &http.Client{
		Transport: &http.Transport{
			TLSClientConfig: &tls.Config{InsecureSkipVerify: true}, //nolint:gosec // test servers
		},
	}

	client, err := NewClient("secret-key", Options{
		BaseURL:    origin.URL,
		HTTPClient: httpClient,
	})
	if err != nil {
		t.Fatalf("NewClient: %v", err)
	}

	// The call may succeed or fail; what matters is that the key did not travel.
	_, _ = client.Health().Get(context.Background(), nil)

	if got := elsewhereSaw.Get(APIKeyHeader); got != "" {
		t.Errorf("the api key leaked to the redirect target: %s = %q", APIKeyHeader, got)
	}
}

func TestNewClientRejectsEmptyAPIKey(t *testing.T) {
	if _, err := NewClient(""); err == nil {
		t.Fatal("expected an error for an empty api key")
	}
}

func TestRejectsRelativeBaseURL(t *testing.T) {
	for _, baseURL := range []string{"api.prdb.net", "/videos", "not a url"} {
		if _, err := NewClient("k", Options{BaseURL: baseURL}); err == nil {
			t.Errorf("BaseURL %q: expected an error", baseURL)
		}
	}
}

func TestDefaultBaseURLIsProduction(t *testing.T) {
	if !strings.HasPrefix(DefaultBaseURL, "https://") {
		t.Errorf("DefaultBaseURL = %q, want an https URL", DefaultBaseURL)
	}
}
