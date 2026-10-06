> Traducción al español de `docs/12-host-protocol.md` (commit `9cad584`). Documento de lectura; la versión de referencia es la inglesa.

# Protocolo del host

> Estado: borrador, propuesta de la comunidad pendiente de validación del mantenedor (draft (community proposal, awaiting maintainer validation)).

> **Boceto de diseño (design sketch) [community], no una especificación.** Esta página esboza el protocolo cliente ↔ servicio del servicio host (host service) local compartido que se propone en la [propuesta 0004](07-proposals/0004-host-service.md), cuya arquitectura está en [11-host-service.md](11-host-service.md). Nada de lo que aquí se describe existe hoy en el repositorio del escritorio, y nada está decidido. Los nombres de las tramas y sus campos son ilustrativos. El contrato servicio ↔ gentle-shell sigue siendo [04-rpc-contract.md](04-rpc-contract.md), sin cambios.

**En un párrafo.** **[community]** Cada cliente WebSocket (una pestaña del navegador, una futura app móvil y la ventana de Electron con la ubicación (a); con la ubicación (b) la ventana puede conservar el puente del preload, ver [11, Ubicación del proceso](11-host-service.md#ubicación-del-proceso-abierta)) abre un WebSocket hacia el servicio host e intercambia tramas JSON: primero un handshake `hello`/`welcome`, después peticiones y respuestas correlacionadas por `id`, suscripciones por chat y eventos enviados por el servidor. El protocolo parte del `GentleBridge` actual del escritorio (8 métodos de petición, 2 canales de envío) y añade lo que el IPC de Electron nunca necesitó: un `chatId` en cada trama con ámbito de chat (B1), un handshake de versión (B3), un sobre de error con un código y un indicador `retryable`, y autenticación con validación de argumentos (B4). Los envíos siguen siendo instantáneas completas de `ChatState`, como hoy, así que un cliente que se reconecta vuelve a suscribirse y recibe la instantánea actual en lugar de reproducir un registro. La política de versionado, el modelo de autenticación remota, la propiedad de un chat entre varios clientes, los límites de contrapresión, la elección de la delimitación de registros y las instantáneas completas frente a los deltas están abiertos (HP-01 a HP-06), igual que si los clientes de loopback necesitan una credencial (HP-07).

## Cómo leer esta página

| Etiqueta | Significado |
|---|---|
| **[maintainer]** | Declarado en los documentos del repositorio del escritorio del mantenedor o en sus mensajes de Discord. |
| **[community]** | Propuesto por la comunidad. No decidido. |
| `Inference:` | Razonamiento a partir de evidencias citadas, no un hecho declarado. "(no ejecutado)" significa que no se construyó ni se ejecutó nada. |
| `UNVERIFIED:` | Comprobado pero no confirmado. |

- **Claves de cita.** El código se cita como `repo@shortsha:path:line`: `gentle-shell-desktop@5ab4a00` (el código fuente no cambia en esta rama), `gentle-shell@ac67159` (`main` de gentle-shell, versión del paquete 4.0.0), `pi@a13d35a` (pi 1.0.0), `paseo@485221b`, `t3code@eac52f0`, `herdr-web-ui@7c5fe4e` y `open-pi-viewer@908245a`. `:N` después de una cita completa repite su archivo. Las fuentes web llevan una fecha de consulta. Las páginas del corpus se enlazan por ruta relativa.
- **ID cualificados.** Los ID de otras páginas llevan su página: `audit A3`, `gap G9`, `vision Q3`, `QW-05`. **B1–B6** son los requisitos del runtime de la [propuesta 0004](07-proposals/0004-host-service.md#requisitos-del-runtime), y se escriben sin cualificar, como en [11](11-host-service.md#cómo-leer-esta-página). **HP-01 a HP-07** son las preguntas abiertas de esta página; en otros lugares se escriben tal cual (el prefijo `HP-` es único en el corpus).
- **Método.** Solo lectura estática, como en la [auditoría](03-architecture/audit.md#método-y-alcance). No se prototipó nada.

## De un vistazo

| Pregunta | Respuesta | Evidencia |
|---|---|---|
| ¿Qué conecta? | **[community]** Una pestaña del navegador, una futura app móvil y la ventana de Electron con la ubicación (a) con el servicio host, mediante un WebSocket por cliente. Con la ubicación (b) la ventana puede conservar el puente del preload. | [propuesta 0004](07-proposals/0004-host-service.md#propuesta); [11, Ubicación del proceso](11-host-service.md#ubicación-del-proceso-abierta) |
| ¿A partir de qué se construye? | El `GentleBridge` actual: 8 métodos de petición y 2 suscripciones de envío, reflejados en 8 + 2 canales de IPC. | [Punto de partida](#punto-de-partida-el-puente-actual) |
| ¿Qué añade? | `chatId` en las tramas con ámbito de chat, suscripciones, un handshake de versión, un sobre de error, autenticación y validación de argumentos. | [Qué debe añadir un transporte de red](#qué-debe-añadir-un-transporte-de-red) |
| ¿Codificación? | Tramas de texto JSON. Todas las cargas del puente son datos planos; dos campos tienen el tipo `unknown`. | [Transporte y delimitación de registros](#transporte-y-delimitación-de-registros) |
| ¿Cómo se resincroniza un cliente? | Vuelve a suscribirse y recibe el `ChatState` actual, que hoy ya es una instantánea completa en cada envío. | [Reconexión y repetición](#reconexión-y-repetición) |
| ¿Quién puede conectarse? | Loopback por defecto; un token o un emparejamiento para cualquier otra cosa; una lista de `Origin` permitidos para los navegadores. | [Autenticación y origen](#autenticación-y-origen) |
| ¿Cambia el contrato RPC? | No. El servicio habla [04-rpc-contract.md](04-rpc-contract.md) con sus procesos hijo, como hace hoy el escritorio. | [11, Responsabilidades](11-host-service.md#responsabilidades) |
| ¿Qué está abierto? | La política de versionado, la autenticación remota, la propiedad entre varios clientes, los límites de contrapresión, la delimitación de registros, instantáneas frente a deltas, una credencial en loopback. | [Preguntas abiertas](#preguntas-abiertas) |

## Punto de partida: el puente actual

El renderer habla con el proceso principal mediante `GentleBridge` (`gentle-shell-desktop@5ab4a00:src/shared/bridge-types.ts:273-295`), que el preload expone como `window.gentle` (`gentle-shell-desktop@5ab4a00:src/preload/index.ts:4`). `createBridge` asocia cada método a un canal de IPC (`gentle-shell-desktop@5ab4a00:src/preload/bridge.ts:19-43`), y `registerHandlers` pasa cada canal a `ChatHost` o a `SetupService` (`gentle-shell-desktop@5ab4a00:src/main/ipc/registerHandlers.ts:27-40`). La misma tabla, desde el lado del IPC, está en [current.md](03-architecture/current.md#ipc-entre-el-proceso-principal-y-el-renderer).

| Miembro del puente | Canal | Argumentos | Resultado | Evidencia (`gentle-shell-desktop@5ab4a00:src/`) |
|---|---|---|---|---|
| `listChats()` | `sessions.list` | — | `ChatSummary[]` | `shared/bridge-types.ts:274`; `shared/ipc-channels.ts:9`; `main/ipc/registerHandlers.ts:28` |
| `openChat(id)` | `chat.open` | `id: string` (el id de sesión de pi) | `ChatState` | `shared/bridge-types.ts:275-276`; `shared/ipc-channels.ts:10`; `main/ipc/registerHandlers.ts:29`; `main/domain/session/ChatHost.ts:100-102` |
| `newChat()` | `chat.new` | — | `ChatState` (sin id) | `shared/bridge-types.ts:277-278`; `shared/ipc-channels.ts:11`; `main/ipc/registerHandlers.ts:30` |
| `sendMessage(text)` | `chat.send` | `text: string` | `PromptResult` (`{queued, reason?}`) | `shared/bridge-types.ts:279-282`, `:106-109`; `shared/ipc-channels.ts:12`; `main/ipc/registerHandlers.ts:31` |
| `abort()` | `chat.abort` | — | `void` | `shared/bridge-types.ts:283`; `shared/ipc-channels.ts:13`; `main/ipc/registerHandlers.ts:32` |
| `answerDialog(id, answer)` | `dialog.answer` | `id: string`, `answer: DialogAnswer` | `void` | `shared/bridge-types.ts:284`, `:92`; `shared/ipc-channels.ts:14`; `main/ipc/registerHandlers.ts:33-35` |
| `setupStatus()` | `setup.status` | — | `SetupStatus` | `shared/bridge-types.ts:289-291`, `:261-264`; `shared/ipc-channels.ts:20`; `main/ipc/registerHandlers.ts:36` |
| `chooseHome(mode)` | `setup.chooseHome` | `mode: HomeMode` (`"link"` o `"isolated"`) | `void` | `shared/bridge-types.ts:292-294`, `:237-242`; `shared/ipc-channels.ts:22`; `main/ipc/registerHandlers.ts:37` |
| `onState(cb)` | `chat.state` (envío) | — | `ChatState` por envío; devuelve una función para cancelar la suscripción | `shared/bridge-types.ts:285-286`; `shared/ipc-channels.ts:16`; `main/ipc/registerHandlers.ts:39` |
| `onError(cb)` | `chat.error` (envío) | — | `string` por envío; devuelve una función para cancelar la suscripción | `shared/bridge-types.ts:287-288`; `shared/ipc-channels.ts:18`; `main/ipc/registerHandlers.ts:40` |

`ChatState` es `{messages, working, pendingDialogs, lastError?, activity, helpers}` (`gentle-shell-desktop@5ab4a00:src/shared/bridge-types.ts:122-129`).

### Qué debe añadir un transporte de red

| Lo que falta hoy | Evidencia | Lo añade |
|---|---|---|
| **Un id de chat.** Los comandos actúan sobre "whichever chat is currently open", y `onState` se suscribe a "ChatState pushes for the currently open chat". Ni `ChatState` ni los envíos llevan un id. | `gentle-shell-desktop@5ab4a00:src/shared/bridge-types.ts:279`, `:285`, `:122-129`; [audit A3](03-architecture/audit.md#a3-host-de-sesión-única-con-ids-de-mensaje-posicionales) | `chatId` en cada trama con ámbito de chat (B1) |
| **Suscripciones.** Cada ventana recibe todos los envíos del único `ChatHost`: `registerHandlers` reenvía todos los eventos de estado y de error a su `webContents`. | `gentle-shell-desktop@5ab4a00:src/main/ipc/registerHandlers.ts:39-40`; `gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts:85-93`, `:192-198` | `subscribe` / `unsubscribe` por chat |
| **Un sobre de error.** Una petición rechazada llega al renderer solo como una cadena de mensaje. | [Errores](#errores) | `{code, message, retryable}` |
| **Autenticación y validación.** Los manejadores de IPC confían en el renderer y usan sus argumentos tal cual. | `gentle-shell-desktop@5ab4a00:src/main/ipc/registerHandlers.ts:28-37`; [audit A14](03-architecture/audit.md#a14-endurecimiento-del-preload-y-del-ipc) | Autenticación en el handshake y validación por esquema (B4) |
| **Una versión.** Nada en el puente ni en la cadena RPC la lleva. | [audit A8](03-architecture/audit.md#a8-sin-handshake-de-versión); [gap G10](04-rpc-contract.md#carencias-que-necesita-el-escritorio) | `hello` / `welcome` (B3) |

## Transporte y delimitación de registros

**[community]** Un WebSocket por cliente. Cada trama es un objeto JSON en un mensaje de texto de WebSocket, discriminado por `type`.

| `type` de la trama | Dirección | Campos (ilustrativos) | Propósito |
|---|---|---|---|
| `hello` | cliente → servicio | `protocol`, `client: {name, version}`, `auth?` | Debe ser la primera trama. Ver [Handshake y versiones](#handshake-y-versiones). |
| `welcome` | servicio → cliente | `protocol`, `service: {version}`, `runtime: {gentleShell, pi}` o `null`, `runtimeError?` | Respuesta del handshake. |
| `request` | cliente → servicio | `id`, `method`, `params` | Una llamada a un método del puente. |
| `response` | servicio → cliente | `id`, y después `ok: true, result` u `ok: false, error: {code, message, retryable}` | Se correlaciona con su petición por `id`, no por orden. |
| `subscribe` | cliente → servicio | `id`, `chatId` | Empezar a recibir los envíos de un chat. Se responde con una `response` cuyo `result` es el `ChatState` actual. |
| `unsubscribe` | cliente → servicio | `id`, `chatId` | Dejar de recibirlos. |
| `event` | servicio → cliente | `event`, `chatId`, `data` | Un envío: `chat.state` o `chat.error`. |

- **Correlación por `id`.** La misma regla que usa el RPC de pi: "Correlate by `id`, not by order" ([04, Correlación y errores](04-rpc-contract.md#correlación-y-errores)).
- **`chatId` en cada trama con ámbito de chat.** Las peticiones sobre un chat lo llevan en `params`; `subscribe`, `unsubscribe` y `event` lo llevan en el nivel superior. Esto es B1 en la conexión: audit A3 recomienda "Add a `chatId` to every push and command" ([audit A3](03-architecture/audit.md#a3-host-de-sesión-única-con-ids-de-mensaje-posicionales), recomendación 2), y gap G9 sitúa los varios chats en la arquitectura del escritorio, no en el protocolo RPC ([gap G9](04-rpc-contract.md#carencias-que-necesita-el-escritorio)).
- **Qué es un `chatId`.** Hoy el id de un chat es el id de sesión de pi: "ChatSummary.id is pi's session id, not a file path" (`gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts:100-102`). `newChat()` devuelve un `ChatState` sin id (`gentle-shell-desktop@5ab4a00:src/shared/bridge-types.ts:277-278`). `Inference:` el servicio debe devolver el id del chat nuevo desde `chat.new`; el `get_state` de pi informa del id de sesión ([04, Comandos](04-rpc-contract.md#comandos-escritorio--runtime)), y el escritorio ya lo tiene tipado sin enviarlo.
- **JSON basta.** Todas las cargas del puente son datos planos (`gentle-shell-desktop@5ab4a00:src/shared/bridge-types.ts:23-264`). Dos campos tienen el tipo `unknown`: `HelperThreadToolItem.args` y `.output` (`:157-158`). El parser los copia directamente de un resultado de `JSON.parse` (`gentle-shell-desktop@5ab4a00:src/main/domain/rpc/helpersActivity.ts:43`, `:113-114`). `Inference:` por tanto ya son valores JSON y se vuelven a codificar sin pérdida; los campos opcionales que quedan en `undefined` simplemente se omiten.

**Ejemplo de intercambio** (ilustrativo):

```json
{"type":"request","id":"7","method":"chat.send","params":{"chatId":"<pi session id>","text":"Run the tests"}}
{"type":"response","id":"7","ok":true,"result":{"queued":true}}
{"type":"event","event":"chat.state","chatId":"<pi session id>","data":{"messages":[],"working":true,"pendingDialogs":[],"activity":0,"helpers":{"summary":{"running":0,"queued":0,"waiting":0,"finished":0},"tasks":[]}}}
```

**Cómo delimitan los registros los precedentes.**

| Proyecto | Delimitación de registros | Evidencia |
|---|---|---|
| **Paseo** | Una "WebSocket API" (`paseo@485221b:README.md:172`) en la ruta `/ws` (`paseo@485221b:packages/server/src/server/websocket-server.ts:821-823`). Las tramas se discriminan por `type`: de entrada `ping`, `hello`, `recording_state`, `session`; de salida `pong`, `session`, `hello.rejected` (`paseo@485221b:packages/protocol/src/messages.ts:7545-7556`). Las peticiones llevan un `requestId` (por ejemplo `:1849-1852`); algunas peticiones de listado aceptan un campo `subscribe` para seguir recibiendo actualizaciones (`:993-997`, `:1253-1257`). | según se cita |
| **T3 Code** | Un grupo RPC de Effect servido sobre WebSocket en `/ws` con serialización JSON (`t3code@eac52f0:apps/server/src/ws.ts:3772-3775`, `:3806-3823`; cliente: `t3code@eac52f0:packages/client-runtime/src/rpc/protocol.ts:1-5`). Las suscripciones son RPC declarados con `stream: true`, por ejemplo la suscripción por hilo (`t3code@eac52f0:packages/contracts/src/rpc.ts:1575-1580`). | según se cita |

`Inference:` ambos usan un socket por cliente, tramas tipadas y suscripciones por recurso, que es la forma descrita arriba. El sobre propio de Paseo y el definido por el framework de T3 son los dos extremos de [HP-05](#preguntas-abiertas).

## Handshake y versiones

**[community]** La primera trama del cliente es `hello`. El servicio responde `welcome`, o rechaza y cierra. Los clientes y el servicio pueden actualizarse por separado (B3), así que el handshake existe desde la versión 1 del protocolo.

| Paso | Qué ocurre |
|---|---|
| 1. `hello` | El cliente envía su versión del protocolo (un entero) y su propio nombre y versión, más las credenciales cuando se requieren ([Autenticación y origen](#autenticación-y-origen)). Cualquier otra primera trama, o la ausencia de `hello` dentro de un tiempo límite, cierra el socket. |
| 2. Versiones del runtime | El servicio lee las versiones de gentle-shell y pi por fuera del canal, con `gentle-shell --version`, como recomienda audit A8 (`gentle-shell@ac67159:bin/gentle-shell.mjs:1217-1219`; [audit A8](03-architecture/audit.md#a8-sin-handshake-de-versión)). La salida tiene tres líneas, `gentle-shell <version>`, `pi <version>` y `home <mode> <dir>` (`gentle-shell@ac67159:lib/gentle-shell-launcher.ts:1138-1144`). |
| 3. `welcome` | El servicio responde con su versión del protocolo, su propia versión y las versiones del runtime. |
| 4. Discrepancia | Una versión del protocolo que el servicio no admite recibe un rechazo tipado (`protocol_unsupported`, con el rango admitido) y después un cierre. La versión de un cliente es informativa. |

**Por qué por fuera del canal.** El protocolo RPC no lleva ningún campo de versión, y ningún registro de arranque anuncia una ([04, ¿Hay un handshake de versión?](04-rpc-contract.md#hay-un-handshake-de-versión)). La única solución alternativa de gap G10 es `gentle-shell --version` ([gap G10](04-rpc-contract.md#carencias-que-necesita-el-escritorio)). El lanzador comprueba pi antes de imprimir las versiones y termina con un error cuando la comprobación falla (`gentle-shell@ac67159:bin/gentle-shell.mjs:1215-1219`).

`Inference:` (no ejecutado)

- **Un problema del runtime no es un fallo del handshake.** Cuando falta el lanzador o pi es demasiado antiguo, `welcome` sigue teniendo éxito con `runtime: null` y un `runtimeError`, así que el cliente puede mostrar indicaciones de configuración en lugar de un socket muerto.
- **La línea `home` se queda en local.** Lleva un directorio local (`gentle-shell@ac67159:lib/gentle-shell-launcher.ts:1142`). Un cliente remoto necesita las versiones, no la ruta. Lo mismo se aplica a `PiDetection.dir` en `setup.status` (`gentle-shell-desktop@5ab4a00:src/shared/bridge-types.ts:249-254`).
- **Cuándo leer las versiones.** Una vez al iniciar el servicio y otra antes de lanzar un proceso hijo tras un cambio de home; un proceso hijo en ejecución conserva las versiones con las que arrancó.

**Cómo versionan los precedentes.**

- **Paseo.** `hello` lleva `protocolVersion`, un `appVersion` opcional y un mapa de indicadores de capacidades del cliente (`paseo@485221b:packages/protocol/src/messages.ts:7487-7520`). El servidor cierra un socket que no envía `hello` en 15 s (código 4001) y solo rechaza un `protocolVersion` inferior a 1, con el código 4003; por encima de ese mínimo se basa en los indicadores de capacidades (`paseo@485221b:packages/server/src/server/websocket-server.ts:484-489`, `:1336-1351`, `:1568-1579`). Los clientes que anuncian que lo admiten reciben antes una trama tipada `hello.rejected` con un motivo (`:1705-1734`; `paseo@485221b:packages/protocol/src/messages.ts:7538-7542`). Su app de escritorio reinicia un daemon en ejecución cuya versión no coincide (`paseo@485221b:packages/desktop/src/daemon/daemon-manager.ts:291-297`).
- **T3 Code.** El cliente pone la versión del protocolo en la URL del upgrade (`orchestrationProtocol`), y el servidor responde a una discrepancia con HTTP 426 y el código `orchestration_protocol_incompatible` antes de que exista ningún WebSocket (`t3code@eac52f0:packages/contracts/src/environment.ts:12-15`; `t3code@eac52f0:apps/server/src/ws.ts:602-606`, `:3778-3786`). La superficie del cliente y la versión de la app también viajan como parámetros de consulta (`t3code@eac52f0:apps/server/src/ws.ts:618-630`). El descriptor del servidor lleva `serverVersion` y la versión del protocolo (`t3code@eac52f0:packages/contracts/src/environment.ts:203-211`).

`Inference:` un `hello` como primera trama (Paseo) funciona para cualquier cliente WebSocket, incluida la API `WebSocket` del navegador, que no puede establecer cabeceras de upgrade personalizadas; un parámetro de consulta (T3) rechaza antes, pero pone la versión en la URL. Esta página sigue a Paseo; la regla de evolución es [HP-01](#preguntas-abiertas).

## Tabla de correspondencias

**[community]** Cada miembro del puente asociado a tramas. "chatId" marca las tramas a las que B1 lo añade.

| Miembro del puente | Trama | `params` / carga | Resultado o envío | chatId |
|---|---|---|---|---|
| `listChats()` | `request` `chats.list` | — | `ChatSummary[]` | no (lista todos los chats) |
| `openChat(id)` | `request` `chat.open` | `chatId` | `ChatState` | sí |
| `newChat()` | `request` `chat.new` | `cwd?` (B6) | `{chatId, state: ChatState}` | se devuelve |
| `sendMessage(text)` | `request` `chat.send` | `chatId`, `text` | `PromptResult` | sí |
| `abort()` | `request` `chat.abort` | `chatId` | — | sí |
| `answerDialog(id, answer)` | `request` `dialog.answer` | `chatId`, `dialogId`, `answer: DialogAnswer` | — | sí |
| `setupStatus()` | `request` `setup.status` | — | `SetupStatus` | no |
| `chooseHome(mode)` | `request` `setup.chooseHome` | `mode` | — | no |
| `onState(cb)` | `subscribe` / `unsubscribe` | `chatId` | `event` `chat.state` con un `ChatState` completo | sí |
| `onError(cb)` | cubierto por la misma suscripción | `chatId` | `event` `chat.error` con `{code, message, retryable}` | sí |

Notas:

- **Nombres de los métodos.** `chats.list` sustituye al canal de IPC `sessions.list` (ilustrativo); los demás nombres siguen los canales de IPC de [Punto de partida](#punto-de-partida-el-puente-actual).
- **`PromptResult` sigue siendo un resultado.** Un prompt enviado mientras el chat trabaja se declina con `{queued: false, reason}` en lugar de rechazarse, "so the caller reports it exactly once" (`gentle-shell-desktop@5ab4a00:src/shared/bridge-types.ts:279-282`; `gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:168-180`). Declinar no es una trama de error.
- **`chat.open` ya no detiene otros chats.** Hoy `performStart` detiene antes la sesión actual (`gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts:156-157`). `Inference:` con un registro (B1), `chat.open` significa "asegurar que este chat tiene un proceso hijo", y cerrar un chat pasa a ser una petición aparte (por ejemplo `chat.close`), que el puente no tiene hoy.
- **`chat.new` acepta `cwd`.** B6: `PiSession` acepta un `cwd`, pero `ChatHost` nunca le pasa uno (`gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:15`, `:135`; `gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts:159-166`; [audit A10](03-architecture/audit.md#a10-los-chats-nuevos-se-ejecutan-en-el-directorio-de-trabajo-de-la-aplicación)).
- **`chats.list` y las actualizaciones.** La barra lateral carga la lista una vez ([audit A11](03-architecture/audit.md#a11-ciclo-de-vida-de-la-lista-de-chats-y-de-la-selección)). `Inference:` una suscripción a nivel de lista permitiría al servicio enviar los cambios de la lista a todos los clientes; se deja fuera de este boceto.

### `dialog.answer`: id de chat más id de diálogo

- **Los ids de diálogo vienen de pi.** El id de un diálogo es el `id` del `extension_ui_request` de pi (`gentle-shell-desktop@5ab4a00:src/main/domain/rpc/chatReducer.ts:165-179`), un `crypto.randomUUID()` generado por petición (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-mode.ts:99`, `:129`). `Inference:` único en la práctica, pero el servicio sigue necesitando `chatId` para encontrar el proceso hijo que debe recibir la respuesta.
- **Las respuestas tardías o duplicadas se descartan en silencio.** pi resuelve por su cuenta un diálogo que tiene un `timeout` (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-mode.ts:115-120`) e ignora una respuesta cuyo id ya no está pendiente (`:774-779`). Hoy el escritorio quita la tarjeta y escribe la respuesta en ambos casos (`gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:193-207`). Esto es [audit A12](03-architecture/audit.md#a12-timeouts-de-los-diálogos-no-modelados): el codec decodifica `timeout`, pero el tipo `Dialog` lo descarta.
- `Inference:` el servicio sabe qué diálogos están pendientes en cada chat, así que puede responder a una respuesta obsoleta o a una segunda respuesta con `dialog_not_pending` en lugar de aceptarla en silencio. Con varios clientes esto deja de ser raro: dos clientes que muestran la misma tarjeta pueden responderla los dos ([HP-03](#preguntas-abiertas)).

## Errores

**Hoy hay dos caminos de error, ambos solo con mensaje.**

| Camino | De dónde viene | Qué recibe el renderer |
|---|---|---|
| **Petición rechazada** | Los manejadores lanzan: `ChatHost: no session found for id …` (`gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts:106`), `ChatHost: no chat is open …` (`:188`), `Could not save the home choice: …` (`gentle-shell-desktop@5ab4a00:src/main/adapters/setupService.ts:37`). Electron: "Errors thrown through `handle` in the main process are not transparent as they are serialized and only the `message` property from the original error is provided to the renderer process." (https://www.electronjs.org/docs/latest/api/ipc-main, consultado el 2026-10-05). El código del escritorio dice lo mismo: "ipc's handle() rejection carries only the message text to the renderer" (`gentle-shell-desktop@5ab4a00:src/main/adapters/setupService.ts:33-34`). | Una cadena: `errorText` conserva `cause.message` (`gentle-shell-desktop@5ab4a00:src/renderer/features/conversation/ConversationContainer.tsx:35-37`, `:89-91`, `:107`, `:111`, `:115`). |
| **Error enviado** | `PiSession` "Never throws from a public method"; los fallos establecen `lastError` y emiten `error` (`gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:77-81`, `:326-330`). Un lanzador que falta acaba aquí: `locate()` lanza dentro del `try` de `start()` (`:125-126`, `:148-149`; `gentle-shell-desktop@5ab4a00:src/main/adapters/launcherLocator.ts:25-29`). También una salida inesperada (`gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:319-321`). | Una cadena en `chat.error` (`gentle-shell-desktop@5ab4a00:src/main/ipc/registerHandlers.ts:40`) y `ChatState.lastError`. |

**[community] El sobre.** Ambos caminos llevan el mismo objeto: `{code, message, retryable}`. `code` es una cadena estable sobre la que un cliente puede ramificar; `message` es legible por personas; `retryable` dice si la misma petición, sin cambios, puede tener éxito más adelante.

| `code` (ilustrativo) | `retryable` | Origen hoy |
|---|---|---|
| `bad_request` | no | Ninguno: no hay validación de argumentos ([audit A14](03-architecture/audit.md#a14-endurecimiento-del-preload-y-del-ipc)). |
| `unauthorized` | no | Ninguno: nuevo con la autenticación. |
| `protocol_unsupported` | no | Ninguno: nuevo con el handshake. |
| `chat_not_found` | no | `gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts:106` |
| `chat_not_open` | no | `gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts:188` |
| `dialog_not_pending` | no | Ninguno: pi descarta la respuesta en silencio ([dialog.answer](#dialoganswer-id-de-chat-más-id-de-diálogo)). |
| `launcher_not_found` | sí, después de que el usuario lo instale | `gentle-shell-desktop@5ab4a00:src/main/adapters/launcherLocator.ts:25-29`, hoy se envía |
| `child_exited` | sí | `gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:319-321`, hoy se envía |
| `config_write_failed` | sí | `gentle-shell-desktop@5ab4a00:src/main/adapters/setupService.ts:37` |
| `internal` | no | Cualquier otra cosa. |

`Inference:` `retryable` permite a un cliente decidir entre reintentar, mostrar una acción para solucionarlo y desistir sin interpretar `message`. La respuesta de fallo del propio RPC de pi es `{type:"response", command, success:false, error}` con una cadena `error` ([04, Correlación y errores](04-rpc-contract.md#correlación-y-errores)); el servicio traduce los fallos de los procesos hijo al sobre en lugar de reenviar esa cadena.

**Precedentes.** El `rpc_error` de Paseo lleva `requestId`, un `requestType` opcional, `error` y un `code` opcional (`paseo@485221b:packages/protocol/src/messages.ts:3748-3756`). T3 declara una unión tipada de errores por RPC (`t3code@eac52f0:packages/contracts/src/rpc.ts:1575-1580`) y responde a un protocolo incompatible con un cuerpo JSON que contiene `code` y `message` (`t3code@eac52f0:apps/server/src/ws.ts:3779-3785`). Ninguno tiene un campo `retryable` en el código leído aquí.

## Reconexión y repetición

**Hecho: los envíos ya son instantáneas completas.** `PiSession` integra cada línea decodificada en `this.state` y emite el objeto completo (`gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:253`, `:259`); lo mismo hacen `prompt` y `answerDialog` (`:182-183`, `:194-198`). `ChatHost` lo reenvía sin cambios (`gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts:167`, `:192-194`), y `registerHandlers` lo envía como carga de `chat.state` (`gentle-shell-desktop@5ab4a00:src/main/ipc/registerHandlers.ts:39`). El renderer sustituye su estado con cada envío (`gentle-shell-desktop@5ab4a00:src/renderer/features/conversation/ConversationContainer.tsx:60-67`).

**[community] Reconexión.**

1. El cliente se reconecta y vuelve a enviar `hello`.
2. Envía `subscribe` para cada chat que muestra.
3. Cada respuesta a `subscribe` lleva el `ChatState` actual de ese chat; los eventos `chat.state` posteriores lo sustituyen.

`Inference:` no hace falta ningún registro de eventos ni ningún cursor más allá del `rev` descrito abajo, porque ningún envío depende de uno anterior. El propio historial del chat sigue en los archivos de sesión de pi, no en el servicio ([11, Ubicación de la configuración y del estado](11-host-service.md#ubicación-de-la-configuración-y-del-estado-abierta)).

`Inference:` (no ejecutado)

- **Un número de revisión por chat.** El renderer ya enfrenta un resultado de `openChat` con los envíos del mismo chat (`gentle-shell-desktop@5ab4a00:src/renderer/features/conversation/ConversationContainer.tsx:60-67`, `:81-95`). Un `rev` que aumente con cada instantánea, tanto en el resultado de `subscribe` como en cada evento, permite a un cliente descartar una instantánea más antigua que otra que ya tiene.
- **Las instantáneas abaratan la gestión de los clientes lentos.** Una instantánea más reciente sustituye a todas las anteriores, así que el servicio puede conservar solo la última instantánea pendiente por chat y cliente y descartar el resto sin perder estado.
- **Las instantáneas no son gratis.** Cada delta de texto en streaming vuelve a enviar el `ChatState` completo, con todos los mensajes. Los hilos de los helpers están acotados en upstream (los últimos 40 elementos, [04, gap G8](04-rpc-contract.md#carencias-que-necesita-el-escritorio)), pero `messages` crece con el chat. Mantener las instantáneas o pasar a deltas es [HP-06](#preguntas-abiertas).

**Cómo repiten y acotan la salida los precedentes.**

| Proyecto | Qué transmite | Repetición al reconectar | Contrapresión | Evidencia |
|---|---|---|---|---|
| **Paseo** | Líneas de tiempo de agentes y otro estado | Basada en cursor: una consulta de la línea de tiempo recibe un cursor `{epoch, seq}`, y la respuesta informa de `reset`, `staleCursor` y `gap` | Cierra (termina) un socket cuya salida en búfer superaría 64 MiB. Los clientes hacen ping cada 10 s; se cierra un socket de aplicación sin tráfico durante 45 s. `docs/architecture.md:268` de Paseo indica 8 MiB; la constante del código es 64 MiB (`physical-socket.ts:4`), también usada para la cola del relay (`encrypted-relay-socket.ts:62`). | `paseo@485221b:packages/protocol/src/messages.ts:1844-1861`, `:4591-4616`; `paseo@485221b:packages/server/src/server/websocket-server.ts:1245-1262`; `paseo@485221b:packages/server/src/server/websocket/physical-socket.ts:4-8`, `:89-95` |
| **T3 Code** | Proyecciones y eventos de hilos | Una suscripción empieza con una instantánea o, si se indica `afterSequence`, "the server skips the initial snapshot frame and instead replays events after this sequence before streaming live events" | Un presupuesto por suscripción: 1.000 elementos u 8 MiB; si se desborda, el flujo falla con "The live event buffer is full. Resume from the last received sequence." | `t3code@eac52f0:packages/contracts/src/orchestrationV2.ts:3061-3075`, `:3078-3093`; `t3code@eac52f0:apps/server/src/orchestration-v2/LiveStreamBudget.ts:17-18`, `:39`, `:72-74` |
| **herdr-web-ui** | Un flujo de bytes de terminal | Una cola de repetición con los últimos 256 KiB por panel adjunto | Crédito por ACK: el navegador confirma desplazamientos de bytes después de que xterm los interpreta; la salida se pausa con 256 KiB pendientes y se reanuda con 64 KiB; un cliente bloqueado durante 2 s, o que supera un presupuesto de 1 MiB, se cierra con el código 4008, y la UI no se reconecta automáticamente: "Overloaded output stops this connection; automatic replay could conceal lost ANSI state." | `herdr-web-ui@7c5fe4e:server/index.ts:78`, `:620`, `:284-297`, `:446-475`; `herdr-web-ui@7c5fe4e:server/output-window.ts:3-6`, `:16-28`; `herdr-web-ui@7c5fe4e:shared/protocol.ts:582-585`; `herdr-web-ui@7c5fe4e:shared/terminal-flow.ts:1-2` |

`Inference:` los tres difieren porque sus datos difieren. herdr-web-ui transmite bytes que no pueden descartarse ni volver a derivarse, así que necesita crédito, y no repite automáticamente tras un cierre por sobrecarga; una reconexión normal sigue repitiendo su cola de 256 KiB (`herdr-web-ui@7c5fe4e:server/index.ts:78`, `:620`; `herdr-web-ui@7c5fe4e:shared/protocol.ts:591`; `herdr-web-ui@7c5fe4e:shared/terminal-flow.ts:1`). Paseo y T3 transmiten registros, así que necesitan cursores y huecos. Este protocolo transmite estado autocontenido, así que puede agrupar y no necesita ninguna de las dos cosas, a costa del tamaño de los mensajes. Los tres acotan la memoria por cliente y desconectan a un cliente que no puede seguir el ritmo; el servicio host también necesita una cota así ([HP-04](#preguntas-abiertas)).

## Autenticación y origen

**[community]** Los valores por defecto de la [propuesta 0004](07-proposals/0004-host-service.md#propuesta), en términos del protocolo:

| Regla | Qué significa en la conexión | Precedente |
|---|---|---|
| **Loopback por defecto** | El servicio escucha en `127.0.0.1` salvo que se configure otra cosa. | Paseo usa por defecto `127.0.0.1:6767` (`paseo@485221b:packages/server/src/server/config.ts:470`, `:476-480`); T3, `127.0.0.1` (`t3code@eac52f0:apps/server/src/server.ts:249`). |
| **Una credencial para cualquier otra cosa** | `hello.auth` lleva un token, o el cliente se emparejó antes. | Ver abajo. |
| **Una lista de `Origin` permitidos** | El upgrade se rechaza cuando el `Origin` de un navegador no está permitido. | Ver abajo. |
| **Validación de argumentos** | Cada trama se comprueba contra un esquema antes de llegar al dominio; los fallos responden `bad_request`. | Paseo analiza cada trama de entrada con un esquema de zod, `WSInboundMessageSchema.safeParse` (`paseo@485221b:packages/protocol/src/messages.ts:7545-7556`; `paseo@485221b:packages/server/src/server/websocket-server.ts:2305`); T3 declara un esquema de carga por RPC (`t3code@eac52f0:packages/contracts/src/rpc.ts:1575-1580`). |

**Credenciales en los precedentes.**

- **Paseo.** `hello.auth` es o bien una contraseña o bien un token `localCredential` (`paseo@485221b:packages/protocol/src/messages.ts:7492-7497`). La credencial local son 32 bytes aleatorios escritos en un archivo con modo `0o600` (`paseo@485221b:packages/server/src/server/local-credential.ts:12-17`). Sin contraseña configurada, todo `hello` se admite como propietario (`paseo@485221b:packages/server/src/server/session-admission-auth.ts:18-20`). Los dispositivos remotos se emparejan mediante una oferta de conexión que contiene el id del servidor, la clave pública del daemon y un endpoint de relay, codificada en un fragmento de URL (`paseo@485221b:packages/server/src/server/connection-offer.ts:30-50`).
- **T3 Code.** Cada upgrade de `/ws` se autentica: un parámetro de consulta `wsTicket`, o la propia credencial de la petición (cookie o bearer token); una petición sin ninguno de los dos falla (`t3code@eac52f0:apps/server/src/auth/EnvironmentAuth.ts:517`, `:638-656`, `:1075-1094`; `t3code@eac52f0:apps/server/src/ws.ts:3788-3801`). El servidor crea, lista y revoca los enlaces de emparejamiento (`t3code@eac52f0:apps/server/src/auth/EnvironmentAuth.ts:448-466`).

**`Origin` en los precedentes.** Paseo rechaza un upgrade con 403 "Origin not allowed" salvo que la cabecera `Origin` falte, esté en la lista de permitidos (o sea `*`) o sea del mismo origen, y además comprueba `Host` contra los nombres de host permitidos (`paseo@485221b:packages/server/src/server/websocket-server.ts:825-832`, `:880-912`). En el `ws.ts` de T3 no se encontró ninguna comprobación de `Origin` en `/ws` (`rg` de `headers.origin`). Su única lista de permitidos es una capa CORS de HTTP, y solo en desarrollo, cuando `devUrl` está establecido; los builds empaquetados usan el origen comodín por defecto (`t3code@eac52f0:apps/server/src/http.ts:238-239`, `:246-251`). `UNVERIFIED:` si el framework de T3 comprueba `Origin` en los upgrades de WebSocket.

`Inference:`

- **`Origin` protege frente a los navegadores, no frente a los procesos locales.** Paseo admite un `Origin` ausente, que es lo que envía un cliente que no es un navegador; así que la lista de permitidos impide que otras páginas web del navegador del usuario abran el socket, y solo una credencial detiene a otro proceso local. Paseo sin contraseña admite a todos los clientes locales.
- **Incluso loopback necesita una credencial.** Esto se aparta del valor por defecto de la propuesta 0004, que exige una credencial solo fuera de loopback ([0004, Propuesta](07-proposals/0004-host-service.md#propuesta)). Un servicio solo de loopback sin credencial es accesible para todos los procesos de todos los usuarios locales. Un archivo de token por usuario, como la credencial local de Paseo, es la respuesta más barata. Si exigirlo es [HP-07](#preguntas-abiertas); el modelo de autenticación más allá de la máquina local es [HP-02](#preguntas-abiertas).
- **El origen de la ventana de Electron.** `UNVERIFIED:` no se comprobó qué `Origin` envía un renderer de Electron cargado desde un archivo. T3 incluye orígenes de renderer con esquema propio (`t3code://app`) en su lista CORS de permitidos, pero solo en desarrollo, cuando `devUrl` está establecido; los builds empaquetados usan el origen comodín por defecto (`t3code@eac52f0:apps/server/src/http.ts:53`, `:238-239`, `:246-251`).

**La CSP del renderer bloquearía el socket.** La política es `default-src 'self'; script-src 'self' 'unsafe-eval'; style-src … ; font-src …`, sin `connect-src` (`gentle-shell-desktop@5ab4a00:src/renderer/index.html:7`). `Inference:` `connect-src` recurre por tanto a `default-src 'self'`, que no cubre un endpoint `ws://127.0.0.1:<port>`; el puente WebSocket necesita una entrada `connect-src` explícita ([11, El lado del renderer](11-host-service.md#el-lado-del-renderer)). Endurecer la CSP ya es [QW-05](09-roadmap.md#qw-05-endurecimiento-de-la-csp-la-navegación-y-el-ipc-audit-a14-parte).

**Contraejemplo: el servidor de open-pi-viewer.** La propuesta 0004 lo registra como un patrón que evitar ([0004, Alternativas consideradas y descartadas](07-proposals/0004-host-service.md#alternativas-consideradas-y-descartadas)): un plugin del servidor de desarrollo de Vite (`open-pi-viewer@908245a:vite.config.ts:9-12`) que escucha en `0.0.0.0` (`:71`), con `Access-Control-Allow-Origin: *` (`:18`) y sin comprobación de token, cookie ni origen en ese archivo, cuyos procesos hijo se ejecutan con `--approve` (`open-pi-viewer@908245a:server/bridge/rpc.ts:81`). `Inference:` allí falta cada una de las reglas de la tabla anterior, y sus procesos hijo se saltan las aprobaciones, así que cualquier página o host que llegue al puerto puede manejar un agente.

## Preguntas abiertas

Los hechos se citan; los juicios son `Inference:`. Nada de esto está decidido.

| ID | Pregunta | Hechos | Opciones e `Inference:` |
|---|---|---|---|
| **HP-01** | **Política de versionado del protocolo.** ¿Cómo evoluciona el protocolo sin romper los clientes más antiguos? | Paseo combina una única versión entera usada como mínimo, que solo rechaza `protocolVersion < 1` con el código 4003 (`paseo@485221b:packages/server/src/server/websocket-server.ts:489`, `:1568-1579`), con indicadores de capacidades por funcionalidad en `hello` (`paseo@485221b:packages/protocol/src/messages.ts:7499-7519`) y comentarios de compatibilidad fechados, por ejemplo "added in v0.3.x, remove optional after 2027-02-12" (`:1258`). T3 exige que la versión del protocolo coincida exactamente (`t3code@eac52f0:apps/server/src/ws.ts:602-606`). El esquema de actividad de gentle-shell se versiona por nombre (`gentle-agents.activity/v1`) sin una regla de evolución declarada ([04, Canales del host y de las extensiones](04-rpc-contract.md#canales-del-host-y-de-las-extensiones)). | (a) Coincidencia exacta. (b) Un rango admitido más cambios solo aditivos dentro de una versión mayor. (c) (b) más indicadores de capacidades. `Inference:` con clientes que se actualizan por separado (un build de una tienda de apps, una pestaña del navegador, una app de escritorio), (a) obliga a actualizar todo a la vez; (b) o (c) lo evitan. |
| **HP-02** | **Modelo de autenticación más allá de loopback.** ¿Emparejamiento, token o relay? | Paseo: un archivo de token local y una contraseña, más un emparejamiento mediante una oferta de conexión que nombra un relay ([Autenticación y origen](#autenticación-y-origen)). T3: tickets, cookies o bearer tokens, y enlaces de emparejamiento emitidos por el servidor (misma sección). Las topologías son el objeto de [Clientes y topologías](13-clients-and-topologies.md#topologías). | (a) Un token estático. (b) Emparejamiento de dispositivos con credenciales revocables por dispositivo. (c) Un relay. `Inference:` (a) es lo más simple, pero difícil de revocar por dispositivo; (b) se adapta a un teléfono; (c) añade un tercero en el que confiar y que operar. |
| **HP-03** | **Propiedad de un chat entre varios clientes.** ¿Qué ocurre cuando dos clientes actúan sobre un chat, por ejemplo cuando ambos responden a un diálogo? | pi acepta la primera respuesta y descarta en silencio las posteriores (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-mode.ts:774-779`). El escritorio quita la tarjeta de `pendingDialogs` y envía el nuevo estado cuando responde (`gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:193-198`). herdr-web-ui da a cada conexión un rol `interact` u `observe` (`herdr-web-ui@7c5fe4e:shared/protocol.ts:587-591`). | (a) Gana la primera respuesta; las posteriores reciben `dialog_not_pending`, y todos los suscriptores ven desaparecer la tarjeta. (b) Un cliente que controla cada chat; los demás observan. `Inference:` (a) no necesita ningún concepto nuevo y coincide con el comportamiento de pi; (b) evita sorpresas, pero necesita un traspaso. Enviar prompts desde dos clientes plantea la misma pregunta. |
| **HP-04** | **Límites de contrapresión.** ¿Cuánto puede almacenar en búfer el servicio por cliente antes de descartar o desconectar? | Paseo: 64 MiB por socket en el código (su documento de arquitectura dice 8 MiB), y después termina. T3: 1.000 elementos u 8 MiB por suscripción. herdr-web-ui: 256 KiB de crédito, 1 MiB de presupuesto estricto, bloqueo de 2 s ([Reconexión y repetición](#reconexión-y-repetición)). | `Inference:` con instantáneas, conservar solo la última instantánea por chat y cliente acota la memoria según el número de suscripciones; quedan por elegir un tope de tamaño para una sola instantánea y un tiempo límite de bloqueo. |
| **HP-05** | **¿Reutilizar una delimitación de registros existente?** JSON-RPC 2.0, la forma del propio RPC de pi o un sobre propio. | JSON-RPC 2.0 define peticiones, respuestas, notificaciones (peticiones sin `id`, que no reciben respuesta) y un objeto de error cuyo `code` "MUST be an integer", con `message` y un `data` opcional (https://www.jsonrpc.org/specification, consultado el 2026-10-05). El RPC de pi usa `type`, un `id` opcional y registros `response` con `success` y `error` ([04, Correlación y errores](04-rpc-contract.md#correlación-y-errores)). T3 usa el protocolo RPC de su framework ([Transporte y delimitación de registros](#transporte-y-delimitación-de-registros)). | `Inference:` JSON-RPC aporta bibliotecas y una forma conocida; los envíos pasan a ser notificaciones y `retryable` vive en `data`, pero no define la semántica del handshake ni de las suscripciones, así que esas siguen siendo propias. Reflejar la forma de pi mantiene un único estilo en los dos tramos. Un protocolo de framework ata a todos los clientes a ese framework. |
| **HP-06** | **¿Instantáneas completas o deltas?** | Hoy cada envío es un `ChatState` completo ([Reconexión y repetición](#reconexión-y-repetición)). | `Inference:` las instantáneas mantienen triviales las reconexiones y los clientes lentos; los deltas reducen el ancho de banda en chats largos sobre redes móviles, pero vuelven a traer cursores y repetición, como en Paseo y T3. Una opción intermedia: instantáneas por mensaje (solo viaja el mensaje que cambia). |
| **HP-07** | **¿Una credencial en loopback?** La propuesta 0004 exige un token o un emparejamiento solo fuera de loopback. | La [propuesta 0004](07-proposals/0004-host-service.md#propuesta) escucha en loopback por defecto: "Any other bind requires a token or device pairing". Paseo admite todo `hello` como propietario cuando no hay contraseña configurada (`paseo@485221b:packages/server/src/server/session-admission-auth.ts:18-20`); T3 autentica cada upgrade de `/ws` (`t3code@eac52f0:apps/server/src/auth/EnvironmentAuth.ts:1075-1094`). | (a) Mantener el valor por defecto de 0004: sin credencial en loopback. (b) Exigir un token por usuario incluso en loopback. `Inference:` (a) deja el socket abierto a todos los procesos y usuarios locales ([Autenticación y origen](#autenticación-y-origen)); (b) cuesta un archivo de token y una forma de entregarlo a cada cliente local. |

## Lo que no cubre esta página

- **La arquitectura** (mapa de componentes, ubicación, configuración, migración): [11-host-service.md](11-host-service.md).
- **El contrato servicio ↔ gentle-shell**: [04-rpc-contract.md](04-rpc-contract.md), sin cambios.
- **Clientes y topologías** (local, LAN, remoto, móvil): [13-clients-and-topologies.md](13-clients-and-topologies.md).

## Fuentes

**Repositorios fijados** (clones de solo lectura; `repo@sha:path:line`):

| Nombre en las citas | Repositorio | Commit |
|---|---|---|
| `gentle-shell-desktop` | `Gentleman-Programming/gentle-shell-desktop` | `5ab4a00` |
| `gentle-shell` | `Gentleman-Programming/gentle-shell` (`main`, versión del paquete 4.0.0) | `ac67159` |
| `pi` | `earendil-works/pi` (v1.0.0) | `a13d35a` |
| `paseo` | `getpaseo/paseo` | `485221b` |
| `t3code` | `pingdotgg/t3code` | `eac52f0` |
| `herdr-web-ui` | `devswha/herdr-web-ui` | `7c5fe4e` |
| `open-pi-viewer` | `gonzalez962/open-pi-viewer` | `908245a` |

**Web** (consultado el 2026-10-05):

- Documentación de `ipcMain` de Electron: https://www.electronjs.org/docs/latest/api/ipc-main
- Especificación de JSON-RPC 2.0: https://www.jsonrpc.org/specification

**Corpus:** [propuesta 0004](07-proposals/0004-host-service.md), [arquitectura del servicio host](11-host-service.md), [contrato RPC](04-rpc-contract.md), [arquitectura actual](03-architecture/current.md), [auditoría](03-architecture/audit.md), [hoja de ruta](09-roadmap.md).
