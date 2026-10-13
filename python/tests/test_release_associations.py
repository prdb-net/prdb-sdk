import json
from pathlib import Path
from uuid import UUID

import httpx
import pytest

from prdb_sdk import create_client
from prdb_sdk.generated.models.validation_problem_details import ValidationProblemDetails

FIXTURE = json.loads((Path(__file__).resolve().parents[2] / "tests/fixtures/release-associations.json").read_text())
ORIGIN = "https://api.example.test"


async def test_baseline_empty_and_followup_keep_states_and_typed_cursor():
    pages = iter(FIXTURE["pages"])

    def respond(request):
        assert request.url.path == "/video-release-associations/changes"
        assert request.headers["X-Api-Key"] == "test-key"
        assert "Since" in request.url.params
        return httpx.Response(200, json=next(pages))

    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as transport:
        client = create_client("test-key", base_url=ORIGIN, http_client=transport)
        builder = client.video_release_associations.changes
        baseline = await builder.with_url(ORIGIN + "/video-release-associations/changes?Since=0001-01-01T00%3A00%3A00Z").get()
        rows = [item.video_release_association for item in baseline.items]
        assert rows[0].is_confirmed is True
        assert rows[1].is_confirmed is False
        assert rows[2].source_available is False
        assert rows[3].is_deleted is True
        assert isinstance(baseline.next_cursor.id, UUID)
        empty = await builder.with_url(ORIGIN + f"/video-release-associations/changes?Since=2026-10-13T12%3A00%3A00Z&SinceId={baseline.next_cursor.id}").get()
        assert empty.items == []
        assert empty.next_cursor.id == baseline.next_cursor.id
        following = await builder.with_url(ORIGIN + "/video-release-associations/changes?Since=2026-10-13T12%3A02%3A00Z").get()
        assert following.items[0].video_release_association.id == rows[0].id
        assert following.items[0].video_release_association.video_id != rows[0].video_id


async def test_invalid_cursor_has_typed_problem():
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _: httpx.Response(400, json=FIXTURE["invalidCursor"]))) as transport:
        client = create_client("test-key", base_url=ORIGIN, http_client=transport)
        with pytest.raises(ValidationProblemDetails) as caught:
            await client.video_release_associations.changes.get()
        assert caught.value.status == 400
        assert caught.value.errors is not None
