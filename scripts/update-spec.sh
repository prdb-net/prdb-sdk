#!/usr/bin/env bash
# Refresh spec/openapi.json from the published prdb Public API document.
#
# This does not regenerate the SDKs. Run scripts/generate.sh afterwards and
# commit the spec together with the regenerated code, so the checked-in
# clients always correspond to the checked-in spec.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=config.sh
source "$repo_root/scripts/config.sh"

spec_path="$repo_root/spec/openapi.json"
tmp_path="$(mktemp)"
trap 'rm -f "$tmp_path"' EXIT

echo "Fetching $SPEC_URL"
curl -fsS -o "$tmp_path" "$SPEC_URL"

# Fail loudly on an error page served with a 200, or on a truncated download.
if ! jq -e '.openapi and .paths' "$tmp_path" >/dev/null 2>&1; then
    echo "error: downloaded file is not a valid OpenAPI document" >&2
    exit 1
fi

if [[ -f "$spec_path" ]] && cmp -s "$tmp_path" "$spec_path"; then
    echo "Spec unchanged ($(sha256sum "$spec_path" | cut -c1-16))"
    exit 0
fi

mv "$tmp_path" "$spec_path"
trap - EXIT

echo "Spec updated ($(sha256sum "$spec_path" | cut -c1-16))"
echo "Operations: $(jq '[.paths[] | to_entries[] | select(.key | test("^(get|post|put|patch|delete)$"))] | length' "$spec_path")"
echo
echo "Next: scripts/generate.sh"
