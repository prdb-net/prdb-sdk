import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { it } from "node:test";
import { createClient, ResponseStatusOption, RETRY_DISABLED } from "../src/index.js";
import type { OwnReviewState, ProblemDetails } from "../src/generated/models/index.js";

// Synthetic wire responses shared with the other three SDK contract tests.
const fixture = JSON.parse(readFileSync(new URL("../../../tests/fixtures/ratings.json", import.meta.url), "utf8"));
const origin = "https://api.example.test";
const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), {
	status, headers: { "content-type": "application/json" },
});

for (const resource of ["actors", "videos"]) {
	it(`executes all ${resource} rating operations with typed bodies and statuses`, async () => {
		const exchanges: [string, string, number, string?][] = [
			["GET", "/rating-summary", 200, "emptySummary"],
			["GET", "/rating-summary", 200, "summary"],
			["GET", "/rating", 200, "noRating"],
			["PUT", "/rating", 200, "deletedReceipt"],
			["PUT", "/rating", 202, "receipt"],
			["POST", "/rating/review", 202, "receipt"],
			["DELETE", "/rating/review", 204],
			["DELETE", "/rating", 204],
		];
		let calls = 0;
		const client = createClient({
			apiKey: "test-key", baseUrl: origin,
			customFetch: async (url, init) => {
				const [method, suffix, code, payload] = exchanges[calls++];
				assert.equal(init.method, method);
				assert.equal(new URL(url).pathname, `/${resource}/${fixture.targetId}${suffix}`);
				const headers = new Headers(init.headers);
				assert.equal(headers.get("X-Api-Key"), "test-key");
				if (method === "PUT" || method === "POST") {
					const body = await new Response(init.body).json();
					if (calls === 4) {
						assert.equal(body.stars, 4);
						assert.ok(body.reviewText == null);
						assert.equal(headers.get("Idempotency-Key"), null);
					} else {
						assert.equal(headers.get("Idempotency-Key"), "synthetic-submission-key");
						assert.deepEqual(body, method === "PUT"
							? { stars: 4, reviewText: "Carefully made." } : { text: "Carefully made." });
					}
				}
				return payload ? json(fixture[payload], code) : new Response(null, { status: code });
			},
		});
		const target = resource === "actors" ? client.actors.byActorId(fixture.targetId) : client.videos.byId(fixture.targetId);
		const summary = await target.ratingSummary.get();
		assert.equal(summary?.ratingCount, 0);
		assert.equal(summary?.reviewCount, 0);
		assert.ok(summary?.averageRating == null);
		assert.equal((await target.ratingSummary.get())?.averageRating, 3.75);
		// The pinned JSON runtime materializes null objects as {}. Required IDs
		// distinguish an absent rating/review from a populated one.
		assert.ok((await target.rating.get())?.rating?.id == null);
		const deleted = await target.rating.put({ stars: 4 });
		assert.ok(deleted?.ratingId == null && deleted?.reviewId == null && deleted?.reviewState == null);
		const status = new ResponseStatusOption();
		const config = { headers: { "Idempotency-Key": "synthetic-submission-key" }, options: [status] };
		const pending = await target.rating.put({ stars: 4, reviewText: "Carefully made." }, config);
		assert.equal(status.statusCode, 202);
		assert.equal(pending?.ratingId, fixture.ratingId);
		assert.equal(pending?.reviewState, "Pending");
		const receipt = await target.rating.review.post({ text: "Carefully made." }, config);
		assert.equal(receipt?.reviewId, fixture.reviewId);
		assert.equal(status.statusCode, 202);
		assert.equal(await target.rating.review.delete(config), undefined);
		assert.equal(status.statusCode, 204);
		assert.equal(await target.rating.delete(config), undefined);
		assert.equal(status.statusCode, 204);
		assert.equal(calls, 8);
	});

	for (const code of [400, 401, 403, 404, 409, 429, 503]) {
		it(`returns a typed ${code} for ${resource} review submissions`, async () => {
			const client = createClient({
				apiKey: "test-key", baseUrl: origin, retry: RETRY_DISABLED,
				customFetch: async () => new Response(JSON.stringify(fixture.problems[code]), {
					status: code, headers: { "content-type": "application/json", "Retry-After": "300" },
				}),
			});
			const target = resource === "actors" ? client.actors.byActorId(fixture.targetId) : client.videos.byId(fixture.targetId);
			const status = new ResponseStatusOption();
			await assert.rejects(target.rating.review.post({ text: "Carefully made." }, { options: [status] }), error => {
				const problem = error as ProblemDetails;
				assert.equal(problem.status, code);
				if (code === 429) assert.deepEqual(problem.responseHeaders?.["retry-after"], ["300"]);
				return true;
			});
			assert.equal(status.statusCode, code);
		});
	}
}

for (const state of ["None", "Published", "Pending", "Rejected", "Hidden"] satisfies OwnReviewState[]) {
	it(`reads the safe own review state ${state}`, async () => {
		const payload = structuredClone(fixture.own);
		payload.rating.review.state = state;
		const client = createClient({ apiKey: "test-key", baseUrl: origin, customFetch: async () => json(payload) });
		const rating = (await client.actors.byActorId(fixture.targetId).rating.get())?.rating;
		assert.equal(rating?.id, fixture.ratingId);
		assert.equal(rating?.targetType, "Actor");
		assert.notDeepEqual(rating?.createdAtUtc, rating?.updatedAtUtc);
		assert.equal(rating?.review?.text, "Carefully made.");
		assert.equal(rating?.review?.state, state);
		assert.ok(rating?.review?.publishedAtUtc == null);
	});
}

it("pages own ratings with all filters and an opaque cursor", async () => {
	let calls = 0;
	const client = createClient({
		apiKey: "test-key", baseUrl: origin,
		customFetch: async (url, init) => {
			const parsed = new URL(url);
			assert.equal(parsed.pathname, "/ratings/mine");
			assert.equal(new Headers(init.headers).get("X-Api-Key"), "test-key");
			const expected = { ...fixture.filters, ...(calls ? { cursor: fixture.page.nextCursor } : {}) };
			for (const field of ["fromUtc", "toUtc"]) expected[field] = new Date(expected[field]).toISOString();
			assert.deepEqual(Object.fromEntries(parsed.searchParams), expected);
			return json(fixture[calls++ === 0 ? "page" : "lastPage"]);
		},
	});
	const config = { queryParameters: {
		search: "Example actor", type: "Actor" as const, stars: 4,
		fromUtc: new Date(fixture.filters.fromUtc), toUtc: new Date(fixture.filters.toUtc),
		hasText: true, reviewState: "Pending" as const, sortBy: "Stars" as const,
		sortDirection: "desc" as const, pageSize: 2, cursor: undefined as string | undefined,
	} };
	const page = await client.ratings.mine.get(config);
	assert.equal(page?.hasMore, true);
	assert.equal(page?.items?.[0].review?.state, "Pending");
	assert.ok(page?.items?.[1].review?.id == null);
	config.queryParameters.cursor = page?.nextCursor ?? undefined;
	const last = await client.ratings.mine.get(config);
	assert.deepEqual(last?.items, []);
	assert.equal(last?.hasMore, false);
	assert.ok(last?.nextCursor == null);
	assert.equal(calls, 2);
});
