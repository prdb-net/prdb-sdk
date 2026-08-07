#!/usr/bin/env bash
# Shared configuration for the SDK generation scripts.

# Where the published spec lives. The path is not guessable: the docs UI at
# https://apidocs.prdb.net/ fetches /configuration.json to discover it, and
# /openapi.json returns 404. api.prdb.net never serves the document at all --
# the API only maps its OpenAPI endpoint in the Development environment.
SPEC_URL="https://apidocs.prdb.net/openapi/openapi.json"

# Pinned generator version. Bumping this regenerates every SDK, so change it
# deliberately and in its own commit.
KIOTA_VERSION="1.34.1"

# Client class name and repository coordinates, shared by all four languages.
CLIENT_NAME="PrdbClient"
GO_MODULE="github.com/prdb-net/prdb-sdk/go"
