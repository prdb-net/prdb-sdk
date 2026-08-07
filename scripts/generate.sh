#!/usr/bin/env bash
# Regenerate all four SDKs from spec/openapi.json.
#
# The generated code is committed to this repository, so consumers can read it
# on GitHub and contributors can build without a generator toolchain. Running
# this script should therefore produce no diff unless the spec or the pinned
# Kiota version changed.
#
# Only the generated/ directories are rewritten. The hand-written wrapper next
# to each of them is never touched.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=config.sh
source "$repo_root/scripts/config.sh"

spec_path="$repo_root/spec/openapi.json"
[[ -f "$spec_path" ]] || { echo "error: $spec_path not found; run scripts/update-spec.sh" >&2; exit 1; }

export PATH="$PATH:$HOME/.dotnet/tools"

if ! command -v kiota >/dev/null 2>&1; then
    echo "Installing Kiota $KIOTA_VERSION"
    dotnet tool install --global Microsoft.OpenApi.Kiota --version "$KIOTA_VERSION"
fi

installed="$(kiota --version 2>/dev/null | tail -1 | cut -d+ -f1)"
if [[ "$installed" != "$KIOTA_VERSION" ]]; then
    echo "error: Kiota $installed is installed but $KIOTA_VERSION is pinned in scripts/config.sh" >&2
    echo "  dotnet tool update --global Microsoft.OpenApi.Kiota --version $KIOTA_VERSION" >&2
    exit 1
fi

generate() {
    local language="$1" namespace="$2" output="$3"
    echo "==> $language"
    kiota generate \
        --language "$language" \
        --openapi "$spec_path" \
        --output "$repo_root/$output" \
        --class-name "$CLIENT_NAME" \
        --namespace-name "$namespace" \
        --exclude-backward-compatible \
        --clean-output \
        --log-level Warning
}

generate python     "prdb_sdk.generated"      "python/src/prdb_sdk/generated"
generate typescript "prdb-sdk"                "typescript/src/generated"
generate go         "$GO_MODULE/generated"    "go/generated"
generate csharp     "Prdb.Sdk.Generated"      "csharp/src/Prdb.Sdk/Generated"

echo
echo "Done. Review the diff, then commit spec/ and the generated/ directories together."
