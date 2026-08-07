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

// An API key must not travel in cleartext. Kiota refuses to attach one to an
// http:// URL at request time; the wrapper rejects it at construction instead,
// which is the earlier and clearer failure and matches the other three SDKs.
// Worth pinning either way: a staging deployment has to terminate TLS.
func TestAPIKeyRequiresHTTPS(t *testing.T) {
	_, err := NewClient("secret-key", Options{BaseURL: "http://localhost:8080"})
	if err == nil {
		t.Fatal("expected a plain HTTP base URL to be refused")
	}
	if !strings.Contains(err.Error(), "https") {
		t.Errorf("error should say why: %v", err)
	}
}

// With no credential to protect, plain HTTP is the caller's business.
func TestAnonymousClientAllowsHTTP(t *testing.T) {
	var seen http.Header
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		seen = r.Header.Clone()
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write([]byte(`{"status":"healthy","timestamp":"2026-08-07T12:00:00Z"}`))
	}))
	t.Cleanup(server.Close)

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
	if seen.Get(APIKeyHeader) != "" {
		t.Errorf("%s = %q, want it absent", APIKeyHeader, seen.Get(APIKeyHeader))
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

// Refusing cross-host redirects must not refuse ordinary ones.
func TestSameHostRedirectIsFollowed(t *testing.T) {
	var paths []string
	var keys []string

	server := httptest.NewTLSServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		paths = append(paths, r.URL.Path)
		keys = append(keys, r.Header.Get(APIKeyHeader))

		if r.URL.Path == "/health" {
			http.Redirect(w, r, "/healthz", http.StatusTemporaryRedirect)
			return
		}
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

	if _, err := client.Health().Get(context.Background(), nil); err != nil {
		t.Fatalf("Health().Get: %v", err)
	}

	if len(paths) != 2 || paths[0] != "/health" || paths[1] != "/healthz" {
		t.Errorf("paths = %v, want [/health /healthz]", paths)
	}
	for i, key := range keys {
		if key != "secret-key" {
			t.Errorf("request %d: %s = %q, want %q", i, APIKeyHeader, key, "secret-key")
		}
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
