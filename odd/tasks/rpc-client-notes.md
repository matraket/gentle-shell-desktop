# Feature: pi client implementer notes in the RPC contract

Feature document (ODD). Repository: `matraket/gentle-shell-desktop`. Base: `docs/integration` (`b6c0eeb`). Branch: `consolidation/rpc-client-notes`. Locator: `odd/tasks/rpc-client-notes.md`. Engram mirror: `odd/rpc-client-notes/tasks`. Source: issue #16; pi client facts of PR #30 (`pr30:docs/pi-rpc-mode.md`).

## Objective

Land the pi client facts of PR #30 in `docs/04-rpc-contract.md` as a section of notes for client implementers, re-checked against pi 1.0.0, together with the three corrections the issue assigns to this page (pi version, `extension_error`, `prompt` disposition) and the inventory C10 correction in `docs/05-capability-inventory.md`, with the Spanish mirror updated in the same commits and without shifting any line other pages cite.

## Constraints and scope

- One branch from `docs/integration` and one pull request into it, opened with the first commit. Both authors may commit to the branch. Pushing the branch and opening the PR need separate explicit authorization.
- New section is inserted at the boundary after English `docs/04-rpc-contract.md:362`, immediately before `## How to propose contract changes upstream` (Spanish counterpart: after `docs-es/04-rpc-contract.md:364`). Other corpus files cite this page at lines `:217`, `:286-299`, `:301` and `:353`; nothing above those lines may move, and `docs/09-roadmap.md` (both languages) plus `docs/assets/mockup-v2/TRACEABILITY.md` must keep resolving.
- `docs/05-capability-inventory.md` C10 (line 180) is corrected in place as a single-line replacement; no new row is added to any of its tables, because `05` is cited up to `:690`.
- The `pr30:` prefix is defined in the citation paragraph at `docs/04-rpc-contract.md:17` on the same line (no line inserted), following the proposal 0005 precedent. `pr30:` is not used in `05`, which cites pi directly.
- Every new claim carries `pr30:docs/pi-rpc-mode.md:<line>` or a full `pi@a13d35a:packages/coding-agent/...` path. No bare `PC` abbreviation outside the section that defines it.
- Facts already in the corpus (§What RPC mode drops, §Events, §Differences between pi 0.85.1 and 0.99.1, inventory C12) are cross-linked, not restated as new; `Inference:` and `UNVERIFIED:` labels keep their existing meaning.
- Spanish mirror: line N+2 mirrors English line N, identical fenced-code lines, same code spans, link count and URLs per line, and every changed English line has a changed Spanish line (`--changed-since`).
- Commit messages in English, conventional commits, no bare `#N` (write `matraket/gentle-shell-desktop#16` or a full URL).
- The main worktree keeps an unrelated uncommitted change to `odd/tasks/proposal-0005-session-process.md`; this work runs in a separate linked worktree and must not touch it.
- Docs-only change: no behavior tests apply. Structural verification and offline re-verification of the pi 1.0.0 citations are required.

## Tasks

| ID | Task | Route | Status | Evidence |
|---|---|---|---|---|
| T1 | Write the client-implementer notes section in `04` (English and Spanish), define `pr30:` on line 17, and commit the work unit | delegated `gentle-ai-worker` (multi-file write trigger); parent commits | pending | — |
| T2 | Land correction 1 (pi version the notes were checked against) and commit | parent | pending | — |
| T3 | Land correction 2 (`extension_error` is documented outside the type unions) and commit | parent | pending | — |
| T4 | Land correction 3 (`prompt` carries `data.disposition`) and commit | parent | pending | — |
| T5 | Correct inventory C10 in `05` (English and Spanish, single line each) and commit | parent | pending | — |
| T6 | Independently verify mirror parity, line stability, citation accuracy and diff hygiene | delegated `gentle-ai-verify` + parent | pending | — |
| T7 | Native review preflight over the candidate and close with evidence | parent | pending | — |

## Acceptance criteria

- `docs/04-rpc-contract.md` carries a section of notes for pi client implementers after line 353's cited region, covering: `RpcClient` limits and its `node <cliPath>` launch, `@file` rejection, `get_commands` and built-in TUI commands, Esc emulation with `clear_queue` + `abort` + restore, `bash` context timing, the extra degraded `ctx.ui` calls, `message_update.usage` staying zero, the missing session header, `rpc-entry`, a new-client checklist and a Python skeleton.
- The three corrections are each one reviewable commit on top of the section commit.
- `docs/05-capability-inventory.md` C10 no longer presents `@file` CLI arguments as usable over RPC, and cites pi 1.0.0.
- English and Spanish change together, and `python3 .fork/check-mirror.py --changed-since docs/integration` reports 0 problems.
- No line cited by another corpus file moved; `git diff --unified=0` shows only insertions below line 353 in `04` and exactly one replaced line in `05`.
- Every new `pi@a13d35a:` line citation was re-verified against the installed pi 1.0.0 package (docs by line, `src/` via `.js.map` `sourcesContent`).
- All failed, skipped or pending checks are reported truthfully.

## Progress

- Planning complete. Branch `consolidation/rpc-client-notes` created from `docs/integration` (`b6c0eeb`) in the linked worktree `/Volumes/tuxevo/gentle-shell-desktop-issue16`; the main worktree's pending issue #15 change is untouched.
- Exploration findings recorded before writing: cited-line ceiling of `04` is `:353`; `05` citations reach `:690`; `pr30:` appears nowhere on `docs/integration` yet; the generic PR skill's `status:approved` label does not exist in this repo, so issue #1's branch/PR convention is the authority.
