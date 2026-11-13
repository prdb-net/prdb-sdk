"""Ratings wire contracts, using synthetic responses shared by all four SDKs."""

import copy
import json
from datetime import datetime
from pathlib import Path
from uuid import UUID

import httpx
import pytest
from kiota_abstractions.base_request_configuration import RequestConfiguration

from prdb_sdk import ResponseStatusOption, RetryOptions, create_client
from prdb_sdk.generated.models.own_review_state import OwnReviewState
from prdb_sdk.generated.models.problem_details import ProblemDetails
from prdb_sdk.generated.models.rating_sort_by import RatingSortBy
from prdb_sdk.generated.models.rating_target_type import RatingTargetType
from prdb_sdk.generated.models.set_rating_request import SetRatingRequest
from prdb_sdk.generated.models.submit_rating_review_request import SubmitRatingReviewRequest
from prdb_sdk.generated.ratings.mine.get_sort_direction_query_parameter_type import GetSortDirectionQueryParameterType
from prdb_sdk.generated.ratings.mine.mine_request_builder import MineRequestBuilder

FIXTURE = json.loads((Path(__file__).resolve().parents[2] / "tests/fixtures/ratings.json").read_text())
ORIGIN = "https://api.example.test"
TARGET = UUID(FIXTURE["targetId"])


@pytest.mark.parametrize("resource", ["actors", "videos"])
async def test_rating_operations_keep_bodies_headers_statuses_and_nulls(resource):
    path = f"/{resource}/{TARGET}"
    exchanges = iter([
        ("GET", "/rating-summary", 200, "emptySummary"),
        ("GET", "/rating-summary", 200, "summary"),
        ("GET", "/rating", 200, "noRating"),
        ("PUT", "/rating", 200, "deletedReceipt"),
        ("PUT", "/rating", 202, "receipt"),
        ("POST", "/rating/review", 202, "receipt"),
        ("DELETE", "/rating/review", 204, None),
        ("DELETE", "/rating", 204, None),
    ])
    calls = 0

    def respond(request):
        nonlocal calls
        method, suffix, code, payload = next(exchanges)
        calls += 1
        assert request.method == method
        assert request.url.path == path + suffix
        assert request.headers["X-Api-Key"] == "test-key"
        if method in ("PUT", "POST"):
            body = json.loads(request.content)
            if calls == 4:
                assert body["stars"] == 4
                assert body.get("reviewText") is None
                assert "Idempotency-Key" not in request.headers
            else:
                assert request.headers["Idempotency-Key"] == "synthetic-submission-key"
                assert body == ({"stars": 4, "reviewText": "Carefully made."} if method == "PUT" else {"text": "Carefully made."})
        return httpx.Response(code, json=FIXTURE[payload]) if payload else httpx.Response(code)

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as transport:
        client = create_client("test-key", base_url=ORIGIN, http_client=transport)
        target = client.actors.by_actor_id(TARGET) if resource == "actors" else client.videos.by_id(TARGET)
        summary = await target.rating_summary.get()
        assert (summary.rating_count, summary.review_count, summary.average_rating) == (0, 0, None)
        assert (await target.rating_summary.get()).average_rating == 3.75
        assert (await target.rating.get()).rating is None
        receipt = await target.rating.put(SetRatingRequest(stars=4))
        assert (receipt.rating_id, receipt.review_id, receipt.review_state) == (None, None, None)
        status = ResponseStatusOption()
        config = RequestConfiguration(options=[status])
        config.headers.add("Idempotency-Key", "synthetic-submission-key")
        for receipt in [
            await target.rating.put(SetRatingRequest(stars=4, review_text="Carefully made."), config),
            await target.rating.review.post(SubmitRatingReviewRequest(text="Carefully made."), config),
        ]:
            assert receipt.rating_id == UUID(FIXTURE["ratingId"])
            assert receipt.review_state == "Pending"
            assert status.status_code == 202
        assert await target.rating.review.delete(config) is None
        assert status.status_code == 204
        assert await target.rating.delete(config) is None
        assert status.status_code == 204
    assert calls == 8


@pytest.mark.parametrize("state", list(OwnReviewState))
async def test_own_review_safe_states_and_nullable_publication(state):
    payload = copy.deepcopy(FIXTURE["own"])
    payload["rating"]["review"]["state"] = state.value
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _: httpx.Response(200, json=payload))) as transport:
        client = create_client("test-key", base_url=ORIGIN, http_client=transport)
        rating = (await client.actors.by_actor_id(TARGET).rating.get()).rating
        assert rating.id == UUID(FIXTURE["ratingId"])
        assert rating.target_type == RatingTargetType.Actor
        assert rating.created_at_utc != rating.updated_at_utc
        assert rating.review.text == "Carefully made."
        assert rating.review.state == state
        assert rating.review.published_at_utc is None


async def test_mine_preserves_all_filters_and_opaque_cursor():
    calls = 0

    def respond(request):
        nonlocal calls
        assert request.url.path == "/ratings/mine"
        assert request.headers["X-Api-Key"] == "test-key"
        expected = dict(FIXTURE["filters"])
        if calls:
            expected["cursor"] = FIXTURE["page"]["nextCursor"]
        actual = dict(request.url.params)
        for field in ("fromUtc", "toUtc"):
            assert datetime.fromisoformat(actual.pop(field).replace("Z", "+00:00")) == datetime.fromisoformat(expected.pop(field).replace("Z", "+00:00"))
        assert actual == expected
        calls += 1
        return httpx.Response(200, json=FIXTURE["page" if calls == 1 else "lastPage"])

    query = MineRequestBuilder.MineRequestBuilderGetQueryParameters(
        search="Example actor", type=RatingTargetType.Actor, stars=4,
        from_utc=datetime.fromisoformat("2026-11-01T00:00:00+00:00"),
        to_utc=datetime.fromisoformat("2026-12-01T00:00:00+00:00"),
        has_text=True, review_state=OwnReviewState.Pending,
        sort_by=RatingSortBy.Stars, sort_direction=GetSortDirectionQueryParameterType.Desc,
        page_size=2,
    )
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as transport:
        client = create_client("test-key", base_url=ORIGIN, http_client=transport)
        config = RequestConfiguration(query_parameters=query)
        page = await client.ratings.mine.get(config)
        assert page.has_more is True
        assert page.items[0].review.state == OwnReviewState.Pending
        assert page.items[1].review is None
        query.cursor = page.next_cursor
        last = await client.ratings.mine.get(config)
        assert (last.items, last.has_more, last.next_cursor) == ([], False, None)
    assert calls == 2


@pytest.mark.parametrize("code", [400, 401, 403, 404, 409, 429, 503])
@pytest.mark.parametrize("resource", ["actors", "videos"])
async def test_rating_errors_are_typed_and_keep_retry_after(resource, code):
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _: httpx.Response(
        code, json=FIXTURE["problems"][str(code)], headers={"Retry-After": "300"},
    ))) as transport:
        client = create_client("test-key", base_url=ORIGIN, http_client=transport, retry=RetryOptions.disabled())
        target = client.actors.by_actor_id(TARGET) if resource == "actors" else client.videos.by_id(TARGET)
        status = ResponseStatusOption()
        with pytest.raises(ProblemDetails) as caught:
            await target.rating.review.post(SubmitRatingReviewRequest(text="Carefully made."), RequestConfiguration(options=[status]))
        assert caught.value.status == code
        assert status.status_code == code
        if code == 429:
            assert caught.value.response_headers["retry-after"] == "300"
