# 0004. Shared local host service

> Status: proposed.

| Field | Value |
|---|---|
| Author | Matrak (community) |
| Source | Conversation with Matrak, 2026-10-04 (not published): "No se podria hacer algo que sirviera tanto para desktop como para web, o a futuro una app. Para mi eso son solo interfaces. Es decir algo que se pone entre medio de las UI y gentle-shell" (could we not build something that serves desktop, web and, later, an app? To me those are only interfaces: something that sits between the UIs and gentle-shell) |
| Trigger | **[maintainer]** "fijense si no conviene una version web y listo tambien" (check whether just a web version wouldn't be better, too; Discord, Alan Buscaglia, 2026-09-30 22:34), then "como herdr web" (like herdr web; Discord, Alan Buscaglia, 2026-10-01 11:17) |
| Status | `proposed` (only the maintainer moves it to `accepted` or `declined`) |
| Principles | vision P1 **[maintainer]**, **[community]** (every client keeps gentle-shell's helpers, ODD and dialogs, because the RPC contract is unchanged); vision P5 **[maintainer]** (mockup intent), **[gentle-shell]** (several chats at once, "needs you" across clients, through B1); must respect vision P4 **[maintainer]** (the registry keeps helpers per chat) |
| Related | [vision Q3 and Q9](../00-vision.md#open-questions-for-the-maintainer) **[open question]**; [roadmap F1](../09-roadmap.md#f1-foundations-several-chats-at-once-community-proposal) **[community]** |

## Problem

Every chat session is owned by Electron's main process, so no other kind of client can use it:

- The composition root builds the one `ChatHost` and its adapters inside Electron (`gentle-shell-desktop@5ab4a00:src/main/index.ts:60-67`).
- The renderer reaches it only through the preload bridge over Electron IPC (`gentle-shell-desktop@5ab4a00:src/preload/index.ts:4`; `gentle-shell-desktop@5ab4a00:src/main/ipc/registerHandlers.ts:27-40`).
- In a plain browser (`pnpm dev:web`, `gentle-shell-desktop@5ab4a00:package.json:12`) the renderer falls back to an in-memory mock (`gentle-shell-desktop@5ab4a00:src/renderer/shared/bridge/useBridge.ts:4-11`).

The maintainer then asked whether a web version would be better (Trigger above). The vision keeps a remote or mobile client as an open question ([vision Q9](../00-vision.md#open-questions-for-the-maintainer)). `Inference:` a web or mobile app written next to the desktop would have to own sessions again, in a second place.

## Proposal

**[community]** One local **host service** sits between every Gentle Shell UI and `gentle-shell --mode rpc`:

```text
Electron window ──┐
Browser tab ──────┼── WebSocket, one versioned protocol ──► host service ──► gentle-shell --mode rpc children ──► pi
Mobile app ───────┘                                         (session registry)    (proposed: one per chat, pending vision Q3)
```

| Responsibility | What the service does |
|---|---|
| Sessions | Owns the session registry: which chats are open, their state, their children. |
| Runtime | Spawns `gentle-shell --mode rpc` children. The proposed shape is one child per chat, pending vision Q3 (see [Open questions](#open-questions)). The contract with gentle-shell does not change ([RPC contract](../04-rpc-contract.md)). |
| Clients | Exposes one versioned protocol over WebSocket to many clients at once. |
| Access | Binds to loopback by default. Any other bind requires a token or device pairing, and every connection checks `Origin`. |

Electron, the browser and a future mobile app become clients of the same service. One child per chat is the shape audit A3 recommends ([audit A3](../03-architecture/audit.md#a3-single-session-host-with-positional-message-ids), recommendation 1) and gap G9 allows ([gap G9](../04-rpc-contract.md#gaps-the-desktop-needs)); it is a proposal, not a decision.

## Why it fits the current code

| Fact | Evidence (`gentle-shell-desktop@5ab4a00`) |
|---|---|
| Electron is imported by 3 source files only: the composition root and the preload at runtime, and the IPC handlers as types only. `registerHandlers.ts` says it "never executes `require("electron")` at module load time". The only other hit is a type import in a test. | `src/main/index.ts:2`; `src/preload/index.ts:1`; `src/main/ipc/registerHandlers.ts:1`, `:11-13`; `src/main/ipc/registerHandlers.test.ts:2` (`git grep` for `electron` imports over `src/`) |
| `ChatHost` and `PiSession` depend on ports, "so the domain never imports Electron/Node APIs directly". Their tests run in Vitest's `node` environment. | `src/main/domain/session/ChatHost.ts:4`; `src/main/domain/session/PiSession.ts:6`; `src/main/ports/index.ts:3-5`; `vitest.config.ts:5-6`, `:21`; `src/main/domain/session/ChatHost.test.ts:3-4` |
| The bridge is 8 request methods and 2 push subscriptions, mirrored by 8 + 2 IPC channels. The IPC handlers are a "thin pass-through to ChatHost". | `src/shared/bridge-types.ts:273-295`; `src/shared/ipc-channels.ts:8-23`; `src/main/ipc/registerHandlers.ts:8-9`, `:28-40` |
| The bridge carries no chat id: `sendMessage` acts on "whichever chat is currently open". | `src/shared/bridge-types.ts:279-282` |
| The renderer picks its bridge in one place: `window.gentle ?? mockBridge`. | `src/renderer/shared/bridge/useBridge.ts:11` |

`Inference:` (read, not prototyped) the service can be extracted rather than written: move `ChatHost`, `PiSession` and their adapters behind a WebSocket server, and add a third `GentleBridge` implementation that speaks WebSocket, selected at the same point as the preload and mock bridges. The payload types are plain data that already cross a process boundary, so they can travel as JSON; this was not checked field by field.

## Runtime requirements

What must change first, in this order. B1 is the same work as [roadmap F1](../09-roadmap.md#f1-foundations-several-chats-at-once-community-proposal).

| # | Change | Why the service needs it | Evidence |
|---|---|---|---|
| B1 | A session registry keyed by chat; a chat id on every push and command; message ids taken from pi | Many clients and chats share one service. Today there is one `current` session and ids are positional. | `gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts:70`; [audit A3](../03-architecture/audit.md#a3-single-session-host-with-positional-message-ids); [gap G9](../04-rpc-contract.md#gaps-the-desktop-needs) |
| B2 | List sessions without mutating `PI_CODING_AGENT_DIR` | The listing saves, sets and restores a process-wide variable; the audit notes that several chats at once "would make this race routine". | `gentle-shell-desktop@5ab4a00:src/main/adapters/piSessionStore.ts:32-39`; [audit A1](../03-architecture/audit.md#a1-two-data-paths-to-pi-and-a-global-pi_coding_agent_dir-mutation) |
| B3 | A version handshake: the service reads the gentle-shell and pi versions, and the host protocol carries its own version | Clients and the service may be updated separately. The RPC protocol has no version field, and the desktop's only version text is an error message. | `gentle-shell-desktop@5ab4a00:src/main/adapters/launcherLocator.ts:26-28`; [audit A8](../03-architecture/audit.md#a8-no-version-handshake); [gap G10](../04-rpc-contract.md#gaps-the-desktop-needs) |
| B4 | Authentication and argument validation | IPC handlers use the renderer's arguments as-is. `Inference:` a socket can be reached by any local process, and by the network when not on loopback, so the service cannot trust its callers the way main trusts its own window. | `gentle-shell-desktop@5ab4a00:src/main/ipc/registerHandlers.ts:28-37`; [audit A14](../03-architecture/audit.md#a14-preload-and-ipc-hardening) |
| B5 | Fix the activity parser; it moves into the service with the domain | The desktop's helper status set does not match gentle-shell's. Fixed once in the service, it is fixed for every client. | `gentle-shell-desktop@5ab4a00:src/main/domain/rpc/helpersActivity.ts:21`; [audit A5](../03-architecture/audit.md#a5-helper-status-set-and-tool-items-do-not-match-gentle-shell) |
| B6 | A `cwd` per chat | `PiSession` supports `cwd`, but `ChatHost` never passes one, so chats inherit the host process's directory. `Inference:` a service started in the background has no meaningful working directory of its own. | `gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:15`, `:135`; `gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts:159-166`; [audit A10](../03-architecture/audit.md#a10-new-chats-run-in-the-apps-working-directory) |

## Prior art in the ecosystem

Two projects already put one local server between several clients and `pi --mode rpc`.

| Project | Shape | How it reaches pi | Default bind | License |
|---|---|---|---|---|
| **Paseo** (`getpaseo/paseo`) | "a local server called the daemon that manages your coding agents" (`paseo@485221b:README.md:60`), with a "WebSocket API" (`paseo@485221b:README.md:172`); clients are an Expo app for iOS, Android and web (`paseo@485221b:README.md:173`) and Electron (`paseo@485221b:README.md:175`) | Launches pi with `--mode rpc` unless told otherwise (`paseo@485221b:packages/server/src/server/agent/providers/pi/runtime.ts:92`, `:123`); the command defaults to `pi` (`paseo@485221b:packages/server/src/server/agent/providers/pi/cli-runtime.ts:30`) | `127.0.0.1:6767` (`paseo@485221b:packages/server/src/server/config.ts:470`, `:480`) | Apache-2.0 (`paseo@485221b:LICENSE:7-8`) |
| **T3 Code** (`pingdotgg/t3code`) | A server with a mobile app, a web app and an Electron desktop app (`t3code@eac52f0:README.md:3`); `t3` starts the server and opens the local web app (`t3code@eac52f0:README.md:37`) | Its Pi provider "Spawns `pi --mode rpc`" over stdio JSONL (`t3code@eac52f0:apps/server/src/orchestration-v2/Adapters/PiRpc.ts:1-8`); the command is the configured `binaryPath` or `pi` (`t3code@eac52f0:apps/server/src/orchestration-v2/Adapters/PiAdapterV2.ts:422-427`) | `127.0.0.1` (`t3code@eac52f0:apps/server/src/server.ts:249`) | MIT (`t3code@eac52f0:LICENSE:1-3`) |

T3 Code's Pi provider is in nightly builds only: the nightly tag `v0.0.46-nightly.20261004.2644` contains `PiDriver.ts` and `PiRpc.ts`, and the latest stable release, `v0.0.45` (2026-10-02), contains neither (GitHub API, accessed 2026-10-05).

## Optional remote execution: gentle-mesh

**[community]** gentle-mesh is Rafael The Hutt's protocol proposal (`Rafaeldelinares/gentle-mesh`). He described his vision as "aplicacion multiplataforma no dependiente. ya sea pc o movil." (a multiplatform, independent app, PC or mobile) with "posibilidad de acceso a agentes remotos en entornos vpn" (access to remote agents over VPN) (Discord, Rafael The Hutt, 2026-09-27 23:33). In this proposal it is optional: a way for the host service to run a chat on another machine, behind the same session registry.

**What it offers today, as ideas:**

- **The thin-client idea.** Its mobile proposal argues that mobile operating systems "no permiten gestionar subprocesos locales arbitrarios de Node" (do not allow arbitrary local Node subprocesses) and proposes a front end that switches between a local mode and a "Modo Red / Mesh" over HTTP REST and SSE to a remote server (`gentle-mesh@2d1d324:propuesta-discord-mobile.txt:12`, `:18-23`).
- **Signed receipts, as a UI idea.** A `SettlementReceipt` carries a verdict (`SETTLED_CLEAN` … `SETTLEMENT_TIMEOUT`), the executor's Ed25519 signature, the emitter's countersignature and a link to the previous receipt (`gentle-mesh@f52335e:pkg/receipt/types.go:25`, `:64`, `:71`, `:88`, `:222-230`). `Inference:` a client could show it as a "verified, not just claimed" card; it complements [0003](0003-post-hoc-audit-by-questions.md), which asks a finished helper why.

**What it lacks today** (the code cited below is identical on `2d1d324` and `f52335e`: `git diff` over `cmd/gentle-mesh`, `pkg/server/runner`, `pkg/server/worker`, `pkg/client/bridge.go` and `pkg/server/http/middleware.go` is empty):

- **Worker nodes run a simulated runner.** `gentle-mesh worker` builds its server without a runner (`gentle-mesh@2d1d324:cmd/gentle-mesh/main.go:568-571`), and the worker then falls back to `NewSimulatedRunner` (`gentle-mesh@2d1d324:pkg/server/worker/server.go:40-41`).
- **The coordinator runs pi one-shot per task (`--print --mode json`).** `server -runner pi` builds a `PiRunner` with only a workspace root (`gentle-mesh@2d1d324:cmd/gentle-mesh/main.go:306-311`); for each task it starts the binary once with those arguments (`gentle-mesh@2d1d324:pkg/server/runner/pi.go:102`, `:175`). The binary defaults to `"pi"` (`:63-67`), and the CLI never sets it, so gentle-shell is not run.
- **The `rpc` bridge covers 5 commands with no extension UI.** It handles `get_state`, `get_messages`, `new_session`, `abort` and `prompt`; "Unknown commands are ignored" (`gentle-mesh@2d1d324:pkg/client/bridge.go:225-252`). `extension_ui` does not occur in that file on either commit (`git grep`). `Inference:` ask cards and the helpers feed ([04, gentle-shell additions over RPC](../04-rpc-contract.md#gentle-shell-additions-over-rpc)) would not reach a client.
- **CORS echoes any origin.** When a request carries `Origin`, the middleware copies it into `Access-Control-Allow-Origin`, with no allowlist (`gentle-mesh@2d1d324:pkg/server/http/middleware.go:110-133`). The README describes an allowlist of Tauri, localhost and Tailscale origins (`gentle-mesh@2d1d324:README.md:115`). Bearer-token auth is optional: it is added only when a token is configured (`gentle-mesh@2d1d324:pkg/server/http/server.go:251-253`).
- **No LICENSE file** on either commit (`git ls-tree` of both roots); the author said on 2026-10-04 he will add one (MIT). `UNVERIFIED:` his belief that RFC-001 had one ("rfc001 si tenia"), since no LICENSE exists on any branch. `main`'s README states an intent: "Código abierto bajo licencia MIT (o la que determine la gobernanza comunitaria de Gentleman Programming)." (open source under MIT, or whatever Gentleman Programming's community governance decides; `gentle-mesh@2d1d324:README.md:680`). `Inference:` its ideas can be cited, but its code cannot be reused until a license file exists.

**Status.** Questions about these points were sent to the author on the gentle-mesh Discord post on 2026-10-04. He replied on 2026-10-04: he will add an MIT LICENSE ("Mñn por la tarde cuando llegue a casa le pongo licence Mit"); the maintainer has not reviewed gentle-mesh yet; the other questions are pending (Discord, Rafael The Hutt, 2026-10-04 23:20). Integration depends on the maintainer, as the README's governance note says: "Este proyecto avanzará, evolucionará y se integrará de forma oficial única y exclusivamente bajo la revisión, orientación y aprobación explícita de Alan Buscaglia (@gentleman-programming), creador y líder del ecosistema Gentle AI." (this project will advance, evolve and be officially integrated only under Alan Buscaglia's explicit review, guidance and approval; `gentle-mesh@2d1d324:README.md:22`).

## Alternatives considered and rejected

**[community]** Alternatives assessed for this proposal (author Matrak; analysis by the corpus authors, 2026-10-04). Main reason each; supporting facts are under Evidence.

| Alternative | Main reason for rejection | Evidence |
|---|---|---|
| **Go server** | It re-implements the session domain in a second language. | The domain is TypeScript (`gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts`). Node is still required to run gentle-shell: its binary is a Node script, `#!/usr/bin/env node` (`gentle-shell@ac67159:package.json:7-8`; `gentle-shell@ac67159:bin/gentle-shell.mjs:1`), with `"node": ">=22.19.0"` (`gentle-shell@ac67159:package.json:101-102`). |
| **Build on T3 Code** | Pi support is in nightly builds only. | Nightly only: see [Prior art in the ecosystem](#prior-art-in-the-ecosystem). Blocking `select`, `confirm`, `input` and `editor` dialogs work (`t3code@eac52f0:docs/user/providers-pi.md:32-33`), but "Pi terminal decoration such as titles, status lines, and widgets does not have a T3 Code equivalent" (`:33-34`). `Inference:` the helpers feed, a `setWidget` payload ([04, gentle-shell additions over RPC](../04-rpc-contract.md#gentle-shell-additions-over-rpc)), is lost. |
| **Build on pi-web-ui** (`xing-shuyin/pi-web-ui`) | It runs the pi SDK in-process, not `gentle-shell --mode rpc`. | "the pi SDK runs in-process" (README `:70`); it "ships and loads its own copy of the pi SDK" (`:234`); it loads pi extensions, with per-extension switches (`:146`), and renders `setWidget` panels (`:160`). `UNVERIFIED:` whether it loads gentle-shell's extensions and homes specifically; not tested. Source: https://github.com/xing-shuyin/pi-web-ui/blob/eb49d432ebd69b83fa2593695f586cfe569e7097/README.md (commit `eb49d432`, accessed 2026-10-05) |
| **Herdr plugin** (the literal "herdr web") | It needs Herdr. | Installed with `herdr plugin install devswha/herdr-web-ui` (`herdr-web-ui@7c5fe4e:README.md:98`); "herdr owns the processes" (`herdr-web-ui@7c5fe4e:docs/guide.md:422`). Herdr's docs say it works on a phone "without a mobile app or web dashboard" (`herdr@5da0a01:docs/next/website/src/content/docs/how-to-work.mdx:49`); `Inference:` there is no official herdr web. `kcosr/herdr-web` is "not associated with ... the official Herdr project" and uses private Herdr APIs "for terminal attach" (`herdr-web@f1312e2:README.md:3`, `:14-15`); herdr-web-ui's chat "reads the agents' own session files" (`herdr-web-ui@7c5fe4e:docs/guide.md:420`). `Inference:` terminal or transcript clients cannot drive ask cards, helpers or the ODD panel. gentle-shell does not auto-load its Herdr bridge in RPC mode: automatic loading "is skipped for ... print/JSON/RPC modes (including interactive RPC hosts)" (`gentle-shell@ac67159:docs/readme-reference.md:380-382`; `gentle-shell@ac67159:bin/gentle-shell.mjs:191-199`). |
| **pi's `pi-server`** | Development-only. | "Development-only command dispatch", run only with `PI_EXPERIMENTAL=1` (`pi@a13d35a:packages/coding-agent/src/experimental/commands.ts:84-86`; `pi@a13d35a:packages/coding-agent/src/core/experimental.ts:1-3`); excluded from npm packages (`pi@a13d35a:packages/coding-agent/src/experimental/services/README.md:12`). It runs pi-durable sessions with Chord facets (`:30`, `:36`; `pi@a13d35a:packages/coding-agent/src/experimental/session-worker.ts:15`). `Inference:` (no `ExtensionAPI`/`loadExtensions` in `experimental/`, `rg`, 0 hits) it does not load classic extensions, which is how gentle-shell ships (`gentle-shell@ac67159:package.json:59-62`). |

**Security counter-example: open-pi-viewer's server.** It was suggested in the thread as a web connector (Discord, bojack7080, 2026-10-04 09:00). It is not an option here, but a pattern to avoid: a Vite dev-server plugin (`open-pi-viewer@908245a:vite.config.ts:9-12`) bound to `0.0.0.0` (`:71`), with `Access-Control-Allow-Origin: *` (`:18`) and no token, cookie or origin check in that file (`rg`), whose children run with `--approve` (`open-pi-viewer@908245a:server/bridge/rpc.ts:81`). It is licensed GPL-3.0 (`open-pi-viewer@908245a:LICENSE:1-2`).

## Open questions

**For the maintainer:**

1. What "web" means: a browser UI for the local agent (optionally reached remotely), or a hosted multi-user service.
2. Which herdr web was meant. Candidates are `kcosr/herdr-web` and `devswha/herdr-web-ui`, which was linked in the thread (Discord, Rafael The Hutt, 2026-09-30 09:27).
3. Web instead of desktop, or both.
4. One child per chat or a shared host ([vision Q3](../00-vision.md#open-questions-for-the-maintainer)). Q3 sets "a shared host" against "one child process per chat", so there it means one runtime process serving several chats. That is a different thing from this proposal's host service, which sits above the children and works with either answer.

**Design questions:**

1. **Separate process or embedded in Electron main.**

   | Option | For | Against |
   |---|---|---|
   | Separate process | Browser and mobile clients work without the desktop app running; one service for every client. | `Inference:` a second executable to package, sign and update (today nothing is signed; [platforms, packaging and signing](../10-platforms.md#packaging-and-signing), [milestone M5](../09-roadmap.md#m5-signing-and-auto-update)), plus a lifecycle (who starts and stops it). |
   | Embedded in Electron main | Nothing new to package or sign; the desktop keeps a single process tree. | `Inference:` browser and mobile clients work only while the desktop app is open. |

2. **Roadmap F1 before or after extraction.** B1 is F1's work; doing it first keeps the extraction a move, doing it after designs the registry once, in the service.
3. **Where the service keeps its configuration.** Today the first-run choice is stored under Electron's per-user data directory (`gentle-shell-desktop@5ab4a00:src/main/index.ts:52`), which a separate process does not have.

## Dependencies

Three documents will detail this proposal; they do not exist yet:

- Host service architecture
- Host protocol
- Clients and topologies

## Sources

**Pinned repositories** (read-only clones; `repo@sha:path:line`):

| Name in citations | Repository | Commit |
|---|---|---|
| `gentle-shell-desktop` | `Gentleman-Programming/gentle-shell-desktop` | `5ab4a00` |
| `gentle-shell` | `Gentleman-Programming/gentle-shell` (`main`, package version 4.0.0) | `ac67159` |
| `pi` | `earendil-works/pi` (v1.0.0) | `a13d35a` |
| `paseo` | `getpaseo/paseo` | `485221b` |
| `t3code` | `pingdotgg/t3code` | `eac52f0` |
| `gentle-mesh` | `Rafaeldelinares/gentle-mesh`: `main` (tag `v1.0.2`) and integration branch `feat/rfc-002-settlement` | `2d1d324`, `f52335e` |
| `herdr` | `herdrdev/herdr` | `5da0a01` |
| `herdr-web-ui` | `devswha/herdr-web-ui` | `7c5fe4e` |
| `herdr-web` | `kcosr/herdr-web` | `f1312e2` |
| `open-pi-viewer` | `gonzalez962/open-pi-viewer` | `908245a` |

**Web** (accessed 2026-10-05):

- `xing-shuyin/pi-web-ui` README at commit `eb49d432`: https://github.com/xing-shuyin/pi-web-ui/blob/eb49d432ebd69b83fa2593695f586cfe569e7097/README.md
- T3 Code latest release `v0.0.45` and its tree, through the GitHub API: https://github.com/pingdotgg/t3code/releases/tag/v0.0.45

**Community:**

- Discord thread "Gentle Desktop" (saved copy, not in the repository): Alan Buscaglia, 2026-09-30 22:34 and 2026-10-01 11:17; Rafael The Hutt, 2026-09-27 23:33 and 2026-09-30 09:27; bojack7080, 2026-10-04 09:00.
- Discord, gentle-mesh post: Rafael The Hutt, 2026-10-04 23:20.
- Conversation with Matrak, 2026-10-04 (not published).

**Corpus:** [audit](../03-architecture/audit.md), [RPC contract](../04-rpc-contract.md), [vision](../00-vision.md), [roadmap](../09-roadmap.md), [platforms](../10-platforms.md).
