#!/usr/bin/env bash
# Check that the four packages all carry the same version, and that it matches
# the one passed in (the release tag, without its leading "v").
#
#   scripts/check-version.sh          # just check the manifests agree
#   scripts/check-version.sh 0.1.0    # and that they say 0.1.0
#
# Go is not listed: it takes its version from the git tag rather than a
# manifest, and its tag carries the module subdirectory as a prefix
# (go/v0.1.0), because the module does not live at the repository root.
#
# Prdb.Hashing is not listed either, and that is deliberate rather than an
# oversight. It is not generated from the OpenAPI document and does not change
# when the API does, so it carries its own version and releases from its own
# tag (hashing/v0.1.0). Adding it here would force a version bump on a package
# that nothing changed in.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
expected="${1:-}"

pyproject="$repo_root/python/pyproject.toml"
package_json="$repo_root/typescript/package.json"
package_lock="$repo_root/typescript/package-lock.json"
csproj="$repo_root/csharp/src/Prdb.Sdk/Prdb.Sdk.csproj"

# Only the [project] version, not a dependency pin that happens to precede it.
python_version="$(sed -n '/^\[project\]/,/^\[/p' "$pyproject" \
    | sed -n 's/^version[[:space:]]*=[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)"
typescript_version="$(jq -r '.version' "$package_json")"
# npm only rewrites this on the next install, so a bump leaves it behind.
lock_version="$(jq -r '.version' "$package_lock")"
csharp_version="$(sed -n 's|.*<Version>\([^<]*\)</Version>.*|\1|p' "$csproj" | head -1)"

status=0

report() {
    local name="$1" value="$2" file="$3"
    if [[ -z "$value" ]]; then
        echo "error: no version found in $file" >&2
        status=1
        return
    fi
    printf '%-12s %-10s %s\n' "$name" "$value" "$file"
}

report "python"     "$python_version"     "python/pyproject.toml"
report "typescript" "$typescript_version" "typescript/package.json"
report "lockfile"   "$lock_version"       "typescript/package-lock.json"
report "csharp"     "$csharp_version"     "csharp/src/Prdb.Sdk/Prdb.Sdk.csproj"

[[ $status -eq 0 ]] || exit 1

if [[ "$typescript_version" != "$lock_version" ]]; then
    echo >&2
    echo "error: package-lock.json is still at $lock_version; run npm install in typescript/" >&2
    exit 1
fi

if [[ "$python_version" != "$typescript_version" || "$python_version" != "$csharp_version" ]]; then
    echo >&2
    echo "error: the packages disagree on the version; they are released together" >&2
    exit 1
fi

if [[ -n "$expected" && "$python_version" != "$expected" ]]; then
    echo >&2
    echo "error: the tag says $expected but the manifests say $python_version" >&2
    echo "  bump the three manifests and CHANGELOG.md, then move the tag" >&2
    exit 1
fi

echo
if [[ -n "$expected" ]]; then
    echo "All four packages are at $expected."
else
    echo "All four packages are at $python_version."
fi
