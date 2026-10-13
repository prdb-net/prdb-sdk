import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { it } from "node:test";
import { createClient, RETRY_DISABLED } from "../src/index.js";

const fixture = JSON.parse(readFileSync(new URL("../../../tests/fixtures/release-resolution.json", import.meta.url), "utf8"));

it("posts int64 hints and preserves typed mixed release results and nullable dates", async () => {
    const client = createClient({apiKey: "test-key",baseUrl: "https://api.example.test",customFetch: async (url,init) => {
        assert.equal(new URL(url).pathname,"/releases/resolve");
        const body = JSON.parse(new TextDecoder().decode(init!.body as ArrayBuffer));
        assert.equal(body.releases[0].sizeBytes,4294967296);
        assert.equal(body.releases[0].postedAtUtc,"2026-10-13T14:00:00.000Z");
        return new Response(JSON.stringify(fixture.response),{status:200,headers:{"content-type":"application/json"}});
    }});
    const result = (await client.releases.resolve.post({releases:fixture.request.releases.map((x:any) => ({...x,postedAtUtc:x.postedAtUtc ? new Date(x.postedAtUtc) : undefined}))}))!;
    assert.deepEqual(result.results!.map(x => x.ref),fixture.response.results.map((x:any) => x.ref));
    assert.equal(result.results![2].status,"retryLater");
    assert.ok(result.evaluatedAtUtc instanceof Date);
    assert.equal(result.results![3].recheckAfterUtc,undefined);
    assert.equal(result.results![1].videos![0].releaseDate,undefined);
    assert.equal(result.results![2].sourceState!.lastSuccessfulSyncAtUtc,undefined);
    assert.deepEqual(result.results![1].videoIds,[fixture.ids.creator]);
    assert.deepEqual(result.results![5].videoIds,[]);
    assert.equal(result.results![5].candidates!.length,1);
});

for (const status of [401,403,429,503]) it(`returns typed release gate ${status} without retrying`, async () => {
    const client = createClient({apiKey:"test-key",baseUrl:"https://api.example.test",retry:RETRY_DISABLED,
        customFetch: async () => new Response(JSON.stringify(fixture.problems[status]),{status,headers:{"content-type":"application/json","Retry-After":"300"}})});
    await assert.rejects(() => client.releases.resolve.post({releases:[{ref:"r",title:"x"}]}),(error:any) => error.status === status && error.detail === "Bounded synthetic problem.");
});
