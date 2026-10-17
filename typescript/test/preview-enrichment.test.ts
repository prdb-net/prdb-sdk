import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { it } from "node:test";
import { createClient } from "../src/index.js";

const fixture = JSON.parse(readFileSync(new URL("../../../tests/fixtures/preview-enrichment.json", import.meta.url), "utf8"));
const origin = "https://api.example.test";
const videoId = fixture.detail.id as string;
const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: { "content-type": "application/json" } });

it("keeps a true detail value and reads an absent field as unknown", async () => {
	const bodies = [fixture.detail, fixture.detailFromOlderServer];
	const client = createClient({ apiKey: "test-key", baseUrl: origin, customFetch: async (url) => {
		assert.equal(new URL(url).pathname, `/videos/${videoId}`);
		return json(bodies.shift());
	} });
	const current = (await client.videos.byId(videoId).get())!;
	const older = (await client.videos.byId(videoId).get())!;
	assert.equal(current.previewEnrichmentEligible, true);
	assert.equal(older.previewEnrichmentEligible, undefined);
});

it("keeps true, false and absent apart in a batch", async () => {
	const client = createClient({ apiKey: "test-key", baseUrl: origin, customFetch: async (url, init) => {
		assert.equal(new URL(url).pathname, "/videos/batch"); assert.equal(init?.method, "POST");
		return json(fixture.batch);
	} });
	const videos = (await client.videos.batch.post({ ids: fixture.batch.map((v: any) => v.id) }))!;
	assert.deepEqual(videos.map(v => v.previewEnrichmentEligible), [true, false, undefined]);
});

it("carries upserts, tombstones and flips across cursor pages", async () => {
	const queries: URLSearchParams[] = [];
	let index = 0;
	const client = createClient({ apiKey: "test-key", baseUrl: origin, customFetch: async (url) => {
		assert.equal(new URL(url).pathname, "/videos/changes");
		queries.push(new URL(url).searchParams);
		return json(fixture.pages[index++]);
	} });
	const changes = client.videos.changes;
	const first = (await changes.get({ queryParameters: { since: new Date("0001-01-01T00:00:00Z"), pageSize: 2 } }))!;
	assert.equal(first.hasMore, true);
	assert.deepEqual(first.items!.map(item => item.video!.previewEnrichmentEligible), [true, false]);
	const second = (await changes.get({ queryParameters: { since: first.nextCursor!.updatedAtUtc!, sinceId: first.nextCursor!.id!, pageSize: 2 } }))!;
	const tombstone = second.items![0];
	assert.equal(tombstone.eventType, "deleted"); assert.equal(tombstone.video!.isDeleted, true);
	assert.equal(tombstone.video!.previewEnrichmentEligible, false);
	const following = (await changes.get({ queryParameters: { since: second.serverTimeUtc! } }))!;
	assert.equal(following.items![0].video!.id, first.items![0].video!.id);
	assert.equal(following.items![0].video!.previewEnrichmentEligible, false);
	assert.equal(queries[1].get("SinceId"), first.nextCursor!.id);
	assert.equal(index, 3);
});

for (const [status, body, call] of [
	[404, "notFound", (c: ReturnType<typeof createClient>) => c.videos.byId(videoId).get()],
	[403, "forbidden", (c: ReturnType<typeof createClient>) => c.videos.batch.post({ ids: [videoId] })],
	[400, "invalidCursor", (c: ReturnType<typeof createClient>) => c.videos.changes.get()],
] as const) {
	it(`returns a typed problem for a declared ${status}`, async () => {
		const client = createClient({ apiKey: "test-key", baseUrl: origin, customFetch: async () => json(fixture[body], status) });
		await assert.rejects(() => call(client), (error: any) => error.status === status && error.title === fixture[body].title);
	});
}
