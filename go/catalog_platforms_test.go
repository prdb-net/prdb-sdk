package prdb

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"net/url"
	"testing"

	"github.com/google/uuid"
)

// Typed Video query configurations visit nil timestamp fields and panic in the
// pinned Kiota runtime. Exercise the documented raw-URL filters through the
// wrapper, including typed platform metadata and null values for classic sites.
func TestCataloguePlatformFiltersViaRawURL(t *testing.T) {
	platformID := uuid.MustParse("00000000-0000-0000-0000-000000000001")
	for _, resource := range []string{"sites", "videos"} {
		for _, filter := range []string{"PlatformId", "ClassicOnly"} {
			t.Run(resource+"/"+filter, func(t *testing.T) {
				value := platformID.String()
				if filter == "ClassicOnly" {
					value = "true"
				}
				requests := 0
				server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
					requests++
					if r.URL.Path != "/"+resource || r.URL.Query().Get(filter) != value || len(r.URL.Query()) != 1 {
						t.Errorf("unexpected request URL: %s", r.URL)
					}
					if r.Header.Get(APIKeyHeader) != "test-key" {
						t.Error("API key is missing")
					}
					w.Header().Set("Content-Type", "application/json")
					if filter == "ClassicOnly" {
						fmt.Fprint(w, `{"items":[{"platformId":null,"platformKey":null,"platformTitle":null,"accountHandle":null}]}`)
					} else {
						fmt.Fprintf(w, `{"items":[{"platformId":%q,"platformKey":"example","platformTitle":"Example","accountHandle":"creator"}]}`, platformID.String())
					}
				}))
				defer server.Close()
				client, err := NewClient("test-key", Options{BaseURL: server.URL, HTTPClient: server.Client()})
				if err != nil {
					t.Fatal(err)
				}
				requestURL := server.URL + "/" + resource + "?" + url.Values{filter: {value}}.Encode()
				var metadata interface {
					GetPlatformId() *uuid.UUID
					GetPlatformKey() *string
					GetPlatformTitle() *string
					GetAccountHandle() *string
				}
				if resource == "sites" {
					page, err := client.Sites().WithUrl(requestURL).Get(context.Background(), nil)
					if err != nil || page == nil || len(page.GetItems()) != 1 {
						t.Fatalf("Sites().Get: page=%v, error=%v", page, err)
					}
					metadata = page.GetItems()[0]
				} else {
					page, err := client.Videos().WithUrl(requestURL).Get(context.Background(), nil)
					if err != nil || page == nil || len(page.GetItems()) != 1 {
						t.Fatalf("Videos().Get: page=%v, error=%v", page, err)
					}
					metadata = page.GetItems()[0]
				}
				if filter == "ClassicOnly" {
					if metadata.GetPlatformId() != nil || metadata.GetPlatformKey() != nil || metadata.GetPlatformTitle() != nil || metadata.GetAccountHandle() != nil {
						t.Fatal("classic catalogue metadata must be nil")
					}
				} else if id, key, title, handle := metadata.GetPlatformId(), metadata.GetPlatformKey(), metadata.GetPlatformTitle(), metadata.GetAccountHandle(); id == nil || *id != platformID || key == nil || *key != "example" || title == nil || *title != "Example" || handle == nil || *handle != "creator" {
					t.Fatal("platform catalogue metadata was not deserialized")
				}
				if requests != 1 {
					t.Fatalf("requests = %d, want 1", requests)
				}
			})
		}
	}
}
