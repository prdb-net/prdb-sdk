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
import type { HttpClient } from "@microsoft/kiota-http-fetchlibrary";

import { createPrdbClient, type PrdbClient } from "./generated/prdbClient.js";

/** Header the API expects the key in. */
export const API_KEY_HEADER = "X-Api-Key";

/** Production base URL, also the default baked into the generated client. */
export const DEFAULT_BASE_URL = "https://api.prdb.net";

export interface ClientOptions {
	/** The API key, sent in the `X-Api-Key` header on every request. */
	apiKey: string;
	/** Override the API root. Useful for a staging deployment. */
	baseUrl?: string;
	/** Supply your own HTTP client to control timeouts, proxies or retries. */
	httpClient?: HttpClient;
}

export type AnonymousClientOptions = Omit<ClientOptions, "apiKey">;

/**
 * Create a client authenticated with an API key.
 *
 * @throws If `apiKey` is empty or `baseUrl` is not an absolute URL.
 */
export function createClient(options: ClientOptions): PrdbClient {
	const { apiKey, baseUrl = DEFAULT_BASE_URL, httpClient } = options;

	if (!apiKey) {
		throw new Error("apiKey must not be empty");
	}

	const host = hostOf(baseUrl);

	// Restricting the key to the API host means a redirect to somewhere else
	// cannot carry the credential off-site.
	const authProvider = new ApiKeyAuthenticationProvider(
		apiKey,
		API_KEY_HEADER,
		ApiKeyLocation.Header,
		new Set([host]),
	);

	return buildClient(authProvider, baseUrl, httpClient);
}

/**
 * Create a client without credentials.
 *
 * Only `GET /health` is reachable this way; every other endpoint answers 401.
 * Provided so health probes do not need an API key.
 */
export function createAnonymousClient(
	options: AnonymousClientOptions = {},
): PrdbClient {
	const { baseUrl = DEFAULT_BASE_URL, httpClient } = options;
	hostOf(baseUrl);

	return buildClient(new AnonymousAuthenticationProvider(), baseUrl, httpClient);
}

function buildClient(
	authProvider: ConstructorParameters<typeof DefaultRequestAdapter>[0],
	baseUrl: string,
	httpClient?: HttpClient,
): PrdbClient {
	const adapter = new DefaultRequestAdapter(
		authProvider,
		undefined,
		undefined,
		httpClient,
	);
	adapter.baseUrl = baseUrl;

	return createPrdbClient(adapter);
}

function hostOf(baseUrl: string): string {
	let host: string;
	try {
		host = new URL(baseUrl).host;
	} catch {
		throw new Error(`baseUrl must be an absolute URL, got ${baseUrl}`);
	}
	if (!host) {
		throw new Error(`baseUrl must be an absolute URL, got ${baseUrl}`);
	}
	return host;
}

export type { PrdbClient };
