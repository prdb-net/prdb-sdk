import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { it } from "node:test";
import { createClient } from "../src/index.js";

const fixture = JSON.parse(readFileSync(new URL("../../../tests/fixtures/release-associations.json", import.meta.url), "utf8"));
const origin = "https://api.example.test";

it("keeps typed release states and resumes baseline, empty and correction pages", async () => {
	let index = 0;
	const client = createClient({ apiKey: "test-key", baseUrl: origin, customFetch: async (url) => {
		assert.equal(new URL(url).pathname, "/video-release-associations/changes");
		assert.ok(new URL(url).searchParams.has("Since"));
		return new Response(JSON.stringify(fixture.pages[index++]), { status: 200, headers: { "content-type": "application/json" } });
	} });
	const baseline = (await client.videoReleaseAssociations.changes.get({ queryParameters: { since: new Date("0001-01-01T00:00:00Z") } }))!;
	const rows = baseline.items!.map(item => item.videoReleaseAssociation!);
	assert.equal(rows[0].isConfirmed, true); assert.equal(rows[1].isConfirmed, false);
	assert.equal(rows[2].sourceAvailable, false); assert.equal(rows[3].isDeleted, true);
	assert.ok(baseline.nextCursor?.updatedAtUtc instanceof Date);
	const empty = (await client.videoReleaseAssociations.changes.get({ queryParameters: { since: baseline.nextCursor!.updatedAtUtc!, sinceId: baseline.nextCursor!.id! } }))!;
	assert.deepEqual(empty.items, []); assert.equal(empty.nextCursor?.id, baseline.nextCursor!.id);
	const following = (await client.videoReleaseAssociations.changes.get({ queryParameters: { since: empty.serverTimeUtc! } }))!;
	assert.equal(following.items![0].videoReleaseAssociation!.id, rows[0].id);
	assert.notEqual(following.items![0].videoReleaseAssociation!.videoId, rows[0].videoId);
	assert.equal(index, 3);
});

it("returns a typed validation problem for an invalid cursor", async () => {
	const client = createClient({ apiKey: "test-key", baseUrl: origin, customFetch: async () => new Response(JSON.stringify(fixture.invalidCursor), { status: 400, headers: { "content-type": "application/json" } }) });
	await assert.rejects(() => client.videoReleaseAssociations.changes.get(), (error: any) => error.status === 400 && error.errors != null);
});
