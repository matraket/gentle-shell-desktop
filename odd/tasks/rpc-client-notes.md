# Feature: pi client implementer notes in the RPC contract

Feature document (ODD). Repository: `matraket/gentle-shell-desktop`. Base: `docs/integration` (`b6c0eeb`). Branch: `consolidation/rpc-client-notes`. Locator: `odd/tasks/rpc-client-notes.md`. Engram mirror: `odd/rpc-client-notes/tasks`. Source: matraket/gentle-shell-desktop#16; pi client facts of PR #30 (`pr30:docs/pi-rpc-mode.md`).

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
| T1 | Write the client-implementer notes section in `04` (English and Spanish), define `pr30:` on line 17, and commit the work unit | delegated `gentle-ai-worker` (multi-file write trigger); parent commits | done | Commit `514a750` (`docs: add notes for pi client implementers to the RPC contract`). Section inserted after `04:362` / `docs-es/04:364`, 74 added lines per language; `pr30:` defined on `04:17` in place. Parent review corrected four `pr30` anchors the writer had off by two to four lines (degraded-`ctx.ui` rows to `:258`, `:260`, `:261`, `:262`; launch bullet to `:46-50`) and tightened `:208-210`. |
| T2 | Land correction 1 (pi version the notes were checked against) and commit | parent | done | Commit `563d206`. Records PR #30 against pi 0.87.1 (`pr30:docs/pi-rpc-mode.md:15-16`), the launcher floor of 0.99.1 (`gentle-shell@ac67159:lib/gentle-shell-launcher.ts:392`, verified as `MIN_PI_VERSION = "0.99.1"` in the installed 4.0.0 package) and gentle-shell 4.0.0 developing against 1.0.0 (`gentle-shell@ac67159:package.json:78`, `:95-97`). |
| T3 | Land correction 2 (`extension_error` is documented outside the type unions) and commit | parent | done | Commit `70082a8`. Four added lines per language. `extension_error` confirmed absent from the shipped `dist/modes/rpc/rpc-types.d.ts`, documented at `pi@a13d35a:packages/coding-agent/docs/json.md:190-194` and emitted at `rpc-mode.ts:348-350` (source map). |
| T4 | Land correction 3 (`prompt` carries `data.disposition`) and commit | parent | done | Commit `c674a6c`. One added line per language in the command caveats; PR #30's example at `:102-105` verified as the pre-0.99.1 response shape. |
| T5 | Correct inventory C10 in `05` (English and Spanish, single line each) and commit | parent | done | Commit `fd532e2`. Exactly one replaced line per language (`05:180`, `docs-es/05:182`). Line 340 of the same page (CLI argument parsing) was inspected and left unchanged: its claim is CLI-level and still true. |
| T6 | Independently verify mirror parity, line stability, citation accuracy and diff hygiene | delegated `gentle-ai-verify` + parent | done | Independent verifier report: `check-mirror.py --changed-since docs/integration` → `37 pairs checked, 0 problems`; `check-messages.py docs/integration..HEAD` → `0 bare references`; `git diff --check` clean; hunks exactly the four in-place replacements (`04:17`, `docs-es/04:19`, `05:180`, `docs-es/05:182`) plus one insertion after `04:362` and one after `docs-es/04:364` and the new task file; all 12 link anchors resolve; every `pr30` anchor and pi 1.0.0 source-map citation matched. Falsification attempts on `get_commands` excluding built-in TUI commands, `ctx.hasUI === true` under RPC, and Spanish register found nothing. Residual: those two behaviours were verified statically from the shipped source, not by running `pi --mode rpc` live, and the Spanish register was checked with a pattern list, not by a native reading. |
| T7 | Native review preflight over the candidate and close with evidence | parent | done | `assess` over `docs/integration..HEAD`: risk `passive`, 5 paths, 216 lines, `reviewDue: false` (`passive`), plan `structuralReadbackOnly` with no separate verifier and no tests. `inspect` then projected exactly those five paths. The offered START route printed a tree hash as `base-ref`, which its own validator rejected (`native-start-base-ref-unresolvable`, `lineage_created: false`, no mutation); re-expressing the same range with the resolvable ref name `docs/integration` closed it: `state: approved`, `risk_tier: low`, `changed_files: 5`, `selected_lenses: []`, `action: closed`, `lenses_required: false`, reason `non_executable_only`. No capture and no acknowledgement ran, so no review authority was burned and the lifecycle ends here. |

## Acceptance criteria

- `docs/04-rpc-contract.md` carries a section of notes for pi client implementers after line 353's cited region, covering: `RpcClient` limits and its `node <cliPath>` launch, `@file` rejection, `get_commands` and built-in TUI commands, Esc emulation with `clear_queue` + `abort` + restore, `bash` context timing, the extra degraded `ctx.ui` calls, `message_update.usage` staying zero, the missing session header, `rpc-entry`, a new-client checklist and a Python skeleton.
- The three corrections are each one reviewable commit on top of the section commit.
- `docs/05-capability-inventory.md` C10 no longer presents `@file` CLI arguments as usable over RPC, and cites pi 1.0.0.
- English and Spanish change together, and `python3 .fork/check-mirror.py --changed-since docs/integration` reports 0 problems.
- No line cited by another corpus file moved; `git diff --unified=0` shows only insertions below line 353 in `04` and exactly one replaced line in `05`.
- Every new `pi@a13d35a:` line citation was re-verified against the installed pi 1.0.0 package (docs by line, `src/` via `.js.map` `sourcesContent`).
- All failed, skipped or pending checks are reported truthfully.

## Progress

- Planning complete. Branch `consolidation/rpc-client-notes` created from `docs/integration` (`b6c0eeb`) in a separate linked worktree; the main worktree's pending matraket/gentle-shell-desktop#15 change is untouched.
- Exploration findings recorded before writing: cited-line ceiling of `04` is `:353`; `05` citations reach `:690`; `pr30:` appears nowhere on `docs/integration` yet; the generic PR skill's `status:approved` label does not exist in this repo, so matraket/gentle-shell-desktop#1's branch/PR convention is the authority.
- T1-T5 are complete as five separate commits: `514a750`, `563d206`, `70082a8`, `c674a6c`, `fd532e2`. Every commit ran `python3 .fork/check-mirror.py --changed-since docs/integration` (37 pairs, 0 problems), `git diff --check` (clean) and a `git diff --unified=0` hunk inspection: one in-place replacement at `04:17` plus one insertion after `04:362` for the section, and single-line replacements at `05:180` for the inventory correction.
- Citation verification: 16 `pr30:docs/pi-rpc-mode.md` anchors and 9 `pi@a13d35a` source citations were re-verified, `src/` lines through the `sourcesContent` of the shipped `.js.map` files. The writer's anchors for the degraded `ctx.ui` table and the launch bullet were wrong and were corrected before the first commit.
- Docs-only change: no behavior tests apply. Independent verification is T6; native review preflight is T7.
- T6 independent verification passed with no findings; the two residual limitations are recorded in the task row.
- T7 closed the candidate natively: passive risk, no lenses required, terminal `action: closed`. The provider-issued START route was internally inconsistent (tree hash offered as `base-ref`), so the same five-path range was started with the ref name `docs/integration` (`b6c0eeb`, tree `7d74378`); the failed attempt created no lineage and mutated nothing.
- Branch state at close: `consolidation/rpc-client-notes` held 7 commits over `docs/integration`; the branch was then pushed to `matraket/gentle-shell-desktop` and opened as PR `matraket/gentle-shell-desktop#21`.
