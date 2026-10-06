#!/usr/bin/env bash
# Build the upstream delivery: docs/integration without the fork-only paths, as a
# fast-forward of docs/corpus (the head of upstream PR #29). Dry run by default;
# --push pushes it to docs/corpus, without force, only when every check passes.
#
# The rewrite starts at a fixed fork point, so it is deterministic: an earlier
# delivery is a prefix of the next one, and author, date and message are kept.
set -euo pipefail

REMOTE=${EXPORT_REMOTE:-https://github.com/matraket/gentle-shell-desktop.git}
INTEGRATION=docs/integration
CORPUS=docs/corpus
FORK_POINT=dfaf9d5c03a9900505c5237be7a6c0f56b76d983
FORK_ONLY=(docs-es/ .fork/)
FORK_ONLY_GLOB='.github/workflows/fork-*'
FORK_ONLY_RE='^(docs-es/|\.fork/|\.github/workflows/fork-)'
# Everything delivered must live here; anything else stops the delivery.
DELIVERED_RE='^(docs/|odd/|CONTRIBUTING\.md$)'

push=false
[ "${1:-}" = "--push" ] && push=true
here=$(cd "$(dirname "$0")" && pwd)
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

git clone --quiet --no-tags --no-checkout "$REMOTE" "$work/repo"
cd "$work/repo"
git fetch --quiet origin "$INTEGRATION:integration" "$CORPUS:corpus"
git branch export integration

paths=()
for p in "${FORK_ONLY[@]}"; do paths+=(--path "$p"); done
paths+=(--path-glob "$FORK_ONLY_GLOB")
# --preserve-commit-hashes keeps SHAs quoted in messages (git revert writes one) unchanged.
git filter-repo --force --quiet --preserve-commit-hashes --refs "$FORK_POINT..export" "${paths[@]}" --invert-paths --prune-empty always
git config core.quotePath false

ok=0
pass() { echo "PASS $1"; }
fail() { echo "FAIL $1"; ok=1; }

[ -z "$(git ls-tree -r --name-only export | rg "$FORK_ONLY_RE" || true)" ] \
  && pass "no fork-only path in the delivered tree" || fail "fork-only paths in the delivered tree"
[ -z "$(git log --format= --name-only corpus..export | rg "$FORK_ONLY_RE" || true)" ] \
  && pass "no fork-only path in any delivered commit" || fail "fork-only paths in delivered commits"
excludes=()
for p in "${FORK_ONLY[@]}"; do excludes+=(":(exclude)$p"); done
excludes+=(":(exclude,glob)$FORK_ONLY_GLOB")
git diff --quiet integration export -- . "${excludes[@]}" \
  && pass "delivered tree equals $INTEGRATION without the fork-only paths" || fail "delivered tree differs from $INTEGRATION"
[ -z "$(git rev-list --merges corpus..export)" ] \
  && pass "no merge commits" || fail "merge commits in the delivery (docs/integration must stay linear)"
[ -z "$(git log --format= --name-only corpus..export | rg -v "$DELIVERED_RE" | rg . || true)" ] \
  && pass "delivered commits touch only docs/, odd/ and CONTRIBUTING.md" || fail "delivered commits touch paths outside docs/, odd/ and CONTRIBUTING.md"
git merge-base --is-ancestor corpus export \
  && pass "fast-forward of $CORPUS" || fail "not a fast-forward of $CORPUS"
bad=0
while read -r old new; do
  [ "$old" = old ] && continue
  [ "$new" = 0000000000000000000000000000000000000000 ] && continue
  [ "$(git log -1 --format='%an|%ae|%ad|%B' "$old")" = "$(git log -1 --format='%an|%ae|%ad|%B' "$new")" ] || bad=1
done < .git/filter-repo/commit-map
[ "$bad" = 0 ] && pass "author, date and message kept on every delivered commit" || fail "authorship changed"
python3 "$here/check-messages.py" corpus..export >/dev/null \
  && pass "no bare #N in delivered commit messages" || fail "bare #N in commit messages (run .fork/check-messages.py)"

echo "--- commits to deliver:"
git log --reverse --format='%h %an | %s' corpus..export
[ -z "$(git log --format=%h corpus..export)" ] && echo "(none)"

if [ "$ok" != 0 ]; then echo "Not delivered: a check failed."; exit 1; fi
if $push; then
  git push origin "export:refs/heads/$CORPUS"
else
  echo "Dry run. Run with --push to update $CORPUS (upstream PR #29)."
fi
