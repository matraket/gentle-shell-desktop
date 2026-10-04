# Host service corpus: one service between every Gentle Shell UI and gentle-shell

Objective: extend the verified desktop corpus with a shared local host service that serves desktop (Electron), web (browser) and a future mobile app, plus a new issue, a draft PR and a concept mockup. Branch: `docs/host-service-corpus`, stacked on `docs/corpus` (PR #29). Delivery: `ask-on-risk`. Test runner: none (documentation; structural checks: line parity EN/ES, relative links and anchors, citation spot checks). Engram mirror: `odd/host-service-corpus/tasks`.

## Specs

- **S1** New corpus reusing the desktop corpus, with its own issue, PR and concept mockup: "generamos un nuevo corpus (aprobechando lo que se pueda del que tenemos), creamos una nueva issue, pr y mockup conceptual." (L1)
- **S2** Research before writing: "debemos previamente invetigar herdr web (obre todo), open-pi-viewer y lo que encontremos." (L1)
- **S3** Stack: "Decidir stack (o podemos plantear distintas opciones de stack)" (L1). Resolved by L3: the corpus proposes one architecture as a **[community]** proposal and records the others as "Alternatives considered and rejected", one reason and its evidence each.
- **S4** One middle layer for every interface: "No se podria hacer algo que sirviera tanto para desktop como para web, o a futuro una app. Para mi eso son solo interfaces. Es decir algo que se pone entre medio de las UI y gentle-shell" (L4).
- **S5** gentle-mesh, analysed on every branch: "Traete todos lo nuevo de gentle-mesh y actualiza el analisis." (L2). It enters the corpus as optional remote execution behind the service, attributed to its author, pending his answers and the maintainer's approval.
- **S6** The branch is stacked on PR #29 ("Vamos con eso", L5).
- **S7** Rigor (standing rule of the desktop corpus): every claim cites a pinned source (`repo@sha:path:line` or a dated URL); `Inference:` and `UNVERIFIED:` labels; nothing invented; English artifacts; Spanish reading copy unversioned.

## Tasks

| ID | Specs | Task | Route | Status | Evidence |
|---|---|---|---|---|---|
| W1 | S2 | Herdr and "herdr web" | delegated researcher | done | `research/W1-herdr.md` (logbook) |
| W2 | S2 | open-pi-viewer and its server | delegated researcher | done | `research/W2-open-pi-viewer.md` |
| W3 | S2 | pi 1.0.0 `pi-server` / `pi-client` / `pi-protocol` | delegated researcher | done | `research/W3-pi-remote.md` |
| W4 | S2 | Landscape of web front ends for pi | delegated researcher | done | `research/W4-landscape.md` (+ errata) |
| W5 | S3 | Synthesis and stack options | parent | done | `research/W5-synthesis.md` |
| W6 | S5 | gentle-mesh on every branch | delegated researcher | done | `research/W6-gentle-mesh.md` (+ parent spot check) |
| W7 | S1, S3, S4, S7 | Verify the host-service premise in the desktop code; reuse map of the desktop corpus; proposed document plan | delegated explorer (mapping trigger: corpus-wide and code-wide evidence) | done | Premise holds with blockers. Parent spot check: `ChatHost.ts:70` single `current`; `useBridge.ts:11-12` `window.gentle ?? mockBridge`; Electron imported only by `src/main/index.ts`, `src/main/ipc/registerHandlers.ts`, `src/preload/index.ts` |
| U1 | S1, S3, S5, S7 | Proposal `07-proposals/0004-host-service.md` with "Alternatives considered and rejected"; index row in `07-proposals/README.md` | delegated writer → independent verifier → one correction → commit | done | Verifier PASS-WITH-FIXES, 15 defects (1 wrong: Rafael's reply missing; attribution of rejections; 4 overstatements; conventions; neutrality on vision Q3); 15/15 applied. Parent fixes: exact quote of Rafael's reply, gentle-mesh post is not "not published" (saved copy: logbook `discord-gentle-mesh-post.md`). Parent spot check: `gentle-mesh@2d1d324:pkg/server/http/server.go:251-253`. Links 0 broken; privacy 0. Commit: see Log |
| U2 | S1, S4, S7 | `11-host-service.md` + ADR README Undecided rows | delegated writer | pending | |
| U3 | S1, S4, S7 | `12-host-protocol.md` | delegated writer | pending | |
| U4 | S1, S4, S5, S7 | `13-clients-and-topologies.md` + `10-platforms` extension | delegated writer | pending | |
| U5 | S1, S7 | Cross-document extensions (vision, glossary, ecosystem, audit, 07 index, 08, 09, screens, README) | delegated writer | pending | |
| U6 | S1, S7 | Research snapshots in `docs/assets/research/` (human consent first) + `assets/README` | delegated writer | pending | |
| U7 | S1 | Spanish mirror of U1–U6 in `docs-es/` (unversioned) | delegated writer | pending | |
| W9 | S1 | Concept mockup (host service clients) | pending | pending | |
| W10 | S1 | Issue and draft PR | parent | pending | |

## Log

- **L1** (2026-10-04, verbatim): "Voy con la opcion (a). Es decir generamos un nuevo corpus (aprobechando lo que se pueda del que tenemos), creamos una nueva issue, pr y mockup conceptual. En este caso si tenemos mucho % del corpus pero por contra debemos previamente invetigar herdr web (obre todo), open-pi-viewer y lo que encontremos. Decidir stack (o podemos plantear distintas opciones de stack), etc- Hay mucho trabajo por delante"
- **L2** (2026-10-04, verbatim): "Traete todos lo nuevo de gentle-mesh y actualiza el analisis."
- **L3** (2026-10-04, verbatim): "Por otro lado, veo que solo S1 tiene sentido. S2, S3 y S4 parece que estan forzadas solo para que haya opciones de decision pero que no tienen mucho sentido." Parent assessment, accepted ("Me sirve"): S2 (Go server) is weak; S3 (T3 Code / pi-web-ui) and S4 (Herdr plugin, the literal "herdr web") were raised in the thread and must be answered, so they go to "Alternatives considered and rejected".
- **L4** (2026-10-04, verbatim): "No se podria hacer algo que sirviera tanto para desktop como para web, o a futuro una app. Para mi eso son solo interfaces. Es decir algo que se pone entre medio de las UI y gentle-shell". Reframes the scope: one local host service (owns sessions, spawns `gentle-shell --mode rpc`, one versioned WebSocket protocol, auth, multiple clients); precedents Paseo and T3 Code (`research/W4-landscape.md:16`, `:86`, `:127`).
- **L5** (2026-10-05, verbatim): "Vamos con eso" — branch stacked on `docs/corpus` (PR #29).
- Context: the maintainer suggested a web version "como herdr web" (Discord, Alan Buscaglia, 2026-09-30 22:34; 2026-10-01 11:17). Questions sent to Rafael The Hutt on the gentle-mesh Discord post (2026-10-04; draft in the logbook, `web/mensaje-rafael.md`). The research reports live in the author's logbook (`~/bitacoras/gs-desktop/web/research/`, not versioned); where they go in the repository is decided in W7.
- Pending human decision for PR #29: add "D. pi's experimental remote-session protocol: considered, not viable at pi 1.0.0" to the host-channel alternatives and the "RPC-only vs mixed" row (`research/W3-pi-remote.md`).
- 2026-10-05: branch created from `docs/corpus@dfaf9d5`; this document moved from the logbook (`web/odd-web-corpus.md`).
- 2026-10-05 W7 result. Premise holds with blockers: only the composition root, IPC handlers and preload import Electron; `ChatHost`/`PiSession` depend on ports and already run under Node in tests; the 8+2 bridge payloads are serializable but carry no chat id. Blockers in order: B1 single session and positional ids (audit A3, gap G9; same work as roadmap F1), B2 global `PI_CODING_AGENT_DIR` mutation (audit A1), B3 no version handshake (A8, G10), B4 no auth or argument validation (A14), B5 activity parser (A5, moves into the service), B6 no `cwd` (A10). Proposed plan, 6 work units: (1) proposal `07-proposals/0004-host-service.md` with "Alternatives considered and rejected"; (2) `11-host-service.md` + ADR Undecided rows; (3) `12-host-protocol.md` (new ID prefix `HP-`); (4) `13-clients-and-topologies.md` + `10-platforms` extension; (5) cross-document extensions (vision Q9 with the maintainer's web suggestion as [maintainer] evidence, glossary, ecosystem, audit, 07 index, 08, 09, screens, README); (6) research snapshots in `docs/assets/research/` (scrub 10 local paths) + `assets/README`. Open: separate process vs embedded in Electron main; F1 before or after extraction; publishing snapshots that quote community members.
- 2026-10-05: Rafael The Hutt answered on the gentle-mesh Discord post (2026-10-04 23:20): he will add an MIT LICENSE "Mñn por la tarde"; he believes RFC-001 had one ("rfc001 si tenia") — `UNVERIFIED:` no LICENSE file exists on any branch as of 2026-10-04 (W6); Alan has not given feedback yet ("no he tenido esa oportinidad"); the other questions are pending ("Respecto al resto mñn lo miro y te respondo"); his goal is "un a2a con verificacion". U1 states his answers as pending until he replies.
- **L6** (2026-10-05, verbatim): "Ok dale" — plan approved (U1–U6), with these defaults: process placement (separate vs embedded) recorded as an open decision with both options; F1 (multi-chat) as a dependency; research-snapshot publication asked at U6.
