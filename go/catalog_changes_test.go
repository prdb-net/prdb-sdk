package prdb

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"net/url"
	"testing"
	"time"

	"github.com/google/uuid"
)

// Kiota's Go runtime cannot serialize typed timestamp query parameters. Pin the
// documented WithUrl path through our authenticated wrapper, including a year-1
// baseline, a resumed UUID cursor and fractional timestamp precision.
func TestCatalogueChangesBaselineAndResume(t *testing.T) {
	for _, resource := range []string{"sites", "videos"} {
		t.Run(resource, func(t *testing.T) {
			baseline := time.Date(1, 1, 1, 0, 0, 0, 0, time.UTC)
			serverTime := time.Date(2026, 10, 1, 7, 0, 0, 123456700, time.UTC)
			cursorID := uuid.MustParse("00000000-0000-0000-0000-000000000001")
			requests := 0
			server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				requests++
				if r.URL.Path != "/"+resource+"/changes" {
					t.Errorf("path = %q", r.URL.Path)
				}
				if r.Header.Get(APIKeyHeader) != "test-key" {
					t.Error("API key is missing")
				}
				query := r.URL.Query()
				if query.Get("PageSize") != "1000" {
					t.Errorf("PageSize = %q", query.Get("PageSize"))
				}
				wantSince := baseline
				if requests == 1 {
					if query.Has("SinceId") {
						t.Error("baseline must omit SinceId")
					}
				} else {
					wantSince = serverTime
					if query.Get("SinceId") != cursorID.String() {
						t.Errorf("SinceId = %q", query.Get("SinceId"))
					}
				}
				if query.Get("Since") != wantSince.Format(time.RFC3339Nano) {
					t.Errorf("Since = %q, want %q", query.Get("Since"), wantSince.Format(time.RFC3339Nano))
				}
				w.Header().Set("Content-Type", "application/json")
				fmt.Fprintf(w, `{"items":[],"pageSize":1000,"hasMore":false,"serverTimeUtc":%q,"nextCursor":null}`, serverTime.Format(time.RFC3339Nano))
			}))
			defer server.Close()
			client, err := NewClient("test-key", Options{BaseURL: server.URL, HTTPClient: server.Client()})
			if err != nil {
				t.Fatal(err)
			}
			for _, sinceID := range []*uuid.UUID{nil, &cursorID} {
				since := baseline
				if sinceID != nil {
					since = serverTime
				}
				query := url.Values{"Since": {since.Format(time.RFC3339Nano)}, "PageSize": {"1000"}}
				if sinceID != nil {
					query.Set("SinceId", sinceID.String())
				}
				requestURL := server.URL + "/" + resource + "/changes?" + query.Encode()
				var clock *time.Time
				switch resource {
				case "sites":
					page, err := client.Sites().Changes().WithUrl(requestURL).Get(context.Background(), nil)
					if err != nil || page == nil {
						t.Fatalf("Sites().Changes().Get: %v", err)
					}
					if len(page.GetItems()) != 0 || page.GetNextCursor() != nil {
						t.Fatal("expected an empty page with a null row cursor")
					}
					clock = page.GetServerTimeUtc()
				case "videos":
					page, err := client.Videos().Changes().WithUrl(requestURL).Get(context.Background(), nil)
					if err != nil || page == nil {
						t.Fatalf("Videos().Changes().Get: %v", err)
					}
					if len(page.GetItems()) != 0 || page.GetNextCursor() != nil {
						t.Fatal("expected an empty page with a null row cursor")
					}
					clock = page.GetServerTimeUtc()
				}
				if clock == nil || !clock.Equal(serverTime) {
					t.Fatalf("server clock = %v, want %v", clock, serverTime)
				}
			}
			if requests != 2 {
				t.Fatalf("requests = %d, want 2", requests)
			}
		})
	}
}
