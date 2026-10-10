# 0005. Per-chat session process design

> Status: proposed.

| Field | Value |
|---|---|
| Author | memoTux (@memotux, community) |
| Source | [PR #30](https://github.com/Gentleman-Programming/gentle-shell-desktop/pull/30); numbered as proposal 0005 by [issue #15](https://github.com/matraket/gentle-shell-desktop/issues/15) |
| Status | `proposed` (only the maintainer moves it to `accepted` or `declined`) |
| Principles | vision P4 **[maintainer]** (helpers stay tied to the chat that started them) |
| Related | [vision Q3](../00-vision.md#open-questions-for-the-maintainer) **[open question]**; [roadmap F1](../09-roadmap.md#f1-foundations-several-chats-at-once-community-proposal) **[community]** |

## Problem

Every chat session is owned by a single-session host, so several chats cannot run at once:

- `ChatHost` owns exactly one live `PiSession` with no registry (`gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts:70`; [audit A3](../03-architecture/audit.md#a3-single-session-host-with-positional-message-ids)).
- Message ids are positional, so concurrent chats would collide ([audit A3](../03-architecture/audit.md#a3-single-session-host-with-positional-message-ids); [gap G9](../04-rpc-contract.md#gaps-the-desktop-needs)).

PR #30 designed the target state for this host. This proposal records that design, with one correction: each chat is at least two OS processes, not one (see [Proposal](#proposal)).

## Proposal

**[community]** PR #30 proposes one supervisor in Electron main owning one RPC child per active chat:

```text
Electron main (supervisor: registry, lifecycle, authorization, logs)
  ├── chat A: gentle-shell --mode rpc --> pi (at least two OS processes)
  └── chat B: gentle-shell --mode rpc --> pi (at least two OS processes)
```

- **One child per active conversation.** Each active chat gets its own long-lived RPC child, owned and supervised by main; a renderer never spawns pi (`pr30:docs/pi-electron-session-process-design.md:7`). A child serves one conversation for its lifetime and is never shared via `switch_session`; reopening starts a new process (`pr30:docs/pi-electron-session-process-design.md:24`).
- **At least two OS processes per chat (correction).** PR #30 says one operating-system process (`pr30:docs/pi-electron-session-process-design.md:35`; `pr30:docs/system-design.md:108`). Electron main launches the `gentle-shell` launcher (`gentle-shell --mode rpc`) (`desktop@5ab4a00:src/main/domain/session/PiSession.ts:127-135`), and the launcher spawns pi with inherited stdio (`gs@ac67159:bin/gentle-shell.mjs:1396`, `:1403-1408`; [process chain](../04-rpc-contract.md#process-chain)). `Inference:` child caps and eviction policies must count at least two processes per chat, not one; `Inference:` on Windows, the gentle-shell launcher implementation's `shell: launchPlan.shell` may add `cmd.exe` for a batch shim, so no exact count beyond at least two is asserted.
- **Alternatives discussed in PR #30 (not decided here).** A shared child via `switch_session` stays open under [vision Q3](../00-vision.md#open-questions-for-the-maintainer): PR #30 prefers isolation unless resource evidence outweighs it, but this proposal does not decide it. Pi embedded in main via SDK is PR #30's rejected position for an RPC integration (`pr30:docs/system-design.md:350-352`).
- **Deferred: Utility Process host.** Hosting the registry in a Utility Process is deferred until measured workload or reliability evidence justifies it (`pr30:docs/system-design.md:353`); where the owner lives is [issue #2](https://github.com/matraket/gentle-shell-desktop/issues/2), still open.

## Runtime requirements

What the desktop must build before this design can run, in dependency order:

| # | Need | Source |
|---|---|---|
| R1 | A session registry keyed by conversation id: at most one active child per id, no cross-routing, idempotent close, settled requests and dialogs on exit; never key authorization or identity on the session file path or PID; scope child ids and command ids so concurrent chats cannot collide, since positional message ids would otherwise clash ([audit A3](../03-architecture/audit.md#a3-single-session-host-with-positional-message-ids)) | `pr30:docs/pi-electron-session-process-design.md:114-123` |
| R2 | PR #30 proposes a generation or attachment token per child, so late output from a stopped child cannot update a newer attachment, while [issue #6](https://github.com/matraket/gentle-shell-desktop/issues/6) also leaves a monotonic revision as an option | `pr30:docs/pi-electron-session-process-design.md:168` |
| R3 | No two live writers on one session file: prevent duplicate ownership within one instance, or define an explicit read-only or multi-attachment behavior | `pr30:docs/pi-electron-session-process-design.md:64`, `:123` |
| R4 | PR #30 proposes an allowlisted child environment and an explicit working directory, while [issue #3](https://github.com/matraket/gentle-shell-desktop/issues/3) also leaves full environment inheritance as an option | `pr30:docs/pi-electron-session-process-design.md:176` |
| R5 | Bounded graceful shutdown and a failure matrix: an individual child failure marks only its conversation and reports once, while app shutdown stops all active chains under a bounded deadline, with redacted diagnostics | `pr30:docs/pi-electron-session-process-design.md:186-198` |
| R6 | A verification ladder: protocol and framing tests, fake-child transport and supervisor tests (including LF-only framing with embedded U+2028 and U+2029), IPC and preload tests, UI and component tests, Electron integration tests, packaged smoke tests, and real-child smoke tests | `pr30:docs/system-design.md:326-334`; `pr30:docs/pi-electron-session-process-design.md:214-222` |
| R7 | Lifecycle UI states per chat — `accepted`, `streaming`, `settled`, `failed`, `disconnected` — clearly proposed, not accepted | `pr30:docs/system-design.md:382` |

Open topics with no dedicated issue: session persistence, deletion, duplicate opens and recovery; extension UI methods, widgets, timeouts and cancellation; the supported pi version and launcher resolution and update (`pr30:docs/system-design.md:365-369`).

## Prior art in the ecosystem

- **pi `--mode rpc`:** a long-lived child-process control interface, one stdin/stdout/stderr stream triple per child (`pr30:docs/pi-electron-session-process-design.md:59`). One child per chat aligns with the protocol instead of multiplexing sessions through `switch_session`.
- **Electron process roles:** main supervises, preload exposes a narrow typed API, renderer presents (`pr30:docs/pi-electron-session-process-design.md:68-96`); child records stay untrusted (`pr30:docs/pi-electron-session-process-design.md:200-208`). No new pattern is invented here.

## Relationship to proposal 0004

The two proposals converge on one child per chat but answer different layers: this one runs from pi to the session owner (one supervised child per chat); [0004](0004-host-service.md) runs from the client to a shared service (many clients, one registry). The per-chat shape in 0004 remains proposed, pending [vision Q3](../00-vision.md#open-questions-for-the-maintainer) and tracked for multi-chat delivery by [roadmap F1](../09-roadmap.md#f1-foundations-several-chats-at-once-community-proposal). Proposal 0004 does not yet cite this proposal; that cross-reference belongs to the [issue #1](https://github.com/matraket/gentle-shell-desktop/issues/1) reconciliation. Where they differ, the decision issues below apply; this proposal does not choose host placement.

## Open decisions

Each row is an open issue; both alternatives stay on the table until the maintainer decides:

| Issue | Question | Alternatives left open |
|---|---|---|
| [issue #2](https://github.com/matraket/gentle-shell-desktop/issues/2) | Where the session owner lives | Supervisor in main (Utility Process only on measured evidence) vs a host service, separate or embedded in main, with a Utility Process as a third placement |
| [issue #3](https://github.com/matraket/gentle-shell-desktop/issues/3) | Which environment the child inherits | Explicit allowlist and working directory vs inheriting the whole environment |
| [issue #4](https://github.com/matraket/gentle-shell-desktop/issues/4) | How many children stay alive | Keep idle children alive, with a cap and a warn, queue or evict policy, vs stop them and reopen on demand |
| [issue #5](https://github.com/matraket/gentle-shell-desktop/issues/5) | Two writers on one session file | Prevent double ownership within one instance vs an explicit read-only or multi-attachment behavior |
| [issue #6](https://github.com/matraket/gentle-shell-desktop/issues/6) | Late events after a child restart | Generation or attachment token per child vs a per-chat revision in every snapshot |
| [issue #7](https://github.com/matraket/gentle-shell-desktop/issues/7) | Catching up after a service restart | Durable cursor (`get_entries` with `since`), which may combine with snapshots, vs full snapshots with no client-side cursor; how the service rebuilds its state from pi after a restart is still unwritten |
| [issue #8](https://github.com/matraket/gentle-shell-desktop/issues/8) | Dialog ownership across windows or clients | One window owns the dialogs and close behavior vs first answer wins with `dialog_not_pending` for the second |
| [issue #9](https://github.com/matraket/gentle-shell-desktop/issues/9) | Validating the IPC sender | Validate the sender frame in main vs trust the app's own window and authenticate only the socket |

## Sources

Citation prefixes follow [issue #1](https://github.com/matraket/gentle-shell-desktop/issues/1): `pr30:` refers to PR #30.

Signed-off-by: memoTux (@memotux), author of PR #30.
