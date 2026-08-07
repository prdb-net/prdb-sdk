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
} from "@microsoft/kiota-abstractions";
import { DefaultRequestAdapter } from "@microsoft/kiota-bundle";
import {
	type HttpClient,
	KiotaClientFactory,
	type Middleware,
	MiddlewareFactory,
	RedirectHandler,
	RedirectHandlerOptions,
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
}

export type AnonymousClientOptions = Omit<ClientOptions, "apiKey">;

/**
 * Create a client authenticated with an API key.
 *
 * @throws If `apiKey` is empty, or `baseUrl` is not an absolute `https` URL.
 */
export function createClient(options: ClientOptions): PrdbClient {
	const { apiKey, baseUrl = DEFAULT_BASE_URL, customFetch } = options;

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

	return buildClient(authProvider, baseUrl, customFetch);
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
	const { baseUrl = DEFAULT_BASE_URL, customFetch } = options;
	hostOf(baseUrl, { requireHttps: false });

	return buildClient(
		new AnonymousAuthenticationProvider(),
		baseUrl,
		customFetch,
	);
}

function buildClient(
	authProvider: ConstructorParameters<typeof DefaultRequestAdapter>[0],
	baseUrl: string,
	customFetch?: FetchLike,
): PrdbClient {
	const adapter = new DefaultRequestAdapter(
		authProvider,
		undefined,
		undefined,
		buildHttpClient(customFetch),
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
function buildHttpClient(customFetch?: FetchLike): HttpClient {
	const middlewares: Middleware[] =
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

	return KiotaClientFactory.create(customFetch, middlewares);
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
