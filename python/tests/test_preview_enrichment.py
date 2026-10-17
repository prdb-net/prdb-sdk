import json
from pathlib import Path
from uuid import UUID

import httpx
import pytest

from prdb_sdk import create_client
from prdb_sdk.generated.models.get_videos_by_ids_request import GetVideosByIdsRequest
from prdb_sdk.generated.models.problem_details import ProblemDetails

FIXTURE = json.loads((Path(__file__).resolve().parents[2] / "tests/fixtures/preview-enrichment.json").read_text())
ORIGIN = "https://api.example.test"
VIDEO_ID = UUID(FIXTURE["detail"]["id"])


def client_for(respond):
    transport = httpx.AsyncClient(transport=httpx.MockTransport(respond))
    return transport, create_client("test-key", base_url=ORIGIN, http_client=transport)


async def test_detail_keeps_true_and_reads_an_absent_field_as_unknown():
    bodies = iter([FIXTURE["detail"], FIXTURE["detailFromOlderServer"]])

    def respond(request):
        assert request.url.path == f"/videos/{VIDEO_ID}"
        return httpx.Response(200, json=next(bodies))

    transport, client = client_for(respond)
    async with transport:
        current = await client.videos.by_id(VIDEO_ID).get()
        older = await client.videos.by_id(VIDEO_ID).get()
    assert current.preview_enrichment_eligible is True
    assert older.preview_enrichment_eligible is None


async def test_batch_keeps_true_false_and_absent_apart():
    def respond(request):
        assert request.url.path == "/videos/batch"
        assert request.method == "POST"
        return httpx.Response(200, json=FIXTURE["batch"])

    transport, client = client_for(respond)
    async with transport:
        videos = await client.videos.batch.post(GetVideosByIdsRequest(ids=[UUID(v["id"]) for v in FIXTURE["batch"]]))
    assert [video.preview_enrichment_eligible for video in videos] == [True, False, None]


async def test_feed_carries_upserts_tombstones_and_flips_across_cursor_pages():
    pages = iter(FIXTURE["pages"])
    queries = []

    def respond(request):
        assert request.url.path == "/videos/changes"
        queries.append(dict(request.url.params))
        return httpx.Response(200, json=next(pages))

    transport, client = client_for(respond)
    async with transport:
        changes = client.videos.changes
        first = await changes.with_url(ORIGIN + "/videos/changes?Since=0001-01-01T00%3A00%3A00Z&PageSize=2").get()
        assert first.has_more is True
        assert [item.video.preview_enrichment_eligible for item in first.items] == [True, False]
        cursor = first.next_cursor
        second = await changes.with_url(ORIGIN + f"/videos/changes?Since=2026-10-17T12%3A00%3A00Z&SinceId={cursor.id}&PageSize=2").get()
        tombstone = second.items[0].video
        assert second.items[0].event_type == "deleted"
        assert tombstone.is_deleted is True
        assert tombstone.preview_enrichment_eligible is False
        following = await changes.with_url(ORIGIN + "/videos/changes?Since=2026-10-17T12%3A02%3A00Z").get()
    flipped = following.items[0].video
    assert flipped.id == first.items[0].video.id
    assert flipped.preview_enrichment_eligible is False
    assert queries[1]["SinceId"] == str(cursor.id)


@pytest.mark.parametrize(
    ("status", "body", "call"),
    [
        (404, "notFound", lambda client: client.videos.by_id(VIDEO_ID).get()),
        (403, "forbidden", lambda client: client.videos.batch.post(GetVideosByIdsRequest(ids=[VIDEO_ID]))),
        (400, "invalidCursor", lambda client: client.videos.changes.get()),
    ],
)
async def test_declared_errors_stay_typed_problems(status, body, call):
    transport, client = client_for(lambda _: httpx.Response(status, json=FIXTURE[body]))
    async with transport:
        with pytest.raises(ProblemDetails) as caught:
            await call(client)
    assert caught.value.status == status
