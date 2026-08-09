/**
 * Tests for the hand-written client wrapper.
 *
 * The generated code is not tested here; it is Kiota's output and is covered by
 * the drift check in CI. What is worth testing is the wrapper's own promises:
 * where the API key goes, and where it must not go.
 *
 * Requests are served by a recording `fetch` stub rather than a real socket, so
 * no TLS certificates are needed and every test stays in-process.
 */
import assert from "node:assert/strict";
import { describe, it } from "node:test";

import {
	API_KEY_HEADER,
	CrossOriginRedirectError,
	DEFAULT_BASE_URL,
	type FetchLike,
	RETRY_DISABLED,
	RateLimitOption,
	ResponseStatusOption,
	createAnonymousClient,
	createClient,
} from "../src/index.js";

const API_ORIGIN = "https://api.example.test";
const OTHER_ORIGIN = "https://elsewhere.example.test";

const HEALTH_BODY = JSON.stringify({
	status: "healthy",
	timestamp: "2026-08-07T12:00:00Z",
});

interface SeenRequest {
	url: string;
	apiKey: string | undefined;
}

class Recorder {
	readonly requests: SeenRequest[] = [];

	/** Wraps a handler so every request it serves is recorded first. */
	fetch(handler: (url: string) => Response): FetchLike {
		return async (url, init) => {
			const headers = (init.headers ?? {}) as Record<string, string>;
			this.requests.push({
				url,
				// The adapter lower-cases header keys on the way through.
				apiKey:
					headers[API_KEY_HEADER] ?? headers[API_KEY_HEADER.toLowerCase()],
			});
			return handler(url);
		};
	}

	keysSentTo(host: string): (string | undefined)[] {
		return this.requests
			.filter((request) => new URL(request.url).host === host)
			.map((request) => request.apiKey)
			.filter((key) => key !== undefined);
	}
}

function healthy(): Response {
	return new Response(HEALTH_BODY, {
		status: 200,
		headers: { "content-type": "application/json" },
	});
}

describe("createClient", () => {
	it("sends the api key header", async () => {
		const recorder = new Recorder();
		const client = createClient({
			apiKey: "secret-key",
			baseUrl: API_ORIGIN,
			customFetch: recorder.fetch(healthy),
		});

		await client.health.get();

		assert.equal(recorder.requests[0]?.apiKey, "secret-key");
	});

	it("rejects an empty api key", () => {
		assert.throws(() => createClient({ apiKey: "" }));
	});

	for (const baseUrl of ["api.prdb.net", "/videos", "not a url", ""]) {
		it(`rejects the relative base url ${JSON.stringify(baseUrl)}`, () => {
			assert.throws(() => createClient({ apiKey: "secret-key", baseUrl }));
		});
	}

	// An API key must not travel in cleartext. The Go SDK's Kiota provider
	// refuses this outright; the others do not, so the wrapper enforces it to
	// keep the four SDKs behaving alike. A staging deployment has to terminate
	// TLS.
	it("rejects a plaintext base url", () => {
		assert.throws(
			() =>
				createClient({ apiKey: "secret-key", baseUrl: "http://localhost:8080" }),
			/https/,
		);
	});
});

describe("createAnonymousClient", () => {
	it("sends no api key", async () => {
		const recorder = new Recorder();
		const client = createAnonymousClient({
			baseUrl: API_ORIGIN,
			customFetch: recorder.fetch(healthy),
		});

		await client.health.get();

		assert.equal(recorder.requests[0]?.apiKey, undefined);
	});

	// With no credential to protect, plain HTTP is the caller's business.
	it("allows a plaintext base url", () => {
		assert.doesNotThrow(() =>
			createAnonymousClient({ baseUrl: "http://localhost:8080" }),
		);
	});
});

describe("redirects", () => {
	/**
	 * The guarantee the README makes, pinned down.
	 *
	 * Kiota's default scrubbing drops only `authorization`, `cookie` and
	 * `proxy-authorization`, and `fetch` keeps custom headers across a redirect,
	 * so without the wrapper's own rule the key would travel to whoever answers
	 * at the redirect target.
	 */
	it("refuses one that leaves the origin, without leaking the key", async () => {
		const recorder = new Recorder();
		const client = createClient({
			apiKey: "secret-key",
			baseUrl: API_ORIGIN,
			customFetch: recorder.fetch((url) =>
				url.startsWith(API_ORIGIN)
					? new Response(null, {
							status: 307,
							headers: { location: `${OTHER_ORIGIN}/health` },
						})
					: healthy(),
			),
		});

		await assert.rejects(
			() => client.health.get(),
			(error: unknown) => error instanceof CrossOriginRedirectError,
		);

		assert.deepEqual(recorder.keysSentTo("elsewhere.example.test"), []);
	});

	// Refusing cross-origin redirects must not refuse ordinary ones.
	it("follows one that stays on the origin", async () => {
		const recorder = new Recorder();
		const client = createClient({
			apiKey: "secret-key",
			baseUrl: API_ORIGIN,
			customFetch: recorder.fetch((url) =>
				url.endsWith("/health")
					? new Response(null, {
							status: 307,
							headers: { location: `${API_ORIGIN}/healthz` },
						})
					: healthy(),
			),
		});

		const result = await client.health.get();

		assert.notEqual(result, undefined);
		assert.deepEqual(
			recorder.requests.map((request) => new URL(request.url).pathname),
			["/health", "/healthz"],
		);
		assert.deepEqual(recorder.keysSentTo("api.example.test"), [
			"secret-key",
			"secret-key",
		]);
	});
});

describe("retrying", () => {
	function refuseOnce(recorder: Recorder): (url: string) => Response {
		return () =>
			recorder.requests.length === 1
				? new Response(null, { status: 503 })
				: healthy();
	}

	// Kiota's retry handler is in the default pipeline, so this is the status quo.
	it("retries a refused request by default", async () => {
		const recorder = new Recorder();
		const client = createClient({
			apiKey: "secret-key",
			baseUrl: API_ORIGIN,
			customFetch: recorder.fetch(refuseOnce(recorder)),
			retry: { maxRetries: 1, delay: 0 },
		});

		const result = await client.health.get();

		assert.notEqual(result, undefined);
		assert.equal(recorder.requests.length, 2);
	});

	/**
	 * The opt-out an application with its own retry policy needs.
	 *
	 * Without it the SDK's retry sits outside the application's and the two
	 * multiply: one logical call becomes several requests against an API that
	 * rate limits, and the outer circuit breaker never sees a stable failure.
	 */
	it("does not retry when retrying is disabled", async () => {
		const recorder = new Recorder();
		const client = createClient({
			apiKey: "secret-key",
			baseUrl: API_ORIGIN,
			customFetch: recorder.fetch(() => new Response(null, { status: 503 })),
			retry: RETRY_DISABLED,
		});

		await assert.rejects(() => client.health.get());

		assert.equal(recorder.requests.length, 1);
	});

	for (const retry of [
		{ maxRetries: -1 },
		{ maxRetries: 11 },
		{ delay: -1 },
		{ delay: 181 },
	]) {
		it(`rejects the out-of-range option ${JSON.stringify(retry)}`, () => {
			assert.throws(() =>
				createClient({ apiKey: "secret-key", baseUrl: API_ORIGIN, retry }),
			);
		});
	}
});

describe("ResponseStatusOption", () => {
	const ENTRY_BODY = JSON.stringify({
		id: "00000000-0000-0000-0000-000000000100",
		indexerId: "indexer-entry-id",
	});

	function entry(status: number): Response {
		return new Response(ENTRY_BODY, {
			status,
			headers: { "content-type": "application/json" },
		});
	}

	function addEntry(
		client: ReturnType<typeof createClient>,
		status: ResponseStatusOption,
	) {
		return client.downloadedFromIndexers.post(
			{ indexerId: "indexer-entry-id" },
			{ options: [status] },
		);
	}

	/**
	 * Both halves at once.
	 *
	 * `POST /downloaded-from-indexers` answers 201 when it created the entry and
	 * 200 when an equivalent one already existed, and the bodies are the same
	 * shape, so a caller who has to tell them apart has nothing else to go on.
	 * Kiota's native response handler surfaces the response but suppresses
	 * deserialisation, so it cannot serve both.
	 */
	for (const status of [201, 200]) {
		it(`reports ${status} alongside the typed result`, async () => {
			const recorder = new Recorder();
			const client = createClient({
				apiKey: "secret-key",
				baseUrl: API_ORIGIN,
				customFetch: recorder.fetch(() => entry(status)),
			});
			const option = new ResponseStatusOption();

			const result = await addEntry(client, option);

			assert.equal(result?.indexerId, "indexer-entry-id");
			assert.equal(option.statusCode, status);
		});
	}

	// The handler sits above the retry handler, so the attempt that succeeded wins.
	it("reports the last attempt when a refusal is retried", async () => {
		const recorder = new Recorder();
		const client = createClient({
			apiKey: "secret-key",
			baseUrl: API_ORIGIN,
			customFetch: recorder.fetch(() =>
				recorder.requests.length === 1
					? new Response(null, { status: 503 })
					: entry(201),
			),
			retry: { maxRetries: 1, delay: 0 },
		});
		const option = new ResponseStatusOption();

		await addEntry(client, option);

		assert.equal(recorder.requests.length, 2);
		assert.equal(option.statusCode, 201);
	});

	// A refusal records too, for a caller that catches the error.
	it("reports the status when the api refuses", async () => {
		const recorder = new Recorder();
		const client = createClient({
			apiKey: "secret-key",
			baseUrl: API_ORIGIN,
			customFetch: recorder.fetch(
				() =>
					new Response(
						JSON.stringify({
							title: "Forbidden",
							status: 403,
							detail: "no api plan",
						}),
						{ status: 403, headers: { "content-type": "application/json" } },
					),
			),
			retry: RETRY_DISABLED,
		});
		const option = new ResponseStatusOption();

		await assert.rejects(() => addEntry(client, option));

		assert.equal(option.statusCode, 403);
	});

	// Nothing answered, so there is no status -- rather than an invented one.
	it("reports no status when no response was reached", async () => {
		const recorder = new Recorder();
		const client = createClient({
			apiKey: "secret-key",
			baseUrl: API_ORIGIN,
			customFetch: recorder.fetch((url) =>
				url.startsWith(API_ORIGIN)
					? new Response(null, {
							status: 307,
							headers: { location: `${OTHER_ORIGIN}/health` },
						})
					: healthy(),
			),
		});
		const option = new ResponseStatusOption();

		await assert.rejects(
			() => client.health.get({ options: [option] }),
			(error: unknown) => error instanceof CrossOriginRedirectError,
		);

		assert.equal(option.statusCode, undefined);
	});
});

describe("RateLimitOption", () => {
	const SITES_BODY = JSON.stringify({
		items: [],
		page: 1,
		pageSize: 20,
		totalCount: 7,
	});

	const RATE_LIMIT_HEADERS: Record<string, string> = {
		"X-RateLimit-Limit-Hour": "1000",
		"X-RateLimit-Remaining-Hour": "993",
		"X-RateLimit-Reset-Hour": "2471",
		"X-RateLimit-Limit-Month": "50000",
		"X-RateLimit-Remaining-Month": "48120",
		"X-RateLimit-Reset-Month": "1904322",
	};

	function sites(
		status = 200,
		headers: Record<string, string> = {},
	): Response {
		return new Response(SITES_BODY, {
			status,
			headers: { "content-type": "application/json", ...headers },
		});
	}

	/**
	 * The point of the option: pace off the response you already have.
	 *
	 * Kiota can surface the headers, but as raw multi-valued strings. This is the
	 * typed reading, and it arrives with the model rather than instead of it.
	 */
	it("reports both windows alongside the typed result", async () => {
		const recorder = new Recorder();
		const client = createClient({
			apiKey: "secret-key",
			baseUrl: API_ORIGIN,
			customFetch: recorder.fetch(() => sites(200, RATE_LIMIT_HEADERS)),
		});
		const limits = new RateLimitOption();

		const page = await client.sites.get({ options: [limits] });

		assert.equal(page?.totalCount, 7);
		assert.deepEqual(limits.hour, {
			limit: 1000,
			remaining: 993,
			resetInSeconds: 2471,
		});
		assert.deepEqual(limits.month, {
			limit: 50000,
			remaining: 48120,
			resetInSeconds: 1904322,
		});
	});

	// A 429 carries only the window it came from, so one window alone is normal.
	it("reports only the window that refused a request", async () => {
		const recorder = new Recorder();
		const hourlyOnly = Object.fromEntries(
			Object.entries(RATE_LIMIT_HEADERS).filter(([name]) =>
				name.endsWith("-Hour"),
			),
		);
		const client = createClient({
			apiKey: "secret-key",
			baseUrl: API_ORIGIN,
			customFetch: recorder.fetch(() =>
				sites(429, { ...hourlyOnly, "retry-after": "2471" }),
			),
			retry: RETRY_DISABLED,
		});
		const limits = new RateLimitOption();

		await assert.rejects(() => client.sites.get({ options: [limits] }));

		// A refusal is exactly when a caller wants the reading, so it records too.
		assert.deepEqual(limits.hour, {
			limit: 1000,
			remaining: 993,
			resetInSeconds: 2471,
		});
		assert.equal(limits.month, undefined);
	});

	// 401, 403, 503 and GET /rate-limit carry no headers -- that is an answer.
	it("reports no rate limit for an unmetered response", async () => {
		const recorder = new Recorder();
		const client = createClient({
			apiKey: "secret-key",
			baseUrl: API_ORIGIN,
			customFetch: recorder.fetch(() => sites()),
		});
		const limits = new RateLimitOption();

		await client.sites.get({ options: [limits] });

		assert.equal(limits.hour, undefined);
		assert.equal(limits.month, undefined);
	});

	// Metadata about a call that already worked must not be able to break it.
	it("survives a malformed header without failing the call", async () => {
		const recorder = new Recorder();
		const client = createClient({
			apiKey: "secret-key",
			baseUrl: API_ORIGIN,
			customFetch: recorder.fetch(() =>
				sites(200, {
					...RATE_LIMIT_HEADERS,
					"X-RateLimit-Remaining-Hour": "12abc",
				}),
			),
		});
		const limits = new RateLimitOption();

		const page = await client.sites.get({ options: [limits] });

		assert.equal(page?.totalCount, 7);
		// parseInt("12abc") would be 12 — a plausible-looking wrong reading.
		assert.equal(limits.hour, undefined);
		// The other window is independent, so it still reads.
		assert.deepEqual(limits.month, {
			limit: 50000,
			remaining: 48120,
			resetInSeconds: 1904322,
		});
	});
});

describe("conditional requests", () => {
	const ETAG = 'W/"abc123"';

	/**
	 * A 304 is the request working, not failing.
	 *
	 * Kiota generates no handling for a declared 3xx in any language, so what
	 * each SDK does with one is its request adapter's fallback rather than
	 * anything generated. TypeScript falls through to "no body, return
	 * undefined". Pinned here because C# does not — it throws, and needs a
	 * handler in the pipeline to match the other three — so a Kiota upgrade that
	 * moved TypeScript the same way should fail the build rather than the caller.
	 */
	it("returns undefined on a 304 rather than rejecting", async () => {
		const recorder = new Recorder();
		const client = createClient({
			apiKey: "secret-key",
			baseUrl: API_ORIGIN,
			customFetch: async (url, init) => {
				const headers = (init.headers ?? {}) as Record<string, string>;
				const sent = headers["If-None-Match"] ?? headers["if-none-match"];
				recorder.requests.push({ url, apiKey: undefined });

				return sent === ETAG
					? new Response(null, { status: 304, headers: { etag: ETAG } })
					: new Response(
							JSON.stringify({
								items: [],
								page: 1,
								pageSize: 20,
								totalCount: 7,
							}),
							{
								status: 200,
								headers: { "content-type": "application/json", etag: ETAG },
							},
						);
			},
		});
		const status = new ResponseStatusOption();

		const page = await client.sites.get({
			headers: { "If-None-Match": ETAG },
			options: [status],
		});

		assert.equal(page, undefined);
		// undefined alone cannot be told apart from an empty page; the status can.
		assert.equal(status.statusCode, 304);
	});
});

describe("defaults", () => {
	it("point at production over https", () => {
		assert.ok(DEFAULT_BASE_URL.startsWith("https://"));
	});
});
