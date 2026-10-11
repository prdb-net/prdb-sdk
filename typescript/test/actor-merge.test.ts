import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { it } from "node:test";
import { createClient, ResponseStatusOption } from "../src/index.js";

// Synthetic wire responses shared with the other three SDK contract tests.
const fixture = JSON.parse(readFileSync(new URL("../../../tests/fixtures/actor-merge.json", import.meta.url), "utf8"));
const origin = "https://api.example.test";
const json = (body: unknown) => new Response(JSON.stringify(body), {
	status: 200, headers: { "content-type": "application/json" },
});

for (const omitMapping of [false, true]) {
	it(`reads canonical detail and batch UUID mappings (omitted: ${omitMapping})`, async () => {
		let requests = 0;
		const client = createClient({
			apiKey: "test-key", baseUrl: origin,
			customFetch: async (url, init) => {
				requests++;
				if (new URL(url).pathname === "/actors/batch") {
					assert.equal(init.method, "POST");
					assert.deepEqual((await new Response(init.body).json()).ids, [fixture.sourceId, fixture.targetId]);
					return json(fixture.batch);
				}
				assert.equal(new URL(url).pathname, `/actors/${fixture.sourceId}`);
				const detail = { ...fixture.detail };
				if (omitMapping) delete detail.requestedIds;
				return json(detail);
			},
		});
		const status = new ResponseStatusOption();
		const detail = await client.actors.byId(fixture.sourceId).get({ options: [status] });
		assert.equal(status.statusCode, 200);
		assert.equal(detail?.id, fixture.targetId);
		assert.ok(detail?.requestedIds == null);
		const batch = await client.actors.batch.post({ ids: [fixture.sourceId, fixture.targetId] });
		assert.equal(batch?.length, 1);
		assert.equal(batch?.[0].id, fixture.targetId);
		assert.deepEqual(batch?.[0].requestedIds, [fixture.sourceId, fixture.targetId]);
		assert.equal(requests, 2);
	});
}

for (const favorite of [false, true]) {
	it(`preserves source tombstones and nullable merge targets (favorite: ${favorite})`, async () => {
		const path = favorite ? "/favorite-actors/changes" : "/actors/changes";
		const client = createClient({
			apiKey: "test-key", baseUrl: origin,
			customFetch: async (url) => {
				assert.equal(new URL(url).pathname, path);
				assert.equal(new URL(url).searchParams.get("Since"), "0001-01-01T00:00:00.000Z");
				return json(favorite ? fixture.favoriteActorChanges : fixture.actorChanges);
			},
		});
		const config = { queryParameters: { since: new Date("0001-01-01T00:00:00Z") } };
		const result = favorite
			? await client.favoriteActors.changes.get(config).then(page => ({
				events: page?.items?.map(item => item.eventType),
				rows: page?.items?.map(item => item.favoriteActor), cursor: page?.nextCursor?.id,
			}))
			: await client.actors.changes.get(config).then(page => ({
				events: page?.items?.map(item => item.eventType),
				rows: page?.items?.map(item => item.actor), cursor: page?.nextCursor?.id,
			}));
		assert.deepEqual(result.events, ["deleted", "updated", "deleted"]);
		const rows = result.rows;
		assert.equal(rows?.[0]?.id, fixture.sourceId);
		assert.equal(rows?.[0]?.isDeleted, true);
		assert.equal(rows?.[0]?.mergedIntoActorId, fixture.targetId);
		assert.equal(rows?.[1]?.id, fixture.targetId);
		assert.equal(rows?.[1]?.isDeleted, false);
		assert.ok(rows?.[1]?.mergedIntoActorId == null);
		assert.equal(rows?.[2]?.isDeleted, true);
		assert.ok(rows?.[2]?.mergedIntoActorId == null);
		assert.equal(result.cursor, fixture.ordinaryId);
	});
}
