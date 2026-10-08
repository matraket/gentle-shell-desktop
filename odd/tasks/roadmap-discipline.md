# Roadmap discipline in `docs/09-roadmap.md`

## Goal
Carry the approved roadmap-discipline proposal for issue #18 into the English roadmap and its Spanish mirror, preserving the current roadmap shape.

## Problem and rationale
`docs/09-roadmap.md` already proposes milestones, dependencies, a critical path, and exit criteria, but its sequencing principles, debt ownership, structural invariants/change protocol, and recurring release qualification are not explicit. Issue #18 asks to add those disciplines while leaving the roadmap shape (issue #10) unchanged.

## Scope
- Add explicit sequencing principles grounded in the existing roadmap's gates and partial dependencies.
- Add a debt register that maps documented limitations to a milestone or explicit deferral, with closure evidence and source links; do not duplicate audit prose.
- Add proposed invariants and a change protocol, preserving community-proposal status and maintainer authority.
- Add a recurring release gate as a release-time qualification checklist, distinct from milestones and conditional on supported platforms.
- Correct inherited M0/M7 and pi real-child smoke version errors where relevant; use the launcher minimum pi 0.99.1+.
- Add memoTux/@memotux co-author credit in the roadmap header. The commit uses configured memoTux identity; omit a redundant self `Co-authored-by` trailer per the user's selection.
- Update `docs-es/09-roadmap.md` in the same work unit, preserving the repository's mirror convention.

## Constraints
- Do not rename/reorder existing milestones or silently resolve issue #10.
- Do not import a source roadmap's sequencing as an accepted decision where it conflicts with the target. In particular, surface the stable-message-ID-before-concurrency mismatch rather than silently changing F1.
- Distinguish evidence, inference, community proposal, maintainer decisions, full versus partial paydown, and supported versus unqualified platforms.
- No new product claims, release platform commitments, dates, or effort estimates without cited evidence.
- The user explicitly authorized the work-unit commit and branch push to `roadmap` (matraket/gentle-shell-desktop), and selected `Closes #18` for the PR draft. Use the configured Git identity; do not add a self co-author trailer. Do not open a PR or merge.

## Tasks
- [x] **T1 — Integrate approved discipline in both roadmaps.** Added the approved material and corrections to `docs/09-roadmap.md` and `docs-es/09-roadmap.md` as one bilingual work unit. Route: delegated writer (2 non-trivial files); parent reconciled the final diff.
- [x] **T2 — Verify and record evidence.** Independent verifier and parent checked mirror structure, Markdown, citations, and diff. Route: delegated verifier after native assessment failed validation.
- [ ] **T3 — Close the work unit with a commit.** Commit under the configured memoTux identity; no redundant self co-author trailer.
- [ ] **T4 — Push and draft PR metadata.** Push to `roadmap` is authorized; PR draft should use `Closes #18`. Obtain explicit current Git credential/session authorization before push; do not open the PR.

## Acceptance criteria
- English roadmap states reusable sequencing principles and links their rationale to current gates/dependencies without changing roadmap shape.
- Each roadmap-relevant limitation is assigned to a paying milestone or explicitly deferred/gated, with enough evidence to judge completion.
- Invariants are explicit proposed constraints; the change protocol names triggers, impact review, authority, and synchronized updates.
- The recurring gate applies to every release, states evidence and failure handling, and does not assume unsupported platforms or CI capabilities.
- No nonexistent M7 dependency or erroneous 0.87.1 real-child smoke claim is carried over; pi minimum is corrected to 0.99.1+.
- English and Spanish changes are structurally mirror-compatible and keep authorship visible.

## Checks
- Run `.fork/check-mirror.py` with the available supported Python interpreter.
- Run the repository's Markdown/link or docs validation applicable to these files, if available.
- Run `git diff --check` and inspect the final changed-file/stat summary.
- No application behavior changed; tests/build are not applicable unless the repository's docs validation requires them.

## Progress and evidence
- Branch: `consolidation/roadmap-discipline` (created from clean `docs/integration`).
- T1: complete. English and Spanish roadmaps now contain sequencing principles, the concise debt crosswalk, proposed invariants and change protocol, and the recurring release gate; corrections and attribution are included.
- T2: complete. `python3 .fork/check-mirror.py`: 37 pairs checked, 0 problems. `git diff --check -- docs/09-roadmap.md docs-es/09-roadmap.md`: exit 0. Independent verifier verdict: PASS; no high/blocking findings. Parent read the final diff and confirmed only the two roadmaps plus this task record are changed/untracked.
- Failed/unavailable check: native ASSESS returned a controller validation error rejecting inspect-only `intendedUntracked` input. The change was therefore independently verified under the fail-closed high-risk route. No native review was started because the user explicitly said no review was needed.
- Commit: explicitly authorized by the user; local identity is `memoTux <romeo@mendezfuentes.net>`. User selected omitting a redundant self `Co-authored-by` trailer; the document header retains @memotux credit.
- Push: authorized to remote `roadmap` (`matraket/gentle-shell-desktop`); PR draft uses `Closes #18`. Await direct authorization to use the configured Git credential/session for the push. PR creation and merge are not authorized.
- Next: create the local work-unit commit, then confirm Git credential/session authorization and push; provide a draft PR title and description without opening it.
