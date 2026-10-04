# Clients and topologies

> Status: draft (community proposal, awaiting maintainer validation).

> **[community] design sketch, not current state.** This page describes which clients would connect to the shared local host service proposed in [proposal 0004](07-proposals/0004-host-service.md), and where the clients, the service and the runtime could run. The architecture is in [11-host-service.md](11-host-service.md) and the client protocol in [12-host-protocol.md](12-host-protocol.md). Nothing here exists in the desktop repository today, and nothing here is decided. Remote and mobile clients are outside the corpus scope until the maintainer answers [vision Q9](00-vision.md#open-questions-for-the-maintainer).

**In one paragraph.** **[community]** Three kinds of client would reach one host service: the Electron window, a browser tab and a future mobile app. They differ in how they find the service, how they prove who they are, and which parts of the [host protocol](12-host-protocol.md) they lean on. Five topologies place the clients, the service and the runtime: **T1**, everything on one machine over loopback; **T2**, another device of the same user reaching that machine over an SSH tunnel, Tailscale or a relay; **T3**, the service inside WSL with a Windows client; **T4**, a chat executed on another machine behind the service, as gentle-mesh proposes (later, and only with its author's answers and the maintainer's approval); **T5**, a hosted multi-user service, out of scope (`Inference:` a different product). T1 is the baseline; T2 and T3 reuse it with a different route to the port. `Inference:` a mobile app depends on T2, because a phone cannot run gentle-shell itself (the gentle-mesh author's claim, `gentle-mesh@2d1d324:propuesta-discord-mobile.txt:12`; see [Future mobile app](#future-mobile-app)). Which topologies a first version supports is open (CT-01 to CT-07).

## How to read this page

| Label | Meaning |
|---|---|
| **[maintainer]** | Stated in the maintainer's desktop repo documents or Discord messages. |
| **[community]** | Proposed by the community. Not decided. |
| `Inference:` | Reasoning from cited evidence, not a stated fact. "(not run)" means nothing was built or executed. |
| `UNVERIFIED:` | Checked but not confirmed; the text says what was checked. |

- **Citation keys.** Code and docs are cited as `repo@shortsha:path:line`: `gentle-shell-desktop@5ab4a00` (the source is unchanged on this branch), `gentle-shell@ac67159` (gentle-shell `main`, package version 4.0.0), `paseo@485221b`, `t3code@eac52f0`, `herdr@5da0a01`, `herdr-web-ui@7c5fe4e` and `gentle-mesh@2d1d324` (`main`) or `gentle-mesh@f52335e` (integration branch `feat/rfc-002-settlement`). `:N` after a full citation repeats its file. Microsoft documentation is cited by URL with its access date. Corpus pages are linked by relative path.
- **Qualified IDs.** IDs from other pages carry their page: `vision Q9`, `audit A1`, `PLAT-07`, `milestone M5`. **B1–B6** are the runtime requirements of [proposal 0004](07-proposals/0004-host-service.md#runtime-requirements) and **HP-01 to HP-07** the open questions of [12](12-host-protocol.md#open-questions), written bare as on those pages. **T1–T5** are this page's topologies and are written bare here; elsewhere write `topology T1`, because `inventory T1` already exists. **CT-01 to CT-07** are this page's open questions; the `CT-` prefix is unique in the corpus.
- **Names.** "T3 Code" is the product (`pingdotgg/t3code`); a bare "T3" on this page is always topology T3.
- **Method.** Static reading only, as in the [audit](03-architecture/audit.md#method-and-scope). Nothing was prototyped, and no topology was set up.

## At a glance

| Question | Answer | Evidence |
|---|---|---|
| Which clients? | **[community]** The Electron window, a browser tab on the same machine, and a future mobile app. | [proposal 0004](07-proposals/0004-host-service.md#proposal) |
| How does the Electron window connect? | Under placement (a), over WebSocket like any other client; under placement (b), it can keep the preload bridge. | [11, Process placement](11-host-service.md#process-placement-open) |
| Which topologies? | T1 loopback, T2 remote access to your own machine, T3 service inside WSL, T4 remote execution behind the service (later), T5 hosted multi-user (out of scope). | [Topologies](#topologies) |
| What is the baseline? | T1: one machine, the service bound to `127.0.0.1`. | [proposal 0004](07-proposals/0004-host-service.md#proposal); [T1](#t1-all-on-one-machine-loopback) |
| Can a phone run the agent? | `Inference:` no. gentle-shell is a Node program, and the gentle-mesh mobile proposal states that mobile systems do not allow arbitrary local Node subprocesses (its author's claim, not checked). A phone is a remote client (T2). | [Future mobile app](#future-mobile-app); `gentle-mesh@2d1d324:propuesta-discord-mobile.txt:12` |
| What decides remote auth? | HP-02 (pairing, token or relay) and HP-07 (a credential on loopback). | [12, Open questions](12-host-protocol.md#open-questions) |
| Is gentle-mesh part of it? | **[community]** As optional remote execution behind the service, later, pending its author's answers and the maintainer's approval. | [T4](#t4-remote-execution-behind-the-service-gentle-mesh-later) |
| Is a hosted multi-user service part of it? | No. `Inference:` it is a different product. Whether it is wanted at all is a maintainer question. | [T5](#t5-hosted-multi-user-out-of-scope) |

## Clients

| Client | How it finds the service | How it authenticates | What it needs from the [host protocol](12-host-protocol.md) | Exists today? |
|---|---|---|---|---|
| **Electron window** | (a): the app starts the service or connects to a running one. (b): the host is in-process. | (a): a credential the app holds (HP-07). (b): none for the window; IPC stays trusted. | (a): everything. (b): nothing; the other clients still need the socket. | The window and the preload bridge exist (`gentle-shell-desktop@5ab4a00:src/preload/index.ts:4`); the WebSocket bridge does not. |
| **Browser tab, same machine** | A loopback URL, `http://127.0.0.1:<port>`. | An `Origin` allow-list, plus a credential if HP-07 requires one. | Everything; reconnect by re-subscribing. | `pnpm dev:web` runs the renderer in a browser against an in-memory mock (`gentle-shell-desktop@5ab4a00:package.json:12`; `gentle-shell-desktop@5ab4a00:src/renderer/shared/bridge/useBridge.ts:11`). |
| **Future mobile app** | A pairing link or QR code that carries the address (T2). | Device pairing with a revocable per-device credential (HP-02). | Everything, with tolerance for version skew (HP-01) and for mobile networks (HP-04, HP-06). | No. |

### Electron window

- **Placement (a), separate service.** **[community]** The window becomes a WebSocket client like a browser tab ([11, Process placement](11-host-service.md#process-placement-open)). The renderer already picks its bridge at one line, `window.gentle ?? mockBridge` (`gentle-shell-desktop@5ab4a00:src/renderer/shared/bridge/useBridge.ts:11`); a WebSocket bridge is a third choice there ([11, The renderer side](11-host-service.md#the-renderer-side)).
- **Placement (b), embedded host.** The window keeps the preload bridge over Electron IPC, and the host also listens on a WebSocket port for the other clients ([11, Process placement](11-host-service.md#process-placement-open)). `Inference:` the window then needs nothing from the host protocol, but two client endpoints must stay in step ([11, Process placement](11-host-service.md#process-placement-open), row "One port, one endpoint").
- **Finding the service.** Under (a) the app starts the service, or connects to one that is already running ([11, Process placement](11-host-service.md#process-placement-open)). Precedent: Paseo's desktop reuses a running daemon and restarts a daemon it owns on a version mismatch (`paseo@485221b:packages/desktop/src/daemon/daemon-manager.ts:266-267`, `:291-300`). Paseo's supervisor publishes "its ready worker's endpoint in `paseo.pid`", and its CLI "trusts only that live record" (`paseo@485221b:docs/architecture.md:475`). `Inference:` a service on a non-fixed port needs such a record so that a client started later can find it.
- **Authentication.** `Inference:` the app that starts the service can hand it a credential and read the address back, so the window needs no pairing. Whether a loopback client needs a credential at all is HP-07.
- **Renderer constraints.** The renderer's CSP has no `connect-src`, so a socket to `ws://127.0.0.1:<port>` needs an explicit entry ([12, Auth and origin](12-host-protocol.md#auth-and-origin)). Which `Origin` an Electron renderer loaded from a file sends is `UNVERIFIED` there.

### Browser tab on the same machine

- **What it is.** The same renderer, loaded in a browser and connected to the service. Today the browser build talks to an in-memory mock only (`gentle-shell-desktop@5ab4a00:src/renderer/shared/bridge/useBridge.ts:4-11`, as cited in [proposal 0004](07-proposals/0004-host-service.md#problem)).
- **Finding the service.** The user opens a loopback URL. Precedents:
  - T3 Code: "run `t3` to start the server and open the local web app" (`t3code@eac52f0:README.md:37`).
  - Paseo: the daemon "can serve the browser web app itself, from the same address it already uses for the API" (`paseo@485221b:public-docs/web-ui.md:11`), so "the UI you serve always matches your daemon version" (`:19`). It is "off by default" (`:23`).
- `Inference:` if the service serves the renderer itself, the page and the socket share one origin, the `Origin` allow-list has one entry to trust, and client and service cannot drift apart in version. Whether to do so is CT-05.
- **Authentication.** An `Origin` allow-list stops other web pages in the same browser from opening the socket, but not other local processes ([12, Auth and origin](12-host-protocol.md#auth-and-origin)). If HP-07 requires a loopback credential, the tab needs a way to receive it; `Inference:` a one-time link that the service prints or opens, as T3 Code's pairing links do for other devices ([T2](#t2-remote-access-to-your-own-machine)).
- **What it needs from 12.** Every request and push of the [mapping table](12-host-protocol.md#mapping-table). A tab is reloaded and closed freely, so it relies on [reconnect and replay](12-host-protocol.md#reconnect-and-replay): `hello`, then `subscribe` for each chat it shows.

### Future mobile app

- **Why it would not run gentle-shell on the phone.** gentle-shell's binary is a Node script (`gentle-shell@ac67159:package.json:7-8`; `gentle-shell@ac67159:bin/gentle-shell.mjs:1`) that requires Node 22.19 or newer (`gentle-shell@ac67159:package.json:101-103`). The gentle-mesh mobile proposal states that "Los sistemas operativos móviles (iOS/Android) no permiten gestionar subprocesos locales arbitrarios de Node ni correr contenedores Docker." (mobile operating systems do not allow managing arbitrary local Node subprocesses or running Docker containers; `gentle-mesh@2d1d324:propuesta-discord-mobile.txt:12`). That is its author's statement; this page did not check it against Apple's or Google's documentation. `Inference:` a mobile app is therefore a remote client of a service on another machine, and depends on T2 (or on T4 for execution elsewhere).
- **Precedents.** Both precedents ship a mobile client that connects to a server on another machine: Paseo's Expo app for "iOS, Android, web" (`paseo@485221b:README.md:173`), and T3 Code, whose remote access connects "a phone, browser, or another desktop app to T3 Code running on a different machine" (`t3code@eac52f0:docs/user/remote-access.md:3-4`).
- **Finding the service.** A pairing link or QR code. T3 Code: "Scan the QR code on your phone or paste the pairing URL" (`t3code@eac52f0:docs/user/remote-access.md:54`). Paseo: "The QR code or pairing link is the trust anchor. It contains the daemon's public key" (`paseo@485221b:public-docs/security.md:53`). herdr-web-ui: a six-digit code "that lives ten minutes and a QR code that carries it" (`herdr-web-ui@7c5fe4e:docs/guide.md:257`).
- **Authentication.** Device pairing with a per-device credential that can be revoked (HP-02, option (b)). T3 Code: "Pairing authorizes that device for future connections" (`t3code@eac52f0:docs/user/remote-access.md:59`), and the host can "revoke client sessions" (`:148-150`).
- **What it needs from 12.** `Inference:` an app-store build updates on its own schedule, so it needs a versioning rule that tolerates skew (HP-01). On a mobile network, full snapshots cost bandwidth (HP-06) and slow links need a buffer bound (HP-04). Two clients may act on one chat, for example a phone and the desktop answering one dialog (HP-03).

## Topologies

| | Clients | Service | Runtime (`gentle-shell --mode rpc` children) | Route to the service | In this proposal |
|---|---|---|---|---|---|
| **T1** | Same machine | Same machine | Same machine | Loopback | **[community]** baseline |
| **T2** | Another device of the same user | The user's machine | The user's machine | SSH tunnel, Tailscale, LAN, relay | **[community]** optional, open (CT-02) |
| **T3** | Windows (browser or Electron) | Inside WSL | Inside WSL | WSL localhost forwarding (`UNVERIFIED:` reliability), or the distribution's IP address | **[community]** option for Windows, open (CT-04) |
| **T4** | Any of the above | The user's machine | Another machine | gentle-mesh, behind the service | **[community]** later, pending its author and the maintainer (CT-06) |
| **T5** | Many users | A hosted server | A hosted server | The internet | Out of scope (CT-07) |

### T1 All on one machine (loopback)

```text
┌──────────────────────── one machine, one user ────────────────────────┐
│ Electron window ─┐                                                    │
│ Browser tab ─────┼─ ws://127.0.0.1:<port> ─► host service ─► children │
│ (other local     │                                                    │
│  processes) ─────┘  reachable too, unless a credential is required    │
└───────────────────────────────────────────────────────────────────────┘
```

- **What it is.** **[community]** Proposal 0004's default: the service "Binds to loopback by default" ([proposal 0004](07-proposals/0004-host-service.md#proposal)). Under placement (a), the host moves out of Electron's main process; under (b), it stays in main and also listens on loopback.
- **Auth.** An `Origin` allow-list for browsers; argument validation on every frame (B4). Whether loopback clients need a credential is HP-07: Paseo admits every `hello` as owner when no password is configured, and T3 Code authenticates every `/ws` upgrade ([12, Open questions](12-host-protocol.md#open-questions)).
- **Precedents.** Paseo listens on `127.0.0.1:6767` by default (`paseo@485221b:packages/server/src/server/config.ts:470`); its security page says "On localhost this is fine, only local processes have access" (`paseo@485221b:public-docs/security.md:87`). T3 Code binds to `127.0.0.1` (`t3code@eac52f0:apps/server/src/server.ts:249`). herdr-web-ui "listens on `127.0.0.1` by default, which means only this computer" (`herdr-web-ui@7c5fe4e:docs/guide.md:254`).
- **Risks.**
  - `Inference:` "only local processes" still means every process of every local user; that is the case HP-07 weighs.
  - `Inference:` a browser page from another site can try to reach a loopback port; the `Origin` allow-list is what stops it ([12, Auth and origin](12-host-protocol.md#auth-and-origin)). Paseo adds a `Host` allow-list against DNS rebinding, because "CORS is not a complete security boundary" (`paseo@485221b:public-docs/security.md:75`, `:77`).
  - The counter-example is open-pi-viewer's server, bound to `0.0.0.0` with no origin check ([proposal 0004, Alternatives considered and rejected](07-proposals/0004-host-service.md#alternatives-considered-and-rejected)).

### T2 Remote access to your own machine

```text
phone / laptop ──► route ──► user's machine: 127.0.0.1:<port> ─► host service ─► children
                    │
                    ├─ SSH tunnel (ssh -L)          service stays on loopback
                    ├─ Tailscale serve / VPN        service stays on loopback, or binds the VPN address
                    ├─ LAN bind (0.0.0.0)           service exposed to the LAN
                    └─ relay (outbound from host)   service stays on loopback; a third party routes bytes
```

**[community]** Another device of the same user reaches the service on the user's machine. The agents, files and sessions stay on that machine. Routes, with their precedents:

| Route | What gets a client in | Precedent | Evidence |
|---|---|---|---|
| **SSH tunnel** | The service sees a loopback connection; the SSH login is the gate. | herdr-web-ui: `ssh -L 7317:127.0.0.1:7317 host`, "Nothing needed" without a token. Paseo's desktop: "SSH only tunnels to an already-running daemon". T3 Code's desktop "starts or reuses a server there and opens the port forward for you". | `herdr-web-ui@7c5fe4e:docs/guide.md:263`; `paseo@485221b:docs/architecture.md:116`; `t3code@eac52f0:docs/user/remote-access.md:121-126` |
| **Tailscale serve** | The service stays on `127.0.0.1`; Tailscale adds an HTTPS address on the tailnet. | herdr-web-ui: "keep the server on `127.0.0.1` and let Tailscale add the HTTPS address" (`tailscale serve --bg --https=443 http://127.0.0.1:7317`). Identity: "`tailscale serve` states the requesting device's Tailscale login in a header"; a login that matches the PC's own gets in, another is refused. T3 Code: `t3 serve --tailscale-serve` or `t3 pair --tailscale`. | `herdr-web-ui@7c5fe4e:docs/guide.md:204`, `:207`, `:256`; `t3code@eac52f0:docs/user/remote-access.md:83-100` |
| **VPN or LAN address** | A password, a token or a paired device. | Paseo: "Bind the daemon to its VPN address, set a Paseo password", and "Never bind to 0.0.0.0 without a password". herdr-web-ui: a LAN bind needs "Pair each device, or set a token". T3 Code: `t3 serve --host <private-ip>`, then a pairing link. | `paseo@485221b:public-docs/security.md:67`, `:149`; `herdr-web-ui@7c5fe4e:docs/guide.md:266`; `t3code@eac52f0:docs/user/remote-access.md:41-59` |
| **Relay** | The host connects outbound; clients meet it at the relay. | Paseo: "No open ports required"; traffic is end-to-end encrypted and "The relay is designed to be untrusted"; the relay "sees only: IP addresses, timing, message sizes, and session IDs"; it "is off on new installations". T3 Code's T3 Connect: an account-based service that makes an environment reachable "without setting up router forwarding". | `paseo@485221b:public-docs/security.md:21`, `:28`, `:30`, `:40`; `t3code@eac52f0:docs/user/remote-access.md:6-10` |
| **Public proxy** | A token over HTTPS. | herdr-web-ui: "Set a token, with HTTPS", "Never `tailscale funnel` it". | `herdr-web-ui@7c5fe4e:docs/guide.md:267` |

- **Herdr's own position.** Herdr itself offers no remote UI for phones: "Herdr works on your phone without a mobile app or web dashboard. Install any SSH client, connect to the machine where your agents run, and start Herdr there" (`herdr@5da0a01:docs/next/website/src/content/docs/how-to-work.mdx:49`). `Inference:` the same path works for gentle-shell today, with no service at all: SSH into the machine and run its terminal UI. That gives the terminal experience on a phone, not the desktop's ask cards, helpers panel or ODD view. `UNVERIFIED:` how gentle-shell's TUI renders on a narrow phone terminal; not tried.
- **HTTPS for a phone.** herdr-web-ui: "a phone needs two things Tailscale gives at once: a way to reach the PC from outside your network, and HTTPS, which installing the app and push alerts both require" (`herdr-web-ui@7c5fe4e:docs/guide.md:435`). T3 Code: its hosted web app "needs an HTTPS endpoint" (`t3code@eac52f0:docs/user/remote-access.md:113`).
- **Auth.** This is HP-02: a static token, device pairing, or a relay ([12, Open questions](12-host-protocol.md#open-questions)). The precedents combine them: herdr-web-ui accepts a Tailscale identity, a paired device or a token (`herdr-web-ui@7c5fe4e:docs/guide.md:256-258`); Paseo a password, a local credential or relay pairing ([12, Auth and origin](12-host-protocol.md#auth-and-origin)); T3 Code pairing links and revocable sessions (`t3code@eac52f0:docs/user/remote-access.md:146-151`).
- **Risks.**
  - `Inference:` anyone who reaches the service can drive an agent with the user's files and credentials; herdr-web-ui says the same of its terminals: "Anyone who can reach the server can type into your terminals" (`herdr-web-ui@7c5fe4e:docs/guide.md:254`).
  - A LAN bind is open until something closes it: in herdr-web-ui, "Until the first device is paired, and with no token set, a LAN or proxied address is open to anyone who reaches it" (`herdr-web-ui@7c5fe4e:docs/guide.md:269`).
  - Password auth "protects access, not confidentiality" (`paseo@485221b:public-docs/security.md:98`). `Inference:` a plain `ws://` socket off loopback needs a VPN, a tunnel or TLS around it.
  - Pairing secrets leak: T3 Code asks users to "Treat pairing URLs and authorization codes as passwords" (`t3code@eac52f0:docs/user/remote-access.md:172`).

### T3 Service inside WSL

**[community]** On Windows, the service and the runtime run inside a WSL distribution; the client is a Windows browser or the Electron app on Windows.

```text
┌──────────────── Windows ────────────────┐   ┌────────────── WSL 2 distribution ───────────────┐
│ Electron app (.exe) ─┐                  │   │                                                  │
│ Browser (Edge, ...) ─┴─ localhost:<port>┼──►│ host service on 127.0.0.1:<port> ─► children ─► pi │
└─────────────────────────────────────────┘   └──────────────────────────────────────────────────┘
                     WSL localhost forwarding (NAT mode) or mirrored networking
```

- **Relation to [10-platforms](10-platforms.md#wsl-topologies).** Platforms topology B is "Desktop native, runtime inside WSL": the desktop on Windows spawns the runtime through `wsl.exe`, translates `--session` and `--home` paths, forwards `GENTLE_SHELL_INTERACTIVE_HOST` through `WSLENV`, and reads sessions through `\\wsl$` ([10, WSL topologies](10-platforms.md#wsl-topologies)). Topology T3 keeps topology B's split, Windows client and Linux runtime, but moves the cut: the service runs next to the runtime, and only a socket crosses the boundary.
- `Inference:` (not run) inside the distribution the service spawns `gentle-shell` as on Linux, with Linux paths, environment and homes, so the `wsl.exe` spawn, path translation and `WSLENV` rows of topology B no longer apply to the desktop. The session listing moves into the service with the domain ([11, Responsibilities](11-host-service.md#responsibilities)), so it reads the Linux homes directly; that removes the cause of PLAT-07 ("The session list reads the wrong home when the runtime is in WSL", [10, Risks](10-platforms.md#risks)). The DrvFS file-mode limit of PLAT-06 stays: it depends on where the repository is, not on where the service runs.
- **WSL localhost forwarding.** Microsoft: "If you are building a networking app (for example an app running on a NodeJS or SQL server) in your Linux distribution, you can access it from a Windows app (like your Edge or Chrome internet browser) using `localhost` (just like you normally would)." (https://learn.microsoft.com/en-us/windows/wsl/networking, section "Accessing Linux networking apps from Windows (localhost)", accessed 2026-10-05). The `.wslconfig` key `localhostForwarding` defaults to `true` and specifies "if ports bound to wildcard or localhost in the WSL 2 VM should be connectable from the host via `localhost:port`"; the sample file notes "Setting is ignored when networkingMode=mirrored" (https://learn.microsoft.com/en-us/windows/wsl/wsl-config, accessed 2026-10-05). In mirrored mode, "the Windows host and WSL2 VM can connect to each other using `localhost` (127.0.0.1)" (networking page, as above).
- **Precedent.** T3 Code runs its server inside WSL: "Choose a WSL distro in **Settings → Connections** to run agents and projects there. Install the provider CLIs inside that distro. T3 Code installs its own server runtime there automatically" (`t3code@eac52f0:docs/user/install.md:75-77`). Its desktop does not rely on localhost forwarding: it binds the server to `0.0.0.0` inside WSL because "wslhost forwarding is unreliable on some Windows hosts", and advertises the distribution's IP address as the URL the renderer uses; the code comment calls the exposed network "the WSL-vEthernet network, not the LAN" (`t3code@eac52f0:apps/desktop/src/backend/DesktopBackendConfiguration.ts:616-627`). `UNVERIFIED:` that a client on Windows can rely on localhost forwarding to a service bound to `127.0.0.1` inside WSL; Microsoft documents it, T3 Code's comment reports failures, and nothing was tried here. No pinned repository documents the same for Paseo (`rg -i wsl` over its `docs/` and `README.md`: 0 hits).
- **Auth.** As T1, with one difference. `Inference:` a service bound to `127.0.0.1` inside the distribution is reachable from Windows processes through `localhost` forwarding, so "local" spans two operating systems; that strengthens the case for a loopback credential (HP-07).
- **Who starts it.** Open (CT-04). `Inference:` the Electron app on Windows could start it through `wsl.exe`, as topology B starts the runtime ([10, WSL topologies](10-platforms.md#wsl-topologies)); or the distribution could start it with systemd, which WSL supports when `systemd=true` is set under `[boot]` in `/etc/wsl.conf` (https://learn.microsoft.com/en-us/windows/wsl/wsl-config, accessed 2026-10-05).
- **Risks.**
  - **Idle shutdown.** `.wslconfig` `[general]` `instanceIdleTimeout` is "The number of milliseconds that a distro is idle, before it is shut down", default `15000`, "Set to -1 to disable auto shutdown"; `[wsl2]` `vmIdleTimeout` is "The number of milliseconds that a VM is idle, before it is shut down", default `60000`, available on Windows 11 only (https://learn.microsoft.com/en-us/windows/wsl/wsl-config, accessed 2026-10-05). `UNVERIFIED:` whether a running background service counts as activity that keeps the distribution or the VM up; the page does not define "idle".
  - **LAN access is different.** From another device, WSL 2 "isn't the default case": it needs a port proxy or mirrored mode, and a remote client is "treated as connections from the Local Area Network (LAN)" (https://learn.microsoft.com/en-us/windows/wsl/networking, accessed 2026-10-05). `Inference:` T2 over a WSL-hosted service needs one more hop than on Linux or macOS.
  - `UNVERIFIED:` T3 as a whole: no topology was set up, and no pinned repository other than T3 Code documents a server inside WSL with a Windows client.

### T4 Remote execution behind the service (gentle-mesh, later)

**[community]** gentle-mesh is Rafael The Hutt's protocol proposal (`Rafaeldelinares/gentle-mesh`). [Proposal 0004](07-proposals/0004-host-service.md#optional-remote-execution-gentle-mesh) places it behind the session registry, as a way for the host service to run a chat on another machine. Clients would not change: they still speak the host protocol to one service. His stated goal is "un a2a con verificacion" (agent-to-agent with verification; Discord, Rafael The Hutt, 2026-10-04 23:20). This topology depends on his answers, which are pending, and on the maintainer's approval, which the gentle-mesh README itself requires (`gentle-mesh@2d1d324:README.md:22`).

```text
clients ─► host service (session registry) ─┬─► local child: gentle-shell --mode rpc
                                            └─► gentle-mesh coordinator ─► worker node ─► gentle-shell --mode rpc
```

**What gentle-mesh would need** for a chat to run on a remote node with the same experience as a local one. Facts are cited; the code below is identical on `2d1d324` and `f52335e` ([proposal 0004](07-proposals/0004-host-service.md#optional-remote-execution-gentle-mesh)), and `pkg/server/http/server.go` (`git diff` empty).

| Need | Why | Today | Evidence |
|---|---|---|---|
| **A gentle-shell runner** | The remote node must run `gentle-shell --mode rpc`, not bare pi, so helpers, ODD and dialogs exist. | Worker nodes fall back to a simulated runner. The coordinator's `pi` runner starts the binary once per task with `--print --mode json`; the binary defaults to `"pi"`, and the CLI never sets it. | `gentle-mesh@2d1d324:cmd/gentle-mesh/main.go:568-571`; `gentle-mesh@2d1d324:pkg/server/worker/server.go:40-41`; `gentle-mesh@2d1d324:cmd/gentle-mesh/main.go:306-311`; `gentle-mesh@2d1d324:pkg/server/runner/pi.go:63-67`, `:102`, `:175` |
| **An RPC passthrough, extension UI included** | Ask cards and the helpers feed travel as `extension_ui_request` and `setWidget` ([04, gentle-shell additions over RPC](04-rpc-contract.md#gentle-shell-additions-over-rpc)). | The `rpc` bridge handles `get_state`, `get_messages`, `new_session`, `abort` and `prompt`; "Unknown commands are ignored for forward compatibility." `extension_ui` does not occur in that file. | `gentle-mesh@2d1d324:pkg/client/bridge.go:225-252`; [proposal 0004](07-proposals/0004-host-service.md#optional-remote-execution-gentle-mesh) |
| **Working mTLS** | Node identity is the design's first objective: "Toda conexión usa mTLS; el CN/SAN del certificado coincide con el `agent_id` firmante." (every connection uses mTLS; the certificate's CN/SAN matches the signing `agent_id`). | `-require-mtls` sets `RequireMTLS`. `Start` builds a `tls.Config` with `RequireAndVerifyClientCert`, then calls `ListenAndServeTLS`. `Inference:` (read, not run) that config is never assigned to the HTTP server, since the file has no other reference to it, so client certificates are not required; no test sets `RequireMTLS` (`rg` over `*_test.go`, 0 hits). | `gentle-mesh@f52335e:docs/rfcs/002-objectives-and-non-goals.md:41`; `gentle-mesh@2d1d324:cmd/gentle-mesh/main.go:232-238`; `gentle-mesh@2d1d324:pkg/server/http/server.go:271-285` |
| **An origin allow-list** | A browser page must not drive a node ([T1](#t1-all-on-one-machine-loopback) risks). | The CORS middleware echoes any `Origin` into `Access-Control-Allow-Origin`, while the README describes an allow-list of Tauri, localhost and Tailscale origins. Bearer-token auth is added only when a token is configured. | `gentle-mesh@2d1d324:pkg/server/http/middleware.go:110-133`; `gentle-mesh@2d1d324:README.md:115`; `gentle-mesh@2d1d324:pkg/server/http/server.go:251-253` |
| **A LICENSE** | Without one, its code cannot be reused. | No LICENSE file on either commit (`git ls-tree`). The author said he will add MIT ("Mñn por la tarde cuando llegue a casa le pongo licence Mit"; Discord, Rafael The Hutt, 2026-10-04 23:20). | [proposal 0004](07-proposals/0004-host-service.md#optional-remote-execution-gentle-mesh) |

- **Status.** Questions on these points were sent to the author on 2026-10-04. He answered the license question; "Respecto al resto mñn lo miro y te respondo" (the rest, he will look at tomorrow and answer) (Discord, Rafael The Hutt, 2026-10-04 23:20). Nothing on this page assumes his answers.
- **Auth.** `Inference:` two trust boundaries: clients to the service (HP-02, HP-07), and the service to remote nodes (gentle-mesh's mTLS and tokens). A client never talks to a node directly.
- `Inference:` T4 also reaches mobile through the same service: the phone stays a client (T2), and execution may happen on a third machine. The gentle-mesh mobile proposal frames this as a "Modo Red / Mesh" over HTTP REST and SSE "a un servidor remoto, homelab o máquina secundaria (por ejemplo, vía Tailscale)" (to a remote server, homelab or secondary machine, for example over Tailscale; `gentle-mesh@2d1d324:propuesta-discord-mobile.txt:23`); in this proposal that front-end role belongs to the host protocol instead.

### T5 Hosted multi-user (out of scope)

**Out of scope.** Proposal 0004 leaves open what "web" means: "a browser UI for the local agent (optionally reached remotely), or a hosted multi-user service" ([proposal 0004, Open questions](07-proposals/0004-host-service.md#open-questions), question 1). This page covers the first reading only; the second is CT-07.

`Inference:` a hosted multi-user service is a different product, not a further topology of this one:

- **Accounts.** T1–T4 serve one user, whose own machine is the identity boundary; every credential above (token, pairing, Tailscale login) proves "this is the owner". A hosted service needs sign-up, sign-in and account recovery.
- **Isolation.** The children run an agent with shell access. On one user's machine that is the user's own risk; on a shared server, each user's agents, files and credentials must be isolated from every other user's.
- **Per-user homes.** The desktop resolves one home from the process's home directory and environment (`gentle-shell-desktop@5ab4a00:src/main/domain/home/home.ts:45-47`, `:56-67`), and the session listing mutates a process-wide `PI_CODING_AGENT_DIR` (B2, [audit A1](03-architecture/audit.md#a1-two-data-paths-to-pi-and-a-global-pi_coding_agent_dir-mutation)). A shared process would need a home, provider sign-ins and session store per user.
- **Billing and operations.** Someone pays for the compute and the model calls, and someone runs the servers.
- **Hosting the UI is not hosting the agents.** Both precedents host a web front end that connects to the user's own server: T3 Code's `app.t3.codes` "connects directly to your server" (`t3code@eac52f0:docs/user/remote-access.md:113-114`), and Paseo's daemon serves the UI "on infrastructure you control" instead of the hosted app at `app.paseo.sh` (`paseo@485221b:public-docs/web-ui.md:11`). `Inference:` a hosted static client fits T2; hosted execution is T5.

## Mobile

- **What it would need.** `Inference:` a native or web app that speaks the host protocol; a T2 route with HTTPS (herdr-web-ui, above); device pairing with revocation (HP-02); a versioning rule that tolerates an app-store build lagging behind the service (HP-01); and a decision on full snapshots over mobile networks (HP-06).
- **Which topology.** `Inference:` T2 always, since the runtime cannot run on the phone (the gentle-mesh author's claim, `gentle-mesh@2d1d324:propuesta-discord-mobile.txt:12`; see [Future mobile app](#future-mobile-app)); T4 if execution moves to a third machine.
- **Background limits.** The gentle-mesh mobile proposal notes that "Las políticas de ahorro de batería cierran procesos en segundo plano a los pocos segundos" (battery-saving policies close background processes within seconds; `gentle-mesh@2d1d324:propuesta-discord-mobile.txt:13`). `Inference:` the phone app will be disconnected often, so it relies on [reconnect and replay](12-host-protocol.md#reconnect-and-replay); a "needs you" alert while it is closed needs push notifications, which herdr-web-ui ties to HTTPS (`herdr-web-ui@7c5fe4e:docs/guide.md:204`).
- **The vision constraint.** The vision lists "Not, for now, a remote or mobile client" among what Gentle Desktop is not, and keeps mobile and remote access as an open question ([vision, What Gentle Desktop is not](00-vision.md#what-gentle-desktop-is-not); [vision Q9](00-vision.md#open-questions-for-the-maintainer)). This page is **[community]** framing and does not change that: it describes what a mobile client would need if the maintainer brings it into scope.

## Open questions

Facts are cited; judgments are `Inference:`. None of these is decided.

| ID | Question | Facts | Options and `Inference:` |
|---|---|---|---|
| **CT-01** | **Which topologies does a first version support?** | T1 is proposal 0004's default ([proposal 0004](07-proposals/0004-host-service.md#proposal)). | (a) T1 only. (b) T1 plus T3 on Windows. (c) T1 plus T2. `Inference:` (a) proves the service with the least exposure; T2 adds remote auth (HP-02) and T3 adds the WSL questions of CT-04. |
| **CT-02** | **Which remote routes does T2 document or build in?** | Precedents use SSH tunnels, Tailscale serve, LAN binds with a password or pairing, and relays ([T2](#t2-remote-access-to-your-own-machine)). | (a) Document SSH and Tailscale, build nothing. (b) Built-in pairing for LAN and VPN addresses. (c) A relay. `Inference:` (a) keeps the service on loopback; (c) adds a third party to trust and operate (HP-02). |
| **CT-03** | **Does a standalone service start at login?** | T3 Code runs as a per-user service on Linux and macOS, and "Windows background services are not supported" (`t3code@eac52f0:docs/user/background-service.md:3-4`, `:54`). Paseo's desktop stops the daemon it started on quit unless set to keep running ([11, Process placement](11-host-service.md#process-placement-open)). | (a) Only while the desktop app runs. (b) An opt-in login item per OS. `Inference:` (b) is what makes a browser-only or phone client useful when the app is closed. See [10, Host service](10-platforms.md#host-service-proposal-0004). |
| **CT-04** | **On Windows, does the service run on Windows or inside WSL, and who starts it?** | T3 Code runs its server inside a chosen distribution (`t3code@eac52f0:docs/user/install.md:75-77`), bound to `0.0.0.0` because "wslhost forwarding is unreliable on some Windows hosts", and advertises the distribution's IP address (`t3code@eac52f0:apps/desktop/src/backend/DesktopBackendConfiguration.ts:616-627`). Platforms topology B spawns the runtime through `wsl.exe` ([10, WSL topologies](10-platforms.md#wsl-topologies)). | (a) Service on Windows, runtime in WSL (topology B). (b) Service inside WSL (T3). `Inference:` (b) removes topology B's path and environment bridging but adds idle shutdown and a Windows-to-WSL start ([T3](#t3-service-inside-wsl)). |
| **CT-05** | **Does the service serve the browser client itself?** | Paseo serves its web app from the daemon's own address, so the UI "always matches your daemon version" (`paseo@485221b:public-docs/web-ui.md:11`, `:19`). | (a) Yes, same origin. (b) No; the browser loads the client elsewhere. `Inference:` (a) gives one origin to allow and no client-service version skew. |
| **CT-06** | **Is remote execution through gentle-mesh (T4) pursued?** | Pending the author's answers (Discord, Rafael The Hutt, 2026-10-04 23:20) and the maintainer's approval (`gentle-mesh@2d1d324:README.md:22`). | `Inference:` it needs the five changes of [T4](#t4-remote-execution-behind-the-service-gentle-mesh-later) before a chat could run remotely with the same experience. |
| **CT-07** | **For the maintainer: is a hosted multi-user service wanted at all?** | [Proposal 0004](07-proposals/0004-host-service.md#open-questions), question 1. | `Inference:` if yes, it is a separate product with accounts, isolation, per-user homes and billing ([T5](#t5-hosted-multi-user-out-of-scope)), not an extension of this proposal. |

## Not covered here

- **The architecture** (component map, placement, configuration, migration): [11-host-service.md](11-host-service.md).
- **The protocol** (frames, handshake, errors, auth on the wire): [12-host-protocol.md](12-host-protocol.md).
- **Platform details** (service lifecycle per OS, port, packaging): [10-platforms.md, Host service](10-platforms.md#host-service-proposal-0004).

## Sources

**Pinned repositories** (read-only clones; `repo@sha:path:line`):

| Name in citations | Repository | Commit |
|---|---|---|
| `gentle-shell-desktop` | `Gentleman-Programming/gentle-shell-desktop` | `5ab4a00` |
| `gentle-shell` | `Gentleman-Programming/gentle-shell` (`main`, package version 4.0.0) | `ac67159` |
| `paseo` | `getpaseo/paseo` | `485221b` |
| `t3code` | `pingdotgg/t3code` | `eac52f0` |
| `herdr` | `herdrdev/herdr` | `5da0a01` |
| `herdr-web-ui` | `devswha/herdr-web-ui` | `7c5fe4e` |
| `gentle-mesh` | `Rafaeldelinares/gentle-mesh`: `main` (tag `v1.0.2`) and integration branch `feat/rfc-002-settlement` | `2d1d324`, `f52335e` |

**Web** (accessed 2026-10-05):

- Microsoft, Accessing network applications with WSL: https://learn.microsoft.com/en-us/windows/wsl/networking
- Microsoft, Advanced settings configuration in WSL: https://learn.microsoft.com/en-us/windows/wsl/wsl-config

**Community:**

- Discord, gentle-mesh post: Rafael The Hutt, 2026-10-04 23:20.

**Corpus:** [proposal 0004](07-proposals/0004-host-service.md), [host service architecture](11-host-service.md), [host protocol](12-host-protocol.md), [platforms](10-platforms.md), [RPC contract](04-rpc-contract.md), [audit](03-architecture/audit.md), [vision](00-vision.md).
