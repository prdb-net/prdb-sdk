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

A typed call returns the deserialised body, which is all you need until an
operation answers with more than one success status. `POST
/downloaded-from-indexers` is the one that does: **201** when it created the
entry, **200** when an equivalent one already existed and is being returned
unchanged. The bodies are the same shape, so the status is the only thing that
tells the two apart.

Pass a `ResponseStatusOption` to read it:

```go
import (
	abstractions "github.com/microsoft/kiota-abstractions-go"
	prdb "github.com/prdb-net/prdb-sdk/go"
)

status := prdb.NewResponseStatusOption()

entry, err := client.DownloadedFromIndexers().Post(ctx, body,
	&abstractions.RequestConfiguration[abstractions.DefaultQueryParameters]{
		Options: []abstractions.RequestOption{status},
	})
if err != nil {
	return err
}

if status.StatusCode == http.StatusOK {
	// An equivalent entry already existed; entry is the one the API has.
}
```

Kiota's own native response handler cannot serve this: it surfaces the raw
response but suppresses deserialisation while doing so, so the typed result
comes back nil. The option is the other half — the call returns its model as
usual, and the status is on the option afterwards.

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
