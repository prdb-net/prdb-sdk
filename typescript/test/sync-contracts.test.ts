import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { it } from "node:test";
import { createClient, RETRY_DISABLED } from "../src/index.js";

const fixture = JSON.parse(readFileSync(new URL("../../../tests/fixtures/sync-contracts.json", import.meta.url), "utf8"));
const response = (body: unknown, status = 200) => new Response(JSON.stringify(body), {status, headers: {"content-type":"application/json"}});
it("preserves baseline query, full documents and typed 413 continuation", async () => {
    let status = 200;
    const client = createClient({apiKey:"test-key",baseUrl:"https://api.example.test",retry:RETRY_DISABLED,customFetch:async url => {
        const parsed = new URL(url);
        assert.equal(parsed.pathname,"/videos/baseline");
        assert.equal(parsed.searchParams.get("Cursor"),"opaque+/=");
        assert.equal(parsed.searchParams.get("PageSize"),"1000");
        assert.ok(parsed.searchParams.get("CreatedFrom")!.startsWith("2026-10-01"));
        return response(fixture[status === 200 ? "baseline" : "oversized"],status);
    }});
    const config = {queryParameters:{createdFrom:new Date("2026-10-01T00:00:00Z"),createdBefore:new Date("2026-10-22T00:00:00Z"),pageSize:1000,cursor:"opaque+/="}};
    const page = (await client.videos.baseline.get(config))!;
    assert.equal(page.items![0].description,"Full document");
    assert.equal(page.nextCursor,"opaque+/="); assert.equal(page.hasMore,true);
    assert.equal(page.changesSince!.toISOString(),"2026-10-22T10:00:00.000Z");
    status = 413;
    await assert.rejects(() => client.videos.baseline.get(config),(error:any) => error.videoId === fixture.oversized.videoId && error.nextCursor === "after-large" && error.changesSince instanceof Date);
});
it("preserves freshness opt-in, original tuple, mixed nullable results and legacy omissions", async () => {
    let legacy = false;
    const client = createClient({apiKey:"test-key",baseUrl:"https://api.example.test",customFetch:async (url,init) => {
        const body = JSON.parse(new TextDecoder().decode(init!.body as ArrayBuffer));
        if (new URL(url).pathname === "/videos/identify") {
            assert.equal(body.includeFreshness,true); return response(fixture[legacy ? "legacy" : "identify"]);
        }
        assert.equal(new URL(url).pathname,"/videos/identify/validate");
        assert.equal(body.reidentify,false); assert.equal(body.files[0].filesize,4294967296);
        assert.equal(body.files[0].md5,"a".repeat(32)); assert.equal(body.files[0].freshnessToken,"proof");
        return response(fixture.validation);
    }});
    const file = {ref:"r1",filename:"Synthetic.mp4",filesize:4294967296,md5:"a".repeat(32)};
    const result = (await client.videos.identify.post({files:[file],includeFreshness:true}))!;
    assert.equal(result.results![0].freshnessToken,"proof"); assert.ok(result.results![0].freshnessExpiresAtUtc instanceof Date);
    const mixed = (await client.videos.identify.validate.post({files:[{...file,freshnessToken:result.results![0].freshnessToken}],reidentify:false}))!;
    assert.deepEqual(mixed.results!.map(x=>x.status),["unchanged","identified","reidentify"]);
    assert.deepEqual(mixed.results!.map(x=>x.ref),["r1","r2","r3"]);
    // Kiota TS deserializes null model references as empty objects; status controls reuse.
    assert.deepEqual(mixed.results![0].result,{}); assert.deepEqual(mixed.results![2].result,{});
    assert.equal(mixed.results![1].result!.freshnessToken,"replacement");
    legacy = true;
    const old = (await client.videos.identify.post({files:[file],includeFreshness:true}))!;
    assert.equal(old.results![0].freshnessToken,undefined); assert.equal(old.results![0].freshnessExpiresAtUtc,undefined);
});
