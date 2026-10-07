# Proposal 0005: per-chat session process design

Feature document (ODD). Repository: `matraket/gentle-shell-desktop`. Base: `docs/integration` (`b6c0eeb`). Branch: `consolidation/proposal-0005`. Locator: `odd/tasks/proposal-0005-session-process.md`. Engram mirror: `odd/proposal-0005-session-process/tasks`. Source: issue #15; PR #30 session-process design.

## Objective

Move the session-process design from PR #30 into a numbered, community-authored proposal 0005, with the original author credited, the actual launcher-plus-pi process count corrected, open decisions #2–#9 preserved, and English/Spanish corpus files updated together.

## Constraints and scope

- In proposal and tracking text, refer to the source only as `PR #30` and with the established `pr30:` citation prefix.
- The runtime chain is one `gentle-shell` launcher plus one pi process per chat (two OS processes); do not imply a single shared pi runtime or count only one OS process.
- Decision issues #2–#9 remain open; present their alternatives without deciding them.
- Proposal 0005 records the PR #30 design; it does not make it current architecture or settle its placement against proposal 0004.
- Follow the existing proposal template and write an English source plus a structurally aligned Spanish mirror. Update both proposal indexes.
- User explicitly authorized this work-unit commit. Do not push or create a PR without separate explicit authorization.
- No behavior changes; no automated test suite applies. Structural verification is required.

## Tasks

| ID | Task | Route | Status | Evidence |
|---|---|---|---|---|
| P1 | Write the English proposal and both index entries, plus the Spanish mirror; preserve attribution and open decisions | delegated `gentle-ai-worker` (multi-file write trigger) | done | Added `docs/07-proposals/0005-session-process-design.md`, its `docs-es/` mirror, and both index rows. Original PR #30 author @memotux credited/signed; two-process correction and issues #2–#9 preserved. |
| P2 | Verify mirror parity, diff hygiene, citations, relative links, and proposal neutrality; record observed results | parent + independent `gentle-ai-verify` (ASSESS unassessable/high due to untracked paths) | done | Writer and independent verifier: `python3 .fork/check-mirror.py --changed-since docs/integration` → 38 pairs, 0 problems; `git diff --check` → exit 0. Relative links, PR #30 citations, attribution, language parity, and neutrality checked. Parent spot-checks issues #2/#4/#7. Native inspect required intended-untracked selection; selecting the two proposal files and this task file returned terminal `action: closed`, `risk_tier: low`, `lenses_required: false` (not delivery authority). |
| P3 | Commit this work unit | parent | done | Commit `82d99cf4ee9b2ee3f01f51f0459246ec9a39c623` (`docs: add proposal 0005 for per-chat session processes`) records the five intended files. No push. |
| P4 | Normalize proposal source references to `PR #30` / `pr30:` only | delegated `gentle-ai-worker` (multi-file correction) | done | English/Spanish proposal source rows and notes now use only PR #30 plus `pr30:` citations. Independent verification and mirror checks passed. Final native start returned low-risk terminal closure with no review lenses required. |
| P5 | Prepare the issue-scoped PR | parent | in progress | PR creation remains unauthorized; wait for explicit user authorization. |

## Acceptance criteria

- `docs/07-proposals/0005-session-process-design.md` is credited to the original PR #30 author and clearly marked `proposed`.
- The proposal preserves the per-chat launcher/pi topology and states the two-OS-process correction.
- It explains its relationship to proposal 0004 without choosing host placement, and links unresolved alternatives to issues #2–#9.
- Both English and Spanish proposal indexes contain a matching proposal row.
- The Spanish mirror satisfies the repository's line-structure, code-span, label, and link constraints.
- Citations use the issue #1 `pr30:` prefix to refer to the PR #30 source.
- No unrelated files are changed; all failed, skipped, or pending checks are reported truthfully.

## Progress

- Planning completed; branch `consolidation/proposal-0005` was created from `docs/integration`.
- P1 and P2 are complete. The verifier caught an inaccurate claim about proposal 0004 citing PR #30 and underspecified alternatives in issues #2, #4 and #7; those were corrected in English/Spanish before final verification. The Spanish README translation-note date was refreshed.
- Verification passed: mirror check 38 pairs / 0 problems; `git diff --check` exit 0; PR #30 citations and relative links checked. No behavior tests apply to this docs-only change.
- Native inspect resolved the intended-untracked selection and returned a terminal low-risk closure with no review lenses required. This is not commit, PR, or delivery authorization.
- P4 completed after the user's citation-convention clarification; proposal and tracking text use only `PR #30` and `pr30:` for this source. Independent verification and a parent grep confirmed no other source identifier in the proposal, indexes, or tracking document; mirror check stayed at 38 pairs / 0 problems and `git diff --check` stayed clean.
- The latest native start returned `state: approved`, `risk_tier: low`, `action: closed`, and `lenses_required: false` for this five-file candidate. No subsequent lifecycle call was made.
- The user authorized the work-unit commit. Commit `82d99cf4ee9b2ee3f01f51f0459246ec9a39c623` was created with message `docs: add proposal 0005 for per-chat session processes`; committed-range ASSESS against `docs/integration` returned passive risk, 5 changed paths, and structural readback only. No push or PR creation authorized.
- P5 is waiting for separate explicit authorization before opening the issue-scoped PR.
