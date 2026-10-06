> Traducción al español de `docs/13-clients-and-topologies.md` (commit `9cad584`). Documento de lectura; la versión de referencia es la inglesa.

# Clientes y topologías

> Estado: borrador, propuesta de la comunidad pendiente de validación del mantenedor (draft (community proposal, awaiting maintainer validation)).

> **Boceto de diseño (design sketch) [community], no es el estado actual.** Esta página describe qué clientes se conectarían al servicio host (host service) local compartido que se propone en la [propuesta 0004](07-proposals/0004-host-service.md), y dónde podrían ejecutarse los clientes, el servicio y el runtime. La arquitectura está en [11-host-service.md](11-host-service.md) y el protocolo de clientes en [12-host-protocol.md](12-host-protocol.md). Nada de lo que aquí se describe existe hoy en el repositorio del escritorio, y nada está decidido. Los clientes remotos y móviles quedan fuera del alcance del corpus hasta que el mantenedor responda a [vision Q9](00-vision.md#preguntas-abiertas-para-el-mantenedor).

**En un párrafo.** **[community]** Tres tipos de cliente llegarían a un único servicio host: la ventana de Electron, una pestaña del navegador y una futura app móvil. Difieren en cómo encuentran el servicio, cómo demuestran quiénes son y en qué partes del [protocolo del host](12-host-protocol.md) se apoyan. Cinco topologías sitúan los clientes, el servicio y el runtime: **T1**, todo en una máquina sobre loopback; **T2**, otro dispositivo del mismo usuario que llega a esa máquina mediante un túnel SSH, Tailscale o un relay; **T3**, el servicio dentro de WSL con un cliente de Windows; **T4**, un chat ejecutado en otra máquina detrás del servicio, como propone gentle-mesh (más adelante, y solo con las respuestas de su autor y la aprobación del mantenedor); **T5**, un servicio multiusuario alojado, fuera de alcance (`Inference:` un producto distinto). T1 es la base; T2 y T3 la reutilizan con una ruta distinta hasta el puerto. `Inference:` una app móvil depende de T2, porque un teléfono no puede ejecutar gentle-shell por sí mismo (afirmación del autor de gentle-mesh, `gentle-mesh@2d1d324:propuesta-discord-mobile.txt:12`; ver [Futura app móvil](#futura-app-móvil)). Qué topologías admite una primera versión está abierto (CT-01 a CT-07).

## Cómo leer esta página

| Etiqueta | Significado |
|---|---|
| **[maintainer]** | Declarado en los documentos del repositorio del escritorio del mantenedor o en sus mensajes de Discord. |
| **[community]** | Propuesto por la comunidad. No decidido. |
| `Inference:` | Razonamiento a partir de evidencias citadas, no un hecho declarado. "(no ejecutado)" significa que no se construyó ni se ejecutó nada. |
| `UNVERIFIED:` | Comprobado pero no confirmado; el texto indica qué se comprobó. |

- **Claves de cita.** El código y la documentación se citan como `repo@shortsha:path:line`: `gentle-shell-desktop@5ab4a00` (el código fuente no cambia en esta rama), `gentle-shell@ac67159` (`main` de gentle-shell, versión del paquete 4.0.0), `paseo@485221b`, `t3code@eac52f0`, `herdr@5da0a01`, `herdr-web-ui@7c5fe4e` y `gentle-mesh@2d1d324` (`main`) o `gentle-mesh@f52335e` (rama de integración `feat/rfc-002-settlement`). `:N` después de una cita completa repite su archivo. La documentación de Microsoft se cita por URL con su fecha de consulta. Las páginas del corpus se enlazan por ruta relativa.
- **ID cualificados.** Los ID de otras páginas llevan su página: `vision Q9`, `audit A1`, `PLAT-07`, `milestone M5`. **B1–B6** son los requisitos del runtime de la [propuesta 0004](07-proposals/0004-host-service.md#requisitos-del-runtime) y **HP-01 a HP-07** las preguntas abiertas de [12](12-host-protocol.md#preguntas-abiertas), y se escriben sin cualificar, como en esas páginas. **T1–T5** son las topologías de esta página y aquí se escriben sin cualificar; en otros lugares se escribe `topology T1`, porque `inventory T1` ya existe. **CT-01 a CT-07** son las preguntas abiertas de esta página; el prefijo `CT-` es único en el corpus.
- **Nombres.** "T3 Code" es el producto (`pingdotgg/t3code`); un "T3" sin más en esta página es siempre la topología T3.
- **Método.** Solo lectura estática, como en la [auditoría](03-architecture/audit.md#método-y-alcance). No se prototipó nada, y no se montó ninguna topología.

## De un vistazo

| Pregunta | Respuesta | Evidencia |
|---|---|---|
| ¿Qué clientes? | **[community]** La ventana de Electron, una pestaña del navegador en la misma máquina y una futura app móvil. | [propuesta 0004](07-proposals/0004-host-service.md#propuesta) |
| ¿Cómo se conecta la ventana de Electron? | Con la ubicación (a), mediante WebSocket como cualquier otro cliente; con la ubicación (b), puede conservar el puente del preload. | [11, Ubicación del proceso](11-host-service.md#ubicación-del-proceso-abierta) |
| ¿Qué topologías? | T1 loopback, T2 acceso remoto a la máquina propia, T3 servicio dentro de WSL, T4 ejecución remota detrás del servicio (más adelante), T5 multiusuario alojado (fuera de alcance). | [Topologías](#topologías) |
| ¿Cuál es la base? | T1: una máquina, con el servicio escuchando en `127.0.0.1`. | [propuesta 0004](07-proposals/0004-host-service.md#propuesta); [T1](#t1-todo-en-una-máquina-loopback) |
| ¿Puede un teléfono ejecutar el agente? | `Inference:` no. gentle-shell es un programa de Node, y la propuesta móvil de gentle-mesh afirma que los sistemas móviles no permiten subprocesos locales arbitrarios de Node (afirmación de su autor, no comprobada). Un teléfono es un cliente remoto (T2). | [Futura app móvil](#futura-app-móvil); `gentle-mesh@2d1d324:propuesta-discord-mobile.txt:12` |
| ¿Qué decide la autenticación remota? | HP-02 (emparejamiento, token o relay) y HP-07 (una credencial en loopback). | [12, Preguntas abiertas](12-host-protocol.md#preguntas-abiertas) |
| ¿Forma parte gentle-mesh? | **[community]** Como ejecución remota opcional detrás del servicio, más adelante, pendiente de las respuestas de su autor y de la aprobación del mantenedor. | [T4](#t4-ejecución-remota-detrás-del-servicio-gentle-mesh-más-adelante) |
| ¿Forma parte un servicio multiusuario alojado? | No. `Inference:` es un producto distinto. Si se desea siquiera es una pregunta para el mantenedor. | [T5](#t5-multiusuario-alojado-fuera-de-alcance) |

## Clientes

| Cliente | Cómo encuentra el servicio | Cómo se autentica | Qué necesita del [protocolo del host](12-host-protocol.md) | ¿Existe hoy? |
|---|---|---|---|---|
| **Ventana de Electron** | (a): la app inicia el servicio o se conecta a uno en ejecución. (b): el host está en el mismo proceso. | (a): una credencial que guarda la app (HP-07). (b): ninguna para la ventana; el IPC sigue siendo de confianza. | (a): todo. (b): nada; los demás clientes siguen necesitando el socket. | La ventana y el puente del preload existen (`gentle-shell-desktop@5ab4a00:src/preload/index.ts:4`); el puente WebSocket no. |
| **Pestaña del navegador, misma máquina** | Una URL de loopback, `http://127.0.0.1:<port>`. | Una lista de `Origin` permitidos, más una credencial si HP-07 la exige. | Todo; se reconecta volviendo a suscribirse. | `pnpm dev:web` ejecuta el renderer en un navegador contra una simulación en memoria (mock) (`gentle-shell-desktop@5ab4a00:package.json:12`; `gentle-shell-desktop@5ab4a00:src/renderer/shared/bridge/useBridge.ts:11`). |
| **Futura app móvil** | Un enlace de emparejamiento o un código QR que lleva la dirección (T2). | Emparejamiento del dispositivo con una credencial revocable por dispositivo (HP-02). | Todo, con tolerancia al desfase de versiones (HP-01) y a las redes móviles (HP-04, HP-06). | No. |

### Ventana de Electron

- **Ubicación (a), servicio separado.** **[community]** La ventana pasa a ser un cliente WebSocket como una pestaña del navegador ([11, Ubicación del proceso](11-host-service.md#ubicación-del-proceso-abierta)). El renderer ya elige su puente en una línea, `window.gentle ?? mockBridge` (`gentle-shell-desktop@5ab4a00:src/renderer/shared/bridge/useBridge.ts:11`); un puente WebSocket es una tercera opción ahí ([11, El lado del renderer](11-host-service.md#el-lado-del-renderer)).
- **Ubicación (b), host integrado.** La ventana conserva el puente del preload sobre IPC de Electron, y el host además escucha en un puerto WebSocket para los demás clientes ([11, Ubicación del proceso](11-host-service.md#ubicación-del-proceso-abierta)). `Inference:` entonces la ventana no necesita nada del protocolo del host, pero dos endpoints de clientes deben mantenerse sincronizados ([11, Ubicación del proceso](11-host-service.md#ubicación-del-proceso-abierta), fila "Un puerto, un endpoint").
- **Encontrar el servicio.** Con (a) la app inicia el servicio, o se conecta a uno que ya está en ejecución ([11, Ubicación del proceso](11-host-service.md#ubicación-del-proceso-abierta)). Precedente: la app de escritorio de Paseo reutiliza un daemon en ejecución y reinicia un daemon propio si la versión no coincide (`paseo@485221b:packages/desktop/src/daemon/daemon-manager.ts:266-267`, `:291-300`). El supervisor de Paseo publica "its ready worker's endpoint in `paseo.pid`", y su CLI "trusts only that live record" (`paseo@485221b:docs/architecture.md:475`). `Inference:` un servicio en un puerto no fijo necesita un registro así para que un cliente iniciado después pueda encontrarlo.
- **Autenticación.** `Inference:` la app que inicia el servicio puede entregarle una credencial y leer de vuelta la dirección, así que la ventana no necesita emparejamiento. Si un cliente de loopback necesita siquiera una credencial es HP-07.
- **Restricciones del renderer.** La CSP del renderer no tiene `connect-src`, así que un socket hacia `ws://127.0.0.1:<port>` necesita una entrada explícita ([12, Autenticación y origen](12-host-protocol.md#autenticación-y-origen)). Qué `Origin` envía un renderer de Electron cargado desde un archivo está marcado allí como `UNVERIFIED`.

### Pestaña del navegador en la misma máquina

- **Qué es.** El mismo renderer, cargado en un navegador y conectado al servicio. Hoy el build para navegador solo habla con una simulación en memoria (`gentle-shell-desktop@5ab4a00:src/renderer/shared/bridge/useBridge.ts:4-11`, según se cita en la [propuesta 0004](07-proposals/0004-host-service.md#problema)).
- **Encontrar el servicio.** El usuario abre una URL de loopback. Precedentes:
  - T3 Code: "run `t3` to start the server and open the local web app" (`t3code@eac52f0:README.md:37`).
  - Paseo: el daemon "can serve the browser web app itself, from the same address it already uses for the API" (`paseo@485221b:public-docs/web-ui.md:11`), así que "the UI you serve always matches your daemon version" (`:19`). Está "off by default" (`:23`).
- `Inference:` si el servicio sirve el propio renderer, la página y el socket comparten un origen, la lista de `Origin` permitidos tiene una sola entrada en la que confiar, y cliente y servicio no pueden desfasarse en versión. Si hacerlo es CT-05.
- **Autenticación.** Una lista de `Origin` permitidos impide que otras páginas web del mismo navegador abran el socket, pero no otros procesos locales ([12, Autenticación y origen](12-host-protocol.md#autenticación-y-origen)). Si HP-07 exige una credencial en loopback, la pestaña necesita una forma de recibirla; `Inference:` un enlace de un solo uso que el servicio imprime o abre, como hacen los enlaces de emparejamiento de T3 Code para otros dispositivos ([T2](#t2-acceso-remoto-a-la-máquina-propia)).
- **Qué necesita de 12.** Todas las peticiones y todos los envíos de la [tabla de correspondencias](12-host-protocol.md#tabla-de-correspondencias). Una pestaña se recarga y se cierra libremente, así que depende de la [reconexión y repetición](12-host-protocol.md#reconexión-y-repetición): `hello`, y después `subscribe` para cada chat que muestra.

### Futura app móvil

- **Por qué no ejecutaría gentle-shell en el teléfono.** El binario de gentle-shell es un script de Node (`gentle-shell@ac67159:package.json:7-8`; `gentle-shell@ac67159:bin/gentle-shell.mjs:1`) que requiere Node 22.19 o posterior (`gentle-shell@ac67159:package.json:101-103`). La propuesta móvil de gentle-mesh afirma que "Los sistemas operativos móviles (iOS/Android) no permiten gestionar subprocesos locales arbitrarios de Node ni correr contenedores Docker." (los sistemas operativos móviles no permiten gestionar subprocesos locales arbitrarios de Node ni ejecutar contenedores Docker; `gentle-mesh@2d1d324:propuesta-discord-mobile.txt:12`). Es una afirmación de su autor; esta página no la contrastó con la documentación de Apple ni de Google. `Inference:` por tanto, una app móvil es un cliente remoto de un servicio en otra máquina, y depende de T2 (o de T4 para ejecutar en otro sitio).
- **Precedentes.** Los dos precedentes distribuyen un cliente móvil que se conecta a un servidor en otra máquina: la app de Expo de Paseo para "iOS, Android, web" (`paseo@485221b:README.md:173`), y T3 Code, cuyo acceso remoto conecta "a phone, browser, or another desktop app to T3 Code running on a different machine" (`t3code@eac52f0:docs/user/remote-access.md:3-4`).
- **Encontrar el servicio.** Un enlace de emparejamiento o un código QR. T3 Code: "Scan the QR code on your phone or paste the pairing URL" (`t3code@eac52f0:docs/user/remote-access.md:54`). Paseo: "The QR code or pairing link is the trust anchor. It contains the daemon's public key" (`paseo@485221b:public-docs/security.md:53`). herdr-web-ui: un código de seis dígitos "that lives ten minutes and a QR code that carries it" (`herdr-web-ui@7c5fe4e:docs/guide.md:257`).
- **Autenticación.** Emparejamiento del dispositivo con una credencial por dispositivo que puede revocarse (HP-02, opción (b)). T3 Code: "Pairing authorizes that device for future connections" (`t3code@eac52f0:docs/user/remote-access.md:59`), y el host puede "revoke client sessions" (`:148-150`).
- **Qué necesita de 12.** `Inference:` un build de una tienda de apps se actualiza según su propio calendario, así que necesita una regla de versionado que tolere el desfase (HP-01). En una red móvil, las instantáneas completas cuestan ancho de banda (HP-06) y los enlaces lentos necesitan una cota de búfer (HP-04). Dos clientes pueden actuar sobre un chat, por ejemplo un teléfono y el escritorio respondiendo a un mismo diálogo (HP-03).

## Topologías

| | Clientes | Servicio | Runtime (procesos hijo `gentle-shell --mode rpc`) | Ruta hasta el servicio | En esta propuesta |
|---|---|---|---|---|---|
| **T1** | Misma máquina | Misma máquina | Misma máquina | Loopback | **[community]** base |
| **T2** | Otro dispositivo del mismo usuario | La máquina del usuario | La máquina del usuario | Túnel SSH, Tailscale, LAN, relay | **[community]** opcional, abierta (CT-02) |
| **T3** | Windows (navegador o Electron) | Dentro de WSL | Dentro de WSL | Reenvío de localhost de WSL (`UNVERIFIED:` fiabilidad), o la dirección IP de la distribución | **[community]** opción para Windows, abierta (CT-04) |
| **T4** | Cualquiera de los anteriores | La máquina del usuario | Otra máquina | gentle-mesh, detrás del servicio | **[community]** más adelante, pendiente de su autor y del mantenedor (CT-06) |
| **T5** | Muchos usuarios | Un servidor alojado | Un servidor alojado | Internet | Fuera de alcance (CT-07) |

### T1 Todo en una máquina (loopback)

```text
┌──────────────────────── one machine, one user ────────────────────────┐
│ Electron window ─┐                                                    │
│ Browser tab ─────┼─ ws://127.0.0.1:<port> ─► host service ─► children │
│ (other local     │                                                    │
│  processes) ─────┘  reachable too, unless a credential is required    │
└───────────────────────────────────────────────────────────────────────┘
```

- **Qué es.** **[community]** El valor por defecto de la propuesta 0004: el servicio "Binds to loopback by default" ([propuesta 0004](07-proposals/0004-host-service.md#propuesta)). Con la ubicación (a), el host sale del proceso principal de Electron; con (b), se queda en el proceso principal y además escucha en loopback.
- **Autenticación.** Una lista de `Origin` permitidos para los navegadores; validación de argumentos en cada trama (B4). Si los clientes de loopback necesitan una credencial es HP-07: Paseo admite todo `hello` como propietario cuando no hay contraseña configurada, y T3 Code autentica cada upgrade de `/ws` ([12, Preguntas abiertas](12-host-protocol.md#preguntas-abiertas)).
- **Precedentes.** Paseo escucha en `127.0.0.1:6767` por defecto (`paseo@485221b:packages/server/src/server/config.ts:470`); su página de seguridad dice "On localhost this is fine, only local processes have access" (`paseo@485221b:public-docs/security.md:87`). T3 Code escucha en `127.0.0.1` (`t3code@eac52f0:apps/server/src/server.ts:249`). herdr-web-ui "listens on `127.0.0.1` by default, which means only this computer" (`herdr-web-ui@7c5fe4e:docs/guide.md:254`).
- **Riesgos.**
  - `Inference:` "only local processes" sigue significando todos los procesos de todos los usuarios locales; ese es el caso que sopesa HP-07.
  - `Inference:` una página del navegador de otro sitio puede intentar llegar a un puerto de loopback; la lista de `Origin` permitidos es lo que lo impide ([12, Autenticación y origen](12-host-protocol.md#autenticación-y-origen)). Paseo añade una lista de `Host` permitidos contra el DNS rebinding, porque "CORS is not a complete security boundary" (`paseo@485221b:public-docs/security.md:75`, `:77`).
  - El contraejemplo es el servidor de open-pi-viewer, que escucha en `0.0.0.0` sin comprobación de origen ([propuesta 0004, Alternativas consideradas y descartadas](07-proposals/0004-host-service.md#alternativas-consideradas-y-descartadas)).

### T2 Acceso remoto a la máquina propia

```text
phone / laptop ──► route ──► user's machine: 127.0.0.1:<port> ─► host service ─► children
                    │
                    ├─ SSH tunnel (ssh -L)          service stays on loopback
                    ├─ Tailscale serve / VPN        service stays on loopback, or binds the VPN address
                    ├─ LAN bind (0.0.0.0)           service exposed to the LAN
                    └─ relay (outbound from host)   service stays on loopback; a third party routes bytes
```

**[community]** Otro dispositivo del mismo usuario llega al servicio en la máquina del usuario. Los agentes, los archivos y las sesiones se quedan en esa máquina. Rutas, con sus precedentes:

| Ruta | Qué permite entrar a un cliente | Precedente | Evidencia |
|---|---|---|---|
| **Túnel SSH** | El servicio ve una conexión de loopback; el inicio de sesión SSH es el control de acceso. | herdr-web-ui: `ssh -L 7317:127.0.0.1:7317 host`, "Nothing needed" sin token. La app de escritorio de Paseo: "SSH only tunnels to an already-running daemon". La app de escritorio de T3 Code "starts or reuses a server there and opens the port forward for you". | `herdr-web-ui@7c5fe4e:docs/guide.md:263`; `paseo@485221b:docs/architecture.md:116`; `t3code@eac52f0:docs/user/remote-access.md:121-126` |
| **Tailscale serve** | El servicio se queda en `127.0.0.1`; Tailscale añade una dirección HTTPS en la tailnet. | herdr-web-ui: "keep the server on `127.0.0.1` and let Tailscale add the HTTPS address" (`tailscale serve --bg --https=443 http://127.0.0.1:7317`). Identidad: "`tailscale serve` states the requesting device's Tailscale login in a header"; entra un inicio de sesión que coincide con el del propio PC, y se rechaza cualquier otro. T3 Code: `t3 serve --tailscale-serve` o `t3 pair --tailscale`. | `herdr-web-ui@7c5fe4e:docs/guide.md:204`, `:207`, `:256`; `t3code@eac52f0:docs/user/remote-access.md:83-100` |
| **Dirección de VPN o de LAN** | Una contraseña, un token o un dispositivo emparejado. | Paseo: "Bind the daemon to its VPN address, set a Paseo password", y "Never bind to 0.0.0.0 without a password". herdr-web-ui: escuchar en la LAN necesita "Pair each device, or set a token". T3 Code: `t3 serve --host <private-ip>`, y después un enlace de emparejamiento. | `paseo@485221b:public-docs/security.md:67`, `:149`; `herdr-web-ui@7c5fe4e:docs/guide.md:266`; `t3code@eac52f0:docs/user/remote-access.md:41-59` |
| **Relay** | El host se conecta hacia fuera; los clientes se encuentran con él en el relay. | Paseo: "No open ports required"; el tráfico está cifrado de extremo a extremo y "The relay is designed to be untrusted"; el relay "sees only: IP addresses, timing, message sizes, and session IDs"; "is off on new installations". T3 Connect de T3 Code: un servicio basado en cuentas que hace accesible un entorno "without setting up router forwarding". | `paseo@485221b:public-docs/security.md:21`, `:28`, `:30`, `:40`; `t3code@eac52f0:docs/user/remote-access.md:6-10` |
| **Proxy público** | Un token sobre HTTPS. | herdr-web-ui: "Set a token, with HTTPS", "Never `tailscale funnel` it". | `herdr-web-ui@7c5fe4e:docs/guide.md:267` |

- **La postura del propio Herdr.** El propio Herdr no ofrece una UI remota para teléfonos: "Herdr works on your phone without a mobile app or web dashboard. Install any SSH client, connect to the machine where your agents run, and start Herdr there" (`herdr@5da0a01:docs/next/website/src/content/docs/how-to-work.mdx:49`). `Inference:` el mismo camino funciona hoy para gentle-shell, sin ningún servicio: entrar por SSH en la máquina y ejecutar su UI de terminal. Eso da la experiencia de terminal en un teléfono, no las tarjetas de pregunta, el panel de helpers ni la vista de ODD del escritorio. `UNVERIFIED:` cómo se ve la TUI de gentle-shell en una terminal estrecha de teléfono; no se probó.
- **HTTPS para un teléfono.** herdr-web-ui: "a phone needs two things Tailscale gives at once: a way to reach the PC from outside your network, and HTTPS, which installing the app and push alerts both require" (`herdr-web-ui@7c5fe4e:docs/guide.md:435`). T3 Code: su app web alojada "needs an HTTPS endpoint" (`t3code@eac52f0:docs/user/remote-access.md:113`).
- **Autenticación.** Esto es HP-02: un token estático, emparejamiento de dispositivos o un relay ([12, Preguntas abiertas](12-host-protocol.md#preguntas-abiertas)). Los precedentes los combinan: herdr-web-ui acepta una identidad de Tailscale, un dispositivo emparejado o un token (`herdr-web-ui@7c5fe4e:docs/guide.md:256-258`); Paseo, una contraseña, una credencial local o un emparejamiento por relay ([12, Autenticación y origen](12-host-protocol.md#autenticación-y-origen)); T3 Code, enlaces de emparejamiento y sesiones revocables (`t3code@eac52f0:docs/user/remote-access.md:146-151`).
- **Riesgos.**
  - `Inference:` cualquiera que llegue al servicio puede manejar un agente con los archivos y las credenciales del usuario; herdr-web-ui dice lo mismo de sus terminales: "Anyone who can reach the server can type into your terminals" (`herdr-web-ui@7c5fe4e:docs/guide.md:254`).
  - Escuchar en la LAN deja el servicio abierto hasta que algo lo cierra: en herdr-web-ui, "Until the first device is paired, and with no token set, a LAN or proxied address is open to anyone who reaches it" (`herdr-web-ui@7c5fe4e:docs/guide.md:269`).
  - La autenticación por contraseña "protects access, not confidentiality" (`paseo@485221b:public-docs/security.md:98`). `Inference:` un socket `ws://` sin cifrar fuera de loopback necesita una VPN, un túnel o TLS a su alrededor.
  - Los secretos de emparejamiento se filtran: T3 Code pide a los usuarios "Treat pairing URLs and authorization codes as passwords" (`t3code@eac52f0:docs/user/remote-access.md:172`).

### T3 Servicio dentro de WSL

**[community]** En Windows, el servicio y el runtime se ejecutan dentro de una distribución de WSL; el cliente es un navegador de Windows o la app de Electron en Windows.

```text
┌──────────────── Windows ────────────────┐   ┌────────────── WSL 2 distribution ───────────────┐
│ Electron app (.exe) ─┐                  │   │                                                  │
│ Browser (Edge, ...) ─┴─ localhost:<port>┼──►│ host service on 127.0.0.1:<port> ─► children ─► pi │
└─────────────────────────────────────────┘   └──────────────────────────────────────────────────┘
                     WSL localhost forwarding (NAT mode) or mirrored networking
```

- **Relación con [10-platforms](10-platforms.md#topologías-de-wsl).** La topología B de plataformas es "Desktop native, runtime inside WSL": el escritorio en Windows lanza el runtime a través de `wsl.exe`, traduce las rutas de `--session` y `--home`, reenvía `GENTLE_SHELL_INTERACTIVE_HOST` a través de `WSLENV` y lee las sesiones a través de `\\wsl$` ([10, Topologías de WSL](10-platforms.md#topologías-de-wsl)). La topología T3 mantiene la división de la topología B, cliente de Windows y runtime de Linux, pero mueve el corte: el servicio se ejecuta junto al runtime, y solo un socket cruza la frontera.
- `Inference:` (no ejecutado) dentro de la distribución, el servicio lanza `gentle-shell` como en Linux, con rutas, entorno y homes de Linux, así que las filas de lanzamiento con `wsl.exe`, traducción de rutas y `WSLENV` de la topología B dejan de aplicarse al escritorio. El listado de sesiones se traslada al servicio junto con el dominio ([11, Responsabilidades](11-host-service.md#responsabilidades)), así que lee directamente los homes de Linux; eso elimina la causa de PLAT-07 ("The session list reads the wrong home when the runtime is in WSL", [10, Riesgos](10-platforms.md#riesgos)). El límite de modos de archivo de DrvFS de PLAT-06 se mantiene: depende de dónde está el repositorio, no de dónde se ejecuta el servicio.
- **Reenvío de localhost de WSL.** Microsoft: "If you are building a networking app (for example an app running on a NodeJS or SQL server) in your Linux distribution, you can access it from a Windows app (like your Edge or Chrome internet browser) using `localhost` (just like you normally would)." (https://learn.microsoft.com/en-us/windows/wsl/networking, sección "Accessing Linux networking apps from Windows (localhost)", consultado el 2026-10-05). La clave `localhostForwarding` de `.wslconfig` es `true` por defecto y especifica "if ports bound to wildcard or localhost in the WSL 2 VM should be connectable from the host via `localhost:port`"; el archivo de ejemplo indica "Setting is ignored when networkingMode=mirrored" (https://learn.microsoft.com/en-us/windows/wsl/wsl-config, consultado el 2026-10-05). En modo mirrored, "the Windows host and WSL2 VM can connect to each other using `localhost` (127.0.0.1)" (página de redes, como arriba).
- **Precedente.** T3 Code ejecuta su servidor dentro de WSL: "Choose a WSL distro in **Settings → Connections** to run agents and projects there. Install the provider CLIs inside that distro. T3 Code installs its own server runtime there automatically" (`t3code@eac52f0:docs/user/install.md:75-77`). Su app de escritorio no depende del reenvío de localhost: hace que el servidor escuche en `0.0.0.0` dentro de WSL porque "wslhost forwarding is unreliable on some Windows hosts", y anuncia la dirección IP de la distribución como la URL que usa el renderer; el comentario del código llama a la red expuesta "the WSL-vEthernet network, not the LAN" (`t3code@eac52f0:apps/desktop/src/backend/DesktopBackendConfiguration.ts:616-627`). `UNVERIFIED:` que un cliente en Windows pueda confiar en el reenvío de localhost hacia un servicio que escucha en `127.0.0.1` dentro de WSL; Microsoft lo documenta, el comentario de T3 Code informa de fallos, y aquí no se probó nada. Ningún repositorio fijado documenta lo mismo para Paseo (`rg -i wsl` sobre sus `docs/` y `README.md`: 0 coincidencias).
- **Autenticación.** Como en T1, con una diferencia. `Inference:` un servicio que escucha en `127.0.0.1` dentro de la distribución es accesible desde los procesos de Windows mediante el reenvío de `localhost`, así que "local" abarca dos sistemas operativos; eso refuerza el argumento a favor de una credencial en loopback (HP-07).
- **Quién lo inicia.** Abierto (CT-04). `Inference:` la app de Electron en Windows podría iniciarlo a través de `wsl.exe`, igual que la topología B inicia el runtime ([10, Topologías de WSL](10-platforms.md#topologías-de-wsl)); o la distribución podría iniciarlo con systemd, que WSL admite cuando se establece `systemd=true` bajo `[boot]` en `/etc/wsl.conf` (https://learn.microsoft.com/en-us/windows/wsl/wsl-config, consultado el 2026-10-05).
- **Riesgos.**
  - **Apagado por inactividad.** `instanceIdleTimeout` de `[general]` en `.wslconfig` es "The number of milliseconds that a distro is idle, before it is shut down", por defecto `15000`, "Set to -1 to disable auto shutdown"; `vmIdleTimeout` de `[wsl2]` es "The number of milliseconds that a VM is idle, before it is shut down", por defecto `60000`, disponible solo en Windows 11 (https://learn.microsoft.com/en-us/windows/wsl/wsl-config, consultado el 2026-10-05). `UNVERIFIED:` si un servicio en segundo plano en ejecución cuenta como actividad que mantiene encendida la distribución o la VM; la página no define "idle".
  - **El acceso desde la LAN es distinto.** Desde otro dispositivo, WSL 2 "isn't the default case": necesita un port proxy o el modo mirrored, y un cliente remoto queda "treated as connections from the Local Area Network (LAN)" (https://learn.microsoft.com/en-us/windows/wsl/networking, consultado el 2026-10-05). `Inference:` T2 sobre un servicio alojado en WSL necesita un salto más que en Linux o macOS.
  - `UNVERIFIED:` T3 en su conjunto: no se montó ninguna topología, y ningún repositorio fijado aparte de T3 Code documenta un servidor dentro de WSL con un cliente de Windows.

### T4 Ejecución remota detrás del servicio (gentle-mesh, más adelante)

**[community]** gentle-mesh es la propuesta de protocolo de Rafael The Hutt (`Rafaeldelinares/gentle-mesh`). La [propuesta 0004](07-proposals/0004-host-service.md#ejecución-remota-opcional-gentle-mesh) lo sitúa detrás del registro de sesiones, como una forma de que el servicio host ejecute un chat en otra máquina. Los clientes no cambiarían: siguen hablando el protocolo del host con un único servicio. Su objetivo declarado es "un a2a con verificacion" (agente a agente con verificación; Discord, Rafael The Hutt, 2026-10-04 23:20). Esta topología depende de sus respuestas, que están pendientes, y de la aprobación del mantenedor, que el propio README de gentle-mesh exige (`gentle-mesh@2d1d324:README.md:22`).

```text
clients ─► host service (session registry) ─┬─► local child: gentle-shell --mode rpc
                                            └─► gentle-mesh coordinator ─► worker node ─► gentle-shell --mode rpc
```

**Qué necesitaría gentle-mesh** para que un chat se ejecute en un nodo remoto con la misma experiencia que uno local. Los hechos se citan; el código de abajo es idéntico en `2d1d324` y `f52335e` ([propuesta 0004](07-proposals/0004-host-service.md#ejecución-remota-opcional-gentle-mesh)), y también `pkg/server/http/server.go` (`git diff` vacío).

| Necesidad | Por qué | Hoy | Evidencia |
|---|---|---|---|
| **Un runner de gentle-shell** | El nodo remoto debe ejecutar `gentle-shell --mode rpc`, no pi a secas, para que existan los helpers, ODD y los diálogos. | Los nodos worker recurren a un runner simulado. El runner `pi` del coordinador inicia el binario una vez por tarea con `--print --mode json`; el binario es `"pi"` por defecto, y la CLI nunca lo establece. | `gentle-mesh@2d1d324:cmd/gentle-mesh/main.go:568-571`; `gentle-mesh@2d1d324:pkg/server/worker/server.go:40-41`; `gentle-mesh@2d1d324:cmd/gentle-mesh/main.go:306-311`; `gentle-mesh@2d1d324:pkg/server/runner/pi.go:63-67`, `:102`, `:175` |
| **Un paso directo de RPC, con UI de extensiones** | Las tarjetas de pregunta y la actividad de los helpers viajan como `extension_ui_request` y `setWidget` ([04, Añadidos de gentle-shell sobre RPC](04-rpc-contract.md#añadidos-de-gentle-shell-sobre-rpc)). | El puente `rpc` gestiona `get_state`, `get_messages`, `new_session`, `abort` y `prompt`; "Unknown commands are ignored for forward compatibility." `extension_ui` no aparece en ese archivo. | `gentle-mesh@2d1d324:pkg/client/bridge.go:225-252`; [propuesta 0004](07-proposals/0004-host-service.md#ejecución-remota-opcional-gentle-mesh) |
| **mTLS que funcione** | La identidad del nodo es el primer objetivo del diseño: "Toda conexión usa mTLS; el CN/SAN del certificado coincide con el `agent_id` firmante." (toda conexión usa mTLS; el CN/SAN del certificado coincide con el `agent_id` que firma). | `-require-mtls` establece `RequireMTLS`. `Start` construye un `tls.Config` con `RequireAndVerifyClientCert` y después llama a `ListenAndServeTLS`. `Inference:` (leído, no ejecutado) esa configuración nunca se asigna al servidor HTTP, ya que el archivo no tiene ninguna otra referencia a ella, así que no se exigen certificados de cliente; ningún test establece `RequireMTLS` (`rg` sobre `*_test.go`, 0 coincidencias). | `gentle-mesh@f52335e:docs/rfcs/002-objectives-and-non-goals.md:41`; `gentle-mesh@2d1d324:cmd/gentle-mesh/main.go:232-238`; `gentle-mesh@2d1d324:pkg/server/http/server.go:271-285` |
| **Una lista de orígenes permitidos** | Una página del navegador no debe poder manejar un nodo (riesgos de [T1](#t1-todo-en-una-máquina-loopback)). | El middleware de CORS devuelve cualquier `Origin` en `Access-Control-Allow-Origin`, mientras que el README describe una lista de orígenes permitidos de Tauri, localhost y Tailscale. La autenticación con bearer token solo se añade cuando hay un token configurado. | `gentle-mesh@2d1d324:pkg/server/http/middleware.go:110-133`; `gentle-mesh@2d1d324:README.md:115`; `gentle-mesh@2d1d324:pkg/server/http/server.go:251-253` |
| **Una LICENSE** | Sin ella, su código no puede reutilizarse. | No hay archivo LICENSE en ninguno de los dos commits (`git ls-tree`). El autor dijo que añadirá MIT ("Mñn por la tarde cuando llegue a casa le pongo licence Mit"; Discord, Rafael The Hutt, 2026-10-04 23:20). | [propuesta 0004](07-proposals/0004-host-service.md#ejecución-remota-opcional-gentle-mesh) |

- **Estado.** Las preguntas sobre estos puntos se enviaron al autor el 2026-10-04. Respondió a la pregunta de la licencia; "Respecto al resto mñn lo miro y te respondo" (el resto lo mirará mañana y responderá) (Discord, Rafael The Hutt, 2026-10-04 23:20). Nada de esta página da por supuestas sus respuestas.
- **Autenticación.** `Inference:` dos fronteras de confianza: de los clientes al servicio (HP-02, HP-07), y del servicio a los nodos remotos (mTLS y tokens de gentle-mesh). Un cliente nunca habla directamente con un nodo.
- `Inference:` T4 también llega al móvil a través del mismo servicio: el teléfono sigue siendo un cliente (T2), y la ejecución puede ocurrir en una tercera máquina. La propuesta móvil de gentle-mesh lo plantea como un "Modo Red / Mesh" sobre HTTP REST y SSE "a un servidor remoto, homelab o máquina secundaria (por ejemplo, vía Tailscale)" (a un servidor remoto, homelab o máquina secundaria, por ejemplo mediante Tailscale; `gentle-mesh@2d1d324:propuesta-discord-mobile.txt:23`); en esta propuesta, ese papel de front end corresponde en cambio al protocolo del host.

### T5 Multiusuario alojado (fuera de alcance)

**Fuera de alcance.** La propuesta 0004 deja abierto qué significa "web": "a browser UI for the local agent (optionally reached remotely), or a hosted multi-user service" ([propuesta 0004, Preguntas abiertas](07-proposals/0004-host-service.md#preguntas-abiertas), pregunta 1). Esta página solo cubre la primera lectura; la segunda es CT-07.

`Inference:` un servicio multiusuario alojado es un producto distinto, no una topología más de este:

- **Cuentas.** T1–T4 sirven a un único usuario, cuya propia máquina es la frontera de identidad; todas las credenciales anteriores (token, emparejamiento, inicio de sesión de Tailscale) demuestran "este es el propietario". Un servicio alojado necesita registro, inicio de sesión y recuperación de cuentas.
- **Aislamiento.** Los procesos hijo ejecutan un agente con acceso a la shell. En la máquina de un usuario, ese es su propio riesgo; en un servidor compartido, los agentes, archivos y credenciales de cada usuario deben estar aislados de los de todos los demás.
- **Homes por usuario.** El escritorio resuelve un único home a partir del directorio home y del entorno del proceso (`gentle-shell-desktop@5ab4a00:src/main/domain/home/home.ts:45-47`, `:56-67`), y el listado de sesiones muta un `PI_CODING_AGENT_DIR` de todo el proceso (B2, [audit A1](03-architecture/audit.md#a1-dos-caminos-de-datos-hacia-pi-y-una-mutación-global-de-pi_coding_agent_dir)). Un proceso compartido necesitaría un home, unos inicios de sesión de proveedores y un almacén de sesiones por usuario.
- **Facturación y operaciones.** Alguien paga el cómputo y las llamadas al modelo, y alguien opera los servidores.
- **Alojar la UI no es alojar los agentes.** Los dos precedentes alojan un front end web que se conecta al servidor propio del usuario: `app.t3.codes` de T3 Code "connects directly to your server" (`t3code@eac52f0:docs/user/remote-access.md:113-114`), y el daemon de Paseo sirve la UI "on infrastructure you control" en lugar de la app alojada en `app.paseo.sh` (`paseo@485221b:public-docs/web-ui.md:11`). `Inference:` un cliente estático alojado encaja en T2; la ejecución alojada es T5.

## Móvil

- **Qué necesitaría.** `Inference:` una app nativa o web que hable el protocolo del host; una ruta T2 con HTTPS (herdr-web-ui, arriba); emparejamiento de dispositivos con revocación (HP-02); una regla de versionado que tolere que un build de una tienda de apps vaya por detrás del servicio (HP-01); y una decisión sobre las instantáneas completas en redes móviles (HP-06).
- **Qué topología.** `Inference:` siempre T2, ya que el runtime no puede ejecutarse en el teléfono (afirmación del autor de gentle-mesh, `gentle-mesh@2d1d324:propuesta-discord-mobile.txt:12`; ver [Futura app móvil](#futura-app-móvil)); T4 si la ejecución pasa a una tercera máquina.
- **Límites en segundo plano.** La propuesta móvil de gentle-mesh señala que "Las políticas de ahorro de batería cierran procesos en segundo plano a los pocos segundos" (las políticas de ahorro de batería cierran los procesos en segundo plano en pocos segundos; `gentle-mesh@2d1d324:propuesta-discord-mobile.txt:13`). `Inference:` la app del teléfono se desconectará a menudo, así que depende de la [reconexión y repetición](12-host-protocol.md#reconexión-y-repetición); un aviso de "needs you" mientras está cerrada necesita notificaciones push, que herdr-web-ui vincula a HTTPS (`herdr-web-ui@7c5fe4e:docs/guide.md:204`).
- **La restricción de la visión.** La visión incluye "Not, for now, a remote or mobile client" entre lo que Gentle Desktop no es, y mantiene el acceso móvil y remoto como pregunta abierta ([visión, Qué no es Gentle Desktop](00-vision.md#qué-no-es-gentle-desktop); [vision Q9](00-vision.md#preguntas-abiertas-para-el-mantenedor)). Esta página es un planteamiento **[community]** y no cambia eso: describe lo que necesitaría un cliente móvil si el mantenedor lo incluye en el alcance.

## Preguntas abiertas

Los hechos se citan; los juicios son `Inference:`. Nada de esto está decidido.

| ID | Pregunta | Hechos | Opciones e `Inference:` |
|---|---|---|---|
| **CT-01** | **¿Qué topologías admite una primera versión?** | T1 es el valor por defecto de la propuesta 0004 ([propuesta 0004](07-proposals/0004-host-service.md#propuesta)). | (a) Solo T1. (b) T1 más T3 en Windows. (c) T1 más T2. `Inference:` (a) prueba el servicio con la mínima exposición; T2 añade la autenticación remota (HP-02) y T3 añade las preguntas de WSL de CT-04. |
| **CT-02** | **¿Qué rutas remotas documenta o incorpora T2?** | Los precedentes usan túneles SSH, Tailscale serve, escucha en la LAN con contraseña o emparejamiento, y relays ([T2](#t2-acceso-remoto-a-la-máquina-propia)). | (a) Documentar SSH y Tailscale, sin construir nada. (b) Emparejamiento incorporado para direcciones de LAN y de VPN. (c) Un relay. `Inference:` (a) mantiene el servicio en loopback; (c) añade un tercero en el que confiar y que operar (HP-02). |
| **CT-03** | **¿Se inicia un servicio independiente al iniciar sesión?** | T3 Code se ejecuta como servicio por usuario en Linux y macOS, y "Windows background services are not supported" (`t3code@eac52f0:docs/user/background-service.md:3-4`, `:54`). La app de escritorio de Paseo detiene al salir el daemon que inició, salvo que esté configurada para mantenerlo en ejecución ([11, Ubicación del proceso](11-host-service.md#ubicación-del-proceso-abierta)). | (a) Solo mientras se ejecuta la app de escritorio. (b) Un elemento de inicio de sesión de activación voluntaria por sistema operativo. `Inference:` (b) es lo que hace útil un cliente solo de navegador o de teléfono cuando la app está cerrada. Ver [10, Servicio host](10-platforms.md#servicio-host-propuesta-0004). |
| **CT-04** | **En Windows, ¿el servicio se ejecuta en Windows o dentro de WSL, y quién lo inicia?** | T3 Code ejecuta su servidor dentro de una distribución elegida (`t3code@eac52f0:docs/user/install.md:75-77`), escuchando en `0.0.0.0` porque "wslhost forwarding is unreliable on some Windows hosts", y anuncia la dirección IP de la distribución (`t3code@eac52f0:apps/desktop/src/backend/DesktopBackendConfiguration.ts:616-627`). La topología B de plataformas lanza el runtime a través de `wsl.exe` ([10, Topologías de WSL](10-platforms.md#topologías-de-wsl)). | (a) Servicio en Windows, runtime en WSL (topología B). (b) Servicio dentro de WSL (T3). `Inference:` (b) elimina el puenteo de rutas y de entorno de la topología B, pero añade el apagado por inactividad y un arranque de Windows a WSL ([T3](#t3-servicio-dentro-de-wsl)). |
| **CT-05** | **¿Sirve el servicio el propio cliente de navegador?** | Paseo sirve su app web desde la propia dirección del daemon, así que la UI "always matches your daemon version" (`paseo@485221b:public-docs/web-ui.md:11`, `:19`). | (a) Sí, mismo origen. (b) No; el navegador carga el cliente desde otro sitio. `Inference:` (a) da un único origen que permitir y ningún desfase de versión entre cliente y servicio. |
| **CT-06** | **¿Se persigue la ejecución remota mediante gentle-mesh (T4)?** | Pendiente de las respuestas del autor (Discord, Rafael The Hutt, 2026-10-04 23:20) y de la aprobación del mantenedor (`gentle-mesh@2d1d324:README.md:22`). | `Inference:` necesita los cinco cambios de [T4](#t4-ejecución-remota-detrás-del-servicio-gentle-mesh-más-adelante) antes de que un chat pudiera ejecutarse en remoto con la misma experiencia. |
| **CT-07** | **Para el mantenedor: ¿se desea siquiera un servicio multiusuario alojado?** | [Propuesta 0004](07-proposals/0004-host-service.md#preguntas-abiertas), pregunta 1. | `Inference:` si es así, es un producto aparte con cuentas, aislamiento, homes por usuario y facturación ([T5](#t5-multiusuario-alojado-fuera-de-alcance)), no una extensión de esta propuesta. |

## Lo que no cubre esta página

- **La arquitectura** (mapa de componentes, ubicación, configuración, migración): [11-host-service.md](11-host-service.md).
- **El protocolo** (tramas, handshake, errores, autenticación en la conexión): [12-host-protocol.md](12-host-protocol.md).
- **Detalles de plataforma** (ciclo de vida del servicio por sistema operativo, puerto, empaquetado): [10-platforms.md, Servicio host](10-platforms.md#servicio-host-propuesta-0004).

## Fuentes

**Repositorios fijados** (clones de solo lectura; `repo@sha:path:line`):

| Nombre en las citas | Repositorio | Commit |
|---|---|---|
| `gentle-shell-desktop` | `Gentleman-Programming/gentle-shell-desktop` | `5ab4a00` |
| `gentle-shell` | `Gentleman-Programming/gentle-shell` (`main`, versión del paquete 4.0.0) | `ac67159` |
| `paseo` | `getpaseo/paseo` | `485221b` |
| `t3code` | `pingdotgg/t3code` | `eac52f0` |
| `herdr` | `herdrdev/herdr` | `5da0a01` |
| `herdr-web-ui` | `devswha/herdr-web-ui` | `7c5fe4e` |
| `gentle-mesh` | `Rafaeldelinares/gentle-mesh`: `main` (etiqueta `v1.0.2`) y la rama de integración `feat/rfc-002-settlement` | `2d1d324`, `f52335e` |

**Web** (consultado el 2026-10-05):

- Microsoft, Accessing network applications with WSL: https://learn.microsoft.com/en-us/windows/wsl/networking
- Microsoft, Advanced settings configuration in WSL: https://learn.microsoft.com/en-us/windows/wsl/wsl-config

**Comunidad:**

- Discord, publicación de gentle-mesh: Rafael The Hutt, 2026-10-04 23:20.

**Corpus:** [propuesta 0004](07-proposals/0004-host-service.md), [arquitectura del servicio host](11-host-service.md), [protocolo del host](12-host-protocol.md), [plataformas](10-platforms.md), [contrato RPC](04-rpc-contract.md), [auditoría](03-architecture/audit.md), [visión](00-vision.md).
