# Decisions 26 to 28: record the agreed follow-ups in the corpus

Feature document (ODD). Repository: `matraket/gentle-shell-desktop`. Base: `docs/integration`. Commits of this fork are cited by subject, not SHA (rule 9 of matraket/gentle-shell-desktop#1). Branch: `consolidation/decisions-26-28`. Delivery: one pull request, one commit per decision. Locator: `odd/tasks/decisions-26-28.md`. Engram mirror: `odd/decisions-26-28/tasks`. No test runner applies (passive documentation); checks are structural.

## Specs

- **S1. One pull request, one commit per decision.** One pull request against `docs/integration`, with one commit per issue, matraket/gentle-shell-desktop#26, matraket/gentle-shell-desktop#27 and matraket/gentle-shell-desktop#28, closing the three issues. Each commit changes the English page and its Spanish mirror together. These issues carry the new-rule notes of the matraket/gentle-shell-desktop#25 review (`odd/tasks/decisions-2-9.md`, T16).
- **S2. Recorded as agreed, not decided.** Each point is recorded as a **[community]** position agreed by both community authors in its issue, pending the maintainer, next to the decision it completes (#4, #6, #8). Headings and anchors stay unchanged.
- **S3. Lines change in place.** No edit adds or removes a line in a cited page, so no line citation elsewhere in the corpus moves (rule 6).
- **S4. Content is the agreed position.** What each commit records is what the two comments of its issue agree on, with nothing added that the thread does not support:

  | Issue | memoTux | Matrak |
  |---|---|---|
  | #26 | `issuecomment-6251936382` | `issuecomment-6253902610` |
  | #27 | `issuecomment-6252121575` | `issuecomment-6254315659` |
  | #28 | `issuecomment-6252733410` | `issuecomment-6254868904` |

  In #28, how the service learns of a timeout and which side wins when the service timer and pi's timer disagree stay open for the maintainer.
- **S5. Task records.** `odd/tasks/decisions-2-9.md` T16 records the merge of matraket/gentle-shell-desktop#25 and the three issues, in place.
- **S6. Checks.** `python3 .fork/check-mirror.py --changed-since docs/integration` reports 0 problems; `python3 .fork/check-messages.py docs/integration..HEAD` passes; `git diff --check docs/integration` is clean; no U+2013 or U+2014 in added lines; every new citation resolves at its pinned commit; the line count of every changed page is unchanged.
- **S7. Out of scope.** Issue #10 (roadmap shape) waits until this pull request is accepted. No push, pull request or merge without the user's decision.

## Tasks

| ID | Specs | Task | Route | Status | Evidence |
|---|---|---|---|---|---|
| T1 | S1-S4 | Record #26 in `11-host-service.md` (child lifetime) and proposal 0005 (#4 row) | inline | done | `docs: record the agreed idle stop predicate` |
| T2 | S1-S4 | Record #27 in `12-host-protocol.md` (late-event guards) and proposal 0005 (#6 row) | inline | done | `docs: record the agreed launch token and client rev` |
| T3 | S1-S4 | Record #28 in `12-host-protocol.md` (dialog rule) and proposal 0005 (#8 row) | inline | done | `docs: record the agreed dialog trace and timeout display`. New citations checked at their pins: `rpc-extension-ui.md:33` (`undefined` default), `rpc-mode.ts:129` (the request is written after the timer starts at `:115-120`). |
| T4 | S5 | Update T16 of `odd/tasks/decisions-2-9.md` | inline | done | `docs(odd): record decisions 26 to 28` |
| T5 | S6 | Run the checks | inline | done | Mirror 38 pairs, 0 problems; messages 0 bare references; `git diff --check docs/integration` clean; no U+2013 or U+2014 in added lines; line counts of the six changed pages unchanged. |

## Log

- **L1 (2026-10-18).** Assistant: "¿Arranco con el PR que registra el #26, el #27 y el #28 en el corpus?" Matrak decided to record the three issues in one pull request.
- **L2 (2026-10-18).** Route: inline. The edit surface is known from the previous feature (`11-host-service.md:41`, `12-host-protocol.md:156`, `:204`, proposal 0005 rows at `:70`, `:72`, `:74`, Spanish mirror at the same line + 2), so no explorer is needed.
