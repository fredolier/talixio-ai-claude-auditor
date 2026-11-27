#!/usr/bin/env bash
# Clone (or update) a repository into targets/<name>/ for reading only.
# Usage: scripts/fetch.sh <https-url> [branch-or-commit]
# The token comes from $ASSESSOR_READ_TOKEN (optional for public repositories) and reaches git
# through a credential helper that names the variable, so its value is never in the command
# line, in the clone's .git/config, or in a file.
set -euo pipefail

url="${1:?usage: scripts/fetch.sh <https-url> [branch-or-commit]}"
ref="${2:-}"
[[ "$url" =~ ^https://[^@[:space:]]+$ ]] || { echo "fetch: need an https:// URL with no credentials in it" >&2; exit 2; }

name="$(basename "${url%/}" .git | tr -c 'A-Za-z0-9._\n-' '_')"
dest="$(cd "$(dirname "$0")/.." && pwd)/targets/$name"

export GIT_TERMINAL_PROMPT=0        # fail instead of asking for a password
export GIT_ALLOW_PROTOCOL=https     # no ssh, file or ext transports
export GIT_LFS_SKIP_SMUDGE=1        # no extra downloads
helper='!f() { test "$1" = get && test -n "${ASSESSOR_READ_TOKEN:-}" && printf "username=%s\npassword=%s\n" "${ASSESSOR_READ_USER:-oauth2}" "$ASSESSOR_READ_TOKEN"; }; f'
# The empty helper first clears any configured helper (a keychain would store the token).
g() { git -c credential.helper= -c credential.helper="$helper" -c core.hooksPath=/dev/null "$@"; }

if [[ -d "$dest/.git" ]]; then
  chmod -R u+w "$dest"
  g -C "$dest" fetch --quiet --no-recurse-submodules "$url" '+refs/heads/*:refs/remotes/origin/*'
else
  mkdir -p "$(dirname "$dest")"
  g clone --quiet --no-recurse-submodules "$url" "$dest"
fi
git -C "$dest" remote set-url --push origin no-push://read-only   # a push fails in git itself

if [[ -z "$ref" ]]; then ref="$(git -C "$dest" symbolic-ref --short refs/remotes/origin/HEAD)"
elif git -C "$dest" rev-parse -q --verify "origin/$ref^{commit}" >/dev/null; then ref="origin/$ref"; fi
git -C "$dest" -c core.hooksPath=/dev/null checkout --quiet --force --detach "$ref"
find "$dest" -path "$dest/.git" -prune -o -type f -exec chmod a-w {} +   # working files read-only

echo "target:  targets/$name"
echo "ref:     $ref"
echo "commit:  $(git -C "$dest" rev-parse HEAD)  ($(git -C "$dest" log -1 --format=%as))"
