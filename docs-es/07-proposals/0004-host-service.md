> Traducción al español de `docs/07-proposals/0004-host-service.md` (commit `9cad584`). Documento de lectura; la versión de referencia es la inglesa.

# 0004. Servicio host local compartido

> Estado: propuesta (proposed).

| Campo | Valor |
|---|---|
| Autor | Matrak (comunidad) |
| Fuente | Conversación con Matrak, 2026-10-04 (no publicada): "No se podria hacer algo que sirviera tanto para desktop como para web, o a futuro una app. Para mi eso son solo interfaces. Es decir algo que se pone entre medio de las UI y gentle-shell" (¿no se podría construir algo que sirva para escritorio, web y, más adelante, una app? Para mí esas son solo interfaces: algo que se sitúa entre las UI y gentle-shell) |
| Desencadenante | **[maintainer]** "fijense si no conviene una version web y listo tambien" (comprobar si no sería mejor, también, simplemente una versión web; Discord, Alan Buscaglia, 2026-09-30 22:34), y después "como herdr web" (como herdr web; Discord, Alan Buscaglia, 2026-10-01 11:17) |
| Estado | `proposed` (solo el mantenedor la pasa a `accepted` o `declined`) |
| Principios | vision P1 **[maintainer]**, **[community]** (todos los clientes conservan los helpers, ODD y los diálogos de gentle-shell, porque el contrato RPC no cambia); vision P5 **[maintainer]** (mockup intent), **[gentle-shell]** (varios chats a la vez, "needs you" en todos los clientes, mediante B1); debe respetar vision P4 **[maintainer]** (el registro mantiene los helpers por chat) |
| Relacionado | [vision Q3 y Q9](../00-vision.md#preguntas-abiertas-para-el-mantenedor) **[open question]**; [roadmap F1](../09-roadmap.md#f1-fundamentos-varios-chats-a-la-vez-community-proposal) **[community]** |

## Problema

Cada sesión de chat pertenece al proceso principal de Electron, así que ningún otro tipo de cliente puede usarla:

- La raíz de composición construye el único `ChatHost` y sus adaptadores dentro de Electron (`gentle-shell-desktop@5ab4a00:src/main/index.ts:60-67`).
- El renderer solo llega a él a través del puente del preload sobre IPC de Electron (`gentle-shell-desktop@5ab4a00:src/preload/index.ts:4`; `gentle-shell-desktop@5ab4a00:src/main/ipc/registerHandlers.ts:27-40`).
- En un navegador normal (`pnpm dev:web`, `gentle-shell-desktop@5ab4a00:package.json:12`) el renderer recurre a una simulación en memoria (mock) (`gentle-shell-desktop@5ab4a00:src/renderer/shared/bridge/useBridge.ts:4-11`).

Después, el mantenedor preguntó si sería mejor una versión web (Desencadenante, arriba). La visión mantiene un cliente remoto o móvil como pregunta abierta ([vision Q9](../00-vision.md#preguntas-abiertas-para-el-mantenedor)). `Inference:` una app web o móvil escrita junto al escritorio tendría que volver a ser dueña de las sesiones, en un segundo lugar.

## Propuesta

**[community]** Un único **servicio host** (host service) local se sitúa entre cada UI de Gentle Shell y `gentle-shell --mode rpc`:

```text
Electron window ──┐
Browser tab ──────┼── WebSocket, one versioned protocol ──► host service ──► gentle-shell --mode rpc children ──► pi
Mobile app ───────┘                                         (session registry)    (proposed: one per chat, pending vision Q3)
```

| Responsabilidad | Qué hace el servicio |
|---|---|
| Sesiones | Es dueño del registro de sesiones: qué chats están abiertos, su estado, sus procesos hijo. |
| Runtime | Lanza procesos hijo `gentle-shell --mode rpc`. La forma propuesta es un hijo por chat, pendiente de vision Q3 (ver [Preguntas abiertas](#preguntas-abiertas)). El contrato con gentle-shell no cambia ([contrato RPC](../04-rpc-contract.md)). |
| Clientes | Expone un único protocolo versionado sobre WebSocket a muchos clientes a la vez. |
| Acceso | Escucha en loopback por defecto. Escuchar en cualquier otra dirección requiere un token o el emparejamiento (pairing) del dispositivo, y cada conexión comprueba `Origin`. |

Electron, el navegador y una futura app móvil pasan a ser clientes del mismo servicio. Un hijo por chat es la forma que recomienda audit A3 ([audit A3](../03-architecture/audit.md#a3-host-de-sesión-única-con-ids-de-mensaje-posicionales), recomendación 1) y que permite gap G9 ([gap G9](../04-rpc-contract.md#carencias-que-necesita-el-escritorio)); es una propuesta, no una decisión.

## Por qué encaja con el código actual

| Hecho | Evidencia (`gentle-shell-desktop@5ab4a00`) |
|---|---|
| Electron solo lo importan 3 archivos fuente: la raíz de composición y el preload en tiempo de ejecución, y los manejadores de IPC solo como tipos. `registerHandlers.ts` dice que "never executes `require("electron")` at module load time". La única otra coincidencia es una importación de tipo en un test. | `src/main/index.ts:2`; `src/preload/index.ts:1`; `src/main/ipc/registerHandlers.ts:1`, `:11-13`; `src/main/ipc/registerHandlers.test.ts:2` (`git grep` de las importaciones de `electron` sobre `src/`) |
| `ChatHost` y `PiSession` dependen de puertos, "so the domain never imports Electron/Node APIs directly". Sus tests se ejecutan en el entorno `node` de Vitest. | `src/main/domain/session/ChatHost.ts:4`; `src/main/domain/session/PiSession.ts:6`; `src/main/ports/index.ts:3-5`; `vitest.config.ts:5-6`, `:21`; `src/main/domain/session/ChatHost.test.ts:3-4` |
| El puente consta de 8 métodos de petición y 2 suscripciones de envío, reflejados en 8 + 2 canales de IPC. Los manejadores de IPC son un "thin pass-through to ChatHost". | `src/shared/bridge-types.ts:273-295`; `src/shared/ipc-channels.ts:8-23`; `src/main/ipc/registerHandlers.ts:8-9`, `:28-40` |
| El puente no lleva id de chat: `sendMessage` actúa sobre "whichever chat is currently open". | `src/shared/bridge-types.ts:279-282` |
| El renderer elige su puente en un solo lugar: `window.gentle ?? mockBridge`. | `src/renderer/shared/bridge/useBridge.ts:11` |

`Inference:` (leído, no prototipado) el servicio puede extraerse en lugar de escribirse: mover `ChatHost`, `PiSession` y sus adaptadores detrás de un servidor WebSocket, y añadir una tercera implementación de `GentleBridge` que hable WebSocket, seleccionada en el mismo punto que los puentes del preload y simulado. Los tipos de las cargas son datos planos que ya cruzan una frontera de proceso, así que pueden viajar como JSON; esto no se comprobó campo por campo (ver [Protocolo del host, Transporte y delimitación de registros](../12-host-protocol.md#transporte-y-delimitación-de-registros)).

## Requisitos del runtime

Lo que debe cambiar primero, en este orden. B1 es el mismo trabajo que [roadmap F1](../09-roadmap.md#f1-fundamentos-varios-chats-a-la-vez-community-proposal).

| # | Cambio | Por qué lo necesita el servicio | Evidencia |
|---|---|---|---|
| B1 | Un registro de sesiones indexado por chat; un id de chat en cada envío y cada comando; ids de mensaje tomados de pi | Muchos clientes y chats comparten un único servicio. Hoy hay una sola sesión `current` y los ids son posicionales. | `gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts:70`; [audit A3](../03-architecture/audit.md#a3-host-de-sesión-única-con-ids-de-mensaje-posicionales); [gap G9](../04-rpc-contract.md#carencias-que-necesita-el-escritorio) |
| B2 | Listar las sesiones sin mutar `PI_CODING_AGENT_DIR` | El listado guarda, establece y restaura una variable de todo el proceso; la auditoría señala que varios chats a la vez "would make this race routine". | `gentle-shell-desktop@5ab4a00:src/main/adapters/piSessionStore.ts:32-39`; [audit A1](../03-architecture/audit.md#a1-dos-caminos-de-datos-hacia-pi-y-una-mutación-global-de-pi_coding_agent_dir) |
| B3 | Un handshake de versión: el servicio lee las versiones de gentle-shell y pi, y el protocolo del host lleva su propia versión | Los clientes y el servicio pueden actualizarse por separado. El protocolo RPC no tiene campo de versión, y el único texto de versión del escritorio es un mensaje de error. | `gentle-shell-desktop@5ab4a00:src/main/adapters/launcherLocator.ts:26-28`; [audit A8](../03-architecture/audit.md#a8-sin-handshake-de-versión); [gap G10](../04-rpc-contract.md#carencias-que-necesita-el-escritorio) |
| B4 | Autenticación y validación de argumentos | Los manejadores de IPC usan los argumentos del renderer tal cual. `Inference:` cualquier proceso local puede alcanzar un socket, y también la red cuando no está en loopback, así que el servicio no puede confiar en quienes lo llaman como el proceso principal confía en su propia ventana. | `gentle-shell-desktop@5ab4a00:src/main/ipc/registerHandlers.ts:28-37`; [audit A14](../03-architecture/audit.md#a14-endurecimiento-del-preload-y-del-ipc) |
| B5 | Corregir el parser de actividad; se traslada al servicio junto con el dominio | El conjunto de estados de los helpers del escritorio no coincide con el de gentle-shell. Corregido una vez en el servicio, queda corregido para todos los clientes. | `gentle-shell-desktop@5ab4a00:src/main/domain/rpc/helpersActivity.ts:21`; [audit A5](../03-architecture/audit.md#a5-el-conjunto-de-estados-de-los-helpers-y-los-elementos-de-herramienta-no-coinciden-con-gentle-shell) |
| B6 | Un `cwd` por chat | `PiSession` admite `cwd`, pero `ChatHost` nunca le pasa uno, así que los chats heredan el directorio del proceso host. `Inference:` un servicio iniciado en segundo plano no tiene un directorio de trabajo propio que tenga sentido. | `gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:15`, `:135`; `gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts:159-166`; [audit A10](../03-architecture/audit.md#a10-los-chats-nuevos-se-ejecutan-en-el-directorio-de-trabajo-de-la-aplicación) |

## Precedentes en el ecosistema

Dos proyectos ya sitúan un único servidor local entre varios clientes y `pi --mode rpc`.

| Proyecto | Forma | Cómo llega a pi | Dirección de escucha por defecto | Licencia |
|---|---|---|---|---|
| **Paseo** (`getpaseo/paseo`) | "a local server called the daemon that manages your coding agents" (`paseo@485221b:README.md:60`), con una "WebSocket API" (`paseo@485221b:README.md:172`); los clientes son una app de Expo para iOS, Android y web (`paseo@485221b:README.md:173`) y Electron (`paseo@485221b:README.md:175`) | Lanza pi con `--mode rpc` salvo que se indique otra cosa (`paseo@485221b:packages/server/src/server/agent/providers/pi/runtime.ts:92`, `:123`); el comando es `pi` por defecto (`paseo@485221b:packages/server/src/server/agent/providers/pi/cli-runtime.ts:30`) | `127.0.0.1:6767` (`paseo@485221b:packages/server/src/server/config.ts:470`, `:480`) | Apache-2.0 (`paseo@485221b:LICENSE:7-8`) |
| **T3 Code** (`pingdotgg/t3code`) | Un servidor con una app móvil, una app web y una app de escritorio de Electron (`t3code@eac52f0:README.md:3`); `t3` inicia el servidor y abre la app web local (`t3code@eac52f0:README.md:37`) | Su proveedor Pi "Spawns `pi --mode rpc`" sobre JSONL por stdio (`t3code@eac52f0:apps/server/src/orchestration-v2/Adapters/PiRpc.ts:1-8`); el comando es el `binaryPath` configurado o `pi` (`t3code@eac52f0:apps/server/src/orchestration-v2/Adapters/PiAdapterV2.ts:422-427`) | `127.0.0.1` (`t3code@eac52f0:apps/server/src/server.ts:249`) | MIT (`t3code@eac52f0:LICENSE:1-3`) |

El proveedor Pi de T3 Code solo está en las builds nightly: la etiqueta nightly `v0.0.46-nightly.20261004.2644` contiene `PiDriver.ts` y `PiRpc.ts`, y la última release estable, `v0.0.45` (2026-10-02), no contiene ninguno de los dos (API de GitHub, consultada el 2026-10-05).

## Ejecución remota opcional: gentle-mesh

**[community]** gentle-mesh es la propuesta de protocolo de Rafael The Hutt (`Rafaeldelinares/gentle-mesh`). Describió su visión como "aplicacion multiplataforma no dependiente. ya sea pc o movil." (una app multiplataforma e independiente, para PC o móvil) con "posibilidad de acceso a agentes remotos en entornos vpn" (acceso a agentes remotos a través de VPN) (Discord, Rafael The Hutt, 2026-09-27 23:33). En esta propuesta es opcional: una forma de que el servicio host ejecute un chat en otra máquina, detrás del mismo registro de sesiones.

**Qué ofrece hoy, como ideas:**

- **La idea del cliente ligero.** Su propuesta móvil sostiene que los sistemas operativos móviles "no permiten gestionar subprocesos locales arbitrarios de Node" (no permiten subprocesos locales arbitrarios de Node) y propone un front end que alterna entre un modo local y un "Modo Red / Mesh" sobre HTTP REST y SSE hacia un servidor remoto (`gentle-mesh@2d1d324:propuesta-discord-mobile.txt:12`, `:18-23`).
- **Recibos firmados, como idea de UI.** Un `SettlementReceipt` lleva un veredicto (`SETTLED_CLEAN` … `SETTLEMENT_TIMEOUT`), la firma Ed25519 del ejecutor, la contrafirma del emisor y un enlace al recibo anterior (`gentle-mesh@f52335e:pkg/receipt/types.go:25`, `:64`, `:71`, `:88`, `:222-230`). `Inference:` un cliente podría mostrarlo como una tarjeta "verificado, no solo afirmado"; complementa [0003](0003-post-hoc-audit-by-questions.md), que pregunta a un helper que ha terminado por qué.

**Qué le falta hoy** (el código citado abajo es idéntico en `2d1d324` y `f52335e`: `git diff` sobre `cmd/gentle-mesh`, `pkg/server/runner`, `pkg/server/worker`, `pkg/client/bridge.go` y `pkg/server/http/middleware.go` está vacío):

- **Los nodos worker ejecutan un runner simulado.** `gentle-mesh worker` construye su servidor sin runner (`gentle-mesh@2d1d324:cmd/gentle-mesh/main.go:568-571`), y el worker recurre entonces a `NewSimulatedRunner` (`gentle-mesh@2d1d324:pkg/server/worker/server.go:40-41`).
- **El coordinador ejecuta pi de una sola vez por tarea (`--print --mode json`).** `server -runner pi` construye un `PiRunner` solo con una raíz de workspace (`gentle-mesh@2d1d324:cmd/gentle-mesh/main.go:306-311`); para cada tarea inicia el binario una vez con esos argumentos (`gentle-mesh@2d1d324:pkg/server/runner/pi.go:102`, `:175`). El binario es `"pi"` por defecto (`:63-67`), y la CLI nunca lo establece, así que no se ejecuta gentle-shell.
- **El puente `rpc` cubre 5 comandos, sin UI de extensiones.** Gestiona `get_state`, `get_messages`, `new_session`, `abort` y `prompt`; "Unknown commands are ignored" (`gentle-mesh@2d1d324:pkg/client/bridge.go:225-252`). `extension_ui` no aparece en ese archivo en ninguno de los dos commits (`git grep`). `Inference:` las tarjetas de pregunta y la actividad de los helpers ([04, Añadidos de gentle-shell sobre RPC](../04-rpc-contract.md#añadidos-de-gentle-shell-sobre-rpc)) no llegarían a un cliente.
- **CORS devuelve cualquier origen.** Cuando una petición lleva `Origin`, el middleware lo copia en `Access-Control-Allow-Origin`, sin lista de permitidos (`gentle-mesh@2d1d324:pkg/server/http/middleware.go:110-133`). El README describe una lista de orígenes permitidos de Tauri, localhost y Tailscale (`gentle-mesh@2d1d324:README.md:115`). La autenticación con bearer token es opcional: solo se añade cuando hay un token configurado (`gentle-mesh@2d1d324:pkg/server/http/server.go:251-253`).
- **Sin archivo LICENSE** en ninguno de los dos commits (`git ls-tree` de ambas raíces); el autor dijo el 2026-10-04 que añadirá uno (MIT). `UNVERIFIED:` su creencia de que RFC-001 tenía uno ("rfc001 si tenia"), ya que no existe LICENSE en ninguna rama. El README de `main` declara una intención: "Código abierto bajo licencia MIT (o la que determine la gobernanza comunitaria de Gentleman Programming)." (código abierto bajo MIT, o la licencia que decida la gobernanza comunitaria de Gentleman Programming; `gentle-mesh@2d1d324:README.md:680`). `Inference:` sus ideas pueden citarse, pero su código no puede reutilizarse hasta que exista un archivo de licencia.

**Estado.** Las preguntas sobre estos puntos se enviaron al autor en la publicación de gentle-mesh en Discord el 2026-10-04. Respondió el 2026-10-04: añadirá una LICENSE MIT ("Mñn por la tarde cuando llegue a casa le pongo licence Mit"); el mantenedor aún no ha revisado gentle-mesh; las demás preguntas están pendientes (Discord, Rafael The Hutt, 2026-10-04 23:20). La integración depende del mantenedor, como dice la nota de gobernanza del README: "Este proyecto avanzará, evolucionará y se integrará de forma oficial única y exclusivamente bajo la revisión, orientación y aprobación explícita de Alan Buscaglia (@gentleman-programming), creador y líder del ecosistema Gentle AI." (este proyecto avanzará, evolucionará y se integrará oficialmente solo bajo la revisión, orientación y aprobación explícitas de Alan Buscaglia; `gentle-mesh@2d1d324:README.md:22`).

## Alternativas consideradas y descartadas

**[community]** Alternativas evaluadas para esta propuesta (autor Matrak; análisis de los autores del corpus, 2026-10-04). Un motivo principal para cada una; los hechos que lo respaldan están en Evidencia.

| Alternativa | Motivo principal del descarte | Evidencia |
|---|---|---|
| **Servidor en Go** | Reimplementa el dominio de sesión en un segundo lenguaje. | El dominio es TypeScript (`gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts`). Node sigue siendo necesario para ejecutar gentle-shell: su binario es un script de Node, `#!/usr/bin/env node` (`gentle-shell@ac67159:package.json:7-8`; `gentle-shell@ac67159:bin/gentle-shell.mjs:1`), con `"node": ">=22.19.0"` (`gentle-shell@ac67159:package.json:101-102`). |
| **Construir sobre T3 Code** | El soporte de Pi solo está en las builds nightly. | Solo nightly: ver [Precedentes en el ecosistema](#precedentes-en-el-ecosistema). Los diálogos bloqueantes `select`, `confirm`, `input` y `editor` funcionan (`t3code@eac52f0:docs/user/providers-pi.md:32-33`), pero "Pi terminal decoration such as titles, status lines, and widgets does not have a T3 Code equivalent" (`:33-34`). `Inference:` se pierde la actividad de los helpers, una carga `setWidget` ([04, Añadidos de gentle-shell sobre RPC](../04-rpc-contract.md#añadidos-de-gentle-shell-sobre-rpc)). |
| **Construir sobre pi-web-ui** (`xing-shuyin/pi-web-ui`) | Ejecuta el SDK de pi en el mismo proceso, no `gentle-shell --mode rpc`. | "the pi SDK runs in-process" (README `:70`); "ships and loads its own copy of the pi SDK" (`:234`); carga extensiones de pi, con interruptores por extensión (`:146`), y representa paneles `setWidget` (`:160`). `UNVERIFIED:` si carga específicamente las extensiones y los homes de gentle-shell; no probado. Fuente: https://github.com/xing-shuyin/pi-web-ui/blob/eb49d432ebd69b83fa2593695f586cfe569e7097/README.md (commit `eb49d432`, consultado el 2026-10-05) |
| **Plugin de Herdr** (el "herdr web" literal) | Necesita Herdr. | Se instala con `herdr plugin install devswha/herdr-web-ui` (`herdr-web-ui@7c5fe4e:README.md:98`); "herdr owns the processes" (`herdr-web-ui@7c5fe4e:docs/guide.md:422`). La documentación de Herdr dice que funciona en un teléfono "without a mobile app or web dashboard" (`herdr@5da0a01:docs/next/website/src/content/docs/how-to-work.mdx:49`); `Inference:` no hay un herdr web oficial. `kcosr/herdr-web` es "not associated with ... the official Herdr project" y usa APIs privadas de Herdr "for terminal attach" (`herdr-web@f1312e2:README.md:3`, `:14-15`); el chat de herdr-web-ui "reads the agents' own session files" (`herdr-web-ui@7c5fe4e:docs/guide.md:420`). `Inference:` los clientes de terminal o de transcripción no pueden manejar las tarjetas de pregunta, los helpers ni el panel de ODD. gentle-shell no carga automáticamente su puente de Herdr en modo RPC: la carga automática "is skipped for ... print/JSON/RPC modes (including interactive RPC hosts)" (`gentle-shell@ac67159:docs/readme-reference.md:380-382`; `gentle-shell@ac67159:bin/gentle-shell.mjs:191-199`). |
| **`pi-server` de pi** | Solo para desarrollo. | "Development-only command dispatch", que solo se ejecuta con `PI_EXPERIMENTAL=1` (`pi@a13d35a:packages/coding-agent/src/experimental/commands.ts:84-86`; `pi@a13d35a:packages/coding-agent/src/core/experimental.ts:1-3`); excluido de los paquetes de npm (`pi@a13d35a:packages/coding-agent/src/experimental/services/README.md:12`). Ejecuta sesiones pi-durable con facetas Chord (`:30`, `:36`; `pi@a13d35a:packages/coding-agent/src/experimental/session-worker.ts:15`). `Inference:` (sin `ExtensionAPI`/`loadExtensions` en `experimental/`, `rg`, 0 coincidencias) no carga las extensiones clásicas, que es como se distribuye gentle-shell (`gentle-shell@ac67159:package.json:59-62`). |

**Contraejemplo de seguridad: el servidor de open-pi-viewer.** Se sugirió en el hilo como conector web (Discord, bojack7080, 2026-10-04 09:00). No es una opción aquí, sino un patrón que evitar: un plugin del servidor de desarrollo de Vite (`open-pi-viewer@908245a:vite.config.ts:9-12`) que escucha en `0.0.0.0` (`:71`), con `Access-Control-Allow-Origin: *` (`:18`) y sin comprobación de token, cookie ni origen en ese archivo (`rg`), cuyos procesos hijo se ejecutan con `--approve` (`open-pi-viewer@908245a:server/bridge/rpc.ts:81`). Tiene licencia GPL-3.0 (`open-pi-viewer@908245a:LICENSE:1-2`).

## Preguntas abiertas

**Para el mantenedor:**

1. Qué significa "web": una UI de navegador para el agente local (con acceso remoto opcional), o un servicio alojado multiusuario.
2. A qué herdr web se refería. Los candidatos son `kcosr/herdr-web` y `devswha/herdr-web-ui`, que se enlazó en el hilo (Discord, Rafael The Hutt, 2026-09-30 09:27).
3. Web en lugar de escritorio, o ambos.
4. Un hijo por chat o un host compartido ([vision Q3](../00-vision.md#preguntas-abiertas-para-el-mantenedor)). Q3 contrapone "a shared host" a "one child process per chat", así que allí significa un único proceso del runtime que sirve a varios chats. Eso es algo distinto del servicio host de esta propuesta, que se sitúa por encima de los procesos hijo y funciona con cualquiera de las dos respuestas.

**Preguntas de diseño:**

1. **Proceso separado o integrado en el proceso principal de Electron.**

   | Opción | A favor | En contra |
   |---|---|---|
   | Proceso separado | Los clientes de navegador y móviles funcionan sin que la app de escritorio esté en ejecución; un único servicio para todos los clientes. | `Inference:` distribuido dentro de la app, puede ejecutarse con el propio binario de Electron de la app en modo Node, así que no añade un segundo binario que firmar ([11 §Ubicación del proceso](../11-host-service.md#ubicación-del-proceso-abierta)); ejecutarlo sin la app necesita un segundo distribuible que empaquetar, firmar y actualizar (hoy no se firma nada; [plataformas, empaquetado y firma](../10-platforms.md#empaquetado-y-firma), [milestone M5](../09-roadmap.md#m5-firma-y-actualización-automática)), además de un ciclo de vida (quién lo inicia y quién lo detiene). |
   | Integrado en el proceso principal de Electron | Nada nuevo que empaquetar ni firmar; el escritorio mantiene un único árbol de procesos. | `Inference:` los clientes de navegador y móviles solo funcionan mientras la app de escritorio está abierta. |

2. **Roadmap F1 antes o después de la extracción.** B1 es el trabajo de F1; hacerlo antes mantiene la extracción como un simple traslado, hacerlo después diseña el registro una sola vez, en el servicio.
3. **Dónde guarda el servicio su configuración.** Hoy la elección del primer arranque se guarda en el directorio de datos por usuario de Electron (`gentle-shell-desktop@5ab4a00:src/main/index.ts:52`), que un proceso separado no tiene.

## Dependencias

Tres documentos detallan esta propuesta; los tres existen:

- [Arquitectura del servicio host](../11-host-service.md)
- [Protocolo del host](../12-host-protocol.md)
- [Clientes y topologías](../13-clients-and-topologies.md)

## Fuentes

**Repositorios fijados** (clones de solo lectura; `repo@sha:path:line`):

| Nombre en las citas | Repositorio | Commit |
|---|---|---|
| `gentle-shell-desktop` | `Gentleman-Programming/gentle-shell-desktop` | `5ab4a00` |
| `gentle-shell` | `Gentleman-Programming/gentle-shell` (`main`, versión del paquete 4.0.0) | `ac67159` |
| `pi` | `earendil-works/pi` (v1.0.0) | `a13d35a` |
| `paseo` | `getpaseo/paseo` | `485221b` |
| `t3code` | `pingdotgg/t3code` | `eac52f0` |
| `gentle-mesh` | `Rafaeldelinares/gentle-mesh`: `main` (etiqueta `v1.0.2`) y la rama de integración `feat/rfc-002-settlement` | `2d1d324`, `f52335e` |
| `herdr` | `herdrdev/herdr` | `5da0a01` |
| `herdr-web-ui` | `devswha/herdr-web-ui` | `7c5fe4e` |
| `herdr-web` | `kcosr/herdr-web` | `f1312e2` |
| `open-pi-viewer` | `gonzalez962/open-pi-viewer` | `908245a` |

**Web** (consultado el 2026-10-05):

- README de `xing-shuyin/pi-web-ui` en el commit `eb49d432`: https://github.com/xing-shuyin/pi-web-ui/blob/eb49d432ebd69b83fa2593695f586cfe569e7097/README.md
- Última release de T3 Code, `v0.0.45`, y su árbol, mediante la API de GitHub: https://github.com/pingdotgg/t3code/releases/tag/v0.0.45

**Comunidad:**

- Hilo de Discord "Gentle Desktop" (copia guardada, no está en el repositorio): Alan Buscaglia, 2026-09-30 22:34 y 2026-10-01 11:17; Rafael The Hutt, 2026-09-27 23:33 y 2026-09-30 09:27; bojack7080, 2026-10-04 09:00.
- Discord, publicación de gentle-mesh: Rafael The Hutt, 2026-10-04 23:20.
- Conversación con Matrak, 2026-10-04 (no publicada).

**Corpus:** [auditoría](../03-architecture/audit.md), [contrato RPC](../04-rpc-contract.md), [visión](../00-vision.md), [hoja de ruta](../09-roadmap.md), [plataformas](../10-platforms.md), [arquitectura del servicio host](../11-host-service.md), [protocolo del host](../12-host-protocol.md).
