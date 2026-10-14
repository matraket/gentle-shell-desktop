# Decisions 2 to 9: record the agreed positions in the corpus

Feature document (ODD). Repository: `matraket/gentle-shell-desktop`. Base: `docs/integration`. Commits of this fork are cited by subject, not SHA (rule 9 of matraket/gentle-shell-desktop#1). Branch: `consolidation/decisions-2-9`. Delivery: one pull request, one commit per decision. Locator: `odd/tasks/decisions-2-9.md`. Engram mirror: `odd/decisions-2-9/tasks`. No test runner applies (passive documentation); structural checks below.

## Specs

- **S1. One pull request, one commit per decision.** One pull request against `docs/integration`, with one commit per decision issue in order from matraket/gentle-shell-desktop#2 to matraket/gentle-shell-desktop#9, closing the eight issues. Each commit changes the English page and its Spanish mirror together. Matrak opens the pull request and memoTux reviews it. User: "Ok, vamos con tu recomendación."
- **S2. Recorded as agreed, not decided.** Each decision is recorded as a **[community]** position agreed by both community authors in its issue, pending the maintainer. Alternatives and tradeoffs stay on record; proposals keep their status (`proposed`); section headings and anchors stay unchanged so existing links keep working.
- **S3. Content is the accepted position.** What each commit records is Matrak's published position in the issue, as accepted by memoTux, with nothing added that the thread does not support. memoTux's acceptance on each issue: "Open the PR; I will review it and bring my remaining notes there."

  | Issue | Position comment | Acceptance comment |
  |---|---|---|
  | #2 | (published 2026-10-12) | `issuecomment-6151486338` |
  | #3 | (published 2026-10-12) | `issuecomment-6151505845` |
  | #4 | (published 2026-10-12) | `issuecomment-6151735341` |
  | #5 | `issuecomment-6135359520` | `issuecomment-6151852821` |
  | #6 | `issuecomment-6140470320` | `issuecomment-6151956765` |
  | #7 | `issuecomment-6140596426` | `issuecomment-6152059587` |
  | #8 | `issuecomment-6140653360` | `issuecomment-6152146419` |
  | #9 | `issuecomment-6140725256` | `issuecomment-6152969199` |

- **S4. Items raised in the threads.** Correct pi citations that lack `packages/coding-agent/` where the corpus repeats them (#5, #7). For #9, link the other three points of audit A14 to roadmap QW-05, as memoTux proposed in the acceptance comment.
- **S5. Task records.** `odd/tasks/proposal-0005-session-process.md:13` records that decision issues #2 to #9 remain open; add a dated note pointing to this record, without rewriting the original constraint.
- **S6. Checks.** `python3 .fork/check-mirror.py --changed-since docs/integration` reports 0 problems; `python3 .fork/check-messages.py docs/integration..HEAD` passes; `git diff --check docs/integration` is clean; no U+2013 or U+2014 in added lines; every new citation resolves at its pinned commit.
- **S7. Out of scope.** Issue #10 (roadmap shape) waits until this pull request is accepted. User: "Creo que deberiamos crear los PRs y solo cuando estos esten validados y aceptados entonces trabajar el issue #10 (roadmap) basandonos en el corpus validado y cerrado." No push, pull request or merge without the user's decision.

## Tasks

| ID | Specs | Task | Route | Status | Evidence |
|---|---|---|---|---|---|
| T1 | S1, S6 | This feature document | inline | done | First commit on the branch. |
| T2 | S2, S3 | #2: host service as a separate process (placement (a)) | inline | done | Commit `docs: record the agreed host service placement`: proposals 0005 (line 35, open-decisions table with a new agreed column) and 0004 (design question 1), `11-host-service.md` (summary, at a glance, process placement), ADR index, glossary, platforms; English and Spanish. Headings and anchors unchanged. Mirror check: 38 pairs, 0 problems; `git diff --check` clean. |
| T3 | S2, S3 | #3: inherit by default, adjustable in the service configuration, service secrets scrubbed | inline | done | Commit `docs: record the agreed child environment`: proposal 0005 (R4, agreed column), `11-host-service.md` (child-environment bullet in the config section), `10-platforms.md` (service started without a terminal), proposal 0004 (design question 3), ADR index; English and Spanish. pi and gentle-shell citations checked at `pi@a13d35a` and `gentle-shell@ac67159`. Mirror check: 38 pairs, 0 problems; `git diff --check` clean. |
| T4 | S2, S3 | #4: stop idle children and reopen on demand, with a safe idle rule and a grace period | inline | done | Commit `docs: record the agreed child lifetime`: proposal 0005 (agreed column) and a new "Child lifetime" row in the responsibilities table of `11-host-service.md`; English and Spanish. Mirror check: 38 pairs, 0 problems; `git diff --check` clean. |
| T5 | S2, S3, S4 | #5: one live session shared by every client | inline | done | Commit `docs: record the agreed multi-attachment session`: proposal 0005 (R3, agreed column), HP-03 in `12-host-protocol.md` (prompts from two clients queue), new "Terminal (gentle-shell TUI)" section in `13-clients-and-topologies.md`; English and Spanish. pi citations checked at `pi@a13d35a`. S4: the corpus does not repeat the pi path that lacks `packages/coding-agent/` (search for `pi@<sha>:src/` found none); the wrong path is only in the issue body, to be noted in the pull request. Mirror check: 38 pairs, 0 problems; `git diff --check` clean. |
| T6 | S2, S3 | #6: per-chat `rev` for clients, per-launch token inside the service | inline | done | Commit `docs: record the agreed late-event guards`: proposal 0005 (R2, agreed column) and an agreed paragraph in the reconnect section of `12-host-protocol.md`; English and Spanish. Mirror check: 38 pairs, 0 problems; `git diff --check` clean. |
| T7 | S2, S3, S4 | #7: full snapshots for clients; the service rebuilds by reopening | inline | done | Commit `docs: record the agreed restart catch-up`: proposal 0005 (agreed column; the "still unwritten" note now points to it), an agreed paragraph in the reconnect section and HP-06 of `12-host-protocol.md`, the chat-state bullet of `11-host-service.md`; English and Spanish. memoTux's citations in the acceptance checked: `docs/04-rpc-contract.md:37` (`stdio: "inherit"`), `:74` (stdin close), `:119` (`get_messages`), `:333` (custom entries with `since`); `pi@a13d35a:packages/coding-agent/docs/rpc-commands.md:691` checked. S4: no wrong pi path in the corpus. Mirror check: 38 pairs, 0 problems; `git diff --check` clean. |
| T8 | S2, S3 | #8: first answer wins, shown on every client | inline | done | Commit `docs: record the agreed dialog answers`: proposal 0005 (agreed column), an agreed bullet in the `dialog.answer` section and HP-03 of `12-host-protocol.md`; English and Spanish. `pi@a13d35a:packages/coding-agent/docs/rpc-extension-ui.md:10` (timeout default) checked. Mirror check: 38 pairs, 0 problems; `git diff --check` clean. |
| T9 | S2, S3, S4 | #9: the app window authenticates like any other client | inline | done | Commit `docs: record the agreed window authentication`: proposal 0005 (agreed column, now complete), B4 in `11-host-service.md`, HP-07 in `12-host-protocol.md`, the window authentication bullet in `13-clients-and-topologies.md`, audit A14 and roadmap QW-05 linked both ways; English and Spanish. S4 correction: QW-05 covers the CSP, navigation and argument items of A14 but explicitly not the sandbox (`docs/09-roadmap.md`, QW-05 scope), so the record says the sandbox stays outside QW-05, not that all three remaining items are there. Mirror check: 38 pairs, 0 problems; `git diff --check` clean. |
| T10 | S5 | Note in the proposal 0005 task record | inline | done | Commit `docs(odd): point the proposal 0005 record to the agreed decisions`: a dated sub-item under the original constraint, which is left as written. |
| T11 | S6 | Branch-wide checks | inline | done | Against `docs/integration`: mirror check 38 pairs, 0 problems; message check 0 bare references; `git diff --check` clean; 106 relative links on added lines resolve to an existing file and heading (scratch link checker); review assessment `passive`, no review due. Added lines carry no new U+2013 or U+2014; the only two hits are the existing dash in the range B1 to B6 of the summary paragraph of `11-host-service.md` and its mirror, left for the deferred dash cleanup. |
| T12 | S1 | Push and open the pull request | parent, after the user's decision | pending | |

Route evidence: no Writer trigger fires (one sequential series of commits that share files such as proposal 0005, so no disjoint parallel units). The parent writes inline.

## Log

- **L1 (2026-10-14).** User: "Dale, arranca el PR".
- **L2 (2026-10-14).** A read-only map of where each decision lands found that every decision touches the open-decisions table of proposal 0005 (`docs/07-proposals/0005-session-process-design.md:68-75`), and that several pairs share passages (HP-03 for #5 and #8; `docs/12-host-protocol.md:185-201` for #6 and #7; `docs/11-host-service.md:199-208` for #3 and #4). Separate pull requests merged by rebase would conflict with each other, hence S1. The corpus reserves decisions to the maintainer (`docs/07-proposals/README.md:23`; `docs/03-architecture/adr/README.md:5`), hence S2.
