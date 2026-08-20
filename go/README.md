# prdb-sdk (Go)

Go client for the [prdb Public API](https://apidocs.prdb.net/).

## Install

```bash
go get github.com/prdb-net/prdb-sdk/go
```

Requires Go 1.23 or newer. The import path ends in `/go` because this is a
multi-language repository; the package name is `prdb`.

## Usage

```go
package main

import (
	"context"
	"fmt"
	"log"

	"github.com/google/uuid"
	prdb "github.com/prdb-net/prdb-sdk/go"
)

func main() {
	ctx := context.Background()

	client, err := prdb.NewClient("...")
	if err != nil {
		log.Fatal(err)
	}

	// GET /videos
	page, err := client.Videos().Get(ctx, nil)
	if err != nil {
		log.Fatal(err)
	}
	for _, video := range page.GetItems() {
		fmt.Println(*video.GetTitle())
	}

	// GET /videos/{id}
	videoID := uuid.MustParse("...")
	video, err := client.Videos().ById(videoID).Get(ctx, nil)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Println(*video.GetTitle())
}
```

The request builders mirror the API's URL structure, so `GET /videos/{id}/filehashes`
is `client.Videos().ById(videoID).Filehashes().Get(ctx, nil)`.

## Authentication

`NewClient` sends the key in the `X-Api-Key` header, and keeps it on the API
host: a redirect to a different host is refused with an error rather than
handing your credential to whoever answers there. Redirects that stay on the
same host are followed normally.

`BaseURL` must use `https`, so the key is never sent in cleartext.

`GET /health` is the only endpoint that works without a key; use
`NewAnonymousClient()` for health probes. That one has no credential to
protect, so it accepts a plain `http` base URL.

## Options

```go
client, err := prdb.NewClient("...", prdb.Options{
	BaseURL:    "https://api.prdb.net", // override for a staging deployment
	HTTPClient: myHTTPClient,           // control timeouts, proxies, retries
})
```

Supplying an `*http.Client` leaves it untouched: the redirect rule is applied to
a copy. It is applied even if you set `CheckRedirect` yourself — yours runs
after ours, so it can refuse more redirects but not re-enable one that leaves
the API host with your key attached.

### Retrying

By default the SDK retries a `429`, `503` or `504` up to three times, honouring
`Retry-After`.

Turn that off if your application already retries prdb calls:

```go
client, err := prdb.NewClient("...", prdb.Options{
	Retry: prdb.RetryDisabled(),
})
```

Otherwise the two policies multiply — one logical call becomes up to *n×m*
requests against an API that rate limits, and an outer circuit breaker never
sees a stable failure to open on. The built-in policy also retries writes, so an
application that must not repeat one should own the retry itself.

To keep it but change it:

```go
client, err := prdb.NewClient("...", prdb.Options{
	Retry: &prdb.RetryOptions{MaxRetries: 5, Delay: time.Second},
})
```

`Retry` and `HTTPClient` are mutually exclusive, and setting both is an error.
Kiota's middleware lives in the `Transport` a supplied client owns, so the SDK's
pipeline does not run for it — configure retrying on that client instead.

## Reading the response status

A typed call returns the deserialised body but not the response status. Pass a
`ResponseStatusOption` when the status itself matters; the conditional-request
example below uses it to distinguish a **304 Not Modified** response from other
responses with no body.

Pass a `ResponseStatusOption` to read it:

```go
import (
	"fmt"

	abstractions "github.com/microsoft/kiota-abstractions-go"
	prdb "github.com/prdb-net/prdb-sdk/go"
)

status := prdb.NewResponseStatusOption()

health, err := client.Health().Get(ctx,
	&abstractions.RequestConfiguration[abstractions.DefaultQueryParameters]{
		Options: []abstractions.RequestOption{status},
	})
if err != nil {
	return err
}

fmt.Println(health, status.StatusCode)
```

Kiota's own native response handler surfaces the raw response but suppresses
deserialisation while doing so. This option keeps the typed result and records
the status alongside it.

## Reading the rate limit

Every metered response carries the rate limit it was counted against, so you can
pace off the answers you are already getting instead of spending a request on
`GET /rate-limit` to ask.

```go
import (
	abstractions "github.com/microsoft/kiota-abstractions-go"
	prdb "github.com/prdb-net/prdb-sdk/go"
	"github.com/prdb-net/prdb-sdk/go/generated/sites"
)

limits := prdb.NewRateLimitOption()

page, err := client.Sites().Get(ctx,
	&abstractions.RequestConfiguration[sites.SitesRequestBuilderGetQueryParameters]{
		Options: []abstractions.RequestOption{limits},
	})
if err != nil {
	return err
}

if limits.Hour != nil && limits.Hour.Remaining < 50 {
	// Slow down; limits.Hour.ResetInSeconds until a slot frees up.
}
```

`Hour` and `Month` are each a `*RateLimitWindow` with `Limit`, `Remaining` and
`ResetInSeconds`, or nil.

`ResetInSeconds` is the wait until the oldest request leaves the sliding window
and frees **one** slot — not a timestamp, and not the time until the whole
window resets. It is the same quantity `resetsInSeconds` carries on
`GET /rate-limit`.

Nil is an answer rather than a gap. A response the API did not meter — `401`,
`403`, `503`, and `GET /rate-limit` itself — carries no headers at all, and a
`429` carries only the window that refused the request, so exactly one of the
two being set is normal. A failed call records too, so the reading is there for
a caller that inspects the error.

Kiota can also surface response headers itself, through
`khttp.HeadersInspectionOptions`. Prefer this option in Go: Kiota's is a
middleware, and middleware lives in the `Transport` that a supplied
`HTTPClient` owns, so it reads nothing at all on that path — silently. This one
is a `RoundTripper` on the client the SDK sends through, so it works whether or
not you brought your own.

## Conditional requests

`GET /sites` returns a weak `ETag` covering the matched rows and the paging,
sorting and search parameters. Send it back as `If-None-Match` and the endpoint
answers **304 Not Modified** with no body while nothing has changed — the whole
site list fits in one request at `PageSize` 1000, so this is worth doing.

```go
import (
	abstractions "github.com/microsoft/kiota-abstractions-go"
	khttp "github.com/microsoft/kiota-http-go"
	prdb "github.com/prdb-net/prdb-sdk/go"
	"github.com/prdb-net/prdb-sdk/go/generated/sites"
)

// First call: read the validator off the response.
inspect := khttp.NewHeadersInspectionOptions()
inspect.InspectResponseHeaders = true

if _, err := client.Sites().Get(ctx,
	&abstractions.RequestConfiguration[sites.SitesRequestBuilderGetQueryParameters]{
		Options: []abstractions.RequestOption{inspect},
	}); err != nil {
	return err
}
etag := inspect.GetResponseHeaders().Get("etag")[0]

// Later: ask only for what changed.
headers := abstractions.NewRequestHeaders()
headers.Add("If-None-Match", etag)
status := prdb.NewResponseStatusOption()

page, err := client.Sites().Get(ctx,
	&abstractions.RequestConfiguration[sites.SitesRequestBuilderGetQueryParameters]{
		Headers: headers,
		Options: []abstractions.RequestOption{status},
	})
if err != nil {
	return err
}

if status.StatusCode == http.StatusNotModified {
	// Nothing changed; page is nil, keep the copy you already have.
}
```

A `304` returns nil from the typed call rather than an error. Nil alone does not
distinguish "not modified" from "no rows", so pass a `ResponseStatusOption` when
you need to tell them apart. Note that reading the validator needs Kiota's
headers-inspection option, which — as above — reads nothing when you supplied
your own `HTTPClient`.

One wrinkle from the API side: the shared read-only cache does not vary by
`If-None-Match`, so a request that hits it is answered `200` with a body even
when your validator still matches. That is expected rather than an error.

Use one instance per call. It is written when the response arrives, so sharing
one across concurrent calls means whichever finishes last wins.

The status recorded is the one the result was built from: after a redirect that
was followed, and after the last retry. A call that fails records too, so the
status is there alongside a `403`'s error. It stays zero when nothing answered
at all — a failed connection or a timeout. Unlike the other three SDKs this also
works with a supplied `HTTPClient`, because the recorder is a `RoundTripper`
rather than Kiota middleware; with one, a refused cross-host redirect leaves the
redirect's own status behind, since `net/http` follows redirects above the
transport.

## Generated code

Everything under `generated/` is produced by Kiota from `spec/openapi.json` in
the repository root and is overwritten on every regeneration. Do not edit it —
see the [root README](../README.md#regenerating).
