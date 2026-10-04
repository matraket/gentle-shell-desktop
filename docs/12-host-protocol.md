# Host protocol

> Status: draft (community proposal, awaiting maintainer validation).

> **[community] design sketch, not a spec.** This page sketches the client ↔ service protocol of the shared local host service proposed in [proposal 0004](07-proposals/0004-host-service.md), whose architecture is in [11-host-service.md](11-host-service.md). Nothing here exists in the desktop repository today, and nothing here is decided. Frame names and fields are illustrative. The service ↔ gentle-shell contract stays [04-rpc-contract.md](04-rpc-contract.md), unchanged.

**In one paragraph.** **[community]** Every WebSocket client (a browser tab, a future mobile app, and the Electron window under placement (a); under placement (b) the window can keep the preload bridge, see [11, Process placement](11-host-service.md#process-placement-open)) opens one WebSocket to the host service and exchanges JSON frames: a `hello`/`welcome` handshake first, then requests and responses correlated by `id`, subscriptions per chat, and server push events. The protocol starts from the desktop's current `GentleBridge` (8 request methods, 2 push channels) and adds what Electron IPC never needed: a `chatId` on every chat-scoped frame (B1), a version handshake (B3), an error envelope with a code and a `retryable` flag, and authentication with argument validation (B4). Pushes stay full `ChatState` snapshots, as they are today, so a reconnecting client re-subscribes and receives the current snapshot instead of replaying a log. Versioning policy, the remote auth model, multi-client ownership of a chat, backpressure limits, the choice of framing, and full snapshots versus deltas are open (HP-01 to HP-06), as is whether loopback clients need a credential (HP-07).

## How to read this page

| Label | Meaning |
|---|---|
| **[maintainer]** | Stated in the maintainer's desktop repo documents or Discord messages. |
| **[community]** | Proposed by the community. Not decided. |
| `Inference:` | Reasoning from cited evidence, not a stated fact. "(not run)" means nothing was built or executed. |
| `UNVERIFIED:` | Checked but not confirmed. |

- **Citation keys.** Code is cited as `repo@shortsha:path:line`: `gentle-shell-desktop@5ab4a00` (the source is unchanged on this branch), `gentle-shell@ac67159` (gentle-shell `main`, package version 4.0.0), `pi@a13d35a` (pi 1.0.0), `paseo@485221b`, `t3code@eac52f0`, `herdr-web-ui@7c5fe4e` and `open-pi-viewer@908245a`. `:N` after a full citation repeats its file. Web sources carry an access date. Corpus pages are linked by relative path.
- **Qualified IDs.** IDs from other pages carry their page: `audit A3`, `gap G9`, `vision Q3`, `QW-05`. **B1–B6** are the runtime requirements of [proposal 0004](07-proposals/0004-host-service.md#runtime-requirements), written bare as in [11](11-host-service.md#how-to-read-this-page). **HP-01 to HP-07** are this page's open questions; elsewhere write them as they are (the `HP-` prefix is unique in the corpus).
- **Method.** Static reading only, as in the [audit](03-architecture/audit.md#method-and-scope). Nothing was prototyped.

## At a glance

| Question | Answer | Evidence |
|---|---|---|
| What does it connect? | **[community]** A browser tab, a future mobile app and the Electron window under placement (a) to the host service, over one WebSocket per client. Under placement (b) the window can keep the preload bridge. | [proposal 0004](07-proposals/0004-host-service.md#proposal); [11, Process placement](11-host-service.md#process-placement-open) |
| What is it built from? | The current `GentleBridge`: 8 request methods and 2 push subscriptions, mirrored by 8 + 2 IPC channels. | [Starting point](#starting-point-the-current-bridge) |
| What does it add? | `chatId` on chat-scoped frames, subscriptions, a version handshake, an error envelope, authentication and argument validation. | [What a network transport must add](#what-a-network-transport-must-add) |
| Encoding? | JSON text frames. Every bridge payload is plain data; two fields are typed `unknown`. | [Transport and framing](#transport-and-framing) |
| How does a client resynchronize? | It re-subscribes and receives the current `ChatState`, which is already a full snapshot on every push today. | [Reconnect and replay](#reconnect-and-replay) |
| Who may connect? | Loopback by default; a token or pairing for anything else; an `Origin` allow-list for browsers. | [Auth and origin](#auth-and-origin) |
| Does the RPC contract change? | No. The service speaks [04-rpc-contract.md](04-rpc-contract.md) to its children, as the desktop does today. | [11, Responsibilities](11-host-service.md#responsibilities) |
| What is open? | Versioning policy, remote auth, multi-client ownership, backpressure limits, framing, snapshots vs deltas, a credential on loopback. | [Open questions](#open-questions) |

## Starting point: the current bridge

The renderer talks to main through `GentleBridge` (`gentle-shell-desktop@5ab4a00:src/shared/bridge-types.ts:273-295`), exposed as `window.gentle` by the preload (`gentle-shell-desktop@5ab4a00:src/preload/index.ts:4`). `createBridge` maps each method to one IPC channel (`gentle-shell-desktop@5ab4a00:src/preload/bridge.ts:19-43`), and `registerHandlers` passes each channel through to `ChatHost` or `SetupService` (`gentle-shell-desktop@5ab4a00:src/main/ipc/registerHandlers.ts:27-40`). The same table, from the IPC side, is in [current.md](03-architecture/current.md#ipc-between-main-and-renderer).

| Bridge member | Channel | Arguments | Result | Evidence (`gentle-shell-desktop@5ab4a00:src/`) |
|---|---|---|---|---|
| `listChats()` | `sessions.list` | — | `ChatSummary[]` | `shared/bridge-types.ts:274`; `shared/ipc-channels.ts:9`; `main/ipc/registerHandlers.ts:28` |
| `openChat(id)` | `chat.open` | `id: string` (pi's session id) | `ChatState` | `shared/bridge-types.ts:275-276`; `shared/ipc-channels.ts:10`; `main/ipc/registerHandlers.ts:29`; `main/domain/session/ChatHost.ts:100-102` |
| `newChat()` | `chat.new` | — | `ChatState` (no id) | `shared/bridge-types.ts:277-278`; `shared/ipc-channels.ts:11`; `main/ipc/registerHandlers.ts:30` |
| `sendMessage(text)` | `chat.send` | `text: string` | `PromptResult` (`{queued, reason?}`) | `shared/bridge-types.ts:279-282`, `:106-109`; `shared/ipc-channels.ts:12`; `main/ipc/registerHandlers.ts:31` |
| `abort()` | `chat.abort` | — | `void` | `shared/bridge-types.ts:283`; `shared/ipc-channels.ts:13`; `main/ipc/registerHandlers.ts:32` |
| `answerDialog(id, answer)` | `dialog.answer` | `id: string`, `answer: DialogAnswer` | `void` | `shared/bridge-types.ts:284`, `:92`; `shared/ipc-channels.ts:14`; `main/ipc/registerHandlers.ts:33-35` |
| `setupStatus()` | `setup.status` | — | `SetupStatus` | `shared/bridge-types.ts:289-291`, `:261-264`; `shared/ipc-channels.ts:20`; `main/ipc/registerHandlers.ts:36` |
| `chooseHome(mode)` | `setup.chooseHome` | `mode: HomeMode` (`"link"` or `"isolated"`) | `void` | `shared/bridge-types.ts:292-294`, `:237-242`; `shared/ipc-channels.ts:22`; `main/ipc/registerHandlers.ts:37` |
| `onState(cb)` | `chat.state` (push) | — | `ChatState` per push; returns an unsubscribe function | `shared/bridge-types.ts:285-286`; `shared/ipc-channels.ts:16`; `main/ipc/registerHandlers.ts:39` |
| `onError(cb)` | `chat.error` (push) | — | `string` per push; returns an unsubscribe function | `shared/bridge-types.ts:287-288`; `shared/ipc-channels.ts:18`; `main/ipc/registerHandlers.ts:40` |

`ChatState` is `{messages, working, pendingDialogs, lastError?, activity, helpers}` (`gentle-shell-desktop@5ab4a00:src/shared/bridge-types.ts:122-129`).

### What a network transport must add

| Missing today | Evidence | Added by |
|---|---|---|
| **A chat id.** Commands act on "whichever chat is currently open", and `onState` subscribes to "ChatState pushes for the currently open chat". Neither `ChatState` nor the pushes carry an id. | `gentle-shell-desktop@5ab4a00:src/shared/bridge-types.ts:279`, `:285`, `:122-129`; [audit A3](03-architecture/audit.md#a3-single-session-host-with-positional-message-ids) | `chatId` on every chat-scoped frame (B1) |
| **Subscriptions.** Each window receives every push from the one `ChatHost`: `registerHandlers` forwards all state and error events to its `webContents`. | `gentle-shell-desktop@5ab4a00:src/main/ipc/registerHandlers.ts:39-40`; `gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts:85-93`, `:192-198` | `subscribe` / `unsubscribe` per chat |
| **An error envelope.** A rejected request reaches the renderer as a message string only. | [Errors](#errors) | `{code, message, retryable}` |
| **Authentication and validation.** IPC handlers trust the renderer and use its arguments as-is. | `gentle-shell-desktop@5ab4a00:src/main/ipc/registerHandlers.ts:28-37`; [audit A14](03-architecture/audit.md#a14-preload-and-ipc-hardening) | Handshake auth and schema validation (B4) |
| **A version.** Nothing in the bridge or the RPC chain carries one. | [audit A8](03-architecture/audit.md#a8-no-version-handshake); [gap G10](04-rpc-contract.md#gaps-the-desktop-needs) | `hello` / `welcome` (B3) |

## Transport and framing

**[community]** One WebSocket per client. Each frame is one JSON object in a WebSocket text message, discriminated by `type`.

| Frame `type` | Direction | Fields (illustrative) | Purpose |
|---|---|---|---|
| `hello` | client → service | `protocol`, `client: {name, version}`, `auth?` | Must be the first frame. See [Handshake and versions](#handshake-and-versions). |
| `welcome` | service → client | `protocol`, `service: {version}`, `runtime: {gentleShell, pi}` or `null`, `runtimeError?` | Handshake reply. |
| `request` | client → service | `id`, `method`, `params` | One bridge method call. |
| `response` | service → client | `id`, then `ok: true, result` or `ok: false, error: {code, message, retryable}` | Correlated to its request by `id`, not by order. |
| `subscribe` | client → service | `id`, `chatId` | Start receiving one chat's pushes. Answered by a `response` whose `result` is the current `ChatState`. |
| `unsubscribe` | client → service | `id`, `chatId` | Stop receiving them. |
| `event` | service → client | `event`, `chatId`, `data` | A push: `chat.state` or `chat.error`. |

- **Correlation by `id`.** The same rule pi's RPC uses: "Correlate by `id`, not by order" ([04, Correlation and errors](04-rpc-contract.md#correlation-and-errors)).
- **`chatId` on every chat-scoped frame.** Requests about a chat carry it in `params`; `subscribe`, `unsubscribe` and `event` carry it at the top level. This is B1 on the wire: audit A3 recommends "Add a `chatId` to every push and command" ([audit A3](03-architecture/audit.md#a3-single-session-host-with-positional-message-ids), recommendation 2), and gap G9 places several chats in desktop architecture, not in the RPC protocol ([gap G9](04-rpc-contract.md#gaps-the-desktop-needs)).
- **What a `chatId` is.** Today a chat's id is pi's session id: "ChatSummary.id is pi's session id, not a file path" (`gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts:100-102`). `newChat()` returns a `ChatState` with no id (`gentle-shell-desktop@5ab4a00:src/shared/bridge-types.ts:277-278`). `Inference:` the service must return the new chat's id from `chat.new`; pi's `get_state` reports the session id ([04, Commands](04-rpc-contract.md#commands-desktop--runtime)), and the desktop already types it without sending it.
- **JSON is enough.** Every bridge payload is plain data (`gentle-shell-desktop@5ab4a00:src/shared/bridge-types.ts:23-264`). Two fields are typed `unknown`: `HelperThreadToolItem.args` and `.output` (`:157-158`). The parser copies them straight out of a `JSON.parse` result (`gentle-shell-desktop@5ab4a00:src/main/domain/rpc/helpersActivity.ts:43`, `:113-114`). `Inference:` they are therefore JSON values already and re-encode losslessly; optional fields left `undefined` are simply omitted.

**Example exchange** (illustrative):

```json
{"type":"request","id":"7","method":"chat.send","params":{"chatId":"<pi session id>","text":"Run the tests"}}
{"type":"response","id":"7","ok":true,"result":{"queued":true}}
{"type":"event","event":"chat.state","chatId":"<pi session id>","data":{"messages":[],"working":true,"pendingDialogs":[],"activity":0,"helpers":{"summary":{"running":0,"queued":0,"waiting":0,"finished":0},"tasks":[]}}}
```

**How the precedents frame it.**

| Project | Framing | Evidence |
|---|---|---|
| **Paseo** | A "WebSocket API" (`paseo@485221b:README.md:172`) on path `/ws` (`paseo@485221b:packages/server/src/server/websocket-server.ts:821-823`). Frames are discriminated by `type`: inbound `ping`, `hello`, `recording_state`, `session`; outbound `pong`, `session`, `hello.rejected` (`paseo@485221b:packages/protocol/src/messages.ts:7545-7556`). Requests carry a `requestId` (for example `:1849-1852`); some list requests take a `subscribe` field to keep receiving updates (`:993-997`, `:1253-1257`). | as cited |
| **T3 Code** | An Effect RPC group served over WebSocket at `/ws` with JSON serialization (`t3code@eac52f0:apps/server/src/ws.ts:3772-3775`, `:3806-3823`; client: `t3code@eac52f0:packages/client-runtime/src/rpc/protocol.ts:1-5`). Subscriptions are RPCs declared `stream: true`, for example the per-thread subscription (`t3code@eac52f0:packages/contracts/src/rpc.ts:1575-1580`). | as cited |

`Inference:` both use one socket per client, typed frames and per-resource subscriptions, which is the shape above. Paseo's custom envelope and T3's framework-defined one are the two ends of [HP-05](#open-questions).

## Handshake and versions

**[community]** The first client frame is `hello`. The service answers `welcome` or rejects and closes. Clients and service may be updated separately (B3), so the handshake exists from protocol version 1.

| Step | What happens |
|---|---|
| 1. `hello` | The client sends its protocol version (an integer) and its own name and version, plus credentials when required ([Auth and origin](#auth-and-origin)). Any other first frame, or no `hello` within a timeout, closes the socket. |
| 2. Runtime versions | The service reads the gentle-shell and pi versions out of band, with `gentle-shell --version`, as audit A8 recommends (`gentle-shell@ac67159:bin/gentle-shell.mjs:1217-1219`; [audit A8](03-architecture/audit.md#a8-no-version-handshake)). The output has three lines, `gentle-shell <version>`, `pi <version>` and `home <mode> <dir>` (`gentle-shell@ac67159:lib/gentle-shell-launcher.ts:1138-1144`). |
| 3. `welcome` | The service replies with its protocol version, its own version and the runtime versions. |
| 4. Mismatch | A protocol version the service does not support gets a typed rejection (`protocol_unsupported`, with the supported range), then a close. A client version is informational. |

**Why out of band.** The RPC protocol carries no version field, and no startup record announces one ([04, Is there a version handshake?](04-rpc-contract.md#is-there-a-version-handshake)). Gap G10's only workaround is `gentle-shell --version` ([gap G10](04-rpc-contract.md#gaps-the-desktop-needs)). The launcher checks pi before it prints versions and exits with an error when the check fails (`gentle-shell@ac67159:bin/gentle-shell.mjs:1215-1219`).

`Inference:` (not run)

- **A runtime problem is not a handshake failure.** When the launcher is missing or pi is too old, `welcome` still succeeds with `runtime: null` and a `runtimeError`, so the client can show setup guidance instead of a dead socket.
- **The `home` line stays local.** It carries a local directory (`gentle-shell@ac67159:lib/gentle-shell-launcher.ts:1142`). A remote client needs the versions, not the path. The same applies to `PiDetection.dir` in `setup.status` (`gentle-shell-desktop@5ab4a00:src/shared/bridge-types.ts:249-254`).
- **When to read versions.** Once at service start and again before spawning a child after a home change; a running child keeps the versions it started with.

**How the precedents version.**

- **Paseo.** `hello` carries `protocolVersion`, an optional `appVersion` and a map of client capability flags (`paseo@485221b:packages/protocol/src/messages.ts:7487-7520`). The server closes a socket that sends no `hello` within 15 s (code 4001) and rejects only a `protocolVersion` below 1, with code 4003; above that floor it relies on the capability flags (`paseo@485221b:packages/server/src/server/websocket-server.ts:484-489`, `:1336-1351`, `:1568-1579`). Clients that announce support first receive a typed `hello.rejected` frame with a reason (`:1705-1734`; `paseo@485221b:packages/protocol/src/messages.ts:7538-7542`). Its desktop app restarts a running daemon whose version does not match (`paseo@485221b:packages/desktop/src/daemon/daemon-manager.ts:291-297`).
- **T3 Code.** The client puts the protocol version in the upgrade URL (`orchestrationProtocol`), and the server answers a mismatch with HTTP 426 and code `orchestration_protocol_incompatible` before any WebSocket exists (`t3code@eac52f0:packages/contracts/src/environment.ts:12-15`; `t3code@eac52f0:apps/server/src/ws.ts:602-606`, `:3778-3786`). The client surface and app version also travel as query parameters (`t3code@eac52f0:apps/server/src/ws.ts:618-630`). The server descriptor carries `serverVersion` and the protocol version (`t3code@eac52f0:packages/contracts/src/environment.ts:203-211`).

`Inference:` a first-frame `hello` (Paseo) works for every WebSocket client, including the browser `WebSocket` API, which cannot set custom upgrade headers; a query parameter (T3) rejects earlier but puts the version in the URL. This page follows Paseo; the evolution rule is [HP-01](#open-questions).

## Mapping table

**[community]** Each bridge member mapped to frames. "chatId" marks the frames B1 adds it to.

| Bridge member | Frame | `params` / payload | Result or push | chatId |
|---|---|---|---|---|
| `listChats()` | `request` `chats.list` | — | `ChatSummary[]` | no (lists every chat) |
| `openChat(id)` | `request` `chat.open` | `chatId` | `ChatState` | yes |
| `newChat()` | `request` `chat.new` | `cwd?` (B6) | `{chatId, state: ChatState}` | returned |
| `sendMessage(text)` | `request` `chat.send` | `chatId`, `text` | `PromptResult` | yes |
| `abort()` | `request` `chat.abort` | `chatId` | — | yes |
| `answerDialog(id, answer)` | `request` `dialog.answer` | `chatId`, `dialogId`, `answer: DialogAnswer` | — | yes |
| `setupStatus()` | `request` `setup.status` | — | `SetupStatus` | no |
| `chooseHome(mode)` | `request` `setup.chooseHome` | `mode` | — | no |
| `onState(cb)` | `subscribe` / `unsubscribe` | `chatId` | `event` `chat.state` with a full `ChatState` | yes |
| `onError(cb)` | covered by the same subscription | `chatId` | `event` `chat.error` with `{code, message, retryable}` | yes |

Notes:

- **Method names.** `chats.list` replaces the IPC channel `sessions.list` (illustrative); the other names follow the IPC channels of [Starting point](#starting-point-the-current-bridge).
- **`PromptResult` stays a result.** A prompt sent while the chat is working is declined with `{queued: false, reason}` instead of rejected, "so the caller reports it exactly once" (`gentle-shell-desktop@5ab4a00:src/shared/bridge-types.ts:279-282`; `gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:168-180`). A decline is not an error frame.
- **`chat.open` no longer stops other chats.** Today `performStart` stops the current session first (`gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts:156-157`). `Inference:` with a registry (B1), `chat.open` means "ensure this chat has a child", and closing a chat becomes a separate request (for example `chat.close`), which the bridge does not have today.
- **`chat.new` takes `cwd`.** B6: `PiSession` accepts a `cwd`, but `ChatHost` never passes one (`gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:15`, `:135`; `gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts:159-166`; [audit A10](03-architecture/audit.md#a10-new-chats-run-in-the-apps-working-directory)).
- **`chats.list` and refreshes.** The sidebar loads the list once ([audit A11](03-architecture/audit.md#a11-chat-list-and-selection-lifecycle)). `Inference:` a list-level subscription would let the service push list changes to every client; it is left out of this sketch.

### `dialog.answer`: chat id plus dialog id

- **Dialog ids come from pi.** A dialog's id is the `id` of pi's `extension_ui_request` (`gentle-shell-desktop@5ab4a00:src/main/domain/rpc/chatReducer.ts:165-179`), a `crypto.randomUUID()` generated per request (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-mode.ts:99`, `:129`). `Inference:` unique in practice, but the service still needs `chatId` to find the child that must receive the answer.
- **Late or duplicate answers are dropped silently.** pi resolves a dialog that has a `timeout` on its own (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-mode.ts:115-120`) and ignores a response whose id is no longer pending (`:774-779`). Today the desktop removes the card and writes the response either way (`gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:193-207`). This is [audit A12](03-architecture/audit.md#a12-dialog-timeouts-not-modeled): the codec decodes `timeout`, but the `Dialog` type drops it.
- `Inference:` the service knows which dialogs are pending per chat, so it can answer a stale or second answer with `dialog_not_pending` instead of accepting it silently. With several clients this is no longer rare: two clients showing the same card can both answer it ([HP-03](#open-questions)).

## Errors

**Today there are two error paths, both message-only.**

| Path | Where it comes from | What the renderer gets |
|---|---|---|
| **Rejected request** | Handlers throw: `ChatHost: no session found for id …` (`gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts:106`), `ChatHost: no chat is open …` (`:188`), `Could not save the home choice: …` (`gentle-shell-desktop@5ab4a00:src/main/adapters/setupService.ts:37`). Electron: "Errors thrown through `handle` in the main process are not transparent as they are serialized and only the `message` property from the original error is provided to the renderer process." (https://www.electronjs.org/docs/latest/api/ipc-main, accessed 2026-10-05). The desktop code says the same: "ipc's handle() rejection carries only the message text to the renderer" (`gentle-shell-desktop@5ab4a00:src/main/adapters/setupService.ts:33-34`). | A string: `errorText` keeps `cause.message` (`gentle-shell-desktop@5ab4a00:src/renderer/features/conversation/ConversationContainer.tsx:35-37`, `:89-91`, `:107`, `:111`, `:115`). |
| **Pushed error** | `PiSession` "Never throws from a public method"; failures set `lastError` and emit `error` (`gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:77-81`, `:326-330`). A missing launcher lands here: `locate()` throws inside `start()`'s `try` (`:125-126`, `:148-149`; `gentle-shell-desktop@5ab4a00:src/main/adapters/launcherLocator.ts:25-29`). An unexpected exit too (`gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:319-321`). | A string on `chat.error` (`gentle-shell-desktop@5ab4a00:src/main/ipc/registerHandlers.ts:40`) and `ChatState.lastError`. |

**[community] The envelope.** Both paths carry the same object: `{code, message, retryable}`. `code` is a stable string a client can switch on; `message` is human-readable; `retryable` says whether the same request, unchanged, may succeed later.

| `code` (illustrative) | `retryable` | Source today |
|---|---|---|
| `bad_request` | no | None: no argument validation ([audit A14](03-architecture/audit.md#a14-preload-and-ipc-hardening)). |
| `unauthorized` | no | None: new with authentication. |
| `protocol_unsupported` | no | None: new with the handshake. |
| `chat_not_found` | no | `gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts:106` |
| `chat_not_open` | no | `gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts:188` |
| `dialog_not_pending` | no | None: pi drops the answer silently ([dialog.answer](#dialoganswer-chat-id-plus-dialog-id)). |
| `launcher_not_found` | yes, after the user installs it | `gentle-shell-desktop@5ab4a00:src/main/adapters/launcherLocator.ts:25-29`, pushed today |
| `child_exited` | yes | `gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:319-321`, pushed today |
| `config_write_failed` | yes | `gentle-shell-desktop@5ab4a00:src/main/adapters/setupService.ts:37` |
| `internal` | no | Anything else. |

`Inference:` `retryable` lets a client decide between retrying, showing a fix-it action and giving up without parsing `message`. pi's own RPC failure response is `{type:"response", command, success:false, error}` with a string `error` ([04, Correlation and errors](04-rpc-contract.md#correlation-and-errors)); the service maps child failures into the envelope instead of forwarding that string.

**Precedents.** Paseo's `rpc_error` carries `requestId`, an optional `requestType`, `error` and an optional `code` (`paseo@485221b:packages/protocol/src/messages.ts:3748-3756`). T3 declares a typed error union per RPC (`t3code@eac52f0:packages/contracts/src/rpc.ts:1575-1580`) and answers an incompatible protocol with a JSON body holding `code` and `message` (`t3code@eac52f0:apps/server/src/ws.ts:3779-3785`). Neither has a `retryable` field in the code read here.

## Reconnect and replay

**Fact: pushes are already full snapshots.** `PiSession` folds each decoded line into `this.state` and emits the whole object (`gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:253`, `:259`); so do `prompt` and `answerDialog` (`:182-183`, `:194-198`). `ChatHost` forwards it unchanged (`gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts:167`, `:192-194`), and `registerHandlers` sends it as the `chat.state` payload (`gentle-shell-desktop@5ab4a00:src/main/ipc/registerHandlers.ts:39`). The renderer replaces its state with each push (`gentle-shell-desktop@5ab4a00:src/renderer/features/conversation/ConversationContainer.tsx:60-67`).

**[community] Reconnect.**

1. The client reconnects and sends `hello` again.
2. It sends `subscribe` for each chat it shows.
3. Each `subscribe` response carries that chat's current `ChatState`; later `chat.state` events replace it.

`Inference:` no event log and no cursor are needed beyond the `rev` below, because no push depends on an earlier one. Chat history itself stays in pi's session files, not in the service ([11, Config and state location](11-host-service.md#config-and-state-location-open)).

`Inference:` (not run)

- **A revision number per chat.** The renderer already races an `openChat` result against pushes for the same chat (`gentle-shell-desktop@5ab4a00:src/renderer/features/conversation/ConversationContainer.tsx:60-67`, `:81-95`). A `rev` that increases with every snapshot, on both the `subscribe` result and each event, lets a client drop a snapshot older than one it already holds.
- **Snapshots make slow clients cheap to handle.** A newer snapshot supersedes every older one, so the service can keep only the latest pending snapshot per chat and client and drop the rest without losing state.
- **Snapshots are not free.** Every streamed text delta resends the whole `ChatState`, all messages included. Helper threads are bounded upstream (the last 40 items, [04, gap G8](04-rpc-contract.md#gaps-the-desktop-needs)), but `messages` grows with the chat. Whether to keep snapshots or move to deltas is [HP-06](#open-questions).

**How the precedents replay and bound output.**

| Project | What it streams | Replay on reconnect | Backpressure | Evidence |
|---|---|---|---|---|
| **Paseo** | Agent timelines and other state | Cursor-based: a timeline fetch takes a cursor `{epoch, seq}`, and the response reports `reset`, `staleCursor` and `gap` | Closes (terminates) a socket whose buffered output would pass 64 MiB. Clients ping every 10 s; an application socket without traffic for 45 s is closed. Paseo's `docs/architecture.md:268` states 8 MiB; the code constant is 64 MiB (`physical-socket.ts:4`), also used for the relay queue (`encrypted-relay-socket.ts:62`). | `paseo@485221b:packages/protocol/src/messages.ts:1844-1861`, `:4591-4616`; `paseo@485221b:packages/server/src/server/websocket-server.ts:1245-1262`; `paseo@485221b:packages/server/src/server/websocket/physical-socket.ts:4-8`, `:89-95` |
| **T3 Code** | Thread projections and events | A subscription starts with a snapshot, or, given `afterSequence`, "the server skips the initial snapshot frame and instead replays events after this sequence before streaming live events" | One budget per subscription: 1,000 items or 8 MiB; on overflow the stream fails with "The live event buffer is full. Resume from the last received sequence." | `t3code@eac52f0:packages/contracts/src/orchestrationV2.ts:3061-3075`, `:3078-3093`; `t3code@eac52f0:apps/server/src/orchestration-v2/LiveStreamBudget.ts:17-18`, `:39`, `:72-74` |
| **herdr-web-ui** | A terminal byte stream | A replay tail of the last 256 KiB per attached pane | Credit by ACK: the browser acknowledges byte offsets after xterm parses them; output pauses at 256 KiB outstanding and resumes at 64 KiB; a client blocked for 2 s, or past a 1 MiB budget, is closed with code 4008, and the UI does not reconnect automatically: "Overloaded output stops this connection; automatic replay could conceal lost ANSI state." | `herdr-web-ui@7c5fe4e:server/index.ts:78`, `:620`, `:284-297`, `:446-475`; `herdr-web-ui@7c5fe4e:server/output-window.ts:3-6`, `:16-28`; `herdr-web-ui@7c5fe4e:shared/protocol.ts:582-585`; `herdr-web-ui@7c5fe4e:shared/terminal-flow.ts:1-2` |

`Inference:` the three differ because their data differ. herdr-web-ui streams bytes that cannot be dropped or re-derived, so it needs credit, and it will not replay automatically after an overload close; an ordinary reattach still replays its 256 KiB tail (`herdr-web-ui@7c5fe4e:server/index.ts:78`, `:620`; `herdr-web-ui@7c5fe4e:shared/protocol.ts:591`; `herdr-web-ui@7c5fe4e:shared/terminal-flow.ts:1`). Paseo and T3 stream logs, so they need cursors and gaps. This protocol streams self-contained state, so it can coalesce and needs neither, at the cost of message size. All three bound per-client memory and disconnect a client that cannot keep up; the host service needs such a bound too ([HP-04](#open-questions)).

## Auth and origin

**[community]** The defaults of [proposal 0004](07-proposals/0004-host-service.md#proposal), in protocol terms:

| Rule | What it means on the wire | Precedent |
|---|---|---|
| **Loopback by default** | The service listens on `127.0.0.1` unless configured otherwise. | Paseo defaults to `127.0.0.1:6767` (`paseo@485221b:packages/server/src/server/config.ts:470`, `:476-480`); T3 to `127.0.0.1` (`t3code@eac52f0:apps/server/src/server.ts:249`). |
| **A credential for anything else** | `hello.auth` carries a token, or the client was paired first. | See below. |
| **An `Origin` allow-list** | The upgrade is refused when a browser's `Origin` is not allowed. | See below. |
| **Argument validation** | Every frame is checked against a schema before it reaches the domain; failures answer `bad_request`. | Paseo parses every inbound frame with a zod schema, `WSInboundMessageSchema.safeParse` (`paseo@485221b:packages/protocol/src/messages.ts:7545-7556`; `paseo@485221b:packages/server/src/server/websocket-server.ts:2305`); T3 declares a payload schema per RPC (`t3code@eac52f0:packages/contracts/src/rpc.ts:1575-1580`). |

**Credentials in the precedents.**

- **Paseo.** `hello.auth` is either a password or a `localCredential` token (`paseo@485221b:packages/protocol/src/messages.ts:7492-7497`). The local credential is 32 random bytes written to a file with mode `0o600` (`paseo@485221b:packages/server/src/server/local-credential.ts:12-17`). With no password configured, every `hello` is admitted as owner (`paseo@485221b:packages/server/src/server/session-admission-auth.ts:18-20`). Remote devices pair through a connection offer holding the server id, the daemon's public key and a relay endpoint, encoded into a URL fragment (`paseo@485221b:packages/server/src/server/connection-offer.ts:30-50`).
- **T3 Code.** Every `/ws` upgrade is authenticated: a `wsTicket` query parameter, or the request's own credential (cookie or bearer token); a request with neither fails (`t3code@eac52f0:apps/server/src/auth/EnvironmentAuth.ts:517`, `:638-656`, `:1075-1094`; `t3code@eac52f0:apps/server/src/ws.ts:3788-3801`). Pairing links are created, listed and revoked by the server (`t3code@eac52f0:apps/server/src/auth/EnvironmentAuth.ts:448-466`).

**`Origin` in the precedents.** Paseo refuses an upgrade with 403 "Origin not allowed" unless the `Origin` header is absent, allow-listed (or `*`) or same-origin, and also checks `Host` against allowed hostnames (`paseo@485221b:packages/server/src/server/websocket-server.ts:825-832`, `:880-912`). In T3's `ws.ts` no `Origin` check on `/ws` was found (`rg` for `headers.origin`). Its only allow-list is an HTTP CORS layer, and only in development, when `devUrl` is set; packaged builds use the default wildcard origin (`t3code@eac52f0:apps/server/src/http.ts:238-239`, `:246-251`). `UNVERIFIED:` whether T3's framework checks `Origin` on WebSocket upgrades.

`Inference:`

- **`Origin` protects against browsers, not local processes.** Paseo admits a missing `Origin`, which is what a non-browser client sends; so the allow-list stops other web pages in the user's browser from opening the socket, and only a credential stops another local process. Paseo with no password admits every local client.
- **Even loopback needs a credential.** This departs from proposal 0004's default, which requires a credential only off loopback ([0004, Proposal](07-proposals/0004-host-service.md#proposal)). A loopback-only service without one is reachable by every process of every local user. A per-user token file, as Paseo's local credential, is the cheapest answer. Whether to require it is [HP-07](#open-questions); the auth model beyond the local machine is [HP-02](#open-questions).
- **The Electron window's origin.** `UNVERIFIED:` which `Origin` an Electron renderer loaded from a file sends was not checked. T3 lists custom-scheme renderer origins (`t3code://app`) in its CORS allow-list, but only in development, when `devUrl` is set; packaged builds use the default wildcard origin (`t3code@eac52f0:apps/server/src/http.ts:53`, `:238-239`, `:246-251`).

**The renderer's CSP would block the socket.** The policy is `default-src 'self'; script-src 'self' 'unsafe-eval'; style-src … ; font-src …`, with no `connect-src` (`gentle-shell-desktop@5ab4a00:src/renderer/index.html:7`). `Inference:` `connect-src` therefore falls back to `default-src 'self'`, which does not cover a `ws://127.0.0.1:<port>` endpoint; the WebSocket bridge needs an explicit `connect-src` entry ([11, The renderer side](11-host-service.md#the-renderer-side)). Hardening the CSP is already [QW-05](09-roadmap.md#qw-05-csp-navigation-and-ipc-hardening-audit-a14-part).

**Counter-example: open-pi-viewer's server.** Proposal 0004 records it as a pattern to avoid ([0004, Alternatives considered and rejected](07-proposals/0004-host-service.md#alternatives-considered-and-rejected)): a Vite dev-server plugin (`open-pi-viewer@908245a:vite.config.ts:9-12`) bound to `0.0.0.0` (`:71`), with `Access-Control-Allow-Origin: *` (`:18`) and no token, cookie or origin check in that file, whose children run with `--approve` (`open-pi-viewer@908245a:server/bridge/rpc.ts:81`). `Inference:` every rule in the table above is missing there, and its children skip approvals, so any page or host that reaches the port can drive an agent.

## Open questions

Facts are cited; judgments are `Inference:`. None of these is decided.

| ID | Question | Facts | Options and `Inference:` |
|---|---|---|---|
| **HP-01** | **Protocol versioning policy.** How does the protocol evolve without breaking older clients? | Paseo combines one integer version used as a floor, rejecting only `protocolVersion < 1` with code 4003 (`paseo@485221b:packages/server/src/server/websocket-server.ts:489`, `:1568-1579`), with per-feature capability flags in `hello` (`paseo@485221b:packages/protocol/src/messages.ts:7499-7519`) and dated compatibility comments, for example "added in v0.3.x, remove optional after 2027-02-12" (`:1258`). T3 requires an exact protocol version match (`t3code@eac52f0:apps/server/src/ws.ts:602-606`). gentle-shell's activity schema is versioned by name (`gentle-agents.activity/v1`) with no stated evolution rule ([04, Host and extension channels](04-rpc-contract.md#host-and-extension-channels)). | (a) Exact match. (b) A supported range plus additive-only changes within a major version. (c) (b) plus capability flags. `Inference:` with clients updated separately (an app store build, a browser tab, a desktop app), (a) forces lockstep updates; (b) or (c) avoid it. |
| **HP-02** | **Auth model beyond loopback.** Pairing, token or relay? | Paseo: a local token file and a password, plus pairing through a connection offer that names a relay ([Auth and origin](#auth-and-origin)). T3: tickets, cookies or bearer tokens, and server-issued pairing links (same section). Topologies are the subject of [Clients and topologies](13-clients-and-topologies.md#topologies). | (a) A static token. (b) Device pairing with revocable per-device credentials. (c) A relay. `Inference:` (a) is simplest but hard to revoke per device; (b) suits a phone; (c) adds a third party to trust and operate. |
| **HP-03** | **Multi-client ownership of a chat.** What happens when two clients act on one chat, for example both answer one dialog? | pi accepts the first answer and silently drops later ones (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-mode.ts:774-779`). The desktop removes the card from `pendingDialogs` and pushes the new state when it answers (`gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:193-198`). herdr-web-ui gives each connection an `interact` or `observe` role (`herdr-web-ui@7c5fe4e:shared/protocol.ts:587-591`). | (a) First answer wins; later ones get `dialog_not_pending`, and every subscriber sees the card disappear. (b) One controlling client per chat; the others observe. `Inference:` (a) needs no new concept and matches pi's behavior; (b) avoids surprises but needs a handover. Sending prompts from two clients raises the same question. |
| **HP-04** | **Backpressure limits.** How much may the service buffer per client before it drops or disconnects? | Paseo: 64 MiB per socket in code (its architecture doc says 8 MiB), then terminate. T3: 1,000 items or 8 MiB per subscription. herdr-web-ui: 256 KiB credit, 1 MiB hard budget, 2 s stall ([Reconnect and replay](#reconnect-and-replay)). | `Inference:` with snapshots, keeping only the latest snapshot per chat and client bounds memory by the number of subscriptions; a size cap on a single snapshot and a stall timeout remain to be chosen. |
| **HP-05** | **Reuse an existing framing?** JSON-RPC 2.0, pi's own RPC shape or a custom envelope. | JSON-RPC 2.0 defines requests, responses, notifications (requests with no `id`, which get no response) and an error object whose `code` "MUST be an integer", with `message` and optional `data` (https://www.jsonrpc.org/specification, accessed 2026-10-05). pi's RPC uses `type`, an optional `id` and `response` records with `success` and `error` ([04, Correlation and errors](04-rpc-contract.md#correlation-and-errors)). T3 uses its framework's RPC protocol ([Transport and framing](#transport-and-framing)). | `Inference:` JSON-RPC brings libraries and a known shape; pushes become notifications and `retryable` lives in `data`, but it defines no handshake or subscription semantics, so those stay custom. Mirroring pi's shape keeps one style across both hops. A framework protocol ties every client to that framework. |
| **HP-06** | **Full snapshots or deltas?** | Every push is a full `ChatState` today ([Reconnect and replay](#reconnect-and-replay)). | `Inference:` snapshots keep reconnects and slow clients trivial; deltas cut bandwidth on long chats over mobile networks but bring back cursors and replay, as in Paseo and T3. A middle option: snapshots per message (only the changed message travels). |
| **HP-07** | **A credential on loopback?** Proposal 0004 requires a token or pairing only off loopback. | [Proposal 0004](07-proposals/0004-host-service.md#proposal) binds to loopback by default: "Any other bind requires a token or device pairing". Paseo admits every `hello` as owner when no password is configured (`paseo@485221b:packages/server/src/server/session-admission-auth.ts:18-20`); T3 authenticates every `/ws` upgrade (`t3code@eac52f0:apps/server/src/auth/EnvironmentAuth.ts:1075-1094`). | (a) Keep 0004's default: no credential on loopback. (b) Require a per-user token even on loopback. `Inference:` (a) leaves the socket open to every local process and user ([Auth and origin](#auth-and-origin)); (b) costs one token file and a way to hand it to each local client. |

## Not covered here

- **The architecture** (component map, placement, configuration, migration): [11-host-service.md](11-host-service.md).
- **The service ↔ gentle-shell contract**: [04-rpc-contract.md](04-rpc-contract.md), unchanged.
- **Clients and topologies** (local, LAN, remote, mobile): [13-clients-and-topologies.md](13-clients-and-topologies.md).

## Sources

**Pinned repositories** (read-only clones; `repo@sha:path:line`):

| Name in citations | Repository | Commit |
|---|---|---|
| `gentle-shell-desktop` | `Gentleman-Programming/gentle-shell-desktop` | `5ab4a00` |
| `gentle-shell` | `Gentleman-Programming/gentle-shell` (`main`, package version 4.0.0) | `ac67159` |
| `pi` | `earendil-works/pi` (v1.0.0) | `a13d35a` |
| `paseo` | `getpaseo/paseo` | `485221b` |
| `t3code` | `pingdotgg/t3code` | `eac52f0` |
| `herdr-web-ui` | `devswha/herdr-web-ui` | `7c5fe4e` |
| `open-pi-viewer` | `gonzalez962/open-pi-viewer` | `908245a` |

**Web** (accessed 2026-10-05):

- Electron `ipcMain` documentation: https://www.electronjs.org/docs/latest/api/ipc-main
- JSON-RPC 2.0 specification: https://www.jsonrpc.org/specification

**Corpus:** [proposal 0004](07-proposals/0004-host-service.md), [host service architecture](11-host-service.md), [RPC contract](04-rpc-contract.md), [current architecture](03-architecture/current.md), [audit](03-architecture/audit.md), [roadmap](09-roadmap.md).
