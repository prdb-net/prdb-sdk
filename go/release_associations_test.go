package prdb

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"

	"github.com/prdb-net/prdb-sdk/go/generated/models"
)

func TestReleaseAssociationBaselineEmptyAndCorrection(t *testing.T) {
	data, err := os.ReadFile("../tests/fixtures/release-associations.json")
	if err != nil {
		t.Fatal(err)
	}
	var fixture struct {
		Pages   []json.RawMessage `json:"pages"`
		Invalid json.RawMessage   `json:"invalidCursor"`
	}
	if err = json.Unmarshal(data, &fixture); err != nil {
		t.Fatal(err)
	}
	index := 0
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/video-release-associations/changes" || r.Header.Get("X-Api-Key") != "test-key" {
			t.Error("unexpected metadata request")
		}
		w.Header().Set("Content-Type", "application/json")
		if index >= len(fixture.Pages) {
			w.WriteHeader(400)
			w.Write(fixture.Invalid)
			return
		}
		w.Write(fixture.Pages[index])
		index++
	}))
	defer server.Close()
	client, err := NewClient("test-key", Options{BaseURL: server.URL, HTTPClient: server.Client()})
	if err != nil {
		t.Fatal(err)
	}
	builder := client.VideoReleaseAssociations().Changes()
	base, err := builder.WithUrl(server.URL+"/video-release-associations/changes?Since=0001-01-01T00%3A00%3A00Z").Get(context.Background(), nil)
	if err != nil {
		t.Fatal(err)
	}
	rows := base.GetItems()
	if len(rows) != 4 || !*rows[0].GetVideoReleaseAssociation().GetIsConfirmed() || *rows[1].GetVideoReleaseAssociation().GetIsConfirmed() || *rows[2].GetVideoReleaseAssociation().GetSourceAvailable() || !*rows[3].GetVideoReleaseAssociation().GetIsDeleted() {
		t.Fatal("release state was lost")
	}
	empty, err := builder.WithUrl(server.URL+"/video-release-associations/changes?Since=2026-10-13T12%3A00%3A00Z&SinceId="+base.GetNextCursor().GetId().String()).Get(context.Background(), nil)
	if err != nil || empty.GetNextCursor() == nil || len(empty.GetItems()) != 0 || *empty.GetNextCursor().GetId() != *base.GetNextCursor().GetId() {
		t.Fatalf("empty cursor: %v", err)
	}
	follow, err := builder.WithUrl(server.URL+"/video-release-associations/changes?Since=2026-10-13T12%3A02%3A00Z").Get(context.Background(), nil)
	if err != nil || len(follow.GetItems()) != 1 {
		t.Fatalf("follow-up: %v", err)
	}
	changed := follow.GetItems()[0].GetVideoReleaseAssociation()
	if *changed.GetId() != *rows[0].GetVideoReleaseAssociation().GetId() || *changed.GetVideoId() == *rows[0].GetVideoReleaseAssociation().GetVideoId() {
		t.Fatal("correction identity was lost")
	}
	_, err = builder.Get(context.Background(), nil)
	if problem, ok := err.(*models.ValidationProblemDetails); !ok || problem.GetStatus() == nil || *problem.GetStatus() != 400 {
		t.Fatalf("typed cursor problem: %T", err)
	}
}
