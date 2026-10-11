"""Exercise the published actor merge wire shapes through the SDK adapter.

The shared fixture is synthetic. Server-side resolution is tested upstream;
these checks ensure consumers receive typed UUIDs and nullable metadata.
"""

import json
from pathlib import Path
from uuid import UUID

import httpx
import pytest
from kiota_abstractions.base_request_configuration import RequestConfiguration

from prdb_sdk import ResponseStatusOption, create_client
from prdb_sdk.generated.models.get_actors_by_ids_request import GetActorsByIdsRequest

FIXTURE = json.loads(
    (Path(__file__).resolve().parents[2] / "tests/fixtures/actor-merge.json").read_text()
)
ORIGIN = "https://api.example.test"


@pytest.mark.parametrize("omit_mapping", [False, True])
async def test_retained_actor_detail_and_batch_mapping(omit_mapping):
    source, target = UUID(FIXTURE["sourceId"]), UUID(FIXTURE["targetId"])
    requests = []

    def respond(request):
        requests.append(request)
        if request.url.path == "/actors/batch":
            assert request.method == "POST"
            assert json.loads(request.content)["ids"] == [str(source), str(target)]
            return httpx.Response(200, json=FIXTURE["batch"])
        assert request.url.path == f"/actors/{source}"
        detail = dict(FIXTURE["detail"])
        if omit_mapping:
            del detail["requestedIds"]
        return httpx.Response(200, json=detail)

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as transport:
        client = create_client("test-key", base_url=ORIGIN, http_client=transport)
        status = ResponseStatusOption()
        detail = await client.actors.by_id(source).get(
            RequestConfiguration(options=[status])
        )
        assert status.status_code == 200
        assert detail.id == target
        assert detail.requested_ids is None
        batch = await client.actors.batch.post(GetActorsByIdsRequest(ids=[source, target]))
        assert len(batch) == 1
        assert batch[0].id == target
        assert batch[0].requested_ids == [source, target]
    assert len(requests) == 2  # A retained ID response requires no redirect.


@pytest.mark.parametrize("favorite", [False, True])
async def test_merge_feed_keeps_source_identity_and_nullable_targets(favorite):
    path = "/favorite-actors/changes" if favorite else "/actors/changes"
    payload = FIXTURE["favoriteActorChanges" if favorite else "actorChanges"]

    def respond(request):
        assert request.url.path == path
        assert request.url.params["Since"] == "0001-01-01T00:00:00Z"
        return httpx.Response(200, json=payload)

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as transport:
        client = create_client("test-key", base_url=ORIGIN, http_client=transport)
        builder = client.favorite_actors.changes if favorite else client.actors.changes
        page = await builder.with_url(f"{ORIGIN}{path}?Since=0001-01-01T00%3A00%3A00Z").get()
        assert [item.event_type for item in page.items] == ["deleted", "updated", "deleted"]
        source, target, ordinary = [
            item.favorite_actor if favorite else item.actor for item in page.items
        ]
        assert source.id == UUID(FIXTURE["sourceId"])
        assert source.is_deleted is True
        assert source.merged_into_actor_id == UUID(FIXTURE["targetId"])
        assert target.id == UUID(FIXTURE["targetId"])
        assert target.is_deleted is False
        assert target.merged_into_actor_id is None  # Omitted property.
        assert ordinary.is_deleted is True
        assert ordinary.merged_into_actor_id is None  # Explicit null.
        assert page.next_cursor.id == UUID(FIXTURE["ordinaryId"])
