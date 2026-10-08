# Issue 17: per-screen authority contracts in screens.md

Feature document (ODD). Repository: `matraket/gentle-shell-desktop`. Base: `docs/integration` (`b6c0eeb`). Branch: `consolidation/screen-contracts`. Engram mirror: `odd/issue-17-screen-contracts/tasks`. Source: issue #17; PR #30 (`pr30:docs/frontend-renderer-design.md:71-109`).

## Objective

Add the per-screen authority contracts of PR #30 to `docs/06-ux/screens.md` (SCR-01…06 Chat, SCR-07 Providers, SCR-08 Extensions, SCR-09 First run), and land the PR #30 theme-token correction in `docs/06-ux/design-system.md`, without shifting any line cited by `docs/assets/mockup-v2/TRACEABILITY.md` or `docs/09-roadmap.md`.

## Constraints and scope

- In proposal and tracking text, refer to the source only as `PR #30` and with the established `pr30:` citation prefix.
- Content placement: one new section after "Open questions" (after `docs/06-ux/screens.md:327`, before "Sources read" at `:329`); the design-system correction after `docs/06-ux/design-system.md:32`. No cited line may shift (`TRACEABILITY.md` cites `screens.md` up to `:317`, `design-system.md:21/:31/:32`; `09-roadmap.md` cites `screens.md:136/:148/:321/:322`).
- Scope agreed in issue #17: contracts for SCR-01…06 (Chat), SCR-07 (Providers), SCR-08 (Extensions), SCR-09 (First run); a closing `Inference:` line notes SCR-10…19 have no PR #30 contract. SCR-01…06 inclusion flagged for @matraket to accept or defer; deferral is structurally free.
- Bullets, not a table, for the new section.
- English and Spanish changes in the same commits; `check-mirror.py` N+2 rule; Conventional Commits without bare `#N`.
- One commit per logical change: contracts, then theme-token correction.
- No behavior changes; no automated test suite applies. Structural verification is required (mirror check, `git diff --check`, citation-shift check, link check).

## Tasks

| ID | Task | Route | Status | Evidence |
|---|---|---|---|---|
| C1 | Write the English authority-contracts section and its Spanish mirror in both screens.md files | delegated `gentle-ai-worker` (multi-file write trigger) | done | Inserted `## Authority contracts per screen` (11 lines) after "Open questions" at `docs/06-ux/screens.md:329-339`; Spanish mirror `docs-es/06-ux/screens.md:331-341`. Contracts for SCR-01…06 (`pr30:...:56-58`), SCR-07 (`:71-75`), SCR-08 (`:89`), SCR-09 (`:107-109`), status note `:7`; closing SCR-10…19 `Inference:` line. |
| C2 | Write the English theme-token correction and its Spanish mirror in both design-system.md files | delegated `gentle-ai-worker` (multi-file write trigger) | done | One-paragraph provenance correction inserted after line 32 (`docs/06-ux/design-system.md:38-39`, ES `:40-41`), citing `pr30:...:11-23` and `corpus@d119d0a:...:17-32`. |
| C3 | Verify mirror parity, diff hygiene, citation shifts, relative links; record observed results | parent + independent `gentle-ai-verify` | done | Independent verifier: mirror check 37 pairs / 0 problems; `git diff --check` exit 0; all hunks pure insertions after the cited positions (EN screens hunk `@@ -328,0 +329,11 @@`, design-system `@@ -37,0 +38,2 @@`; zero deleted lines; 26 insertions, 0 deletions). Every claim checked against `roadmap-memotux:docs/frontend-renderer-design.md` and supported. Verifier finding fixed before commit: SCR-01…06 cite widened `:56` → `:56-58` (EN+ES) because the preload/raw-records claims sit at `:58`. No bare `#N`; no new links. Parent spot-checked the EN/ES insertions and the final mirror run. |
| C4 | Commit each work unit | parent | done | Commit `cc3244a` (`docs: add per-screen authority contracts from the pr30 renderer design`, 2 files, +22) and commit `fe1e5ca` (`docs: correct theme token provenance against the theme file`, 2 files, +4), both on `consolidation/screen-contracts` from base `b6c0eeb`. No bare `#N` in messages. |

## Acceptance criteria

- `docs/06-ux/screens.md` gains the four-screen authority-contract section, `Inference:`-marked where not directly cited, with a closing SCR-10…19 note; every claim cites `pr30:` or is marked.
- `docs/06-ux/design-system.md` gains the token-provenance correction paragraph.
- Spanish mirrors of both files change in the same commits and pass `check-mirror.py`.
- No line cited by `TRACEABILITY.md` or `09-roadmap.md` shifts.
- Commit messages are Conventional, English, without bare `#N`.

## Progress

- Approved proposal recorded (issue #17 discussion; open points resolved per recommendation).
