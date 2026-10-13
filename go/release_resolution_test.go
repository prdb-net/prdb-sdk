package prdb

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"strconv"
	"testing"
	"time"

	"github.com/prdb-net/prdb-sdk/go/generated/models"
)

func TestReleaseResolutionMixedResultsAndTypedGateErrors(t *testing.T) {
	data, err := os.ReadFile("../tests/fixtures/release-resolution.json")
	if err != nil {
		t.Fatal(err)
	}
	var fixture struct {
		Response json.RawMessage            `json:"response"`
		Problems map[string]json.RawMessage `json:"problems"`
		Request  struct {
			Releases []struct {
				Ref         string     `json:"ref"`
				Title       string     `json:"title"`
				SizeBytes   *int64     `json:"sizeBytes"`
				PostedAtUtc *time.Time `json:"postedAtUtc"`
				Source      *struct {
					Kind    string `json:"kind"`
					Origin  string `json:"origin"`
					EntryId string `json:"entryId"`
				} `json:"source"`
			}
		} `json:"request"`
	}
	if err = json.Unmarshal(data, &fixture); err != nil {
		t.Fatal(err)
	}
	status := 200
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "POST" || r.URL.Path != "/releases/resolve" || r.Header.Get("X-Api-Key") != "test-key" {
			t.Error("unexpected request")
		}
		if r.Header.Get("Content-Encoding") != "" {
			t.Error("prdb JSON requests must not be gzip encoded")
		}
		var body struct {
			Releases []struct {
				SizeBytes int64 `json:"sizeBytes"`
			} `json:"releases"`
		}
		if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
			t.Error(err)
		}
		if len(body.Releases) != 7 || body.Releases[0].SizeBytes != 4294967296 {
			t.Error("request hints/correlation were lost")
		}
		w.Header().Set("Content-Type", "application/json")
		if status == 429 || status == 503 {
			w.Header().Set("Retry-After", "300")
		}
		w.WriteHeader(status)
		if status == 200 {
			w.Write(fixture.Response)
		} else {
			w.Write(fixture.Problems[strconv.Itoa(status)])
		}
	}))
	defer server.Close()
	client, err := NewClient("test-key", Options{BaseURL: server.URL, Retry: RetryDisabled()})
	if err != nil {
		t.Fatal(err)
	}
	body := models.NewResolveReleasesRequest()
	inputs := []models.ResolveReleaseInputable{}
	for _, row := range fixture.Request.Releases {
		item := models.NewResolveReleaseInput()
		item.SetRef(&row.Ref)
		item.SetTitle(&row.Title)
		item.SetSizeBytes(row.SizeBytes)
		item.SetPostedAtUtc(row.PostedAtUtc)
		if row.Source != nil {
			source := models.NewResolveReleaseSource()
			kind := models.NZBCACHE_RELEASESOURCEKIND
			if row.Source.Kind == "newznab" {
				kind = models.NEWZNAB_RELEASESOURCEKIND
			}
			source.SetKind(&kind)
			source.SetOrigin(&row.Source.Origin)
			source.SetEntryId(&row.Source.EntryId)
			item.SetSource(source)
		}
		inputs = append(inputs, item)
	}
	body.SetReleases(inputs)
	result, err := client.Releases().Resolve().Post(context.Background(), body, nil)
	if err != nil {
		t.Fatal(err)
	}
	rows := result.GetResults()
	if len(rows) != 7 || *rows[2].GetStatus() != models.RETRYLATER_RELEASERESOLUTIONSTATUS || rows[3].GetRecheckAfterUtc() != nil || rows[1].GetVideos()[0].GetReleaseDate() != nil || rows[2].GetSourceState().GetLastSuccessfulSyncAtUtc() != nil {
		t.Fatal("typed nullable/status fields lost")
	}
	for i, row := range rows {
		if *row.GetRef() != fixture.Request.Releases[i].Ref {
			t.Fatal("correlation lost")
		}
	}
	if len(rows[5].GetVideoIds()) != 0 || len(rows[5].GetCandidates()) != 1 {
		t.Fatal("candidate alternatives became identities")
	}
	for _, code := range []int{401, 403, 429, 503} {
		status = code
		_, err = client.Releases().Resolve().Post(context.Background(), body, nil)
		problem, ok := err.(*models.RateLimitProblemResponse)
		if !ok || problem.GetStatus() == nil || int(*problem.GetStatus()) != code {
			t.Fatalf("typed %d problem: %T", code, err)
		}
	}
}
