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
a copy, unless you have set `CheckRedirect` yourself.

## Generated code

Everything under `generated/` is produced by Kiota from `spec/openapi.json` in
the repository root and is overwritten on every regeneration. Do not edit it —
see the [root README](../README.md#regenerating).
