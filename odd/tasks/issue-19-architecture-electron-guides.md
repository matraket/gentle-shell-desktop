# Issue #19: architecture and Electron guide placement

Feature document (ODD). Repository: `matraket/gentle-shell-desktop`. Branch: `consolidation/architecture-guides`, created from `docs/integration` at `b6c0eeb`. Issue: https://github.com/matraket/gentle-shell-desktop/issues/19.

## Objective

Resolve issue #19's documentation placement question by recording current architecture state in the existing architecture page and folding only source-verified Electron security risks into audit A14. Do not add a standalone generic Electron guide or present its unverified claims as repository facts.

## Decision and constraints

- Human selected: state-ownership table in `docs/03-architecture/current.md`; verified Electron material in existing A14; no standalone guide.
- Human selected: the build alias notes from the incoming document enter the existing *Build and packaging* section of `current.md`.
- Human selected: the "Electron guide not adopted" disposition is recorded in the pull-request body only — no corpus note and no issue comment.
- Correct factual inaccuracies identified by the issue where they occur in the corpus, including renderer isolation vs Chromium sandbox and pi imports in the main process.
- Update every changed English corpus document's Spanish mirror in the same work unit.
- Preserve the project's line-citation, provenance, English/Spanish structural mirror, and fork-only delivery rules.
- Follow issue #19's topic-branch convention from `docs/integration`; do not commit, push, open a PR, or deliver upstream without explicit user authorization.

## Tasks

- [x] R1 Implement the selected bilingual corpus changes in the current architecture page, audit A14, and ADR index.
- [x] R2 Independently verify source claims, cross-references, and Spanish mirror structure.
- [x] R3 Move the issue changes onto a dedicated topic branch based on `docs/integration`.
- [x] R4 Add the path-alias notes and relocate the pi-import correction to the data-paths section.

## Acceptance criteria

- The state-ownership table is in `docs/03-architecture/current.md` and explains current ownership without implying unsupported architecture.
- A14 contains only source-verified Electron risks; no separate generic Electron guide is added.
- Renderer isolation is not mislabeled as sandboxing, and pi's in-process module dependency is accurately represented.
- Every changed English corpus file has its Spanish mirror updated in the same change.
- Fork mirror checks and focused citation/link checks pass; no commit or delivery action is taken without explicit authorization.

## Progress and evidence

- Exploration: issue #19 and parent issue #1 read; source and corpus surfaces mapped. Source confirms `contextIsolation: true` and `sandbox: false` in `src/main/index.ts`; `src/main/adapters/piSessionStore.ts` imports pi in process. Current docs already have architecture, A14, and ADR homes; source for the proposed generic guide is not verified.
- Issue #19's referenced PR #30 documents a state-ownership table, but also inaccurately calls the preload sandboxed and claims the app avoids pi's module graph; those claims were not carried over.
- R1 complete: a delegated writer updated the six bilingual architecture corpus files, added the source-backed table, clarified A14, and corrected ADR wording.
- R2 complete: independent verifier confirmed table ownership and source citations, A14's sandbox distinction, and ADR wording; both mirror checks passed (37 pairs, 0 problems).
- R3 complete: created `consolidation/architecture-guides` from `docs/integration` at `b6c0eeb`; ancestry check passed and the working changes were preserved.
- R4 complete: added a single-line **Path aliases** bullet after **Build.** in both languages (`electron.vite.config.ts:13`, `:21`, `:34-35`; `vitest.config.ts:15-16`), and moved the pi-import sentence out of the state-ownership paragraph into a new intro paragraph under *Data paths to pi*, where a reader asking about pi's module graph now finds it. Independent verifier confirmed the placement, cited lines exactly, Spanish N+2 alignment, and both mirror checks (37 pairs, 0 problems). No file cites `current.md` by line number, so the +15-line shift invalidates nothing.
- Guide disposition: recorded in the PR body only, per the human decision. No corpus note was added; the delivered corpus keeps describing the product, not editorial history.
- Change size: 6 modified files, +36/-6, plus this untracked task document. No source code changed.
- Working changes remain uncommitted; no commit, push, PR, or upstream delivery was authorized or performed.
