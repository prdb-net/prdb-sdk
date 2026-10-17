package prdb

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"net/url"
	"os"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/prdb-net/prdb-sdk/go/generated"
	"github.com/prdb-net/prdb-sdk/go/generated/models"
)

type previewEnrichmentFixture struct {
	Detail    json.RawMessage   `json:"detail"`
	Older     json.RawMessage   `json:"detailFromOlderServer"`
	Batch     json.RawMessage   `json:"batch"`
	Pages     []json.RawMessage `json:"pages"`
	NotFound  json.RawMessage   `json:"notFound"`
	Invalid   json.RawMessage   `json:"invalidCursor"`
	Forbidden json.RawMessage   `json:"forbidden"`
}

func loadPreviewEnrichment(t *testing.T) (previewEnrichmentFixture, uuid.UUID) {
	t.Helper()
	data, err := os.ReadFile("../tests/fixtures/preview-enrichment.json")
	if err != nil {
		t.Fatal(err)
	}
	var fixture previewEnrichmentFixture
	if err = json.Unmarshal(data, &fixture); err != nil {
		t.Fatal(err)
	}
	var detail struct {
		ID uuid.UUID `json:"id"`
	}
	if err = json.Unmarshal(fixture.Detail, &detail); err != nil {
		t.Fatal(err)
	}
	return fixture, detail.ID
}

// previewServer answers each request with the next body in order.
func previewServer(t *testing.T, path string, status int, bodies ...json.RawMessage) (*generated.PrdbClient, string, *[]*http.Request) {
	t.Helper()
	var seen []*http.Request
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != path || r.Header.Get("X-Api-Key") != "test-key" {
			t.Errorf("unexpected request %s %s", r.Method, r.URL.Path)
		}
		seen = append(seen, r)
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(status)
		w.Write(bodies[len(seen)-1])
	}))
	t.Cleanup(server.Close)
	client, err := NewClient("test-key", Options{BaseURL: server.URL, HTTPClient: server.Client()})
	if err != nil {
		t.Fatal(err)
	}
	return client, server.URL, &seen
}

func eligibility(value *bool) string {
	if value == nil {
		return "unknown"
	}
	if *value {
		return "true"
	}
	return "false"
}

func TestPreviewEnrichmentDetailKeepsTrueAndAbsentAsUnknown(t *testing.T) {
	fixture, id := loadPreviewEnrichment(t)
	client, _, _ := previewServer(t, "/videos/"+id.String(), 200, fixture.Detail, fixture.Older)
	current, err := client.Videos().ById(id).Get(context.Background(), nil)
	if err != nil || eligibility(current.GetPreviewEnrichmentEligible()) != "true" {
		t.Fatalf("current detail: %v", err)
	}
	older, err := client.Videos().ById(id).Get(context.Background(), nil)
	if err != nil || eligibility(older.GetPreviewEnrichmentEligible()) != "unknown" {
		t.Fatalf("older server detail: %v", err)
	}
}

func TestPreviewEnrichmentBatchKeepsTrueFalseAndAbsentApart(t *testing.T) {
	fixture, id := loadPreviewEnrichment(t)
	client, _, seen := previewServer(t, "/videos/batch", 200, fixture.Batch)
	body := models.NewGetVideosByIdsRequest()
	body.SetIds([]uuid.UUID{id})
	got, err := client.Videos().Batch().Post(context.Background(), body, nil)
	if err != nil || len(got) != 3 || (*seen)[0].Method != http.MethodPost {
		t.Fatalf("batch: %v", err)
	}
	for i, want := range []string{"true", "false", "unknown"} {
		if have := eligibility(got[i].GetPreviewEnrichmentEligible()); have != want {
			t.Errorf("batch[%d]: got %s, want %s", i, have, want)
		}
	}
}

// Feed requests go through WithUrl, the documented Go path: the pinned Kiota
// runtime cannot serialize typed timestamp query parameters.
func TestPreviewEnrichmentFeedCarriesUpsertsTombstonesAndFlips(t *testing.T) {
	fixture, _ := loadPreviewEnrichment(t)
	client, origin, seen := previewServer(t, "/videos/changes", 200, fixture.Pages...)
	get := func(query url.Values) models.GetVideoChangesResponseable {
		t.Helper()
		page, err := client.Videos().Changes().WithUrl(origin+"/videos/changes?"+query.Encode()).Get(context.Background(), nil)
		if err != nil {
			t.Fatal(err)
		}
		return page
	}
	first := get(url.Values{"Since": {"0001-01-01T00:00:00Z"}, "PageSize": {"2"}})
	items := first.GetItems()
	if !*first.GetHasMore() || len(items) != 2 || eligibility(items[0].GetVideo().GetPreviewEnrichmentEligible()) != "true" || eligibility(items[1].GetVideo().GetPreviewEnrichmentEligible()) != "false" {
		t.Fatal("first page lost eligibility")
	}
	cursor := first.GetNextCursor()
	second := get(url.Values{"Since": {cursor.GetUpdatedAtUtc().Format(time.RFC3339Nano)}, "SinceId": {cursor.GetId().String()}, "PageSize": {"2"}})
	tombstone := second.GetItems()[0]
	if *tombstone.GetEventType() != "deleted" || !*tombstone.GetVideo().GetIsDeleted() || eligibility(tombstone.GetVideo().GetPreviewEnrichmentEligible()) != "false" {
		t.Fatal("tombstone must carry false")
	}
	if (*seen)[1].URL.Query().Get("SinceId") != cursor.GetId().String() {
		t.Fatal("cursor tie-breaker was not sent")
	}
	following := get(url.Values{"Since": {second.GetServerTimeUtc().Format(time.RFC3339Nano)}})
	flipped := following.GetItems()[0].GetVideo()
	if *flipped.GetId() != *items[0].GetVideo().GetId() || eligibility(flipped.GetPreviewEnrichmentEligible()) != "false" {
		t.Fatal("flip to false was lost")
	}
}

func TestPreviewEnrichmentDeclaredErrorsAreTypedProblems(t *testing.T) {
	fixture, id := loadPreviewEnrichment(t)
	cases := []struct {
		status int
		path   string
		body   json.RawMessage
		call   func(*generated.PrdbClient) error
	}{
		{404, "/videos/" + id.String(), fixture.NotFound, func(c *generated.PrdbClient) error {
			_, err := c.Videos().ById(id).Get(context.Background(), nil)
			return err
		}},
		{403, "/videos/batch", fixture.Forbidden, func(c *generated.PrdbClient) error {
			body := models.NewGetVideosByIdsRequest()
			body.SetIds([]uuid.UUID{id})
			_, err := c.Videos().Batch().Post(context.Background(), body, nil)
			return err
		}},
		{400, "/videos/changes", fixture.Invalid, func(c *generated.PrdbClient) error {
			_, err := c.Videos().Changes().Get(context.Background(), nil)
			return err
		}},
	}
	for _, tc := range cases {
		client, _, _ := previewServer(t, tc.path, tc.status, tc.body)
		problem, ok := tc.call(client).(*models.ProblemDetails)
		if !ok || problem.GetStatus() == nil || int(*problem.GetStatus()) != tc.status {
			t.Errorf("%d: expected a typed ProblemDetails", tc.status)
		}
	}
}
