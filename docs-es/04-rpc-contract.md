> Traducción al español de `docs/04-rpc-contract.md` (árbol de trabajo tras la actualización del 2026-10-03). Documento de lectura; la versión de referencia es la inglesa.

# Contrato RPC

> Estado: borrador (draft).

`gentle-shell --mode rpc` se ejecuta como proceso hijo y habla JSON, un mensaje por línea, sobre stdin/stdout. Es la única interfaz formal entre el escritorio y gentle-shell. No es tRPC. El escritorio también importa pi en el mismo proceso para listar sesiones (ver `03-architecture/current.md`), pero ese camino queda fuera de este contrato.

## De un vistazo

| Pregunta | Respuesta | Evidencia |
|---|---|---|
| ¿Quién define el protocolo? | El núcleo de pi (`@earendil-works/pi-coding-agent`), no gentle-shell. gentle-shell no añade ningún comando ni tipo de evento; su tráfico viaja sobre los canales de extensión de pi (peticiones de UI de extensiones, comandos de extensión, mensajes personalizados, entradas de sesión), y parte de él está condicionado por variables de entorno ([Canales del host y de las extensiones](#canales-del-host-y-de-las-extensiones)). | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:20` |
| ¿Qué versión de pi responde al RPC del escritorio? | pi **0.99.1 o posterior**: el lanzador (launcher) de gentle-shell se niega a arrancar un pi anterior. gentle-shell 4.0.0 se desarrolla contra pi 1.0.0, cuya capa RPC es idéntica byte a byte a la de 0.99.1. El pi 0.85.1 bloqueado del propio escritorio solo se usa para la lista de sesiones en el mismo proceso. | `gentle-shell@ac67159:lib/gentle-shell-launcher.ts:392`, `gentle-shell@ac67159:package.json:78`, `:95-97`, `gentle-shell-desktop@5ab4a00:pnpm-lock.yaml:323` |
| ¿Cuánto del protocolo usa el escritorio? | 3 de 33 comandos (`prompt`, `abort`, `get_messages`) más las respuestas a diálogos; 13 tipos de registro de stdout más las peticiones de UI de extensiones. | [Comandos](#comandos-escritorio--runtime), [Eventos](#eventos-runtime--escritorio) |
| ¿Hay un handshake de versión? | No. Solo la carga de actividad lleva una etiqueta de esquema (`gentle-agents.activity/v1`). | [Versionado](#versionado-y-compatibilidad) |
| Mayores carencias (gaps) | Stop de helpers, estado estructurado de ODD, proveedores (providers)/autenticación, gestión de extensiones, estado de perfil (profile)/RDD. | [Carencias](#carencias-que-necesita-el-escritorio) |

**Cómo leer las citas.** Cada afirmación cita `repo@shortsha:path:line`. SHAs fijados (actualizados el 2026-10-03): `gentle-shell-desktop@5ab4a00` (main), `gentle-shell@ac67159` (`main` de gentle-shell, versión de paquete 4.0.0, 19 commits después del commit de la release 4.0.0 `1f35ab1`; los hechos de esos commits se marcan como posteriores a la release), `pi@a13d35a` (pi 1.0.0), `pi@d981de1` (pi 0.85.1, la copia del escritorio en el mismo proceso). `pi@d86654a` (pi 0.99.1) y `gentle-shell@1162ce9` (3.7.0) solo aparecen en comparaciones explícitas de versiones. Las líneas etiquetadas como `Inference:` son razonamiento, no comportamiento verificado. `UNVERIFIED:` marca afirmaciones que se comprobaron pero no se confirmaron. Los IDs de otras páginas van cualificados (`audit A5`, `inventory Y4`); G1–G10 sin cualificar son las carencias de esta página. `pr30:` cita la [PR #30](https://github.com/Gentleman-Programming/gentle-shell-desktop/pull/30) en su último commit `cd6d72f` (base `5ab4a00`).

## Transporte y delimitación de registros

### Cadena de procesos

```text
Electron main (desktop)
  └─ spawn: <gentle-shell launcher> [--home <dir>|--link|--isolated] --mode rpc [--session <path>]
       └─ spawn (stdio: inherit): pi --mode rpc ...   ← the RPC peer
```

| Paso | Qué ocurre | Evidencia |
|---|---|---|
| 1. Localizar el lanzador | Primero `GENTLE_SHELL_BIN` (una entrada `.mjs`/`.js`/`.cjs` se ejecuta bajo `process.execPath` con `ELECTRON_RUN_AS_NODE=1`); si no, `gentle-shell` en `PATH` (candidatos `.cmd`/`.exe` en win32). | `gentle-shell-desktop@5ab4a00:src/main/adapters/launcherLocator.ts:19`, `:41`, `:48` |
| 2. Construir argv | Argumentos del lanzador, luego los indicadores de home, luego `--mode rpc` y luego `--session <path>` al reabrir un chat. Los indicadores de home son `--home <dir>` cuando `GENTLE_SHELL_HOME` está definido y, si no, `--link` o `--isolated`. | `gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:127-133`, `gentle-shell-desktop@5ab4a00:src/main/domain/home/home.ts:34-36` |
| 3. Construir el entorno | Entorno heredado, luego el entorno del lanzador y luego `GENTLE_SHELL_INTERACTIVE_HOST=1`, aplicado al final para que nada pueda sobrescribirlo. | `gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:67`, `:134` |
| 4. Lanzar | `child_process.spawn` con `stdio: ["pipe","pipe","pipe"]` y sin la opción `shell`. | `gentle-shell-desktop@5ab4a00:src/main/adapters/nodeProcessSpawner.ts:10` |
| 5. El lanzador resuelve pi | `GENTLE_SHELL_PI`, luego una CLI de pi incluida en el paquete y luego `pi` en `PATH`. | `gentle-shell@ac67159:lib/gentle-shell-launcher.ts:368-379` |
| 6. Control de versión | El lanzador ejecuta `pi --version` y termina con un error si pi es anterior a `MIN_PI_VERSION = "0.99.1"`. | `gentle-shell@ac67159:bin/gentle-shell.mjs:1206-1215`, `gentle-shell@ac67159:lib/gentle-shell-launcher.ts:392`, `:416` |
| 7. Lanzar pi | El lanzador lanza pi con `stdio: "inherit"`, de modo que las tuberías del escritorio llegan directamente a pi. Reenvía `SIGINT`, `SIGTERM` y `SIGHUP` a pi. | `gentle-shell@ac67159:bin/gentle-shell.mjs:1396`, `:1403-1408` |

### Variables de entorno del contrato

| Variable | La define | Efecto | Evidencia |
|---|---|---|---|
| `GENTLE_SHELL_INTERACTIVE_HOST=1` | El escritorio, en cada lanzamiento | Bajo `--mode rpc`, habilita los diálogos RPC para `ask_user_question`/`ask_user_choice` y el envío de la actividad `gentle-agents`. Solo cuenta el valor exacto `"1"`. Se elimina en los hijos de los subagentes. | `gentle-shell@ac67159:lib/rpc-host.ts:8`, `:15-17`, `gentle-shell@ac67159:lib/agents-runner.ts:471`, `gentle-shell@ac67159:docs/readme-reference.md:376` |
| `GENTLE_SHELL_BIN` | Usuario / script de desarrollo | Sobrescritura de la ruta del lanzador para el escritorio. | `gentle-shell-desktop@5ab4a00:src/main/adapters/launcherLocator.ts:19` |
| `ELECTRON_RUN_AS_NODE=1` | El escritorio, solo para un `GENTLE_SHELL_BIN` con entrada JS | Ejecuta la entrada como Node simple bajo el binario de Electron. | `gentle-shell-desktop@5ab4a00:src/main/adapters/launcherLocator.ts:38-41` |
| `GENTLE_SHELL_HOME` | Usuario | Cuando está definida, el escritorio pasa `--home <dir>` en lugar de `--link`/`--isolated`, y su lista de sesiones en el mismo proceso lee el mismo directorio. | `gentle-shell-desktop@5ab4a00:src/main/domain/home/home.ts:28-31`, `:34-35`, `:61-62` |
| `GENTLE_SHELL_PI` | Usuario | Sobrescritura del ejecutable de pi dentro del lanzador. | `gentle-shell@ac67159:lib/gentle-shell-launcher.ts:369-370` |

### Delimitación de registros

| Regla | Evidencia (documentación de pi) | Conformidad del escritorio |
|---|---|---|
| Un objeto JSON por registro, terminado en LF. | `pi@a13d35a:packages/coding-agent/docs/rpc.md:52`, `pi@d981de1:packages/coding-agent/docs/rpc.md:30` | `encodeCommand` añade `\n` (`gentle-shell-desktop@5ab4a00:src/main/domain/rpc/codec.ts:12-14`) |
| Dividir solo por LF; eliminar un `\r` final opcional; no usar nunca `readline` de Node (divide en U+2028/U+2029). | `pi@a13d35a:packages/coding-agent/docs/rpc.md:52-54`, `pi@d981de1:packages/coding-agent/docs/rpc.md:32-37` | `LineSplitter` divide por `\n` y elimina `\r` (`gentle-shell-desktop@5ab4a00:src/main/domain/rpc/codec.ts:22-49`) |
| Stdout se reserva para los registros del protocolo; los diagnósticos van a stderr. | `pi@a13d35a:packages/coding-agent/docs/rpc.md:56`; pi toma el control de stdout al arrancar (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-mode.ts:55`) | Stderr se registra, nunca se interpreta (`gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:292-295`) |
| Leer stdout de forma continua; pi respeta la contrapresión (backpressure). | `pi@a13d35a:packages/coding-agent/docs/rpc.md:56` | Listener `data`, nunca pausado (`gentle-shell-desktop@5ab4a00:src/main/adapters/nodeProcessSpawner.ts:78-82`) |

El código de delimitación (`jsonl.ts`) es idéntico byte a byte en pi 0.85.1, 0.99.1 y 1.0.0 (comprobado con `git diff --quiet d981de1 a13d35a`).

### Correlación y errores

- Todo comando acepta un `id` de tipo cadena opcional; la `response` correspondiente lo repite (`pi@a13d35a:packages/coding-agent/docs/rpc.md:37-44`). Se correlaciona por `id`, no por orden (`:44`).
- Un comando fallido devuelve `{type:"response", command, success:false, error}` (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:245`).
- Un JSON mal formado devuelve una respuesta con `command: "parse"` y sin `id` (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-mode.ts:752-763`).
- Un `type` desconocido devuelve `Unknown command: <type>` (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-mode.ts:715`).
- Un `extension_ui_response` no produce respuesta; uno con un `id` desconocido se descarta en silencio (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-mode.ts:767-781`).
- El escritorio solo define `id` en `get_messages` (`gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:157-160`).

### Arranque y parada

| Fase | Comportamiento de pi | Comportamiento del escritorio |
|---|---|---|
| Arranque | No existe un registro dedicado de "ready". `Inference:` las únicas llamadas a `output(...)` en `runRpcMode` son respuestas a comandos, eventos de sesión, peticiones de UI de extensiones y `extension_error` (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-mode.ts:59-61`, `:129`, `:349`, `:356`). Las extensiones pueden emitir peticiones de UI en `session_start` (gentle-agents lo hace, `gentle-shell@ac67159:extensions/gentle-agents.ts:1663`, `:1697-1711`). | Escribe comandos inmediatamente después del lanzamiento; envía `get_messages` de inmediato al reabrir (`gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:147`). |
| Parada ordenada | Cerrar stdin desencadena `shutdown()`, que libera el runtime y termina (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-mode.ts:802-805`, `:726-743`; documentado en `pi@a13d35a:packages/coding-agent/docs/rpc.md:93`). | `endStdin()`, espera hasta 3 s y luego `kill()` (`gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:214-235`). |
| Señales | `SIGTERM` termina con 143; `SIGHUP` (no en win32) termina con 129 (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-mode.ts:366-380`). | `kill()` sin argumento (`SIGTERM` por defecto en Node), reenviado por el lanzador. |
| Parada solicitada por una extensión | Se completa tras el comando en curso o tras `agent_settled` (`pi@a13d35a:packages/coding-agent/docs/rpc.md:95`). | Cualquier terminación no solicitada por `stop()` restablece `working` y descarta los diálogos pendientes (`gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:309-324`). |

La documentación de pi 0.85.1 no describe la parada; el camino de código es el mismo (`pi@d981de1:packages/coding-agent/src/modes/rpc/rpc-mode.ts:728`, `:807`).

## Comandos (escritorio → runtime)

La unión `RpcCommand` es idéntica en pi 0.85.1 y 0.99.1, en los mismos números de línea (el `diff` de `rpc-types.ts` solo difiere en la línea 10 y en las respuestas de prompting de las líneas 117-126). Entre 0.99.1 y 1.0.0, las fuentes de RPC (`rpc-types.ts`, `rpc-mode.ts`, `rpc-client.ts`, `jsonl.ts`) y la documentación de RPC son idénticas byte a byte (`git diff --stat d86654a a13d35a` está vacío para ellas). Las filas citan 1.0.0; la misma línea es válida en `pi@d86654a` y `pi@d981de1`.

**Columna Escritorio:** **sent** = se escribe hoy en stdin; **typed** = está en el tipo `RpcCommand` del escritorio pero nunca se envía; **–** = no se usa.

| Comando | Campos de la carga (además del `id` opcional) | `data` de la respuesta | Propósito | Escritorio | Fuente |
|---|---|---|---|---|---|
| `prompt` | `message`, `images?`, `streamingBehavior?: "steer"\|"followUp"` | 0.85.1: ninguno. 0.99.1: `{disposition}` | Enviar un prompt del usuario; los comandos de extensión `/command` se ejecutan de inmediato, incluso durante el streaming. | **sent** (`PiSession.ts:184`) | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:22` |
| `steer` | `message`, `images?` | 0.99.1: `{disposition}` | Encolar un mensaje para entregarlo antes de la siguiente llamada al LLM. | – | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:23` |
| `follow_up` | `message`, `images?` | 0.99.1: `{disposition}` | Encolar un mensaje para después de que termine la ejecución. | – | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:24` |
| `abort` | – | – | Abortar la ejecución en curso. | **sent** (`PiSession.ts:189`) | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:25` |
| `clear_queue` | – | `{steering, followUp}` | Descartar los mensajes de redirección (steer)/seguimiento (follow-up) encolados. | – | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:26` |
| `new_session` | `parentSession?` | `{cancelled}` | Iniciar una sesión nueva en el mismo proceso. | typed (`types.ts:30`) | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:27` |
| `get_state` | – | `RpcSessionState` | Modelo, nivel de razonamiento, indicadores de streaming/compactación, modos de cola, archivo/id/nombre de la sesión, recuentos. | typed (`types.ts:32`) | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:30`, `:96-109` |
| `set_model` | `provider`, `modelId` | `Model` | Cambiar de modelo. | – | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:33` |
| `cycle_model` | – | `{model, thinkingLevel, isScoped}\|null` | Rotar entre los modelos acotados. | – | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:34` |
| `get_available_models` | – | `{models}` | Listar los modelos utilizables con la autenticación actual. | – | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:35` |
| `set_thinking_level` | `level` | – | Establecer el nivel de razonamiento ("effort"). | – | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:38` |
| `cycle_thinking_level` | – | `{level}\|null` | Rotar el nivel de razonamiento. | – | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:39` |
| `get_available_thinking_levels` | – | `{levels}` | Listar los niveles de razonamiento. | – | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:40` |
| `set_steering_mode` | `mode: "all"\|"one-at-a-time"` | – | Modo de entrega de la cola de redirección. | – | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:43` |
| `set_follow_up_mode` | `mode: "all"\|"one-at-a-time"` | – | Modo de entrega de la cola de seguimiento. | – | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:44` |
| `compact` | `customInstructions?` | `CompactionResult` | Compactación manual. | – | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:47` |
| `set_auto_compaction` | `enabled` | – | Activar o desactivar la compactación automática. | – | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:48` |
| `set_auto_retry` | `enabled` | – | Activar o desactivar el reintento automático. | – | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:51` |
| `abort_retry` | – | – | Cancelar un reintento automático pendiente. | – | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:52` |
| `bash` | `command`, `excludeFromContext?` | `BashResult` | Ejecutar directamente un comando de shell; la salida llega en streaming como `bash_execution_update`. | – | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:55` |
| `abort_bash` | – | – | Abortar el comando `bash` en ejecución. | – | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:56` |
| `get_session_stats` | – | `SessionStats` (tokens, `cost`, `contextUsage?`) | Uso y coste de la sesión. | – | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:59`; campos en `pi@a13d35a:packages/coding-agent/src/core/agent-session.ts:326-343` |
| `export_html` | `outputPath?` | `{path}` | Exportar la sesión como HTML. | – | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:60` |
| `switch_session` | `sessionPath` | `{cancelled}` | Cambiar a otro archivo de sesión en el mismo proceso. | typed (`types.ts:31`) | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:61` |
| `fork` | `entryId` | `{text, cancelled}` | Bifurcar desde una entrada. | – | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:62` |
| `clone` | – | `{cancelled}` | Clonar la sesión. | – | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:63` |
| `get_fork_messages` | – | `{messages: [{entryId, text}]}` | Puntos candidatos de bifurcación. | – | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:64` |
| `get_entries` | `since?` | `{entries, leafId}` | Entradas de sesión en bruto. | – | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:65` |
| `get_tree` | – | `{tree, leafId}` | Árbol de la sesión. | – | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:66` |
| `get_last_assistant_text` | – | `{text\|null}` | Último texto del asistente. | – | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:67` |
| `set_session_name` | `name` | – | Renombrar la sesión. | – | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:68` |
| `get_messages` | – | `{messages}` | Historial completo de mensajes. | **sent** con `id` (`PiSession.ts:159`) | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:71` |
| `get_commands` | – | `{commands: RpcSlashCommand[]}` (`name`, `description?`, `source`, `sourceInfo`) | Descubrir los comandos de extensión, las plantillas de prompt y las skills invocables mediante `prompt`. | – | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:74`, `:81-90` |
| `extension_ui_response` | `id` + uno de `value` / `confirmed` / `cancelled: true` | ninguno | Responder a una petición de diálogo. Ver [Peticiones de UI de extensiones](#peticiones-de-ui-de-extensiones). | **sent** (`PiSession.ts:201-205`) | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:294-297` |

Las referencias a archivos del escritorio en esta tabla están bajo `gentle-shell-desktop@5ab4a00:src/main/domain/session/` (`PiSession.ts`) y `gentle-shell-desktop@5ab4a00:src/main/domain/rpc/` (`types.ts`).

### Diferencias entre pi 0.85.1 y 0.99.1 (comandos)

| Área | pi 0.85.1 | pi 0.99.1 | Evidencia |
|---|---|---|---|
| Respuesta de éxito de `prompt` | `{type:"response", command:"prompt", success:true}`, sin `data`. | Añade `data.disposition`: `"started"`, `"queued"` o `"handled"`. | `pi@d981de1:packages/coding-agent/src/modes/rpc/rpc-types.ts:118`, `pi@d981de1:packages/coding-agent/src/modes/rpc/rpc-mode.ts:403-407`; `pi@d86654a:packages/coding-agent/src/modes/rpc/rpc-types.ts:118`, `pi@d86654a:packages/coding-agent/src/modes/rpc/rpc-mode.ts:403-406`, `pi@d86654a:packages/coding-agent/docs/rpc-commands.md:40` |
| Respuesta de fallo de `prompt` | Igual en ambas: la respuesta de éxito se emite solo después de que la comprobación previa tenga éxito; un prompt que falla lanza una excepción, y el `.catch` emite una respuesta de error si todavía no se envió una de éxito. | Igual. pi 0.99.1 llama a `preflightResult` solo con una disposición de éxito. | `pi@d981de1:packages/coding-agent/src/modes/rpc/rpc-mode.ts:395-412`; `pi@d86654a:packages/coding-agent/src/modes/rpc/rpc-mode.ts:395-411`, `pi@d86654a:packages/coding-agent/src/core/agent-session.ts:1896`, `:1915`, `:1939`, `:2024` |
| Respuesta de `steer` / `follow_up` | Sin `data`. | `data.disposition`: `"handled"` o `"queued"`. | `pi@d86654a:packages/coding-agent/src/modes/rpc/rpc-types.ts:119-126`, `pi@d86654a:packages/coding-agent/src/core/agent-session.ts:289-290` |
| Semántica de "handled" | No documentada. | Si es `"handled"`, no se inició ninguna ejecución, así que un cliente no debe esperar a `agent_settled`. | `pi@d86654a:packages/coding-agent/docs/rpc.md:67` |
| Organización de la documentación | Un archivo, `docs/rpc.md` (1.618 líneas). | Dividida en `rpc.md`, `rpc-commands.md`, `rpc-extension-ui.md`, con los eventos en `json.md`. | `pi@d86654a:packages/coding-agent/docs/rpc.md:134-142` |
| `RpcClient` (TypeScript) | `prompt()` devuelve `void`. | `prompt()` recibe `streamingBehavior?` y devuelve la disposición. | `pi@d86654a:packages/coding-agent/src/modes/rpc/rpc-client.ts:198-204` |

No se añadió ni se eliminó ningún comando entre 0.85.1 y 0.99.1, y nada de la capa RPC cambió entre 0.99.1 y 1.0.0 (ver más arriba), así que la columna de 0.99.1 también describe 1.0.0.

## Eventos (runtime → escritorio)

Los eventos son todos los `AgentSessionEvent`, serializados mediante `toJsonEvent` y escritos en stdout (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-mode.ts:355-356`). `toJsonEvent` es idéntico en pi 0.85.1, 0.99.1 y 1.0.0 (`json-event.ts`, comprobado con `git diff --quiet d981de1 a13d35a`); los tipos de eventos de `packages/agent/src/types.ts` y la unión de eventos de `agent-session.ts` no cambiaron en 1.0.0. Los eventos no llevan `id`, excepto `bash_execution_update` (`pi@a13d35a:packages/coding-agent/docs/rpc.md:46`).

**Columna Escritorio:** lo que decodifica `codec.ts` y lo que hace `chatReducer.ts` con ello. Todo lo que no se decodifica se convierte en `{kind:"unknown"}` y se descarta (`gentle-shell-desktop@5ab4a00:src/main/domain/rpc/codec.ts:130-131`, `gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:248`).

| Evento | Campos | Propósito | Escritorio | Fuente (1.0.0) |
|---|---|---|---|---|
| `agent_start` | – | Se inició una ejecución de bajo nivel. | Establece `working: true` (`chatReducer.ts:54`) | `pi@a13d35a:packages/agent/src/types.ts:516` |
| `agent_end` | `messages`, `willRetry` | Terminó una ejecución de bajo nivel; pueden seguir reintentos o trabajo encolado. | Establece `working: false` (`chatReducer.ts:56`) | `pi@a13d35a:packages/coding-agent/src/core/agent-session.ts:192-196` |
| `agent_settled` | – | Ya no se ejecutará nada más automáticamente. | Establece `working: false` (`chatReducer.ts:57`) | `pi@a13d35a:packages/coding-agent/src/core/agent-session.ts:197` |
| `turn_start` | – | Se inició un turno del asistente. | Se decodifica y se ignora (`codec.ts:90`) | `pi@a13d35a:packages/agent/src/types.ts:519` |
| `turn_end` | `message`, `toolResults` | Terminó un turno del asistente. | Se decodifica sin campos y se ignora (`codec.ts:91`) | `pi@a13d35a:packages/agent/src/types.ts:520` |
| `message_start` | `message` | Se inició un mensaje. | Abre una burbuja del asistente (`chatReducer.ts:59`) | `pi@a13d35a:packages/agent/src/types.ts:522` |
| `message_update` | `usage`, `assistantMessageEvent` (sin `message` acumulado) | Delta de streaming; ver la tabla de deltas más abajo. | Añade `text_delta`; los deltas de razonamiento/llamadas a herramientas incrementan un contador de actividad (`chatReducer.ts:61`, `:93-104`) | `pi@a13d35a:packages/coding-agent/src/modes/json-event.ts:11-15` |
| `message_end` | `message` | Mensaje completado; es la versión de referencia. | Resincroniza el texto final (`chatReducer.ts:63`) | `pi@a13d35a:packages/agent/src/types.ts:525` |
| `tool_execution_start` | `toolCallId`, `toolName`, `args`, `parentToolCallId?` (desde 0.99.1) | Se inició la ejecución de una herramienta. | Solo incrementa el contador de actividad (`chatReducer.ts:65`) | `pi@a13d35a:packages/agent/src/types.ts:527`, `pi@a13d35a:packages/coding-agent/src/core/agent-session.ts:183-187` |
| `tool_execution_update` | `toolCallId`, `toolName`, `args`, `partialResult`, `parentToolCallId?` (desde 0.99.1) | Resultado parcial de una herramienta. | Solo incrementa el contador de actividad (`chatReducer.ts:66`) | `pi@a13d35a:packages/agent/src/types.ts:528` |
| `tool_execution_end` | `toolCallId`, `toolName`, `result`, `isError`, `parentToolCallId?` (desde 0.99.1) | La herramienta terminó. | Solo incrementa el contador de actividad (`chatReducer.ts:67`) | `pi@a13d35a:packages/agent/src/types.ts:529` |
| `queue_update` | `steering`, `followUp` | Cambió el contenido de la cola (instantánea completa). | – | `pi@a13d35a:packages/coding-agent/src/core/agent-session.ts:198-202` |
| `entry_appended` | `entry` | Una extensión añadió una entrada de sesión personalizada. | – | `pi@a13d35a:packages/coding-agent/src/core/agent-session.ts:204` |
| `session_info_changed` | `name` | Cambió el nombre visible de la sesión. | – | `pi@a13d35a:packages/coding-agent/src/core/agent-session.ts:205` |
| `thinking_level_changed` | `level` | Cambió el nivel de razonamiento. | – | `pi@a13d35a:packages/coding-agent/src/core/agent-session.ts:206` |
| `compaction_start` | `reason: "manual"\|"threshold"\|"overflow"` | Comenzó la compactación. | – | `pi@a13d35a:packages/coding-agent/src/core/agent-session.ts:203` |
| `compaction_end` | `reason`, `result`, `aborted`, `willRetry`, `errorMessage?` | Terminó la compactación. | – | `pi@a13d35a:packages/coding-agent/src/core/agent-session.ts:207-214` |
| `auto_retry_start` | `attempt`, `maxAttempts`, `delayMs`, `errorMessage` | Reintento tras un error transitorio. | – | `pi@a13d35a:packages/coding-agent/src/core/agent-session.ts:215` |
| `auto_retry_end` | `success`, `attempt`, `finalError?` | Terminó el bucle de reintentos. | – | `pi@a13d35a:packages/coding-agent/src/core/agent-session.ts:216` |
| `summarization_retry_scheduled` | `attempt`, `maxAttempts`, `delayMs`, `errorMessage` | Reintento de resumen programado. | – | `pi@a13d35a:packages/coding-agent/src/core/agent-session.ts:217-223` |
| `summarization_retry_attempt_start` | `source: "branchSummary"`, o `source: "compaction"` + `reason` | Se inició un reintento de resumen. | – | `pi@a13d35a:packages/coding-agent/src/core/agent-session.ts:224-229` |
| `summarization_retry_finished` | – | Terminó el bucle de reintentos de resumen. | – | `pi@a13d35a:packages/coding-agent/src/core/agent-session.ts:230` |
| `bash_execution_update` | `id?`, `delta` | Fragmento de salida de un comando `bash` directo. | – | `pi@a13d35a:packages/coding-agent/src/core/agent-session.ts:231` |
| `extension_error` | `extensionPath`, `event`, `error` | Una extensión lanzó una excepción. Lo emite `rpc-mode.ts`, no la sesión. | Establece `lastError` (`chatReducer.ts:71`) | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-mode.ts:348-350` |
| `response` | Ver [Correlación y errores](#correlación-y-errores) | Acuse de recibo de un comando. | Se decodifica; solo se actúa sobre la respuesta de `get_messages` (`PiSession.ts:257`, `:272-284`) | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:116-245` |
| `extension_ui_request` | Ver la sección siguiente | Subprotocolo de UI de extensiones. | Ver la sección siguiente | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:252-287` |

Referencias del escritorio en esta tabla: `gentle-shell-desktop@5ab4a00:src/main/domain/rpc/chatReducer.ts`, `gentle-shell-desktop@5ab4a00:src/main/domain/rpc/codec.ts`, `gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts`.

### Tipos de delta de `message_update`

`assistantMessageEvent.type` es uno de `text_start`, `text_delta`, `text_end`, `thinking_start`, `thinking_delta`, `thinking_end`, `toolcall_start` (añade `id`, `toolName` en el canal), `toolcall_delta`, `toolcall_end` (`pi@d981de1:packages/coding-agent/docs/rpc.md:965-973`). La documentación de 0.99.1 y 1.0.0 también enumera `start`, `done` y `error` (`pi@a13d35a:packages/coding-agent/docs/json.md:78-89`). El escritorio solo modela los nueve tipos `text_*`/`thinking_*`/`toolcall_*` (`gentle-shell-desktop@5ab4a00:src/main/domain/rpc/types.ts:77-91`).

### Diferencias entre pi 0.85.1 y 0.99.1 (eventos)

| Área | pi 0.85.1 | pi 0.99.1 | Evidencia |
|---|---|---|---|
| `parentToolCallId` en `tool_execution_*` | Ausente. | Opcional; se establece en las llamadas a herramientas anidadas (`ctx.executeTool`, codemode de MCP). El `toolCallId` anidado es `<parent id>/<n>`. | `pi@d981de1:packages/coding-agent/src/core/agent-session.ts:145`; `pi@d86654a:packages/coding-agent/src/core/agent-session.ts:183-191`, `pi@d86654a:packages/coding-agent/docs/extensions.md:148` |
| `entry_appended`, `session_info_changed`, `thinking_level_changed` | Se emiten (`pi@d981de1:packages/coding-agent/src/core/agent-session.ts:158-160`, `:1809`, `:2597`, `:3093`) pero **no figuran** en la tabla de eventos RPC (`pi@d981de1:packages/coding-agent/docs/rpc.md:859-883`). | Se emiten y están documentados. | `pi@d86654a:packages/coding-agent/docs/json.md:122-124` |
| Rol de mensaje `system` | Ausente: `Message` es `UserMessage \| AssistantMessage \| ToolResultMessage`; los eventos de mensaje cubren los mensajes de usuario, de asistente y de toolResult. | Añade `SystemMessage` (`role: "system"`) a `Message`; los eventos del ciclo de vida de los mensajes se documentan como emitidos también para los mensajes de sistema. `Inference:` un host que distinga por `message.role` puede ver un cuarto rol. | `pi@d981de1:packages/ai/src/types.ts:470`, `pi@d981de1:packages/agent/src/types.ts:438`; `pi@d86654a:packages/ai/src/types.ts:523`, `:610`, `pi@d86654a:packages/agent/src/types.ts:521` |
| Puntos de emisión de `entry_appended` | Se encontró 1 punto. | 5 puntos, incluido el precalentador de caché. | `pi@d86654a:packages/coding-agent/src/core/agent-session.ts:461`, `:793`, `:986`, `:1208`, `:3325` |

## Peticiones de UI de extensiones

Las extensiones llaman a `ctx.ui.*`. En modo RPC, las llamadas admitidas se convierten en registros `extension_ui_request` en stdout; los diálogos bloquean hasta que llega a stdin un `extension_ui_response` con el mismo `id` (`pi@a13d35a:packages/coding-agent/docs/rpc-extension-ui.md:5-8`). Si un diálogo tiene `timeout`, pi lo resuelve por sí mismo con un valor por defecto (`:10`; `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-mode.ts:115-120`). El conjunto de métodos y los campos son idénticos en 0.85.1, 0.99.1 y 1.0.0 (las líneas de 0.85.1 tienen números de línea 6 menores: `pi@d981de1:packages/coding-agent/src/modes/rpc/rpc-types.ts:246-291`).

| Método | Tipo | Campos | Respuesta esperada | Escritorio (proceso principal) | Fuente (1.0.0) |
|---|---|---|---|---|---|
| `select` | Diálogo | `title`, `options: string[]`, `timeout?` | `{value}` o `{cancelled:true}` | Se añade a `pendingDialogs` (`chatReducer.ts:167`) | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:253` |
| `confirm` | Diálogo | `title`, `message`, `timeout?` | `{confirmed}` o `{cancelled:true}` | Se añade a `pendingDialogs` (`chatReducer.ts:169`) | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:254` |
| `input` | Diálogo | `title`, `placeholder?`, `timeout?` | `{value}` o `{cancelled:true}` | Se añade a `pendingDialogs` (`chatReducer.ts:171`) | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:255-262` |
| `editor` | Diálogo | `title`, `prefill?` (sin `timeout`) | `{value}` o `{cancelled:true}` | Se añade a `pendingDialogs` (`chatReducer.ts:178`) | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:263` |
| `notify` | Dispara y olvida | `message`, `notifyType?: "info"\|"warning"\|"error"` | ninguna | Se ignora (`chatReducer.ts:182-184`) | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:264-270` |
| `setStatus` | Dispara y olvida | `statusKey`, `statusText` (`undefined` lo borra) | ninguna | Se ignora | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:271-277` |
| `setWidget` | Dispara y olvida | `widgetKey`, `widgetLines: string[]\|undefined`, `widgetPlacement?: "aboveEditor"\|"belowEditor"` | ninguna | Solo se interpreta `widgetKey: "gentle-agents"`; las demás claves se ignoran (`chatReducer.ts:32`, `:180`, `:196-206`) | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:278-285` |
| `setTitle` | Dispara y olvida | `title` | ninguna | Se ignora | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:286` |
| `set_editor_text` | Dispara y olvida | `text` | ninguna | Se ignora | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:287` |

Referencias del escritorio: `gentle-shell-desktop@5ab4a00:src/main/domain/rpc/chatReducer.ts`. Si el renderer puede responder a todos los tipos de diálogo queda fuera del alcance de esta sección; ver `03-architecture/current.md`.

### Qué descarta el modo RPC

Estas llamadas de `ctx.ui` no hacen nada o se degradan bajo `--mode rpc` (`pi@a13d35a:packages/coding-agent/docs/rpc-extension-ui.md:14-23`; 0.85.1 enumera un conjunto más corto en `pi@d981de1:packages/coding-agent/docs/rpc.md:1194-1203`):

- `custom()` devuelve `undefined`: ningún componente de TUI personalizado llega al host (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-mode.ts:228-231`).
- `setWidget` con una factoría de componentes en lugar de `string[]` se ignora en silencio (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-mode.ts:194-207`).
- `setFooter`, `setHeader`, `setEditorComponent`, `setWorkingMessage`, `setWorkingIndicator`, `setToolsExpanded`, `setWorkingVisible`, `setHiddenThinkingLabel` y `addAutocompleteProvider` no hacen nada en ambas versiones. Los tres últimos tampoco hacen nada en el código de 0.85.1 (`pi@d981de1:packages/coding-agent/src/modes/rpc/rpc-mode.ts:183`, `:191`, `:273`); solo la documentación de 0.85.1 los omite.
- `getEditorText()` devuelve `""`. `get theme()` devuelve el tema real, pero `getAllThemes()` devuelve `[]` y `getTheme()` devuelve `undefined`. `setTheme()` devuelve `{success:false}` (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-mode.ts:286-301`).

### Añadidos de gentle-shell sobre RPC

gentle-shell no añade ningún comando ni tipo de evento RPC propio. Los añadidos de esta tabla viajan sobre `extension_ui_request` o sobre comandos de extensión invocados con `prompt`, y la mayor parte de ellos requiere `GENTLE_SHELL_INTERACTIVE_HOST=1`. gentle-shell también llega a un host RPC mediante mensajes personalizados y entradas de sesión (por ejemplo `gentle-agents.result` y `gentle-pi.session-change/v1`); estos, y los demás canales de extensión que pi transporta sobre RPC, se enumeran en [Canales del host y de las extensiones](#canales-del-host-y-de-las-extensiones).

| Añadido | Forma en el canal | Condición | Evidencia |
|---|---|---|---|
| Diálogos de `ask_user_question` | Un `select` por pregunta; la selección múltiple repite `select` sobre opciones conmutables. | Host interactivo. Sin él, la herramienta devuelve un resultado "unavailable". | `gentle-shell@ac67159:extensions/ask-user-question.ts:118`, `:137`, `:157-170`, `:267-268` |
| Diálogos de `ask_user_choice` | Un `select`; le sigue un `input` cuando se permite una respuesta personalizada. | Host interactivo. Sin él, la herramienta lanza una excepción. | `gentle-shell@ac67159:extensions/ask-user-choice.ts:205`, `:208`, `:229-231` |
| Actividad de los helpers (`gentle-agents.activity/v1`) | `setWidget` con `widgetKey: "gentle-agents"` y `widgetLines` con exactamente una cadena JSON. Agregada en un envío cada 150 ms. Limitada a 256 KiB. | Host interactivo, iniciada en `session_start`. | `gentle-shell@ac67159:docs/gentle-agents-activity.md:11-24`, `:80`, `:119`; `gentle-shell@ac67159:extensions/gentle-agents.ts:1697-1711`; `gentle-shell@ac67159:lib/agents-rpc-publisher.ts:12`, `:16`, `:32` |
| Fallo del envío de actividad | `notify` con `notifyType: "warning"`, deduplicado por mensaje. | Host interactivo. | `gentle-shell@ac67159:extensions/gentle-agents.ts:1704-1709` |
| Comandos de extensión (`/gentle:*`) | Se envían como texto de `prompt`; los diálogos que abren usan `select`/`confirm`/`input`. Ejemplo: `/gentle:persona` abre un `select`. Los comandos construidos sobre `ctx.ui.custom()` no obtienen UI: `/gentle:profiles` abre su panel con `custom()`, que devuelve `undefined` bajo RPC, y el manejador lee después `result.type` sin ninguna protección por modo. `Inference:` (no ejecutado) el comando lanza un `TypeError`. | Ninguna en la capa RPC. | `pi@a13d35a:packages/coding-agent/docs/rpc-commands.md:31`; `gentle-shell@ac67159:extensions/gentle-ai.ts:9924-9934`, `:4754-4756` (persona), `:4732-4739`, `:4070` (perfiles); `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-mode.ts:228-231` |
| Indicador YOLO (`/gentle:yolo`) | `setStatus` y `setWidget` (`string[]`) con la clave `gentle:yolo`, texto `YOLO_STATUS_TEXT`; se borra con `undefined`. | Ninguna: `publish` no comprueba el modo ni el host interactivo. `Inference:` (no ejecutado) ambas peticiones llegan a un host RPC, pero nunca como activas: la activación captura una identidad de sesión que requiere `ctx.mode === "tui"`, así que YOLO no se puede activar sobre RPC y un host RPC solo recibe el indicador borrado (`undefined`). El escritorio ignora `setStatus` y todas las claves de `setWidget` excepto `gentle-agents`. Ver [inventory Y4](05-capability-inventory.md#seguridad-y-permisos). | `gentle-shell@ac67159:lib/yolo-session-policy.ts:5-6`, `:105-108`, `:115-118`, `:172`; `gentle-shell@ac67159:lib/review-session-standing-permission.ts:144-162` |

**Carga de `gentle-agents.activity/v1`.** `{schema, summary:{running,queued,waiting,finished}, tasks:[{summary, thread}]}`. El `summary` de cada tarea admite solo `id`, `agent`, `label`, `prompt`, `status`, `createdAt`, `startedAt`, `endedAt`, `lastStep`, `lastActivityAt`, `turns`, `toolCalls`, `error`. Omite deliberadamente `cwd`, `parentSessionId`, `mode`, `model`, `thinking`, `sessionPath`, `result`, `tokens`, `cost` (`gentle-shell@ac67159:docs/gentle-agents-activity.md:62`). Los elementos del hilo son `{kind, text}` para texto/razonamiento/nota, y `{kind:"tool", name, args, running, isError, output}` para herramientas, con `args` serializado como cadena (`:64`; `gentle-shell@ac67159:lib/agents-rpc-publisher.ts:96-108`). El parser del escritorio está en `gentle-shell-desktop@5ab4a00:src/main/domain/rpc/helpersActivity.ts:38-55`.

### Superficies de gentle-shell que no llegan a un host RPC

`Inference:` estas funcionalidades se renderizan mediante API exclusivas de la TUI que el modo RPC descarta (ver [Qué descarta el modo RPC](#qué-descarta-el-modo-rpc)), así que hoy un host de escritorio no ve nada de ellas.

| Superficie | Por qué es exclusiva de la TUI | Evidencia |
|---|---|---|
| Etiqueta de fase de ODD | La renderiza `GentlePromptEditor`, instalado mediante `setEditorComponent`. Ese editor es el único lector del registro de fases, así que las fases inferidas de la actividad de las herramientas nunca salen del proceso. Excepción parcial: cuando el modelo llama a la herramienta `gentle_odd_phase`, la llamada y su argumento `phase` son visibles para un host RPC como eventos `tool_execution_*`. | `gentle-shell@ac67159:extensions/gentle-shell.ts:1108`, `:1120`, `:2383-2387`; `gentle-shell@ac67159:extensions/gentle-ai.ts:9330`, `:9336`; `gentle-shell@ac67159:lib/odd-phase.ts:1-8` |
| Widget de tareas (`gentle-todo`) | `setWidget` con una factoría de componentes. | `gentle-shell@ac67159:extensions/gentle-todo.ts:168-172` |
| Widget de cambios | `setWidget` con una factoría de componentes. | `gentle-shell@ac67159:extensions/gentle-shell.ts:1333-1343` |
| Widget de aviso de binario de desarrollo | `setWidget` con una factoría de componentes. En el `main` de gentle-shell (`ac67159`), después de la release 4.0.0 (#1652), el `notify` de respaldo para una sobrescritura activa o no válida solo se envía cuando el shell está desactivado (`GENTLE_PI_SHELL=0`, o dentro de un helper); una comprobación de sobrescritura fallida sigue enviando un `notify` siempre que se cumpla `ctx.hasUI`. `Inference:` por defecto ningún aviso de binario de desarrollo llega a un host RPC salvo que esa comprobación falle. En la release 4.0.0 y en 3.7.0, una sobrescritura activa o no válida también llegaba como `notify` (`gentle-shell@1f35ab1:extensions/gentle-ai.ts:9368-9370`; `gentle-shell@1162ce9:extensions/gentle-ai.ts:9369-9370`). | `gentle-shell@ac67159:extensions/gentle-shell.ts:1890-1895`; `gentle-shell@ac67159:extensions/gentle-ai.ts:9706-9713`; `gentle-shell@ac67159:lib/shell-bar.ts:107-111` |
| Pie personalizado, cabecera del shell y cabecera de arranque | `setFooter`, un `setWidget` con factoría de componentes para la cabecera del shell (`HEADER_WIDGET_KEY`), y `setHeader` para el banner de arranque. | `gentle-shell@ac67159:extensions/gentle-shell.ts:1789`, `:1852-1874`; `gentle-shell@ac67159:extensions/startup-banner.ts:750` |
| Superposición de agentes (`/gentle:agents`), incluido el Stop por helper; superposición de estadísticas (`/gentle:stats`, nueva en 4.0.0) | Cada una retorna antes de tiempo con un aviso "requires TUI mode" cuando `ctx.mode !== "tui"`. | `gentle-shell@ac67159:extensions/gentle-agents.ts:1081-1086`; `gentle-shell@ac67159:extensions/gentle-stats.ts:49-54` |

## Versionado y compatibilidad

### ¿Hay un handshake de versión?

**No.** Qué se comprobó:

- La capa RPC de pi: una búsqueda sin distinguir mayúsculas de `version` en `packages/coding-agent/src/modes/rpc/` no devuelve nada en 0.85.1 ni en 0.99.1, y de nuevo nada en 1.0.0 (repetida con `git grep -i version a13d35a -- packages/coding-agent/src/modes/rpc/` el 2026-10-03). `RpcSessionState` no tiene campo de versión (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:96-109`). Ningún registro de arranque anuncia una versión (ver [Arranque y parada](#arranque-y-parada)).
- Escritorio: `src/main` nunca ejecuta `--version` y nunca compara versiones. La única referencia es el mensaje de error "gentle-pi 3.7.0 or newer" cuando no se encuentra ningún lanzador (`gentle-shell-desktop@5ab4a00:src/main/adapters/launcherLocator.ts:26-28`).
- La única carga versionada es el esquema de actividad. El escritorio rechaza cualquier trama cuyo `schema` no sea exactamente `gentle-agents.activity/v1` y conserva el estado anterior (`gentle-shell-desktop@5ab4a00:src/main/domain/rpc/helpersActivity.ts:19`, `:48`).
- La única comprobación de versión que se impone en la cadena es el mínimo de pi 0.99.1 del lanzador (`gentle-shell@ac67159:lib/gentle-shell-launcher.ts:392`, `:405-418`).

### Versiones efectivas

| Componente | Versión | Evidencia |
|---|---|---|
| pi que responde al RPC (a través de gentle-shell 4.0.0) | ≥ 0.99.1, impuesta al lanzar; gentle-shell se desarrolla contra ≥ 1.0.0. Las fuentes de RPC son idénticas byte a byte en 0.99.1 y 1.0.0, así que el contrato de esta página es válido para ambas. (gentle-shell 3.7.0 también imponía 0.99.1 y fijaba la versión de desarrollo `0.99.1`: `gentle-shell@1162ce9:package.json:95`.) | `gentle-shell@ac67159:lib/gentle-shell-launcher.ts:392`; `gentle-shell@ac67159:package.json:78` (peer `>=0.99.1`), `:95-97` (dev `>=1.0.0`) |
| pi importado en el mismo proceso por el escritorio | 0.85.1 (bloqueada) | `gentle-shell-desktop@5ab4a00:package.json:42`, `gentle-shell-desktop@5ab4a00:pnpm-lock.yaml:323` |
| pi contra el que se escribieron los tipos RPC del escritorio | `UNVERIFIED:` la cabecera nombra "the local pi checkout" sin versión. `Inference:` el subconjunto modelado coincide con las formas de ambas versiones. | `gentle-shell-desktop@5ab4a00:src/main/domain/rpc/types.ts:7` |

### Observaciones de compatibilidad

| # | Observación | Impacto | Evidencia |
|---|---|---|---|
| 1 | La respuesta de `prompt` de 0.99.1 añade `data.disposition`. El escritorio decodifica `data?: unknown` e ignora las respuestas de prompt. | Compatible. | `gentle-shell-desktop@5ab4a00:src/main/domain/rpc/types.ts:175`, `gentle-shell-desktop@5ab4a00:src/main/domain/rpc/codec.ts:201-210` |
| 2 | Los elementos de herramienta del hilo de gentle-shell no llevan `callId`, pero el parser del escritorio exige un `callId` de tipo cadena para `kind: "tool"`. | `Inference:` los elementos de herramienta reales se descartan del hilo de Helpers. El fixture del escritorio incluye `callId`, así que sus tests no lo detectan. | `gentle-shell@ac67159:lib/agents-rpc-publisher.ts:96-108`, `gentle-shell@ac67159:docs/gentle-agents-activity.md:64`; `gentle-shell-desktop@5ab4a00:src/main/domain/rpc/helpersActivity.ts:107-108`; `gentle-shell-desktop@5ab4a00:src/main/domain/rpc/__fixtures__/helpers-activity.jsonl:2` |
| 3 | El escritorio desactiva `working` en `agent_end`, incluso cuando `willRetry` es true. pi indica esperar a `agent_settled`. | `Inference:` durante un reintento automático el compositor se vuelve a habilitar. Un prompt enviado en ese momento no lleva `streamingBehavior`, así que pi lo rechaza con un error. | `gentle-shell-desktop@5ab4a00:src/main/domain/rpc/chatReducer.ts:56-58`; `pi@a13d35a:packages/coding-agent/docs/rpc.md:69`; `pi@a13d35a:packages/coding-agent/docs/rpc-commands.md:29` |
| 4 | Un `prompt` que es `"handled"` (por ejemplo, un comando `/gentle:*`) no inicia ninguna ejecución. | `Inference:` no llega ningún `agent_start`, así que `working` nunca se activa. Esto es inocuo para el reducer actual. | `pi@a13d35a:packages/coding-agent/docs/rpc.md:67` |
| 5 | `parentToolCallId` y los tres eventos de estado no están modelados. | Nada se rompe: el codec descarta los campos y tipos desconocidos (`gentle-shell-desktop@5ab4a00:src/main/domain/rpc/codec.ts:100-116`, `:130-131`). | — |
| 6 | Los conjuntos de estados de las tareas difieren. Los estados de gentle-shell son `queued`, `running`, `waiting`, `completed`, `failed`, `cancelled`, `timed_out`, publicados sin cambios en el `summary.status` de cada tarea. El escritorio solo acepta `queued`, `running`, `waiting`, `done`, `failed`, `cancelled`, y `toTask` descarta una tarea cuyo estado no está en ese conjunto. | Probable bug del escritorio. `Inference:` (no ejecutado) la fusión de retención del reducer conserva una tarea que se vio mientras estaba en ejecución y que después desapareció de la trama, y convierte `running` en `done`. Así que el efecto visible es sobre todo un estado erróneo: un helper que agotó su tiempo se muestra como terminado (`completed` acaba como terminado por casualidad). Solo un helper visto por primera vez ya en `completed` o `timed_out`, por ejemplo tras abrir un chat, desaparece de la lista, mientras que el contador `summary.finished` (interpretado por separado) todavía lo cuenta. El fixture del escritorio usa `done`, así que sus tests no lo detectan. Ver [audit A5](03-architecture/audit.md#a5-el-conjunto-de-estados-de-los-helpers-y-los-elementos-de-herramienta-no-coinciden-con-gentle-shell). | `gentle-shell@ac67159:lib/agents-protocol.ts:9-17`, `gentle-shell@ac67159:lib/agents-rpc-publisher.ts:116`; `gentle-shell-desktop@5ab4a00:src/main/domain/rpc/helpersActivity.ts:21`, `:83-85`, `:87-95`, `:139-141`; `gentle-shell-desktop@5ab4a00:src/main/domain/rpc/chatReducer.ts:225-240`; `gentle-shell-desktop@5ab4a00:src/main/domain/rpc/__fixtures__/helpers-activity.jsonl` |
| 7 | El listado de sesiones usa pi 0.85.1 en el mismo proceso, mientras que el par RPC ejecuta ≥ 0.99.1. | `UNVERIFIED:` aquí no se comprobó si el formato de archivo de sesión difiere entre esas versiones. Ver `03-architecture/audit.md`. El inventario lo resuelve para los campos que usa la lista: el mismo `CURRENT_SESSION_VERSION` y una interfaz `listAll()` idéntica ([05 §Diferencias entre pi 0.85.1 y 0.99.1](05-capability-inventory.md#diferencias-entre-pi-0851-y-0991-que-importan-al-escritorio)). | `gentle-shell-desktop@5ab4a00:src/main/adapters/piSessionStore.ts:30` |

## Carencias que necesita el escritorio

Una carencia (gap) es una capacidad que necesita el escritorio y que el contrato RPC no ofrece. **Base** indica de dónde procede la necesidad:

- **stated**: el repositorio del escritorio declara la necesidad.
- **intent-driven**: derivada de la maqueta conceptual (mockup) (intención, no especificación).
- **community proposal**: no es intención del mantenedor.

La ausencia se comprueba contra la lista completa de comandos (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:20-74`) y la lista de métodos de UI de extensiones (`:252-287`).

| # | Carencia | Base | Evidencia de la necesidad | Evidencia de la ausencia | Solución parcial hoy |
|---|---|---|---|---|---|
| G1 | **Detener un helper** (un subagente, o todos) | stated | `gentle-shell-desktop@5ab4a00:README.md:62`, `:85-86`; `gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m2-helpers.md:18`, `:22`; botón Stop de la maqueta `gs-mockup.html:603` | Ningún comando RPC se dirige a los subagentes. gentle-agents solo detiene tareas desde la superposición de la TUI (`gentle-shell@ac67159:extensions/gentle-agents.ts:995`, `:1020`, `:1081-1086`) o un atajo de la TUI (`:1656-1660`). `subagent_cancel` es una herramienta del modelo, no un comando del host (`:1602`). | `Inference:` el `abort` de RPC cancela los subagentes **en primer plano** a través del manejador de aborto de la llamada a la herramienta (`gentle-shell@ac67159:extensions/gentle-agents.ts:1371-1378`). Las tareas en segundo plano retornan antes de que ese manejador se conecte (`:1366`), así que un único helper en segundo plano no se puede detener sobre RPC. Detener todos solo existe como efecto secundario destructivo: `new_session`, `switch_session`, `fork`, `clone` y cerrar stdin emiten `session_shutdown` (`pi@a13d35a:packages/coding-agent/src/core/agent-session-runtime.ts:167-177`, `:212`, `:245`, `:299`, `:320`, `:334`, `:404-407`; el `clone` de RPC llama a `fork`, `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-mode.ts:624`), y gentle-agents responde con `runner.cancelAll(...)` (`gentle-shell@ac67159:extensions/gentle-agents.ts:1714`, `:1734`). Pedir al modelo mediante `prompt` que llame a `subagent_cancel` es indirecto y no es un control. |
| G2 | **Estado estructurado de ODD** (funcionalidad, fase, tareas, comprobaciones) | stated + intent-driven | `gentle-shell-desktop@5ab4a00:README.md:63`; `gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m2-helpers.md:69` ("needs the structured ODD document format"); panel de ODD de la maqueta `gs-mockup.html:614-640` | No hay comando ni evento de ODD. La etiqueta de fase es exclusiva de la TUI (ver [Superficies de la TUI](#superficies-de-gentle-shell-que-no-llegan-a-un-host-rpc)). | Solo la fase, y solo cuando la comunica el modelo: las llamadas a `gentle_odd_phase` (con su argumento `phase`) llegan como eventos `tool_execution_*` (`gentle-shell@ac67159:extensions/gentle-ai.ts:9330`, `:9336`). Las fases inferidas de la actividad de las herramientas siguen siendo exclusivas de la TUI (`gentle-shell@ac67159:lib/odd-phase.ts:1-8`). `get_entries` / `entry_appended` transportarían el estado de ODD si gentle-shell lo añadiera como entrada de sesión ([Canales del host y de las extensiones](#canales-del-host-y-de-las-extensiones)), pero no lo hace: los únicos tipos de entrada personalizados que añade gentle-shell son `gentle-pi.session-change/v1`, `gentle-pi.session-worktree/v1`, `gentle-ai-elapsed-timing/v1`, `gentle-pi.review-reminder-receipt/v1` y `gentle-agents.stale-result` (`gentle-shell@ac67159:lib/session-changes.ts:8`, `lib/session-change-capture.ts:28`; `lib/session-worktree-registry.ts:6`, `:114`; `lib/gentle-ai-elapsed-store.ts:1`, `:84`; `lib/review-reminder-receipt.ts:5`, `:107`, `:113`; `extensions/gentle-agents.ts:59`, `:720`; todas las llamadas a `appendEntry(` en `extensions/` y `lib/`, buscadas con `rg` el 2026-10-03). |
| G3 | **Proveedores e inicio de sesión** | stated + intent-driven | `gentle-shell-desktop@5ab4a00:README.md:63` ("no providers ... screens (M4): sign in ... through `gentle-shell` in the terminal"); maqueta `gs-mockup.html:695-723` | No hay comando de autenticación ni de inicio de sesión. Solo `get_available_models` y `set_model` (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:33-35`). El inicio de sesión OAuth de Radius ya existe en pi 0.99.1 (`pi@d86654a:packages/ai/src/auth/oauth/radius.ts`); pi 1.0.0 lo lleva al nivel superior del `/login` interactivo y ofrece configurar el servidor MCP de Radius, sin equivalente en RPC (`pi@a13d35a:packages/coding-agent/CHANGELOG.md:25`; inventory M7). | La elección de modelo por sesión funciona; las credenciales no. |
| G4 | **Modelo por defecto para los chats nuevos** | intent-driven | maqueta `gs-mockup.html:730-731` | `set_model` actúa solo sobre la sesión en ejecución: RPC llama a `session.setModel(model)` sin `persist` (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-mode.ts:476`), y `setModel` escribe el modelo por defecto solo cuando `options.persist` es true (`pi@a13d35a:packages/coding-agent/src/core/agent-session.ts:2439-2442`). Ningún comando persiste un valor por defecto. | El indicador de CLI `--model` al lanzar (`pi@a13d35a:packages/coding-agent/docs/rpc.md:18`). |
| G5 | **Extensiones y paquetes** (instalar, actualizar, eliminar, habilitar) | stated + intent-driven | `gentle-shell-desktop@5ab4a00:README.md:63`; maqueta `gs-mockup.html:754-797` | No hay ningún comando de paquetes en `RpcCommand`. `get_commands` solo lista comandos, prompts y skills (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:81-90`). | Ninguna sobre RPC. |
| G6 | **Perfiles** (leer el activo, cambiar) | intent-driven; concepto central de gentle-shell (`gentle-shell@ac67159:README.md:167`; [issue #28, "Author's framing: reading the concept mockup"](https://github.com/Gentleman-Programming/gentle-shell-desktop/issues/28)) | barra de estado de la maqueta `gs-mockup.html:819`, `:731` | No hay estado de perfil en `RpcSessionState` (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:96-109`). | Ninguna. `/gentle:profiles` no es accesible hoy sobre RPC: su panel usa `ctx.ui.custom()` (`gentle-shell@ac67159:extensions/gentle-ai.ts:4070`), que devuelve `undefined` bajo RPC (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-mode.ts:228-231`), y el manejador lee después `result.type` (`gentle-shell@ac67159:extensions/gentle-ai.ts:4739`). `Inference:` (no ejecutado) lanza un `TypeError`. El perfil activo tampoco se puede leer como dato. |
| G7 | **Datos de la barra de estado** | intent-driven | maqueta `gs-mockup.html:813-822` | Modelo y nivel de razonamiento: `get_state` más `thinking_level_changed` (disponibles). Coste y uso de contexto: `get_session_stats` (solo por consulta; `pi@a13d35a:packages/coding-agent/src/core/agent-session.ts:341-342`). cwd y rama: no están en `RpcSessionState`. `ODD · RDD on`: no hay estado RPC; RDD se lee mediante el comando `/gentle:review-mode` (`gentle-shell@ac67159:docs/readme-reference.md:397`). | Parcialmente disponible; hoy el escritorio no usa nada de ello. |
| G8 | **Transcripción y resultado de un helper** (para auditoría o para "por qué hizo eso") | community proposal | [Issue #28, "Author's framing: philosophy"](https://github.com/Gentleman-Programming/gentle-shell-desktop/issues/28) (propuestas de Matrak); nota de esqueleto en este archivo | La carga de actividad omite `sessionPath`, `result`, `tokens`, `cost` (`gentle-shell@ac67159:docs/gentle-agents-activity.md:62`). Los hilos conservan los últimos 40 elementos (`:79`). | `subagent_result` es una herramienta del modelo, no un comando del host (`gentle-shell@ac67159:extensions/gentle-agents.ts:1578`). |
| G9 | **Varios chats a la vez** | intent-driven | estado "needs you" de la barra lateral de la maqueta `gs-mockup.html:486`; estilos de notificación `gs-mockup.html:308-323` | No es una carencia del protocolo: un proceso de pi atiende una sesión, y nada impide lanzar varios. El escritorio mantiene una única sesión `current` (`gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts:70`). | Trabajo de arquitectura del escritorio, no un cambio en upstream (repositorio de origen). |
| G10 | **Handshake de versión** | `Inference:` derivada del desfase anterior, no declarada en ninguna parte | Ver [Versionado](#versionado-y-compatibilidad) | No hay campo de versión en ninguna parte del protocolo. | Ejecutar `gentle-shell --version` por fuera del canal (`gentle-shell@ac67159:bin/gentle-shell.mjs:1217-1219`). |

Las líneas de la maqueta (`gs-mockup.html:<line>`, en esta página y en todo el corpus) se refieren a [`assets/gs-mockup.html`](https://github.com/matraket/gentle-shell-desktop/blob/d119d0a7a928821c40fff41ad1b1ddc73eaa1834/docs/assets/gs-mockup.html), una instantánea del DOM renderizado de https://claude.ai/artifact/CCpKaRTkrnDrWoErY27KEL guardada el 2026-10-01 (ver [assets/README.md](assets/README.md)). La maqueta es intención, no especificación.

`Inference` (capa responsable de cada carencia): el núcleo de pi es responsable de la unión `RpcCommand`, así que los comandos de host nuevos (G3, G4, G5, G10) necesitan un cambio en pi. gentle-shell puede enviar datos nuevos sin tocar pi usando cargas `setWidget` `string[]`, como hace el esquema de actividad (`gentle-shell@ac67159:docs/gentle-agents-activity.md:13`), o los mensajes personalizados y las entradas de sesión enumerados en [Canales del host y de las extensiones](#canales-del-host-y-de-las-extensiones). Esa vía encaja con G2, G6, G7 y G8. Una acción del host como G1 necesita un canal de entrada, y pi ya encamina el texto del host hacia el código de las extensiones; entre otros caminos, `prompt` llega a los comandos de extensión y a los manejadores `input`, `steer` y `follow_up` llegan a los manejadores `input`, `bash` llega a los manejadores `user_bash`, y `extension_ui_response` responde a los diálogos (misma sección). Así que G1 podría cubrirse dentro de gentle-shell sin ningún cambio en pi, por ejemplo con un comando o un manejador `input` que detenga un helper por su ID. No existe tal manejador en `ac67159`: gentle-agents registra un comando, la superposición exclusiva de la TUI (`gentle-shell@ac67159:extensions/gentle-agents.ts:1646`, `:1081-1086`), y no hay ningún manejador `input` registrado en `extensions/` ni en `lib/` (`rg` el 2026-10-03). Qué canal debería usar un host es una pregunta abierta: ver [Alternativas para un canal del host hacia las funcionalidades de gentle-shell](#alternativas-para-un-canal-del-host-hacia-las-funcionalidades-de-gentle-shell) y [ADR: Sin decidir](03-architecture/adr/README.md#sin-decidir--no-registrado).

### Canales del host y de las extensiones

pi no ofrece ninguna forma de que un host llame por su nombre a código de extensión sobre RPC, pero varias entradas RPC llegan a manejadores de extensiones, y varias API de extensión llegan al host. gentle-shell también ejecuta canales propios fuera del stdio de pi. Verificado en pi 1.0.0 (`pi@a13d35a`) y en gentle-shell `main` (`gentle-shell@ac67159`); más abajo, `PC` abrevia `pi@a13d35a:packages/coding-agent/` y `GS` abrevia `gentle-shell@ac67159:`.

**Sin paso directo (passthrough).**

- `RpcCommand` no tiene ninguna variante genérica ni de extensión (PC`src/modes/rpc/rpc-types.ts:20-74`). Un `type` desconocido cae en la rama `default` y devuelve `Unknown command: <type>`; en ese camino no se ejecuta ningún código de extensión (PC`src/modes/rpc/rpc-mode.ts:713-716`).
- Los métodos de registro de `ExtensionAPI` cubren herramientas, comandos, atajos de teclado, indicadores, renderizadores, proveedores, servidores MCP y modelos virtuales; ninguno registra un comando ni un evento RPC (PC`src/core/extensions/types.ts:1619-1859`).
- `pi.events` es un bus `EventEmitter` en el mismo proceso para "Communicate with another extension" (PC`src/core/event-bus.ts:1-6`; PC`src/core/extensions/types.ts:1862`; PC`docs/extensions.md:86`). `rpc-mode.ts` no hace referencia a él.
- El modo RPC redirige `process.stdout.write` a stderr y escribe sus propios registros mediante `writeRawStdout` (PC`src/modes/rpc/rpc-mode.ts:55`, `:61`; PC`src/core/output-guard.ts:45-70`, `:85-93`). `Inference:` una extensión que escribe en `process.stdout` no puede añadir registros al flujo RPC.

**De entrada: entradas RPC que llegan al código de las extensiones.**

| Entrada RPC | Código de extensión alcanzado | Qué recibe la extensión | Evidencia |
|---|---|---|---|
| `prompt` que empieza por `/name` | El manejador del comando registrado. Se ejecuta antes de las comprobaciones de compactación y de streaming ("execute immediately, even during streaming"); la respuesta indica `disposition: "handled"`. | La cadena de argumentos | PC`src/modes/rpc/rpc-mode.ts:394-414`; PC`src/core/agent-session.ts:1928-1936`, `:2069-2083`; PC`docs/rpc-commands.md:40` |
| `prompt` con otro texto | Manejadores `input`, con `source: "rpc"`. Cada uno devuelve `continue`, `transform` o `handled`; `handled` termina el prompt (disposición `handled`), y esto se ejecuta antes del rechazo "already processing". Un prompt que inicia una ejecución dispara también `before_agent_start`. | `text`, `images`, `source`, `streamingBehavior` | PC`src/modes/rpc/rpc-mode.ts:402`; PC`src/core/agent-session.ts:1945-1955`, `:1870-1888`, `:1966-1969`, `:2012-2019`; PC`src/core/extensions/types.ts:1116-1135`; PC`src/core/extensions/runner.ts:1510-1536` |
| `steer`, `follow_up` | Manejadores `input` (`source: "rpc"`); el texto que empieza por un comando de extensión se rechaza. pi 0.86.0 corrigió que estos comandos estuvieran "bypassing extension `input` handlers", así que esto se cumple por encima de la versión mínima 0.99.1 del lanzador. | Como arriba | PC`src/modes/rpc/rpc-mode.ts:416-424`; PC`src/core/agent-session.ts:2126-2142`, `:2169`, `:2185`; PC`CHANGELOG.md:340` (sección `:270`) |
| `bash` | Manejadores `user_bash`; un manejador puede devolver el resultado por sí mismo. | `command`, `excludeFromContext`, `cwd` | PC`src/modes/rpc/rpc-mode.ts:561-579`; PC`src/core/extensions/runner.ts:1253-1260`; PC`src/core/extensions/types.ts:1101-1109` |
| `extension_ui_response` | Solo el diálogo pendiente con el mismo `id`; los demás ids se ignoran. | La respuesta del diálogo | PC`src/modes/rpc/rpc-mode.ts:122-128`, `:767-779` |
| `compact` | `session_before_compact` (motivo `manual`), y después `session_compact` una vez guardada la compactación. | `customInstructions` y la preparación de la compactación | PC`src/modes/rpc/rpc-mode.ts:533-535`; PC`src/core/agent-session.ts:2745-2754`, `:2811-2817` |
| `set_session_name` | `session_info_changed` (también se escribe en stdout). | `name` | PC`src/modes/rpc/rpc-mode.ts:659-665`; PC`src/core/agent-session.ts:3893-3897`; PC`src/core/extensions/types.ts:730-734` |
| `set_model`, `cycle_model`, `set_thinking_level`, `cycle_thinking_level`, `new_session`, `switch_session`, `fork`, `clone` | Eventos del ciclo de vida: `model_select` (origen `set` o `cycle`), `thinking_level_select`, `session_before_switch`, `session_before_fork`, `session_shutdown`, `session_start`. `session_shutdown` con motivo `quit` también se dispara cuando se cierra stdin, lo cual no es un comando. | Cambios de estado; `switch_session` pasa su ruta de destino | PC`src/core/agent-session.ts:2410-2421`, `:2472-2479`, `:2518`, `:2550`, `:2579-2586`, `:2594-2603`; PC`src/modes/rpc/rpc-mode.ts:435-442`, `:480-486`, `:502-503`, `:603-629`; PC`src/core/agent-session-runtime.ts:138-172` (`:142-146` ruta de destino), `:218`, `:251`, `:305`, `:326`, `:345`; cierre de stdin: PC`src/modes/rpc/rpc-mode.ts:802-805`, `:736`; PC`src/core/agent-session-runtime.ts:404-408` |

`Inference:` el texto libre del host llega al código de las extensiones solo mediante `prompt`, `steer`, `follow_up`, `bash`, `extension_ui_response`, `compact` y `set_session_name`; los demás comandos transportan como mucho identificadores, rutas o ajustes.

**De salida: API de extensión que llegan al host.**

| API de extensión | Registro del host | ¿Se conserva en la sesión? | Evidencia |
|---|---|---|---|
| Diálogos y métodos de tipo dispara y olvida de `ctx.ui` | `extension_ui_request` ([Peticiones de UI de extensiones](#peticiones-de-ui-de-extensiones)); `setWidget` transporta solo `string[]` | No | PC`src/modes/rpc/rpc-mode.ts:136-311`; PC`docs/rpc-extension-ui.md:7-8` |
| `pi.sendMessage` | `message_start` / `message_end` con `role: "custom"`, `customType`, `content`, `display`, `details`. `content` se convierte en un mensaje de usuario para el modelo; `details` no se envía al modelo. La entrega durante el streaming sigue `deliverAs`. | Sí, como entrada `custom_message`. `Inference:` también lo devuelve `get_messages`. | PC`src/core/agent-session.ts:2246-2294`; PC`src/modes/rpc/rpc-mode.ts:355-356`, `:672-673`; PC`docs/message-types.md:207-217`; PC`src/core/session-manager.ts:453-455` |
| `pi.appendEntry(customType, data)` | `entry_appended` con la entrada; reproducible con `get_entries` y un cursor `since` | Sí; "not sent to LLM" | PC`src/core/agent-session.ts:3359-3364`; PC`docs/json.md:122`; PC`src/modes/rpc/rpc-mode.ts:636-647`; PC`docs/rpc-commands.md:689-717`; PC`src/core/extensions/types.ts:1691-1692` |
| `pi.sendUserMessage` | Ejecuta un prompt con `source: "extension"`. `Inference:` el host lo ve como un `message_start` / `message_end` de usuario corriente, sin nada que marque a la extensión como su autora. | `Inference:` sí, como mensaje de usuario | PC`src/core/agent-session.ts:3350-3357`, `:2342-2347` |
| `pi.setSessionName` | `session_info_changed` con `name` | Sí, como información de la sesión | PC`src/core/agent-session.ts:3366-3368`, `:3893-3896`; PC`docs/json.md:123` |
| Un manejador lanza una excepción | `extension_error` con `extensionPath`, `event`, `error` | No | PC`src/modes/rpc/rpc-mode.ts:348-350`; PC`docs/json.md:190-194` |
| Se ejecuta una herramienta registrada | `tool_execution_*` con `args` y `result.details` | Como mensajes de herramienta | PC`docs/json.md:111-114` |

gentle-shell ya usa las filas de mensaje personalizado, mensaje de usuario y entrada:

- entradas, por ejemplo `gentle-pi.session-change/v1` y `gentle-agents.stale-result` (GS`lib/session-changes.ts:8`; GS`lib/session-change-capture.ts:28`; GS`extensions/gentle-agents.ts:59`, `:720`; lista completa en gap G2 más arriba);
- mensajes personalizados, los cuatro tipos que envía: `gentle-agents.result`, `gentle-agents.message`, `gentle-agents.orchestrator-message` y `gentle-pi.review-preflight` (GS`extensions/gentle-agents.ts:56-58`, `:501`, `:700-703`, `:712`, `:725`; GS`extensions/gentle-ai.ts:9843-9850`; todas las llamadas a `sendMessage(` en `extensions/` y `lib/`, buscadas con `rg` el 2026-10-03);
- mensajes de usuario: el texto de despertar del padre inactivo, un comando elegido en la paleta de comandos (usa `ctx.ui.custom()`, así que `Inference:` nunca bajo RPC) y el texto de prompts encolados (GS`extensions/gentle-agents.ts:691`; GS`extensions/gentle-shell.ts:1325`, `:2405`).

**Canales propios de gentle-shell, fuera del stdio de pi.**

- **Ejecutor de helpers.** gentle-agents es en sí mismo un cliente RPC: cada helper ejecuta `--mode rpc` con tres flujos stdio conectados por tubería y un canal `ipc` de Node, más una tubería de permisos en el fd 3 cuando existe un canal de permisos del padre (GS`lib/agents-runner.ts:258-259`, `:475`, `:502-507`, `:530-535`). Envía `steer`, `get_state`, `prompt` y `abort` y responde con `extension_ui_response` (GS`lib/agents-runner.ts:441`, `:560`, `:573`, `:830`, `:863`). Las tramas `ipc` son `notification` y `query`, con tamaño acotado (GS`lib/agents-messaging.ts:1-30`, `:84-90`).
- **Transporte entre sesiones.** Sockets de dominio Unix en un directorio privado `/tmp/gentle-pi-<uid>/<profile hash>/`, con registros de presencia bajo el perfil (GS`lib/agents-session-transport.ts:6-7`, `:64-78`, `:85-87`, `:433`); tuberías con nombre privadas mediante un script auxiliar de PowerShell en Windows (GS`docs/gentle-shell.md:219`). Las tramas llevan `version: 1` y están limitadas a 64 KiB (GS`lib/agents-session-transport.ts:253-257`). Es "notification-and-ACK transport only", y los envíos salientes necesitan el consentimiento humano interactivo (GS`docs/gentle-shell.md:219`). En POSIX, se comprueba que los endpoints de socket y los directorios privados pertenezcan al usuario actual del sistema operativo (GS`lib/agents-session-transport.ts:22-23`, `:44`, `:52`, `:210`, `:440`). Arranca en el `session_start` de cualquier proceso que no sea hijo y tenga gentle-agents activado, sin comprobar el modo: `startSessionTransport` no examina ni `ctx.mode` ni `ctx.hasUI` (GS`extensions/gentle-agents.ts:151-154`, `:336-347`, `:468-520`, `:1663`, `:1689`). Una notificación entrante se convierte en un mensaje personalizado entregado como mensaje de seguimiento (follow-up) que dispara un turno (GS`extensions/gentle-agents.ts:498-501`). `Inference:` (no ejecutado) el hijo RPC del escritorio también abre este punto de escucha (listener).
- **Presencia por archivos.** Archivos de presencia bajo `gentle-agents/presence` del perfil, escritos de forma atómica; un "Same-profile OS-user trust boundary, not an authorization channel" (GS`lib/orchestrator-presence.ts:6-7`, `:106-107`, `:148-155`, `:258-262`).

**Precedente de esquema.** `gentle-agents.activity/v1` es el único esquema documentado para datos dirigidos al host (GS`docs/gentle-agents-activity.md:9-24`; GS`lib/agents-rpc-publisher.ts:12`, `:16`, `:29-32`). Es solo de salida, y el escritorio rechaza cualquier otro valor de `schema` ([¿Hay un handshake de versión?](#hay-un-handshake-de-versión)). `Inference:` el documento no establece ninguna regla para evolucionar el esquema (no se encontró tal regla en GS`docs/gentle-agents-activity.md`).

#### Alternativas para un canal del host hacia las funcionalidades de gentle-shell

Detalle de la pregunta abierta [Canal del host hacia las funcionalidades de gentle-shell](03-architecture/adr/README.md#sin-decidir--no-registrado). Aquí no se recomienda ninguna alternativa; los juicios se etiquetan como `Inference:`.

| Alternativa | Qué repositorio cambia, y su proceso | De entrada (host → gentle-shell) | De salida (gentle-shell → host) | Costes y riesgos |
|---|---|---|---|---|
| **A. Ampliar el `RpcCommand` de pi** | pi, y después gentle-shell para implementarlo y el escritorio para consumirlo. El núcleo de pi es mínimo y los puntos de enganche de las extensiones "should be well considered and discussed" (`pi@a13d35a:CONTRIBUTING.md:7-11`); un contribuidor nuevo presenta una issue `Contribution Proposal`, "required for new contributors before submitting a PR" (`pi@a13d35a:.github/ISSUE_TEMPLATE/contribution.yml:1-2`), y necesita `lgtm` antes de una PR (`pi@a13d35a:CONTRIBUTING.md:29-34`, `:58`); los cambios de mayor envergadura pasan por RFC (`:101-102`). | Comandos tipados con una `response` correlacionada, ya sea uno por funcionalidad o un paso directo (passthrough) genérico de extensiones; ambos son nuevos (PC`src/modes/rpc/rpc-types.ts:20-74`; PC`src/modes/rpc/rpc-mode.ts:713-716`). | Tipos de evento tipados nuevos, si pi los acepta. | `Inference:` necesita una revisión upstream de pi antes de que gentle-shell pueda implementarlo, y puede rechazarse en virtud de la regla de núcleo mínimo de pi. `Inference:` el escritorio dependería de una release de pi por encima de la versión mínima actual, 0.99.1 (`gentle-shell@ac67159:lib/gentle-shell-launcher.ts:392`), sin ningún handshake de versión para detectarla ([Versionado](#versionado-y-compatibilidad)). `UNVERIFIED:` no se encontró ninguna política de estabilidad ni de compatibilidad del RPC para pi; su changelog registra cambios aditivos del RPC (PC`CHANGELOG.md:129`, pi 0.99.0) y anota cuándo "the supported local SDK and stdio RPC API are unchanged" (`:371`, pi 0.85.1). |
| **B. Canales de extensión de pi existentes, con esquemas versionados** | gentle-shell (más el escritorio); sin cambios en pi. gentle-shell no tiene `CONTRIBUTING.md` y recibe las solicitudes de funcionalidad mediante su formulario de issue ([proceso de gentle-shell](#gentle-shell-gentleman-programminggentle-shell-paquete-gentle-pi-responsable-de-los-añadidos-a-nivel-de-extensión)). | `prompt` `/command args` (se ejecuta incluso durante el streaming), manejadores `input` en `prompt`, `steer` y `follow_up`, `user_bash`, respuestas a diálogos ([tabla de entrada](#canales-del-host-y-de-las-extensiones)). | `extension_ui_request` (`setWidget` `string[]`, `notify`, `setStatus`), mensajes personalizados, mensajes de usuario (`sendUserMessage`), `session_info_changed` (`setSessionName`), `entry_appended` con reproducción mediante `get_entries`, `tool_execution_*` ([tabla de salida](#canales-del-host-y-de-las-extensiones)). | La entrada es texto (más imágenes en los prompts), no campos tipados: la carga de un comando o de `input` comparte el espacio de texto del prompt del usuario, y la respuesta de `prompt` solo transporta una `disposition`, no un resultado (PC`docs/rpc-commands.md:40`); `Inference:` los resultados y los errores necesitan un registro de salida aparte y un id de correlación definido por el esquema. El `content` de un mensaje personalizado va al modelo (PC`docs/message-types.md:217`) y las entradas persisten en el archivo de sesión (PC`src/core/extensions/types.ts:1691-1692`); `Inference:` cada vía de salida intercambia contexto del modelo o tamaño de la sesión frente a `setWidget`, que no conserva ninguno de los dos. `Inference:` aún no existe ninguna regla de evolución del esquema (precedente del esquema de actividad, más arriba). |
| **C. Un canal propio de gentle-shell fuera del stdio de pi** | gentle-shell (más el escritorio); sin cambios en pi; el mismo proceso de gentle-shell que en B. | Cualquier cosa que defina el nuevo protocolo. | Cualquier cosa que defina el nuevo protocolo. | Un segundo transporte junto a stdio. El transporte existente es específico de cada plataforma (sockets Unix; tuberías con nombre mediante un script auxiliar de PowerShell en Windows), transporta solo notificaciones y ACK, y necesita consentimiento interactivo para enviar (GS`docs/gentle-shell.md:219`). Su control de acceso es la propiedad por el usuario actual del sistema operativo en POSIX (GS`lib/agents-session-transport.ts:22-23`, `:210`, `:440`), y los archivos de presencia que lo acompañan son un "Same-profile OS-user trust boundary, not an authorization channel" (GS`lib/orchestrator-presence.ts:6`). Sus mensajes entrantes llegan al modelo como mensajes de seguimiento que disparan un turno (GS`extensions/gentle-agents.ts:501`), así que hoy no es un canal de control del host. `Inference:` el escritorio necesitaría descubrimiento de endpoints, autenticación y ordenación respecto al flujo de stdio, y la afirmación de que RPC es "la única interfaz formal entre el escritorio y gentle-shell" (línea 7 de esta página) dejaría de cumplirse. |

## Notas para implementadores de clientes pi

Los datos siguientes son los datos de cliente pi de la PR #30 (`pr30:docs/pi-rpc-mode.md`), verificados de nuevo contra pi 1.0.0 (`pi@a13d35a`). La PR #30 se escribió contra pi 0.87.1 (`pr30:docs/pi-rpc-mode.md:15-16`); el lanzador de gentle-shell se niega a arrancar un pi anterior a 0.99.1 (`gentle-shell@ac67159:lib/gentle-shell-launcher.ts:392`) y gentle-shell 4.0.0 se desarrolla contra 1.0.0 (`gentle-shell@ac67159:package.json:95-97`).

### `RpcClient` (TypeScript)

`RpcClient` se distribuye con pi como cliente de referencia y lanza `node <cliPath> --mode rpc` (`pr30:docs/pi-rpc-mode.md:274-276`; `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-client.ts:94`). Sus límites conocidos (`pr30:docs/pi-rpc-mode.md:294-304`):

- Expone un único canal de oyentes, `onEvent`, sin eventos con nombre (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-client.ts:172`).
- Nunca responde a un `extension_ui_request`: el diálogo llega a los oyentes, así que una extensión a la espera de un diálogo se bloquea hasta su propio timeout (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-client.ts:523-542`).
- `bash()` no reenvía `excludeFromContext`, aunque el protocolo lo admite (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-client.ts:353`).
- `getData()` lanza una excepción si `success` es false (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-client.ts:608-610`); las líneas de stdout que no son JSON se ignoran, y las respuestas sin id llegan a los oyentes en lugar de a las peticiones pendientes (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-client.ts:523-542`).

### Advertencias de comandos, eventos y lanzamiento

- El modo RPC rechaza los argumentos de prompt `@file`; los prompts pasan por `prompt` (`pr30:docs/pi-rpc-mode.md:51-52`; `pi@a13d35a:packages/coding-agent/docs/rpc.md:20`).
- `get_commands` solo enumera comandos de extensión, plantillas de prompt y skills; los comandos TUI integrados como `/settings` ni se enumeran ni son ejecutables mediante `prompt` (`pr30:docs/pi-rpc-mode.md:179-181`; `pi@a13d35a:packages/coding-agent/src/modes/interactive/interactive-mode.ts:700-716`). Ver [inventory C12](05-capability-inventory.md#conversación-y-entrada).
- Emulación de Esc sobre RPC: lee el texto pendiente con `clear_queue`, envía `abort` y restaura el texto en el editor del cliente (`pr30:docs/pi-rpc-mode.md:170-171`).
- La salida de `bash` llega al modelo en el siguiente `prompt`, no de inmediato, salvo que se defina `excludeFromContext` (`pr30:docs/pi-rpc-mode.md:176-178`).
- RPC no emite ningún registro de cabecera de sesión; lee el id y el archivo de la sesión con `get_state` (`pr30:docs/pi-rpc-mode.md:185-187`). Ver [Eventos](#eventos-runtime--escritorio).
- `message_update.usage` es el último uso acumulado notificado por el proveedor y puede permanecer en cero hasta que se complete la respuesta (`pr30:docs/pi-rpc-mode.md:208-210`). Ver [`message_update` tipos de delta](#tipos-de-delta-de-message_update).
- La exportación de subruta `@earendil-works/pi-coding-agent/rpc-entry` es solo de importación: ejecuta `main(["--mode", "rpc", ...argv])` y define `process.title = "pi-rpc"`; el único ejecutable es `pi` y no existe un binario `pi-rpc` aparte (`pr30:docs/pi-rpc-mode.md:46-50`).
- Una respuesta correcta de `prompt` significa que el prompt se aceptó, se encoló o se gestionó, nunca que la ejecución haya terminado (`pr30:docs/pi-rpc-mode.md:99-105`). Desde pi 0.99.x también incluye `data.disposition` (`"started"`, `"queued"`, `"handled"`); el ejemplo de la PR #30 es anterior (ver [Diferencias entre pi 0.85.1 y 0.99.1 (comandos)](#diferencias-entre-pi-0851-y-0991-comandos)). Si `data.disposition` es `"handled"`, no se inició ninguna ejecución, así que no esperes a `agent_settled` (ver [semántica de `"handled"`](#diferencias-entre-pi-0851-y-0991-comandos)).

### Advertencias de la UI de extensiones

[Qué descarta el modo RPC](#qué-descarta-el-modo-rpc) enumera la mayoría de las llamadas `ctx.ui` degradadas; conviene conocer cuatro más (`pr30:docs/pi-rpc-mode.md:250-264`).

- `onTerminalInput()` devuelve una cancelación que no hace nada (`pr30:docs/pi-rpc-mode.md:258`).
- `getEditorComponent()` devuelve `undefined` (`pr30:docs/pi-rpc-mode.md:260`).
- `getToolsExpanded()` devuelve `false` (`pr30:docs/pi-rpc-mode.md:261`).
- `pasteToEditor()` se degrada a `setEditorText()` (`pr30:docs/pi-rpc-mode.md:262`).

`ctx.mode` es `"rpc"` mientras `ctx.hasUI` sigue siendo `true`, porque los diálogos y las notificaciones siguen funcionando; protege las funcionalidades exclusivas de la TUI con `ctx.mode === "tui"`, nunca con `hasUI` (`pr30:docs/pi-rpc-mode.md:266-268`).

### Lista de comprobación para un cliente nuevo

1. Lee con un lector binario/UTF-8 que solo divida en `LF`; nunca uses `readline`.
2. Lee stdout continuamente y reserva stderr para el diagnóstico.
3. Pon un `id` único en cada comando y correlaciona las respuestas por `id`, no por orden.
4. Suscríbete a los eventos antes del primer prompt.
5. Espera a `agent_settled`, no a `agent_end`, salvo que la respuesta de `prompt` traiga `data.disposition` `"handled"`.
6. Recompón el texto a partir de los deltas de `message_update` y confía en `message_end`.
7. Responde a cada diálogo que muestres o deja que expire por timeout.
8. Cierra stdin para apagar con orden y sigue gestionando señales y salidas inesperadas (`pr30:docs/pi-rpc-mode.md:343-352`).

### Cliente mínimo en Python

El cliente mínimo siguiente lanza `["pi", "--mode", "rpc", "--no-session"]`, escribe un comando JSON más un LF, recorre las líneas de stdout dividiendo solo en LF, imprime los deltas `text_delta`, termina con `agent_settled` y cierra stdin.
```python
import json, subprocess

process = subprocess.Popen(
    ["pi", "--mode", "rpc", "--no-session"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
)

process.stdin.write(json.dumps({"id": "p1", "type": "prompt", "message": "Hello"}).encode() + b"\n")
process.stdin.flush()

while line := process.stdout.readline():          # binary read: splits on LF only
    record = json.loads(line)
    if record.get("type") == "message_update":
        update = record["assistantMessageEvent"]
        if update["type"] == "text_delta":
            print(update["delta"], end="", flush=True)
    elif record.get("type") == "agent_settled":
        break

process.stdin.close()
process.wait()
```
El código del cliente es `pr30:docs/pi-rpc-mode.md:306-334`.

### Registros fuera de las uniones de tipos

`extension_error` se emite en stdout pero no está en las uniones de `rpc-types` (`pr30:docs/pi-rpc-mode.md:367-369`). Sí está documentado (`pi@a13d35a:packages/coding-agent/docs/json.md:190-194`) y lleva `extensionPath`, `event` y `error` cuando un manejador de extensión lanza una excepción (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-mode.ts:348-350`). Trata los valores de `type` desconocidos como ignorables, no como fatales. Ver [Eventos](#eventos-runtime--escritorio) y [Canales del host y de las extensiones](#canales-del-host-y-de-las-extensiones).

## Cómo proponer cambios del contrato en upstream

### pi (`earendil-works/pi`): responsable del protocolo RPC

`CONTRIBUTING.md` es idéntico en pi 0.85.1, 0.99.1 y 1.0.0 (`git diff --quiet d981de1 a13d35a -- CONTRIBUTING.md`). Lo que dice:

| Regla | Evidencia |
|---|---|
| El núcleo es mínimo. Las funcionalidades que no pertenecen al núcleo deberían ser extensiones, y los puntos de enganche de las extensiones deben estar "well considered and discussed". | `pi@a13d35a:CONTRIBUTING.md:7-11` |
| Las issues y PR de colaboradores nuevos se cierran automáticamente por defecto. Los mantenedores revisan a diario las **issues** cerradas automáticamente y reabren las que merecen la pena. | `pi@a13d35a:CONTRIBUTING.md:23`, `:27` |
| Las issues deben usar "one of the two GitHub issue templates", ser breves y estar escritas con voz propia. Nota: en realidad pi 0.85.1 y 1.0.0 (directorios idénticos) incluyen tres formularios de issue, `bug.yml`, `contribution.yml` y `package-report.yml`, más `config.yml`. | `pi@a13d35a:CONTRIBUTING.md:38-46`; `pi@a13d35a:.github/ISSUE_TEMPLATE/`, `pi@d981de1:.github/ISSUE_TEMPLATE/` |
| Ningún PR sin aprobación previa de un mantenedor (`lgtm`); `lgtmi` aprueba solo issues. | `pi@a13d35a:CONTRIBUTING.md:31-34`, `:58` |
| Antes de un PR: `npm run check` y `./test.sh`. No editar `CHANGELOG.md`. | `pi@a13d35a:CONTRIBUTING.md:62-69` |
| Los cambios de mayor envergadura se discuten como RFC en rfc.earendil.com. | `pi@a13d35a:CONTRIBUTING.md:101-102` |

La plantilla de propuesta es `Contribution Proposal`, con los campos "What do you want to change?", "Why?" y "How? (optional)" (`pi@a13d35a:.github/ISSUE_TEMPLATE/contribution.yml:1-36`). Las issues en blanco están deshabilitadas; las preguntas van a Discord (`pi@a13d35a:.github/ISSUE_TEMPLATE/config.yml:1-5`).

### gentle-shell (`Gentleman-Programming/gentle-shell`, paquete `gentle-pi`): responsable de los añadidos a nivel de extensión

- No existe `CONTRIBUTING.md` en `ac67159` (comprobado con `fd` a profundidad 3 el 2026-10-03).
- Formularios de issue: `bug_report.yml` y `feature_request.yml` (`gentle-shell@ac67159:.github/ISSUE_TEMPLATE/`). El formulario de funcionalidad pide "Problem or opportunity", "Proposed outcome", "Alternatives considered" y "Additional context", exige una búsqueda de duplicados y una comprobación de datos sensibles, y etiqueta las issues con `enhancement` y `status:needs-review` (`gentle-shell@ac67159:.github/ISSUE_TEMPLATE/feature_request.yml:1-43`).
- Ningún documento describe un proceso específico para cambios del contrato RPC o del host interactivo. El precedente existente es el propio documento del esquema de actividad (`gentle-shell@ac67159:docs/gentle-agents-activity.md`) y los prerrequisitos del hito M2 del escritorio que remiten a las issues #1328 y #1329 de gentle-shell (`gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m2-helpers.md:59`).
