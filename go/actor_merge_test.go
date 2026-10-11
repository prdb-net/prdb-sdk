package prdb

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"reflect"
	"testing"

	"github.com/google/uuid"
	"github.com/prdb-net/prdb-sdk/go/generated/models"
)

type actorMergeFixture struct {
	SourceID             uuid.UUID       `json:"sourceId"`
	TargetID             uuid.UUID       `json:"targetId"`
	OrdinaryID           uuid.UUID       `json:"ordinaryId"`
	Detail               map[string]any  `json:"detail"`
	Batch                json.RawMessage `json:"batch"`
	ActorChanges         json.RawMessage `json:"actorChanges"`
	FavoriteActorChanges json.RawMessage `json:"favoriteActorChanges"`
}

func readActorMergeFixture(t *testing.T) actorMergeFixture {
	t.Helper()
	data, err := os.ReadFile("../tests/fixtures/actor-merge.json")
	if err != nil {
		t.Fatal(err)
	}
	var fixture actorMergeFixture
	if err := json.Unmarshal(data, &fixture); err != nil {
		t.Fatal(err)
	}
	return fixture
}

func TestRetainedActorDetailAndBatch(t *testing.T) {
	for _, omit := range []bool{false, true} {
		name := "null"
		if omit {
			name = "omitted"
		}
		t.Run(name, func(t *testing.T) {
			fixture := readActorMergeFixture(t)
			if omit {
				delete(fixture.Detail, "requestedIds")
			}
			requests := 0
			server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				requests++
				w.Header().Set("Content-Type", "application/json")
				if r.URL.Path == "/actors/batch" {
					var body struct {
						IDs []uuid.UUID `json:"ids"`
					}
					if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
						t.Error(err)
					}
					if r.Method != "POST" || !reflect.DeepEqual(body.IDs, []uuid.UUID{fixture.SourceID, fixture.TargetID}) {
						t.Error("unexpected batch request")
					}
					w.Write(fixture.Batch)
					return
				}
				if r.URL.Path != "/actors/"+fixture.SourceID.String() {
					t.Errorf("unexpected path: %s", r.URL.Path)
				}
				json.NewEncoder(w).Encode(fixture.Detail)
			}))
			defer server.Close()
			client, err := NewClient("test-key", Options{BaseURL: server.URL, HTTPClient: server.Client()})
			if err != nil {
				t.Fatal(err)
			}
			detail, err := client.Actors().ById(fixture.SourceID).Get(context.Background(), nil)
			if err != nil {
				t.Fatal(err)
			}
			if detail == nil || detail.GetId() == nil || *detail.GetId() != fixture.TargetID || detail.GetRequestedIds() != nil {
				t.Fatal("canonical detail or nullable mapping lost")
			}
			body := models.NewGetActorsByIdsRequest()
			body.SetIds([]uuid.UUID{fixture.SourceID, fixture.TargetID})
			batch, err := client.Actors().Batch().Post(context.Background(), body, nil)
			if err != nil {
				t.Fatal(err)
			}
			if len(batch) != 1 || batch[0].GetId() == nil || *batch[0].GetId() != fixture.TargetID || !reflect.DeepEqual(batch[0].GetRequestedIds(), []uuid.UUID{fixture.SourceID, fixture.TargetID}) {
				t.Fatal("batch array or UUID mapping lost")
			}
			if requests != 2 {
				t.Fatalf("requests = %d, want 2", requests)
			}
		})
	}
}

func TestActorMergeFeedMetadata(t *testing.T) {
	for _, path := range []string{"/actors/changes", "/favorite-actors/changes"} {
		t.Run(path, func(t *testing.T) {
			fixture := readActorMergeFixture(t)
			server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				if r.URL.Path != path || r.URL.Query().Get("Since") != "0001-01-01T00:00:00Z" {
					t.Errorf("unexpected URL: %s", r.URL)
				}
				w.Header().Set("Content-Type", "application/json")
				if path == "/actors/changes" {
					w.Write(fixture.ActorChanges)
				} else {
					w.Write(fixture.FavoriteActorChanges)
				}
			}))
			defer server.Close()
			client, err := NewClient("test-key", Options{BaseURL: server.URL, HTTPClient: server.Client()})
			if err != nil {
				t.Fatal(err)
			}
			var rows []interface {
				GetId() *uuid.UUID
				GetIsDeleted() *bool
				GetMergedIntoActorId() *uuid.UUID
			}
			var events []string
			var cursor *uuid.UUID
			url := server.URL + path + "?Since=0001-01-01T00%3A00%3A00Z"
			if path == "/actors/changes" {
				page, err := client.Actors().Changes().WithUrl(url).Get(context.Background(), nil)
				if err != nil || page == nil {
					t.Fatalf("actor changes: %v", err)
				}
				for _, item := range page.GetItems() {
					rows = append(rows, item.GetActor())
					events = append(events, *item.GetEventType())
				}
				cursor = page.GetNextCursor().GetId()
			} else {
				page, err := client.FavoriteActors().Changes().WithUrl(url).Get(context.Background(), nil)
				if err != nil || page == nil {
					t.Fatalf("favorite changes: %v", err)
				}
				for _, item := range page.GetItems() {
					rows = append(rows, item.GetFavoriteActor())
					events = append(events, *item.GetEventType())
				}
				cursor = page.GetNextCursor().GetId()
			}
			if !reflect.DeepEqual(events, []string{"deleted", "updated", "deleted"}) {
				t.Fatalf("events = %v", events)
			}
			if *rows[0].GetId() != fixture.SourceID || !*rows[0].GetIsDeleted() || rows[0].GetMergedIntoActorId() == nil || *rows[0].GetMergedIntoActorId() != fixture.TargetID {
				t.Fatal("source tombstone identity lost")
			}
			if *rows[1].GetId() != fixture.TargetID || *rows[1].GetIsDeleted() || rows[1].GetMergedIntoActorId() != nil {
				t.Fatal("target update or omitted mapping lost")
			}
			if !*rows[2].GetIsDeleted() || rows[2].GetMergedIntoActorId() != nil {
				t.Fatal("ordinary deletion must have nil merge target")
			}
			if cursor == nil || *cursor != fixture.OrdinaryID {
				t.Fatal("cursor ID changed")
			}
		})
	}
}
