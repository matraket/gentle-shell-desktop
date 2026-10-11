# Issue matraket/gentle-shell-desktop#19: architecture and Electron guide placement

Feature document (ODD). Repository: `matraket/gentle-shell-desktop`. Branch: `consolidation/architecture-guides`, created from `docs/integration` at `b6c0eeb`. Issue: https://github.com/matraket/gentle-shell-desktop/issues/19.

## Objective

Resolve matraket/gentle-shell-desktop#19's documentation placement question by recording current architecture state in the existing architecture page and folding only source-verified Electron security risks into audit A14. Do not add a standalone generic Electron guide or present its unverified claims as repository facts.

## Decision and constraints

- Human selected: state-ownership table in `docs/03-architecture/current.md`; verified Electron material in existing A14; no standalone guide.
- Human selected: the build alias notes from the incoming document enter the existing *Build and packaging* section of `current.md`.
- Human selected: the "Electron guide not adopted" disposition is recorded in the pull-request body only — no corpus note and no issue comment.
- Correct factual inaccuracies identified by the issue where they occur in the corpus, including renderer isolation vs Chromium sandbox and pi imports in the main process.
- Update every changed English corpus document's Spanish mirror in the same work unit.
- Preserve the project's line-citation, provenance, English/Spanish structural mirror, and fork-only delivery rules.
- Follow matraket/gentle-shell-desktop#19's topic-branch convention from `docs/integration`; do not push, open another PR, post review replies, or merge without explicit user authorization.
- Local work-unit commits are authorized for this round; GitHub PR-body edits and delivery remain separate actions.

## Tasks

- [x] R1 Implement the selected bilingual corpus changes in the current architecture page, audit A14, and ADR index.
- [x] R2 Independently verify source claims, cross-references, and Spanish mirror structure.
- [x] R3 Move the issue changes onto a dedicated topic branch based on `docs/integration`.
- [x] R4 Add the path-alias notes and relocate the pi-import correction to the data-paths section.

## matraket/gentle-shell-desktop#24 owner-review response

- [x] R5 Add the required dated Electron-source corrections in both language editions, cite `ChatsContainer` for the selection-intent claim, and correct the feature record's stale delivery status. **Done** — commit `8718662`; mirror check: 37 pairs / 0 problems; `git diff --check` clean.
- [x] R6 Apply the remaining optional notes (alias citations, local chats/error ownership, Spanish terminology, and qualified issue references), verify mirror/citation/diff hygiene, and record work-unit commit evidence. **Done** — commit `028b29b`; mirror check: 37 pairs / 0 problems; `git diff --check` clean.

## Acceptance criteria

- The state-ownership table is in `docs/03-architecture/current.md` and explains current ownership without implying unsupported architecture.
- A14 contains only source-verified Electron risks; no separate generic Electron guide is added.
- Renderer isolation is not mislabeled as sandboxing, and pi's in-process module dependency is accurately represented.
- Every changed English corpus file has its Spanish mirror updated in the same change.
- Fork mirror checks and focused citation/link checks pass; no commit or delivery action is taken without explicit authorization.

## Progress and evidence

- Exploration: matraket/gentle-shell-desktop#19 and its parent matraket/gentle-shell-desktop#1 read; source and corpus surfaces mapped. Source confirms `contextIsolation: true` and `sandbox: false` in `src/main/index.ts`; `src/main/adapters/piSessionStore.ts` imports pi in process. Current docs already have architecture, A14, and ADR homes; source for the proposed generic guide is not verified.
- matraket/gentle-shell-desktop#19's referenced PR #30 documents a state-ownership table, but also inaccurately calls the preload sandboxed and claims the app avoids pi's module graph; those claims were not carried over.
- R1 complete: a delegated writer updated the six bilingual architecture corpus files, added the source-backed table, clarified A14, and corrected ADR wording.
- R2 complete: independent verifier confirmed table ownership and source citations, A14's sandbox distinction, and ADR wording; both mirror checks passed (37 pairs, 0 problems).
- R3 complete: created `consolidation/architecture-guides` from `docs/integration` at `b6c0eeb`; ancestry check passed and the working changes were preserved.
- R4 complete: added a single-line **Path aliases** bullet after **Build.** in both languages (`electron.vite.config.ts:13`, `:21`, `:34-35`; `vitest.config.ts:15-16`), and moved the pi-import sentence out of the state-ownership paragraph into a new intro paragraph under *Data paths to pi*, where a reader asking about pi's module graph now finds it. Independent verifier confirmed the placement, cited lines exactly, Spanish N+2 alignment, and both mirror checks (37 pairs, 0 problems). No file cites `current.md` by line number, so the +15-line shift invalidates nothing.
- Guide disposition: recorded in the PR body only, per the human decision. No corpus note was added; the delivered corpus keeps describing the product, not editorial history.
- Original change size: six corpus files, +36/-6; no source code changed. The original corpus and task-record commits are `bf4cf1f` and `8100d7a`.
- Original implementation is in [matraket/gentle-shell-desktop#24](https://github.com/matraket/gentle-shell-desktop/pull/24). The PR body and review thread remain unchanged.

## Owner optional-notes round (head `eccb5fca`)

### Constraints and scope

- Trigger: the repository owner's optional notes on the approved review at `eccb5fca`; addressed because the author took time to write them.
- `odd/` travels upstream: this record must carry no fork process history (prior review ids, push authorizations, PR-description notes) and no bare fork issue/PR numbers; references stay fully qualified as `matraket/gentle-shell-desktop#N`.
- Post-rebase commit hashes must be named: the branch was rebased on GitHub, every commit hash changed, and the pre-rebase hashes no longer resolve on the hosted branch.
- English and Spanish change together: the Spanish A14 sandbox wording mirrors the unchanged English original in the same work unit.
- Docs-only round with structural verification: mirror check, `git diff --check`, `git diff --stat`, `git status --short`, and a targeted stale-reference grep. No functional tests apply.

### Tasks

| ID | Task | Route | Status | Evidence |
|---|---|---|---|---|
| T1 | Trim fork process history and qualify the owner-review heading | `gentle-ai-worker` | done | Heading now reads `## matraket/gentle-shell-desktop#24 owner-review response`; the review-id sentence and the push-authorization clause are gone. Targeted stale-reference grep returned zero matches. |
| T2 | Remove the duplicated R5/R6 "complete" bullets | `gentle-ai-worker` | done | Both duplicated evidence bullets deleted; the R5/R6 checkboxes remain separated from `## Acceptance criteria` by exactly one blank line. |
| T3 | Remove the PR-description line | `gentle-ai-worker` | done | The PR-description authorization line no longer appears anywhere in this record. |
| T4 | Refresh post-rebase hashes in the checkboxes and the provenance bullet | `gentle-ai-worker` | done | R5 now cites `8718662`, R6 now cites `028b29b`, and the original corpus/task-record commits read `bf4cf1f` and `8100d7a`. |
| T5 | Spanish A14 wording mirror | `gentle-ai-worker` | done | `docs-es/03-architecture/audit.md` A14 now reads `separado del aislamiento de contexto`; the English original stays unchanged. |
| T6 | Record this work unit | parent | pending | The commit hash is recorded in the PR body Process section and the Engram mirror after the push — a commit hash cannot be recorded inside its own commit. |

### Progress

- Observed verification output from this worktree (the stale-reference grep is shown without its pattern, because the pattern itself consists of the retired strings this round removed):

```
$ python3 .fork/check-mirror.py
38 pairs checked, 0 problems
$ git diff --check
(no output; exit 0)
$ git status --short
 M docs-es/03-architecture/audit.md
 M odd/tasks/issue-19-architecture-electron-guides.md
$ grep -nE '<stale references>' odd/tasks/issue-19-architecture-electron-guides.md
(no matches; exit 1)
```
