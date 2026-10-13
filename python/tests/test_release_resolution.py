import datetime
import json
from pathlib import Path
from uuid import UUID

import httpx
import pytest
from prdb_sdk import create_client, RetryOptions
from prdb_sdk.generated.models.resolve_releases_request import ResolveReleasesRequest
from prdb_sdk.generated.models.resolve_release_input import ResolveReleaseInput
from prdb_sdk.generated.models.resolve_release_source import ResolveReleaseSource
from prdb_sdk.generated.models.release_source_kind import ReleaseSourceKind
from prdb_sdk.generated.models.release_resolution_status import ReleaseResolutionStatus
from prdb_sdk.generated.models.rate_limit_problem_response import RateLimitProblemResponse

FIXTURE = json.loads((Path(__file__).resolve().parents[2] / "tests/fixtures/release-resolution.json").read_text())


async def test_release_resolution_posts_int64_and_reads_typed_mixed_results():
    def respond(request):
        assert request.url.path == "/releases/resolve"
        assert request.headers["X-Api-Key"] == "test-key"
        body = json.loads(request.content)
        assert body["releases"][0]["sizeBytes"] == 4294967296
        assert body["releases"][0]["postedAtUtc"].endswith(("Z", "+00:00"))
        return httpx.Response(200, json=FIXTURE["response"])
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as transport:
        client = create_client("test-key", base_url="https://api.example.test", http_client=transport)
        body = ResolveReleasesRequest(releases=[ResolveReleaseInput(ref=x["ref"],title=x["title"],size_bytes=x.get("sizeBytes"),
            posted_at_utc=datetime.datetime.fromisoformat(x["postedAtUtc"].replace("Z","+00:00")) if "postedAtUtc" in x else None,
            source=ResolveReleaseSource(kind=ReleaseSourceKind.Nzbcache if x["source"]["kind"] == "nzbcache" else ReleaseSourceKind.Newznab,
                origin=x["source"]["origin"],entry_id=x["source"]["entryId"]) if "source" in x else None)
            for x in FIXTURE["request"]["releases"]])
        result = await client.releases.resolve.post(body)
        assert [row.ref for row in result.results] == [row["ref"] for row in FIXTURE["response"]["results"]]
        assert result.results[0].status == ReleaseResolutionStatus.Resolved
        assert result.results[2].status == ReleaseResolutionStatus.RetryLater
        assert result.results[3].recheck_after_utc is None
        assert result.results[1].videos[0].release_date is None
        assert result.results[2].source_state.last_successful_sync_at_utc is None
        assert result.results[1].video_ids == [UUID(FIXTURE["ids"]["creator"])]
        assert result.results[5].video_ids == []
        assert len(result.results[5].candidates) == 1


@pytest.mark.parametrize("status", [401,403,429,503])
async def test_release_gate_errors_are_typed_without_retrying(status):
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _: httpx.Response(status,json=FIXTURE["problems"][str(status)],headers={"Retry-After":"300"}))) as transport:
        client = create_client("test-key",base_url="https://api.example.test",http_client=transport,retry=RetryOptions.disabled())
        with pytest.raises(RateLimitProblemResponse) as caught:
            await client.releases.resolve.post(ResolveReleasesRequest(releases=[ResolveReleaseInput(ref="r",title="x")]))
        assert caught.value.status == status
