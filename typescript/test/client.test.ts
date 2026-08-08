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

describe("defaults", () => {
	it("point at production over https", () => {
		assert.ok(DEFAULT_BASE_URL.startsWith("https://"));
	});
});
