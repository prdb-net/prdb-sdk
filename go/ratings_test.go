package prdb

import (
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"net/http/httptest"
	"net/url"
	"os"
	"reflect"
	"strconv"
	"testing"

	"github.com/google/uuid"
	abstractions "github.com/microsoft/kiota-abstractions-go"
	"github.com/prdb-net/prdb-sdk/go/generated"
	"github.com/prdb-net/prdb-sdk/go/generated/models"
)

type ratingConfig = abstractions.RequestConfiguration[abstractions.DefaultQueryParameters]

// Both resources must expose the same operations and wire shapes.
type ratingCalls struct {
	summary      func(context.Context, *ratingConfig) (models.RatingSummaryable, error)
	own          func(context.Context, *ratingConfig) (models.OwnRatingResponseable, error)
	set          func(context.Context, models.SetRatingRequestable, *ratingConfig) (models.RatingWriteResponseable, error)
	submit       func(context.Context, models.SubmitRatingReviewRequestable, *ratingConfig) (models.RatingWriteResponseable, error)
	deleteReview func(context.Context, *ratingConfig) error
	deleteRating func(context.Context, *ratingConfig) error
}

func ratingOperations(client *generated.PrdbClient, resource string, id uuid.UUID) ratingCalls {
	if resource == "actors" {
		target := client.Actors().ByActorId(id)
		return ratingCalls{target.RatingSummary().Get, target.Rating().Get, target.Rating().Put,
			target.Rating().Review().Post, target.Rating().Review().Delete, target.Rating().Delete}
	}
	target := client.Videos().ById(id)
	return ratingCalls{target.RatingSummary().Get, target.Rating().Get, target.Rating().Put,
		target.Rating().Review().Post, target.Rating().Review().Delete, target.Rating().Delete}
}

// Synthetic wire responses shared with the other three SDK contract tests.
func ratingFixture(t *testing.T) map[string]json.RawMessage {
	t.Helper()
	data, err := os.ReadFile("../tests/fixtures/ratings.json")
	if err != nil {
		t.Fatal(err)
	}
	var fixture map[string]json.RawMessage
	if err := json.Unmarshal(data, &fixture); err != nil {
		t.Fatal(err)
	}
	return fixture
}

var ratingTarget = uuid.MustParse("11111111-1111-4111-8111-111111111111")

func TestRatingOperations(t *testing.T) {
	for _, resource := range []string{"actors", "videos"} {
		t.Run(resource, func(t *testing.T) {
			fixture := ratingFixture(t)
			exchanges := []struct {
				method, suffix string
				status         int
				payload        string
			}{
				{"GET", "/rating-summary", 200, "emptySummary"}, {"GET", "/rating-summary", 200, "summary"},
				{"GET", "/rating", 200, "noRating"}, {"PUT", "/rating", 200, "deletedReceipt"},
				{"PUT", "/rating", 202, "receipt"}, {"POST", "/rating/review", 202, "receipt"},
				{"DELETE", "/rating/review", 204, ""}, {"DELETE", "/rating", 204, ""},
			}
			calls := 0
			server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				if calls >= len(exchanges) {
					t.Error("unexpected extra request")
					w.WriteHeader(500)
					return
				}
				expected := exchanges[calls]
				calls++
				if r.Method != expected.method || r.URL.Path != "/"+resource+"/"+ratingTarget.String()+expected.suffix || r.Header.Get("X-Api-Key") != "test-key" {
					t.Errorf("unexpected request: %s %s", r.Method, r.URL)
				}
				if r.Method == "PUT" || r.Method == "POST" {
					var body map[string]any
					if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
						t.Error(err)
					}
					if calls == 4 {
						if body["stars"] != float64(4) || body["reviewText"] != nil || r.Header.Get("Idempotency-Key") != "" {
							t.Error("star-only request changed")
						}
					} else {
						want := map[string]any{"text": "Carefully made."}
						if r.Method == "PUT" {
							want = map[string]any{"stars": float64(4), "reviewText": "Carefully made."}
						}
						if !reflect.DeepEqual(body, want) || r.Header.Get("Idempotency-Key") != "synthetic-submission-key" {
							t.Error("text body or idempotency key lost")
						}
					}
				}
				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(expected.status)
				if expected.payload != "" {
					w.Write(fixture[expected.payload])
				}
			}))
			defer server.Close()
			client, err := NewClient("test-key", Options{BaseURL: server.URL, HTTPClient: server.Client()})
			if err != nil {
				t.Fatal(err)
			}
			op, ctx := ratingOperations(client, resource, ratingTarget), context.Background()
			summary, err := op.summary(ctx, nil)
			if err != nil {
				t.Fatal(err)
			}
			if *summary.GetRatingCount() != 0 || *summary.GetReviewCount() != 0 || summary.GetAverageRating() != nil {
				t.Fatal("unrated summary lost")
			}
			summary, err = op.summary(ctx, nil)
			if err != nil || summary == nil || *summary.GetAverageRating() != 3.75 {
				t.Fatalf("average lost: %v", err)
			}
			own, err := op.own(ctx, nil)
			if err != nil || own == nil || own.GetRating() != nil {
				t.Fatalf("nullable own rating: %v", err)
			}
			body := models.NewSetRatingRequest()
			stars := int32(4)
			body.SetStars(&stars)
			receipt, err := op.set(ctx, body, nil)
			if err != nil {
				t.Fatal(err)
			}
			if receipt.GetRatingId() != nil || receipt.GetReviewId() != nil || receipt.GetReviewState() != nil {
				t.Fatal("nullable receipt lost")
			}
			status := &ResponseStatusOption{}
			config := &ratingConfig{Headers: abstractions.NewRequestHeaders(), Options: []abstractions.RequestOption{status}}
			config.Headers.Add("Idempotency-Key", "synthetic-submission-key")
			text := "Carefully made."
			body.SetReviewText(&text)
			receipt, err = op.set(ctx, body, config)
			if err != nil || receipt == nil || status.StatusCode != 202 || *receipt.GetReviewState() != "Pending" {
				t.Fatalf("pending stars: %v", err)
			}
			review := models.NewSubmitRatingReviewRequest()
			review.SetText(&text)
			receipt, err = op.submit(ctx, review, config)
			if err != nil || receipt == nil || status.StatusCode != 202 || receipt.GetReviewId() == nil {
				t.Fatalf("pending review: %v", err)
			}
			if err := op.deleteReview(ctx, config); err != nil || status.StatusCode != 204 {
				t.Fatalf("delete review: %v", err)
			}
			if err := op.deleteRating(ctx, config); err != nil || status.StatusCode != 204 {
				t.Fatalf("delete rating: %v", err)
			}
			if calls != len(exchanges) {
				t.Fatalf("calls = %d", calls)
			}
		})
	}
}

func TestOwnRatingReviewStates(t *testing.T) {
	for _, state := range []string{"None", "Published", "Pending", "Rejected", "Hidden"} {
		t.Run(state, func(t *testing.T) {
			fixture := ratingFixture(t)
			var payload map[string]any
			json.Unmarshal(fixture["own"], &payload)
			payload["rating"].(map[string]any)["review"].(map[string]any)["state"] = state
			server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				w.Header().Set("Content-Type", "application/json")
				json.NewEncoder(w).Encode(payload)
			}))
			defer server.Close()
			client, err := NewClient("test-key", Options{BaseURL: server.URL, HTTPClient: server.Client()})
			if err != nil {
				t.Fatal(err)
			}
			own, err := client.Actors().ByActorId(ratingTarget).Rating().Get(context.Background(), nil)
			if err != nil {
				t.Fatal(err)
			}
			rating := own.GetRating()
			if rating.GetId() == nil || rating.GetTargetType().String() != "Actor" || rating.GetCreatedAtUtc().Equal(*rating.GetUpdatedAtUtc()) || rating.GetReview().GetState().String() != state || rating.GetReview().GetPublishedAtUtc() != nil {
				t.Fatal("own review metadata lost")
			}
		})
	}
}

func TestOwnRatingsPagination(t *testing.T) {
	fixture := ratingFixture(t)
	var filters map[string]string
	json.Unmarshal(fixture["filters"], &filters)
	query := url.Values{}
	for key, value := range filters {
		query.Set(key, value)
	}
	calls := 0
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/ratings/mine" || !reflect.DeepEqual(r.URL.Query(), query) || r.Header.Get("X-Api-Key") != "test-key" {
			t.Errorf("filters or cursor changed: %s", r.URL)
		}
		w.Header().Set("Content-Type", "application/json")
		key := "page"
		if calls > 0 {
			key = "lastPage"
		}
		calls++
		w.Write(fixture[key])
	}))
	defer server.Close()
	client, err := NewClient("test-key", Options{BaseURL: server.URL, HTTPClient: server.Client()})
	if err != nil {
		t.Fatal(err)
	}
	// The pinned runtime panics on typed date query parameters, even unset ones.
	page, err := client.Ratings().Mine().WithUrl(server.URL+"/ratings/mine?"+query.Encode()).Get(context.Background(), nil)
	if err != nil {
		t.Fatal(err)
	}
	if !*page.GetHasMore() || page.GetItems()[0].GetReview().GetState().String() != "Pending" || page.GetItems()[1].GetReview() != nil {
		t.Fatal("page metadata lost")
	}
	query.Set("cursor", *page.GetNextCursor())
	last, err := client.Ratings().Mine().WithUrl(server.URL+"/ratings/mine?"+query.Encode()).Get(context.Background(), nil)
	if err != nil || last == nil || len(last.GetItems()) != 0 || *last.GetHasMore() || last.GetNextCursor() != nil || calls != 2 {
		t.Fatalf("last page: %v", err)
	}
}

func TestRatingErrors(t *testing.T) {
	for _, resource := range []string{"actors", "videos"} {
		for _, code := range []int{400, 401, 403, 404, 409, 429, 503} {
			t.Run(resource+"/"+strconv.Itoa(code), func(t *testing.T) {
				var problems map[string]json.RawMessage
				json.Unmarshal(ratingFixture(t)["problems"], &problems)
				server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
					w.Header().Set("Content-Type", "application/json")
					w.Header().Set("Retry-After", "300")
					w.WriteHeader(code)
					w.Write(problems[strconv.Itoa(code)])
				}))
				defer server.Close()
				client, err := NewClient("test-key", Options{BaseURL: server.URL, HTTPClient: server.Client()})
				if err != nil {
					t.Fatal(err)
				}
				status := &ResponseStatusOption{}
				_, err = ratingOperations(client, resource, ratingTarget).submit(context.Background(), models.NewSubmitRatingReviewRequest(), &ratingConfig{Options: []abstractions.RequestOption{status}})
				var problem *models.ProblemDetails
				if !errors.As(err, &problem) || *problem.GetStatus() != int32(code) || status.StatusCode != code {
					t.Fatalf("typed error lost: %v", err)
				}
				if code == 429 && problem.GetResponseHeaders().Get("Retry-After")[0] != "300" {
					t.Fatal("retry header lost")
				}
			})
		}
	}
}
