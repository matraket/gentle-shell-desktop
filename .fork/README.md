# Fork-only tooling

This folder, `docs-es/` and `.github/workflows/fork-*` exist only in the fork `matraket/gentle-shell-desktop`. They are never delivered upstream: `export-upstream.sh` removes them from every commit before `docs/corpus` (the head of upstream PR #29) moves.

## Working rules

- Every change to the English corpus (`docs/`, `CONTRIBUTING.md`) changes its Spanish mirror (`docs-es/`) in the same pull request. `odd/` holds process files; they are delivered and not mirrored.
- Pull requests target `docs/integration`, enter by rebase, and need one approval from the other author.
- Commit messages describe the English change and never use a bare `#N` or `GH-N`: upstream they would link to a different issue. Write `owner/repo#N` or a full URL.

## Checks

| Script | What it checks | Runs |
|---|---|---|
| `check-mirror.py` | Each Spanish file has a two-line header (a `> ` note and a blank line), then Spanish line N+2 mirrors English line N: same number of lines, same line kind (blank, heading level, list item, table row with its column count, code fence), identical code-block lines, the same code spans, `Inference:`/`UNVERIFIED:` labels, link count and external URLs; a Spanish link pinned to a commit must point at the file the English relative link points at. With `--changed-since <ref>`, every English line added, changed or deleted since `<ref>` must have its Spanish line changed too. Meaning is not checked; that is the reviewers' job. | CI on every pull request (with `--changed-since` its base); locally with `python3 .fork/check-mirror.py` |
| `check-messages.py` | No bare `#N` or `GH-N` in the commit messages of a range. | CI on every pull request |
| `export-upstream.sh` | Builds the delivery in a temporary clone and checks it: no fork-only path in the tree or in any commit; delivered commits touch only `docs/`, `odd/` and `CONTRIBUTING.md`; no merge commits; the English tree equals `docs/integration`; a fast-forward of `docs/corpus`; author, date and message kept; no bare `#N` or `GH-N`. | By hand, when both authors agree to deliver |

## Delivering upstream

```
.fork/export-upstream.sh          # dry run: prints the checks and the commits to deliver
.fork/export-upstream.sh --push   # pushes to docs/corpus, without force, only if every check passes
```

The rewrite starts at the fork point `dfaf9d5` with `git filter-repo`, so it is deterministic: each delivery extends the previous one, and author, date and message are kept (SHAs quoted in messages are left as they are). The delivered commits get new SHAs, because the first fork-only commits are dropped and every later commit gets a new parent. Run the delivery with the same `git` and `git-filter-repo` versions each time; a mismatch fails safely as "not a fast-forward". Requirements: `git-filter-repo`, `ripgrep`, Python 3.

If `docs/corpus` gets a commit from somewhere else (for example a maintainer edit on PR #29), the delivery stops with "not a fast-forward". Nothing is pushed; the two authors decide by hand how to bring that commit in.
