package prdb

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"net/url"
	"os"
	"strings"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/prdb-net/prdb-sdk/go/generated/models"
)

func TestSyncContracts(t *testing.T) {
	data, err := os.ReadFile("../tests/fixtures/sync-contracts.json")
	if err != nil {
		t.Fatal(err)
	}
	var fixture map[string]json.RawMessage
	if err = json.Unmarshal(data, &fixture); err != nil {
		t.Fatal(err)
	}
	status := 200
	legacy := false
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		key := "baseline"
		switch r.URL.Path {
		case "/videos/baseline":
			if r.URL.Query().Get("Cursor") != "opaque+/=" || r.URL.Query().Get("PageSize") != "1000" || !strings.HasPrefix(r.URL.Query().Get("CreatedFrom"), "2026-10-01") {
				t.Errorf("baseline scope lost: %s", r.URL.RawQuery)
			}
			if status == 413 {
				key = "oversized"
			}
		case "/videos/identify", "/videos/identify/validate":
			var body struct {
				IncludeFreshness bool  `json:"includeFreshness"`
				Reidentify       *bool `json:"reidentify"`
				Files            []struct {
					Filesize       int64  `json:"filesize"`
					Md5            string `json:"md5"`
					FreshnessToken string `json:"freshnessToken"`
				} `json:"files"`
			}
			if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
				t.Error(err)
			}
			key = "identify"
			if legacy {
				key = "legacy"
			}
			if r.URL.Path == "/videos/identify" {
				if !body.IncludeFreshness {
					t.Error("opt in lost")
				}
			} else {
				key = "validation"
				if body.Reidentify == nil || *body.Reidentify || len(body.Files) != 1 || body.Files[0].Filesize != 4294967296 || body.Files[0].Md5 != strings.Repeat("a", 32) || body.Files[0].FreshnessToken != "proof" {
					t.Error("original tuple/fallback lost")
				}
			}
		default:
			t.Errorf("unexpected route: %s", r.URL.Path)
		}
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(status)
		w.Write(fixture[key])
	}))
	defer server.Close()
	client, err := NewClient("test-key", Options{BaseURL: server.URL, Retry: RetryDisabled()})
	if err != nil {
		t.Fatal(err)
	}
	from := time.Date(2026, 10, 1, 0, 0, 0, 0, time.UTC)
	before := from.AddDate(0, 0, 21)
	cursor := "opaque+/="
	// Kiota Go's typed date query serialization panics; WithUrl retains the
	// generated response/error mapping while using correctly encoded UTC dates.
	query := url.Values{"CreatedFrom": {from.Format(time.RFC3339)}, "CreatedBefore": {before.Format(time.RFC3339)}, "PageSize": {"1000"}, "Cursor": {cursor}}
	baselineURL := server.URL + "/videos/baseline?" + query.Encode()
	page, err := client.Videos().Baseline().WithUrl(baselineURL).Get(context.Background(), nil)
	if err != nil {
		t.Fatal(err)
	}
	if len(page.GetItems()) != 1 || *page.GetItems()[0].GetDescription() != "Full document" || *page.GetNextCursor() != cursor || !*page.GetHasMore() || page.GetChangesSince() == nil {
		t.Fatal("baseline fields lost")
	}
	if orientation := page.GetItems()[0].GetOrientation(); orientation == nil || *orientation != models.UNKNOWN_VIDEOORIENTATION {
		t.Fatalf("baseline orientation = %v, want unknown", orientation)
	}
	status = 413
	_, err = client.Videos().Baseline().WithUrl(baselineURL).Get(context.Background(), nil)
	large, ok := err.(*models.BaselineDocumentTooLargeResponse)
	if !ok || large.GetVideoId() == nil || *large.GetNextCursor() != "after-large" || !large.GetChangesSince().Equal(*page.GetChangesSince()) {
		t.Fatalf("typed continuation lost: %T", err)
	}
	status = 200
	file := models.NewIdentifyVideoFileDto()
	ref := "r1"
	name := "Synthetic.mp4"
	length := int64(4294967296)
	md5 := strings.Repeat("a", 32)
	file.SetRef(&ref)
	file.SetFilename(&name)
	file.SetFilesize(&length)
	file.SetMd5(&md5)
	body := models.NewIdentifyVideosRequest()
	body.SetFiles([]models.IdentifyVideoFileDtoable{file})
	yes := true
	body.SetIncludeFreshness(&yes)
	result, err := client.Videos().Identify().Post(context.Background(), body, nil)
	if err != nil {
		t.Fatal(err)
	}
	if *result.GetResults()[0].GetFreshnessToken() != "proof" || result.GetResults()[0].GetFreshnessExpiresAtUtc() == nil {
		t.Fatal("proof lost")
	}
	file.SetFreshnessToken(result.GetResults()[0].GetFreshnessToken())
	validation := models.NewValidateIdentificationRequest()
	validation.SetFiles([]models.IdentifyVideoFileDtoable{file})
	no := false
	validation.SetReidentify(&no)
	mixed, err := client.Videos().Identify().Validate().Post(context.Background(), validation, nil)
	if err != nil {
		t.Fatal(err)
	}
	rows := mixed.GetResults()
	if len(rows) != 3 {
		t.Fatal("mixed results lost")
	}
	for i, want := range []string{"unchanged", "identified", "reidentify"} {
		if rows[i].GetStatus().String() != want {
			t.Fatal("status lost")
		}
	}
	if rows[0].GetResult() != nil || rows[2].GetResult() != nil || *rows[1].GetResult().GetFreshnessToken() != "replacement" {
		t.Fatal("nullable result lost")
	}
	legacy = true
	old, err := client.Videos().Identify().Post(context.Background(), body, nil)
	if err != nil {
		t.Fatal(err)
	}
	if old.GetResults()[0].GetFreshnessToken() != nil || old.GetResults()[0].GetFreshnessExpiresAtUtc() != nil {
		t.Fatal("legacy omission lost")
	}
}

func TestVideoOrientationDecodesOnLiveVideosAndTombstones(t *testing.T) {
	data, err := os.ReadFile("../tests/fixtures/sync-contracts.json")
	if err != nil {
		t.Fatal(err)
	}
	var fixture struct {
		VideoOrientation map[string]json.RawMessage `json:"videoOrientation"`
	}
	if err := json.Unmarshal(data, &fixture); err != nil {
		t.Fatal(err)
	}
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		body, ok := fixture.VideoOrientation[r.URL.Path]
		if !ok {
			http.NotFound(w, r)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		w.Write(body)
	}))
	defer server.Close()
	client, err := NewClient("test-key", Options{BaseURL: server.URL})
	if err != nil {
		t.Fatal(err)
	}
	assertOrientation := func(route string, got *models.VideoOrientation, want models.VideoOrientation) {
		t.Helper()
		if got == nil || *got != want {
			t.Errorf("%s orientation = %v, want %s", route, got, want)
		}
	}
	ctx := context.Background()
	videoID := uuid.MustParse("00000000-0000-0000-0000-000000000001")
	page, err := client.Videos().Get(ctx, nil)
	if err != nil {
		t.Fatal(err)
	}
	assertOrientation("list", page.GetItems()[0].GetOrientation(), models.STRAIGHT_VIDEOORIENTATION)
	detail, err := client.Videos().ById(videoID).Get(ctx, nil)
	if err != nil {
		t.Fatal(err)
	}
	assertOrientation("detail", detail.GetOrientation(), models.TRANS_VIDEOORIENTATION)
	body := models.NewGetVideosByIdsRequest()
	body.SetIds([]uuid.UUID{videoID})
	batch, err := client.Videos().Batch().Post(ctx, body, nil)
	if err != nil {
		t.Fatal(err)
	}
	assertOrientation("batch", batch[0].GetOrientation(), models.GAY_VIDEOORIENTATION)
	changes, err := client.Videos().Changes().Get(ctx, nil)
	if err != nil {
		t.Fatal(err)
	}
	items := changes.GetItems()
	if len(items) != 2 {
		t.Fatalf("changes count = %d, want 2", len(items))
	}
	for i, eventType := range []string{"updated", "deleted"} {
		item := items[i]
		if item.GetEventType() == nil || *item.GetEventType() != eventType || item.GetVideo() == nil {
			t.Fatalf("change %d: missing %s video", i, eventType)
		}
		assertOrientation(eventType, item.GetVideo().GetOrientation(), models.UNKNOWN_VIDEOORIENTATION)
	}
}
