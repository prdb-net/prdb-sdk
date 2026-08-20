/**
 * TypeScript SDK for the prdb Public API.
 *
 * The request builders mirror the API's URL structure:
 *
 * ```ts
 * import { createClient } from "@prdb/sdk";
 *
 * const client = createClient({ apiKey: "..." });
 * const page = await client.videos.get();
 * const video = await client.videos.byId(videoId).get();
 * ```
 *
 * Everything under `./generated` is produced by Kiota from `spec/openapi.json`
 * and is overwritten on every regeneration. Do not edit it.
 */
import {
	AnonymousAuthenticationProvider,
	ApiKeyAuthenticationProvider,
	ApiKeyLocation,
	type RequestOption,
} from "@microsoft/kiota-abstractions";
import { DefaultRequestAdapter } from "@microsoft/kiota-bundle";
import {
	type HttpClient,
	KiotaClientFactory,
	type Middleware,
	MiddlewareFactory,
	RedirectHandler,
	RedirectHandlerOptions,
	RetryHandler,
	RetryHandlerOptions,
} from "@microsoft/kiota-http-fetchlibrary";

import { createPrdbClient, type PrdbClient } from "./generated/prdbClient.js";

/** Header the API expects the key in. */
export const API_KEY_HEADER = "X-Api-Key";

/** Production base URL, also the default baked into the generated client. */
export const DEFAULT_BASE_URL = "https://api.prdb.net";

/** A fetch implementation, as Kiota's middleware pipeline expects it. */
export type FetchLike = (
	url: string,
	init: RequestInit,
) => Promise<Response>;

/**
 * Thrown when the API redirects to a different origin.
 *
 * Following such a redirect would hand the API key to whoever answers at the
 * new location, so the SDK refuses it. Redirects that stay on the same origin
 * are followed normally.
 */
export class CrossOriginRedirectError extends Error {
	constructor(originalUrl: string, newUrl: string) {
		super(
			`refusing to follow a redirect from ${new URL(originalUrl).host} to ` +
				`${new URL(newUrl).host}; the api key is bound to the first host`,
		);
		this.name = "CrossOriginRedirectError";
	}
}

/** Key the {@link ResponseStatusOption} travels under. */
export const RESPONSE_STATUS_OPTION_KEY = "prdb.responseStatus";

/**
 * Per-request option reporting which status code the API answered with.
 *
 * A generated method returns the deserialised body and nothing else. That is
 * not enough when the status itself matters, for example when a conditional
 * `GET /sites` returns `304` with no body.
 *
 * Kiota's own way of reaching the response is a native response handler, which
 * suppresses deserialisation while it does so — you get the raw response or the
 * typed model, never both. This option is the other half: the call returns its
 * model as usual, and the status is here afterwards.
 *
 * ```ts
 * const status = new ResponseStatusOption();
 *
 * const health = await client.health.get({
 * 	options: [status],
 * });
 *
 * console.assert(health?.status === "healthy");
 * console.assert(status.statusCode === 200);
 * ```
 *
 * Use one instance per call: it is written when the response arrives, so
 * sharing one across concurrent calls means whichever finishes last wins.
 *
 * The status recorded is the one of the response the result was built from —
 * after any redirect the SDK followed, and after the last retry. A call that
 * rejects records too, so the status is there for a caller that catches the
 * error.
 */
export class ResponseStatusOption implements RequestOption {
	/**
	 * The status the API answered with, or `undefined` until the call has
	 * produced a response — and for good if none was reached at all, as with a
	 * connection failure or a redirect refused by
	 * {@link CrossOriginRedirectError}.
	 */
	statusCode?: number;

	getKey(): string {
		return RESPONSE_STATUS_OPTION_KEY;
	}
}

/** Key the {@link RateLimitOption} travels under. */
export const RATE_LIMIT_OPTION_KEY = "prdb.rateLimit";

/** One rate-limiting window, as the API reported it on a response. */
export interface RateLimitWindow {
	/** How many requests the window allows in total. */
	readonly limit: number;
	/** How many of them are left. */
	readonly remaining: number;
	/**
	 * Seconds until the oldest request leaves the sliding window and frees one
	 * slot — not a timestamp, and not the time until the whole window resets.
	 * The same quantity `resetsInSeconds` carries on `GET /rate-limit`.
	 */
	readonly resetInSeconds: number;
}

/**
 * Per-request option reporting the rate-limit state the API sent back.
 *
 * Every metered response carries its rate-limit headers, so a client can pace
 * itself off the answers it is already getting instead of spending a request on
 * `GET /rate-limit` to ask.
 *
 * Kiota can surface response headers through its own headers-inspection option,
 * but as raw multi-valued strings that a caller has to find, pick apart and
 * parse. This option is the typed form:
 *
 * ```ts
 * const limits = new RateLimitOption();
 *
 * const sites = await client.sites.get({ options: [limits] });
 *
 * if (limits.hour && limits.hour.remaining < 50) {
 * 	// Slow down; limits.hour.resetInSeconds until a slot frees up.
 * }
 * ```
 *
 * Use one instance per call: it is written when the response arrives, so
 * sharing one across concurrent calls means whichever finishes last wins.
 */
export class RateLimitOption implements RequestOption {
	/**
	 * The hourly window, or `undefined` if the response carried no hourly
	 * headers.
	 */
	hour?: RateLimitWindow;

	/**
	 * The monthly window, or `undefined` if the response carried no monthly
	 * headers.
	 *
	 * Both are `undefined` for a response the API did not meter — `401`, `403`,
	 * `503` and `GET /rate-limit` itself — and for a call that never reached a
	 * response. A `429` carries only the window that refused it, so exactly one
	 * of the two being set is normal rather than a partial reading.
	 */
	month?: RateLimitWindow;

	getKey(): string {
		return RATE_LIMIT_OPTION_KEY;
	}
}

/**
 * Read one window's three headers, or `undefined` if they are not all there.
 *
 * Deliberately lenient: rate-limit headers are metadata about a call that has
 * already succeeded, so a missing or malformed one reports "no reading" rather
 * than failing the call the caller actually made.
 */
function readRateLimitWindow(
	headers: Headers,
	window: "Hour" | "Month",
): RateLimitWindow | undefined {
	const values: number[] = [];

	for (const name of ["Limit", "Remaining", "Reset"]) {
		const raw = headers.get(`X-RateLimit-${name}-${window}`);
		if (raw === null) {
			return undefined;
		}
		// Number() rather than parseInt(): parseInt("12abc") is 12, which would
		// turn a malformed header into a plausible-looking reading.
		const value = Number(raw.trim());
		if (!Number.isInteger(value)) {
			return undefined;
		}
		values.push(value);
	}

	const [limit, remaining, resetInSeconds] = values as [number, number, number];
	return { limit, remaining, resetInSeconds };
}

/**
 * Records response metadata into the options a request carries.
 *
 * Sits at the outer end of the SDK's pipeline, above the retry and redirect
 * handlers, so what it records is the response the caller's result is built
 * from rather than an attempt on the way there.
 */
class ResponseMetadataHandler implements Middleware {
	next: Middleware | undefined;

	async execute(
		url: string,
		requestInit: RequestInit,
		requestOptions?: Record<string, RequestOption>,
	): Promise<Response> {
		if (!this.next) {
			throw new Error("next middleware is undefined.");
		}

		const response = await this.next.execute(url, requestInit, requestOptions);

		// Matched by key rather than `instanceof`: the key is ours alone, and two
		// copies of this package in one dependency tree would still agree on it
		// where a class identity check would not.
		const status = requestOptions?.[RESPONSE_STATUS_OPTION_KEY] as
			| ResponseStatusOption
			| undefined;
		if (status) {
			status.statusCode = response.status;
		}

		const limits = requestOptions?.[RATE_LIMIT_OPTION_KEY] as
			| RateLimitOption
			| undefined;
		if (limits) {
			limits.hour = readRateLimitWindow(response.headers, "Hour");
			limits.month = readRateLimitWindow(response.headers, "Month");
		}

		return response;
	}
}

/**
 * How the SDK retries a request the API refused with 429, 503 or 504.
 *
 * Retry belongs to whoever owns the calling application's resilience story. An
 * application that already retries prdb calls itself should pass
 * {@link RETRY_DISABLED}, otherwise the two policies multiply: one logical call
 * becomes up to `n×m` requests against an API that rate limits, and the outer
 * circuit breaker never sees a stable failure to open on.
 *
 * The built-in policy retries idempotent and non-idempotent requests alike, so
 * an application that must not repeat a write should own the retry itself.
 */
export interface RetryOptions {
	/**
	 * How often a refused request is retried. At most 10. Zero leaves the retry
	 * handler out of the pipeline entirely.
	 *
	 * @default 3
	 */
	maxRetries?: number;
	/**
	 * Seconds to wait before a retry, unless the response carries a
	 * `Retry-After` header, which always wins. At most 180.
	 *
	 * @default 3
	 */
	delay?: number;
}

/** No retrying at all: a 429 or 503 reaches the caller as the API sent it. */
export const RETRY_DISABLED: RetryOptions = { maxRetries: 0 };

export interface ClientOptions {
	/** The API key, sent in the `X-Api-Key` header on every request. */
	apiKey: string;
	/**
	 * Override the API root. Useful for a staging deployment. Must use `https`,
	 * so the key is never sent in cleartext.
	 */
	baseUrl?: string;
	/**
	 * Supply your own fetch implementation to control timeouts, proxies or
	 * agents. It is wrapped in the SDK's middleware either way, so the redirect
	 * rule below always applies.
	 */
	customFetch?: FetchLike;
	/**
	 * How the SDK retries a refused request. Defaults to Kiota's policy — three
	 * attempts, honouring `Retry-After`. Pass {@link RETRY_DISABLED} if your
	 * application already retries prdb calls itself.
	 */
	retry?: RetryOptions;
}

export type AnonymousClientOptions = Omit<ClientOptions, "apiKey">;

/**
 * Create a client authenticated with an API key.
 *
 * @throws If `apiKey` is empty, or `baseUrl` is not an absolute `https` URL.
 */
export function createClient(options: ClientOptions): PrdbClient {
	const { apiKey, baseUrl = DEFAULT_BASE_URL, customFetch, retry } = options;

	if (!apiKey) {
		throw new Error("apiKey must not be empty");
	}

	const host = hostOf(baseUrl, { requireHttps: true });

	const authProvider = new ApiKeyAuthenticationProvider(
		apiKey,
		API_KEY_HEADER,
		ApiKeyLocation.Header,
		new Set([host]),
	);

	return buildClient(authProvider, baseUrl, customFetch, retry);
}

/**
 * Create a client without credentials.
 *
 * Only `GET /health` is reachable this way; every other endpoint answers 401.
 * Provided so health probes do not need an API key.
 *
 * With no credential to protect, `baseUrl` may use plain `http`.
 */
export function createAnonymousClient(
	options: AnonymousClientOptions = {},
): PrdbClient {
	const { baseUrl = DEFAULT_BASE_URL, customFetch, retry } = options;
	hostOf(baseUrl, { requireHttps: false });

	return buildClient(
		new AnonymousAuthenticationProvider(),
		baseUrl,
		customFetch,
		retry,
	);
}

function buildClient(
	authProvider: ConstructorParameters<typeof DefaultRequestAdapter>[0],
	baseUrl: string,
	customFetch?: FetchLike,
	retry?: RetryOptions,
): PrdbClient {
	const adapter = new DefaultRequestAdapter(
		authProvider,
		undefined,
		undefined,
		buildHttpClient(customFetch, retry),
	);
	adapter.baseUrl = baseUrl;

	return createPrdbClient(adapter);
}

/**
 * Build Kiota's default middleware pipeline with one change: a redirect to a
 * different origin is refused instead of followed.
 *
 * The API key travels in a custom header, and nothing below this point strips
 * it. Kiota's default scrubbing removes only `authorization`, `cookie` and
 * `proxy-authorization`, and `fetch` itself keeps custom headers across a
 * redirect, so a redirect off the API host would hand the credential to
 * whoever answered.
 */
function buildHttpClient(
	customFetch?: FetchLike,
	retry?: RetryOptions,
): HttpClient {
	let middlewares: Middleware[] =
		MiddlewareFactory.getDefaultMiddlewares(customFetch);

	const ours = new RedirectHandler(
		new RedirectHandlerOptions({
			scrubSensitiveHeaders: refuseCrossOriginRedirect,
		}),
	);

	const index = middlewares.findIndex(
		(middleware) => middleware instanceof RedirectHandler,
	);
	if (index === -1) {
		// Kiota's defaults no longer include one; ours still has to run.
		middlewares.unshift(ours);
	} else {
		middlewares[index] = ours;
	}

	if (retry) {
		middlewares = applyRetryOptions(middlewares, retry);
	}

	// First in the list is outermost, which puts it above the retry and redirect
	// handlers: the status it records is the one the caller's result was built
	// from, not that of an attempt on the way there.
	middlewares = [new ResponseMetadataHandler(), ...middlewares];

	return KiotaClientFactory.create(customFetch, middlewares);
}

/**
 * Replaces Kiota's retry handler with one built from `retry`, or drops it.
 *
 * Dropped rather than configured with zero attempts, so "no retrying" means the
 * handler is not in the pipeline at all and cannot be re-enabled by a
 * per-request option.
 */
function applyRetryOptions(
	middlewares: Middleware[],
	retry: RetryOptions,
): Middleware[] {
	const { maxRetries = 3, delay = 3 } = retry;

	if (maxRetries < 0 || maxRetries > 10) {
		throw new Error(
			`retry.maxRetries must be between 0 and 10, got ${maxRetries}`,
		);
	}
	if (delay < 0 || delay > 180) {
		throw new Error(
			`retry.delay must be between 0 and 180 seconds, got ${delay}`,
		);
	}

	if (maxRetries === 0) {
		return middlewares.filter(
			(middleware) => !(middleware instanceof RetryHandler),
		);
	}

	const index = middlewares.findIndex(
		(middleware) => middleware instanceof RetryHandler,
	);
	const ours = new RetryHandler(new RetryHandlerOptions({ maxRetries, delay }));

	if (index === -1) {
		return [ours, ...middlewares];
	}

	const configured = [...middlewares];
	configured[index] = ours;
	return configured;
}

/**
 * Refuse a redirect that leaves the origin the request started on.
 *
 * The key is deleted before throwing as well, so it is gone from the headers
 * even if a caller catches the error and reuses them.
 */
function refuseCrossOriginRedirect(
	headers: Record<string, string>,
	originalUrl: string,
	newUrl: string,
): void {
	const original = new URL(originalUrl);
	const next = new URL(newUrl);

	if (
		original.protocol.toLowerCase() === next.protocol.toLowerCase() &&
		original.host.toLowerCase() === next.host.toLowerCase()
	) {
		return;
	}

	// The request adapter lower-cases every header key before the middleware
	// sees it, so a PascalCase delete would be a no-op.
	for (const key of Object.keys(headers)) {
		const lower = key.toLowerCase();
		if (
			lower === API_KEY_HEADER.toLowerCase() ||
			lower === "authorization" ||
			lower === "cookie" ||
			lower === "proxy-authorization"
		) {
			delete headers[key];
		}
	}

	throw new CrossOriginRedirectError(originalUrl, newUrl);
}

function hostOf(
	baseUrl: string,
	{ requireHttps }: { requireHttps: boolean },
): string {
	let url: URL;
	try {
		url = new URL(baseUrl);
	} catch {
		throw new Error(`baseUrl must be an absolute URL, got ${baseUrl}`);
	}
	if (!url.host || (url.protocol !== "http:" && url.protocol !== "https:")) {
		throw new Error(`baseUrl must be an absolute URL, got ${baseUrl}`);
	}
	if (requireHttps && url.protocol !== "https:") {
		throw new Error(
			`baseUrl must use https so the api key is not sent in cleartext, got ${baseUrl}`,
		);
	}
	return url.host;
}

export type { PrdbClient };
