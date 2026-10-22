import datetime
import json
from pathlib import Path
from uuid import UUID

import httpx
import pytest
from kiota_abstractions.base_request_configuration import RequestConfiguration
from prdb_sdk import create_client, RetryOptions
from prdb_sdk.generated.videos.baseline.baseline_request_builder import BaselineRequestBuilder
from prdb_sdk.generated.models.baseline_document_too_large_response import BaselineDocumentTooLargeResponse
from prdb_sdk.generated.models.identify_video_file_dto import IdentifyVideoFileDto
from prdb_sdk.generated.models.identify_videos_request import IdentifyVideosRequest
from prdb_sdk.generated.models.validate_identification_request import ValidateIdentificationRequest

FIXTURE = json.loads((Path(__file__).resolve().parents[2] / "tests/fixtures/sync-contracts.json").read_text())

async def test_baseline_query_full_document_and_typed_oversized_continuation():
    status = 200
    def respond(request):
        assert request.url.path == "/videos/baseline"
        assert request.url.params["Cursor"] == "opaque+/="
        assert request.url.params["PageSize"] == "1000"
        assert request.url.params["CreatedFrom"].startswith("2026-10-01")
        return httpx.Response(status, json=FIXTURE["baseline" if status == 200 else "oversized"])
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as transport:
        client = create_client("test-key", base_url="https://api.example.test", http_client=transport, retry=RetryOptions.disabled())
        query = BaselineRequestBuilder.BaselineRequestBuilderGetQueryParameters(created_from=datetime.datetime(2026,10,1,tzinfo=datetime.timezone.utc), created_before=datetime.datetime(2026,10,22,tzinfo=datetime.timezone.utc), page_size=1000, cursor="opaque+/=")
        config = RequestConfiguration(query_parameters=query)
        page = await client.videos.baseline.get(config)
        assert page.items[0].description == "Full document"
        assert page.next_cursor == "opaque+/=" and page.has_more
        assert page.changes_since == datetime.datetime(2026,10,22,10,tzinfo=datetime.timezone.utc)
        status = 413
        with pytest.raises(BaselineDocumentTooLargeResponse) as caught:
            await client.videos.baseline.get(config)
        assert caught.value.next_cursor == "after-large"
        assert caught.value.video_id == UUID(FIXTURE["oversized"]["videoId"])
        assert caught.value.changes_since == page.changes_since

async def test_freshness_opt_in_original_tuple_mixed_results_and_legacy_omission():
    legacy = False
    def respond(request):
        body = json.loads(request.content)
        if request.url.path == "/videos/identify":
            assert body["includeFreshness"] is True
            return httpx.Response(200,json=FIXTURE["legacy" if legacy else "identify"])
        assert request.url.path == "/videos/identify/validate"
        assert body["reidentify"] is False
        assert body["files"][0]["filesize"] == 4294967296
        assert body["files"][0]["md5"] == "a" * 32
        assert body["files"][0]["freshnessToken"] == "proof"
        return httpx.Response(200,json=FIXTURE["validation"])
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as transport:
        client = create_client("test-key",base_url="https://api.example.test",http_client=transport)
        file = IdentifyVideoFileDto(ref="r1", filename="Synthetic.mp4", filesize=4294967296, md5="a"*32)
        request = IdentifyVideosRequest(files=[file],include_freshness=True)
        result = await client.videos.identify.post(request)
        assert result.results[0].freshness_token == "proof"
        assert result.results[0].freshness_expires_at_utc is not None
        file.freshness_token = result.results[0].freshness_token
        mixed = await client.videos.identify.validate.post(ValidateIdentificationRequest(files=[file],reidentify=False))
        assert [x.status.value for x in mixed.results] == ["unchanged","identified","reidentify"]
        assert [x.ref for x in mixed.results] == ["r1","r2","r3"]
        assert mixed.results[0].result is None and mixed.results[2].result is None
        assert mixed.results[1].result.freshness_token == "replacement"
        legacy = True
        old = await client.videos.identify.post(request)
        assert old.results[0].freshness_token is None and old.results[0].freshness_expires_at_utc is None
