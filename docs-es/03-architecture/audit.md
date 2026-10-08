> Traducción al español de `docs/03-architecture/audit.md` (árbol de trabajo tras la actualización del 2026-10-03). Documento de lectura; la versión de referencia es la inglesa.

# Auditoría de arquitectura

> Estado: borrador (draft).

Esta auditoría recoge 21 hallazgos sobre `gentle-shell-desktop@5ab4a00` (A20 y A21 se añadieron el 2026-10-03, ver [Hallazgos añadidos tras la actualización](#hallazgos-añadidos-tras-la-actualización)). Los cuatro más importantes son:

- El host de sesión única bloquea el uso de varios chats (A3).
- Windows no puede iniciar el proceso del lanzador en absoluto, según informa un tester en el issue #23 del escritorio (A4).
- Los datos reales de los helpers no coinciden con el parser del escritorio (A5).
- La lista de chats se ejecuta sobre una versión de pi distinta de la del propio chat (A1, A2).

[Recomendaciones y orden](#recomendaciones-y-orden) agrupa las correcciones. La arquitectura a la que se refieren estos hallazgos se describe en [current.md](current.md).

## Método y alcance

- **Fuentes.** Código fuente y documentación del escritorio en `gentle-shell-desktop@5ab4a00` (el código fuente en `docs/corpus` no ha cambiado), `gentle-shell@ac67159` (`main` de gentle-shell, versión de paquete 4.0.0), `pi@d981de1` (0.85.1) y `pi@a13d35a` (1.0.0); actualizado el 2026-10-03, con los issues #23–#25 del escritorio y las PR abiertas #26 y #27 leídos en GitHub ese día. `gentle-shell@1162ce9` (3.7.0) y `pi@d86654a` (0.99.1) aparecen solo en comparaciones de versiones. Los hallazgos de protocolo remiten a [04-rpc-contract.md](../04-rpc-contract.md). Los IDs de otras páginas llevan calificador (`gap G9`, `inventory C20`); M1–M6 sin calificador son los hitos del mantenedor, y los números T son tareas dentro de ellos.
- **Método.** Solo lectura estática. No se construyó, ejecutó ni instaló nada. El comportamiento derivado de la lectura del código se etiqueta como `Inference:` con "(no ejecutado)".
- **No cubierto.** Rendimiento de renderizado, accesibilidad (salvo el contraste del scrollbar en A21), tamaño de la aplicación empaquetada y una comparación línea por línea del parseo de sesiones de pi 0.85.1 y 0.99.1.

### Criterios de gravedad

| Gravedad | Criterio |
|---|---|
| **Alta** | Bloquea un objetivo de producto declarado (hitos del README, intención de la maqueta), o rompe un flujo principal para algunos usuarios en una plataforma configurada. |
| **Media** | Muestra al usuario datos erróneos o ausentes, o es un defecto latente con un desencadenante plausible, o la falta de una salvaguarda en un componente que la necesita (CI, comprobación de versión). |
| **Baja** | Mantenibilidad, desfase de la documentación, o un defecto con un desencadenante limitado o un efecto estético. Incluye carencias de endurecimiento sin ninguna vía de ataque identificada. |

## Hallazgos

### Resumen

| # | Hallazgo | Gravedad | Grupo |
|---|---|---|---|
| A1 | Dos caminos de datos hacia pi y una mutación global de `PI_CODING_AGENT_DIR` | Media | Varios chats |
| A2 | Desfase de versión de pi entre los dos caminos | Media | Corrección |
| A3 | Host de sesión única con ids de mensaje posicionales | Alta | Varios chats |
| A4 | Lanzador `.cmd` de Windows lanzado sin shell | Alta | Plataforma |
| A5 | El conjunto de estados de los helpers y los elementos de herramienta no coinciden con gentle-shell | Media | Corrección |
| A6 | El reducer descarta de la vista en vivo los mensajes que no son del asistente | Baja | Corrección |
| A7 | Prompts rechazados mientras el agente trabaja, pese a existir steer y follow-up | Media | Corrección |
| A8 | Sin handshake de versión | Media | Corrección |
| A9 | El aprovisionamiento del lanzador en el primer arranque no muestra progreso | Media | Plataforma |
| A10 | Los chats nuevos se ejecutan en el directorio de trabajo de la aplicación | Media | Corrección |
| A11 | Ciclo de vida de la lista de chats y de la selección | Media | Varios chats |
| A12 | Timeouts de los diálogos no modelados | Baja | Corrección |
| A13 | El hilo del chat anterior sigue visible durante el cambio | Baja | Corrección |
| A14 | Endurecimiento del preload y del IPC | Baja | Seguridad |
| A15 | Recurso silencioso al puente simulado en los builds empaquetados | Media | Corrección |
| A16 | Carencias de cobertura de tests y de CI | Media | Proceso |
| A17 | Desviación respecto a las reglas de estructura declaradas | Baja | Mantenibilidad |
| A18 | Descubrimiento del lanzador y cobertura de plataformas | Baja | Plataforma |
| A19 | Dos elecciones de home persistidas | Baja | Corrección |

### A1. Dos caminos de datos hacia pi y una mutación global de `PI_CODING_AGENT_DIR`

**Evidencia**
- La lista de chats importa pi en el mismo proceso: `gentle-shell-desktop@5ab4a00:src/main/adapters/piSessionStore.ts:30`.
- Ese adaptador establece `process.env.PI_CODING_AGENT_DIR`, espera a `SessionManager.listAll()` y después restaura el valor anterior (`:32-39`). Su comentario lo llama "a real, accepted M1 limitation" (`:22-25`).
- El chat pasa por la CLI lanzada: `gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:126-135`.
- El mismo objeto `process.env` alimenta otro código:
  - Entorno de `ChatHost`: `gentle-shell-desktop@5ab4a00:src/main/index.ts:64`.
  - `setupService` y `detectPi`: `gentle-shell-desktop@5ab4a00:src/main/adapters/setupService.ts:17`, `:22` y `gentle-shell-desktop@5ab4a00:src/main/domain/home/home.ts:45-47`.
- Dos llamadas a `listAll()` pueden solaparse. Cada `ChatHost.openChat` ejecuta una (`gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts:104`). La barra lateral ejecuta una al montarse (`gentle-shell-desktop@5ab4a00:src/renderer/features/chats/ChatsContainer.tsx:29-44`). El `StrictMode` de React ejecuta dos veces los efectos de montaje en desarrollo (`gentle-shell-desktop@5ab4a00:src/renderer/main.tsx:13`).

**Impacto**
- El escritorio depende de la API de la biblioteca de pi y de su estructura en disco además del contrato RPC, de modo que el contrato RPC por sí solo no describe el acoplamiento del escritorio con pi.
- `Inference:` (no ejecutado) dos llamadas solapadas pueden dejar la variable establecida de forma permanente. La llamada A guarda `undefined`. La llamada B guarda el valor de A. Después A borra la variable y B restaura el valor de A. Una vez filtrado, `detectPi` y el directorio `link` se resuelven al home listado en lugar de al directorio real de pi del usuario. Todos los lanzamientos posteriores heredan también el valor filtrado. El lanzador lo sobrescribe para el propio pi (`gentle-shell@ac67159:lib/gentle-shell-launcher.ts:960`), pero desde 4.0.0 deriva `GENTLE_SHELL_USER_PI_HOME` del `PI_CODING_AGENT_DIR` heredado cuando no se hereda ningún `GENTLE_SHELL_USER_PI_HOME` (`:197-205`, `:962`), así que `/gentle:stats` leería entonces el home listado como el home de pi del usuario.
- Ejecutar varios chats o homes a la vez convertiría esta condición de carrera en algo habitual.

**Gravedad:** Media. Un defecto latente con un desencadenante plausible; el impacto es limitado mientras solo haya un home.

**Recomendación:** Hacer una de las siguientes cosas:
- Trasladar el listado de sesiones detrás del hijo RPC (pi no tiene hoy un comando de listado; ver la [tabla de comandos](../04-rpc-contract.md#comandos-escritorio--runtime)).
- Leer el directorio de sesiones sin mutar el entorno, por ejemplo enumerando `<home>/sessions/*/` y llamando a la sobrecarga `listAll(sessionDir)` por cada subdirectorio (`gentle-shell-desktop@5ab4a00:src/main/adapters/piSessionStore.ts:10-17`).
- Como mínimo, serializar las llamadas a `listAll()`.

### A2. Desfase de versión de pi entre los dos caminos

**Evidencia**
- El escritorio depende de pi `^0.85.1`, bloqueado en 0.85.1: `gentle-shell-desktop@5ab4a00:package.json:42`, `gentle-shell-desktop@5ab4a00:pnpm-lock.yaml:323`.
- El peer RPC es como mínimo 0.99.1, y gentle-shell 4.0.0 se desarrolla contra ≥ 1.0.0: `gentle-shell@ac67159:lib/gentle-shell-launcher.ts:392`, `gentle-shell@ac67159:package.json:78`, `:95`. El desfase es ahora 0.85.1 frente a ≥ 0.99.1, con 1.0.0 como objetivo de desarrollo.
- La versión del formato de sesión es 3 en las tres: `pi@d981de1:packages/coding-agent/src/core/session-manager.ts:30`, `pi@a13d35a:packages/coding-agent/src/core/session-manager.ts:41` (idéntico byte a byte en 0.99.1).
- El pi incluido trae scripts de instalación transitivos: `gentle-shell-desktop@5ab4a00:pnpm-workspace.yaml:1-10`.

**Impacto**
- La barra lateral lee con un parser más antiguo las sesiones escritas por un pi más reciente.
- `UNVERIFIED:` no se comprobó si las cabeceras o entradas de sesión de 0.99.1 o 1.0.0 rompen el `listAll()` de 0.85.1. La igualdad de la versión del formato reduce el riesgo, pero no lo elimina.
- `Inference:` la aplicación empaquetada también distribuye una biblioteca de pi completa solo para listar sesiones.

**Gravedad:** Media. Un defecto latente cuyo desencadenante es cualquier cambio futuro del formato de sesión.

**Recomendación:** Eliminar el camino en el mismo proceso (ver A1). Si se mantiene, fijar el pi del escritorio a la misma versión menor que el mínimo de gentle-shell y añadir un test con fixture que liste archivos de sesión escritos por pi 0.99.1 y 1.0.0.

### A3. Host de sesión única con ids de mensaje posicionales

**Evidencia**
- Una sesión a la vez:
  - `ChatHost` mantiene una única sesión `current` y la detiene antes de iniciar otra: `gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts:61-70`, `:156-157`.
  - `ChatState` y el envío `chat.state` no llevan id de chat: `gentle-shell-desktop@5ab4a00:src/shared/bridge-types.ts:122-129`, `gentle-shell-desktop@5ab4a00:src/main/ipc/registerHandlers.ts:39`.
  - El puente envía a "whichever chat is currently open": `gentle-shell-desktop@5ab4a00:src/shared/bridge-types.ts:279-282`.
- Ids posicionales:
  - Los ids de mensaje son `msg-<array length>`: `gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:334`, `gentle-shell-desktop@5ab4a00:src/main/domain/rpc/chatReducer.ts:85`, `gentle-shell-desktop@5ab4a00:src/main/domain/rpc/history.ts:20-48`.
  - Descartar un mensaje vacío del asistente cede su id al mensaje siguiente: `gentle-shell-desktop@5ab4a00:src/main/domain/rpc/chatReducer.ts:133-138`.
- Estado en la barra lateral:
  - Todos los chats listados están en `idle`: `gentle-shell-desktop@5ab4a00:src/main/domain/session/sessionList.ts:20-22`, `:35`.

**Impacto**
- No se pueden construir los estados de la barra lateral de la maqueta ("working", "needs you") ni las notificaciones sobre otros chats ([gap G9](../04-rpc-contract.md#carencias-que-necesita-el-escritorio)).
- Los ids no están ligados a los ids de entrada de pi, así que nada puede anclar los helpers bajo un mensaje, bifurcar ni sobrevivir a una recarga. `Inference:` los ids reutilizados pueden hacer que React reutilice un componente para un mensaje distinto.

**Gravedad:** Alta. Bloquea un objetivo de producto declarado (chats concurrentes en la maqueta).

**Recomendación**
1. Introducir un registro de sesiones indexado por el id de sesión de pi: un `PiSession` por cada chat abierto, como permite el protocolo ([gap G9](../04-rpc-contract.md#carencias-que-necesita-el-escritorio)).
2. Añadir un `chatId` a cada envío y a cada comando.
3. Derivar el estado de cada chat a partir del estado de su sesión.
4. Tomar los ids de mensaje de pi (ids de entrada mediante `get_entries`/`entry_appended`, o la propia identidad del mensaje) en lugar de posiciones en el array.

### A4. Lanzador `.cmd` de Windows lanzado sin shell

**Evidencia**
- En win32 el localizador elige primero `gentle-shell.cmd`: `gentle-shell-desktop@5ab4a00:src/main/adapters/launcherLocator.ts:48`.
- El lanzador de procesos llama a `spawn` sin la opción `shell`: `gentle-shell-desktop@5ab4a00:src/main/adapters/nodeProcessSpawner.ts:10`.
- gentle-shell documenta el mismo fallo para su propio lanzamiento de pi ("Current Node releases refuse to spawn a batch file directly without `shell: true` (EINVAL)") y encamina `.cmd`/`.bat` a través de `cmd.exe` con entrecomillado explícito, sin cambios en 4.0.0: `gentle-shell@ac67159:lib/gentle-shell-launcher.ts:969-1019`. Su propio lanzamiento de pi no pasa `windowsHide` (`gentle-shell@ac67159:bin/gentle-shell.mjs:1396`).

**Impacto:** en Windows con un lanzador instalado mediante npm, todos los lanzamientos fallan, así que no puede arrancar ningún chat. El issue #23 del escritorio (Mayloparra24, 2026-09-26, abierto) informa de ello con pasos de reproducción en gentle-pi 3.7.0 y "Pi version 0.87.1": `spawn EFTYPE`, "on some Node versions `spawn EINVAL`"; apuntar `GENTLE_SHELL_BIN` al `bin/gentle-shell.mjs` del paquete permite sortearlo. `Inference:` la versión de pi informada es cuestionable: 0.87.1 está por debajo del `MIN_PI_VERSION = "0.99.1"` del lanzador en 3.7.0 y en `main` (`gentle-shell@1162ce9:lib/gentle-shell-launcher.ts:382`; `gentle-shell@ac67159:lib/gentle-shell-launcher.ts:392`), así que probablemente no es el pi que resuelve el lanzador. El issue #24 (mismo autor, abierto) informa de una ventana de consola visible por cada chat abierto y señala que "may belong to the grandchild `pi` process"; `UNVERIFIED:` qué proceso es el propietario de la ventana. **No reproducido por los autores del corpus.**

**Gravedad:** Alta. Rompe el flujo principal en una plataforma configurada (`gentle-shell-desktop@5ab4a00:electron-builder.yml:31-34`).

**Recomendación:** Replicar el `planSpawn` de gentle-shell en `nodeProcessSpawner` o en el localizador. Para `.cmd`/`.bat` en win32, ejecutar a través de `cmd.exe` con los tokens entrecomillados. Probar unitariamente el plan con `platform` inyectado. Reproducir en Windows antes y después de la corrección. La PR abierta #26 (head `615dd87`, sin fusionar a fecha de 2026-10-03; cierra #23 y #24) siempre establece `windowsHide: true` y establece `shell: true` en win32 cuando el comando termina en `.cmd`/`.bat`, pero pasa el comando y los argumentos sin entrecomillar, a diferencia de `planSpawn`; los argumentos del escritorio incluyen rutas (`--session <path>`, y `--home <dir>` cuando `GENTLE_SHELL_HOME` está establecida: `gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:127-133`, `gentle-shell-desktop@5ab4a00:src/main/domain/home/home.ts:33-36`), y el localizador devuelve una ruta sin entrecomillar (`gentle-shell-desktop@5ab4a00:src/main/adapters/launcherLocator.ts:53-54`). `Inference:` (no ejecutado) `cmd.exe` dividiría o interpretaría una ruta con espacios o metacaracteres de `cmd.exe`. Detalles: [10-platforms.md](../10-platforms.md#lanzamiento-de-shims-por-lotes).

### A5. El conjunto de estados de los helpers y los elementos de herramienta no coinciden con gentle-shell

**Evidencia**
- Los estados de tarea de gentle-shell son `queued`, `running`, `waiting`, `completed`, `failed`, `cancelled`, `timed_out`: `gentle-shell@ac67159:lib/agents-protocol.ts:9-17`. Los archivos de actividad (`lib/agents-protocol.ts`, `lib/agents-rpc-publisher.ts`, `docs/gentle-agents-activity.md`) son idénticos byte a byte entre 3.7.0 (`1162ce9`) y `ac67159`, así que este hallazgo sigue siendo válido tal como está redactado.
- El escritorio acepta `queued`, `running`, `waiting`, `done`, `failed`, `cancelled`, y `toTask` descarta una tarea con cualquier otro estado: `gentle-shell-desktop@5ab4a00:src/main/domain/rpc/helpersActivity.ts:21`, `:83-85`, `:139-141`.
- Los elementos de herramienta del hilo de gentle-shell no tienen `callId` (`gentle-shell@ac67159:lib/agents-rpc-publisher.ts:96-105`). El escritorio lo exige (`gentle-shell-desktop@5ab4a00:src/main/domain/rpc/helpersActivity.ts:107-108`) y lo usa como key de React (`gentle-shell-desktop@5ab4a00:src/renderer/features/helpers/components/HelperThread.tsx:24`).
- El fixture usa `done` e incluye `callId` (`gentle-shell-desktop@5ab4a00:src/main/domain/rpc/__fixtures__/helpers-activity.jsonl:2`, `:4`). El puente simulado también (`gentle-shell-desktop@5ab4a00:src/renderer/shared/bridge/mockBridge.ts:359`).

**Impacto:** `Inference:` (no ejecutado):
- **Las filas de herramientas nunca aparecen.** Todos los elementos reales de herramienta se descartan del hilo de Helpers.
- **Estado final erróneo.** Una tarea vista mientras está en ejecución y enviada después como `completed` o `timed_out` se descarta de la trama, así que la fusión de retención conserva su último registro y convierte `running` en `done` (`gentle-shell-desktop@5ab4a00:src/main/domain/rpc/chatReducer.ts:225-240`). `completed` acaba siendo correcto por casualidad; un timeout se muestra como terminado. `failed` y `cancelled` se aceptan y se muestran correctamente.
- **Helpers ausentes.** Una tarea vista por primera vez ya en `completed` o `timed_out`, por ejemplo tras abrir un chat, se descarta.

Esto precisa la [observación 6 de 04-rpc-contract.md](../04-rpc-contract.md#observaciones-de-compatibilidad): la fusión de retención oculta parte de la pérdida.

**Gravedad:** Media. Se muestran al usuario datos erróneos o ausentes.

**Recomendación:** Aceptar el conjunto de estados de gentle-shell, mapeando `completed` a terminado y manteniendo `timed_out` diferenciado. Hacer opcional `callId` e usar el índice como key de React de los elementos de herramienta. Regenerar el fixture a partir de una salida real de `gentle-agents.activity/v1`.

### A6. El reducer descarta de la vista en vivo los mensajes que no son del asistente

**Evidencia**
- `message_start` y `message_end` se ignoran salvo que `role === "assistant"`: `gentle-shell-desktop@5ab4a00:src/main/domain/rpc/chatReducer.ts:81-82`, `:115-116`.
- Los mensajes del usuario aparecen en vivo solo porque `PiSession.prompt` los añade localmente: `gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:182`.
- El historial conserva los mensajes del usuario y del asistente: `gentle-shell-desktop@5ab4a00:src/main/domain/rpc/history.ts:36-50`.
- pi 0.99.1 añade un rol `system` ([04-rpc-contract.md](../04-rpc-contract.md#diferencias-entre-pi-0851-y-0991-eventos)). Desde gentle-shell 4.0.0, el resultado de un helper para un padre inactivo se guarda como un mensaje personalizado sin turno y después el padre se despierta con un mensaje con rol de usuario, "[System-generated Gentle Agents notification, not written by the user] …" (`gentle-shell@ac67159:extensions/gentle-agents.ts:63-65`, `:691`, `:698-706`; [inventory A7](../05-capability-inventory.md#helpers-subagentes)).

**Impacto:** Los mensajes del usuario que no proceden del compositor solo aparecen tras una recarga, así que el hilo en vivo y el hilo recargado pueden diferir. Ejemplos son los mensajes inyectados por extensiones o entregados desde una cola de steer o follow-up. `Inference:` (no ejecutado) con gentle-shell 4.0.0 el despertar del padre inactivo es uno de esos mensajes: ocurre siempre que un helper termina mientras el chat está inactivo, la vista en vivo lo oculta y, tras una recarga, aparece como una burbuja de usuario sin el resultado del helper. Ocultar las herramientas y el razonamiento es intencionado ([ADR 0007](adr/0007-text-only-chat-view.md)); ocultar estos mensajes es un efecto secundario.

**Gravedad:** Baja hoy, sin cambios por el despertar de 4.0.0: su efecto visible solo aparece tras una recarga, y el texto se identifica a sí mismo como generado por el sistema. Sube a Media en cuanto el escritorio envíe `steer` o `follow_up` (A7).

**Recomendación:** Construir el hilo a partir de los eventos de mensaje de pi para cada rol que muestra la vista, en lugar de añadir localmente, y conciliar por identidad del mensaje (A3).

### A7. Prompts rechazados mientras el agente trabaja, pese a existir steer y follow-up

**Evidencia**
- `PiSession.prompt` devuelve `{queued:false, reason:"Gentle is still working"}` mientras está en `working`: `gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:168-180`.
- El compositor bloquea los envíos mientras está en `working`: `gentle-shell-desktop@5ab4a00:src/renderer/features/conversation/ConversationContainer.tsx:99`.
- `RpcCommand` no tiene `streamingBehavior`, `steer` ni `follow_up`: `gentle-shell-desktop@5ab4a00:src/main/domain/rpc/types.ts:27-41`.
- pi admite ambos, y ejecuta los comandos de extensión inmediatamente incluso durante el streaming: `pi@a13d35a:packages/coding-agent/docs/rpc-commands.md:27-31`.
- `working` se borra en `agent_end` incluso cuando va a seguir un reintento: `gentle-shell-desktop@5ab4a00:src/main/domain/rpc/chatReducer.ts:56-58` ([observación 3](../04-rpc-contract.md#observaciones-de-compatibilidad)).

**Impacto**
- Los usuarios no pueden redirigir (steer) un agente en ejecución ni encolar un mensaje de seguimiento (follow-up).
- Los comandos `/gentle:*` quedan bloqueados mientras el agente trabaja.
- `Inference:` (no ejecutado) durante un reintento automático el compositor se vuelve a habilitar, y un prompt enviado en ese momento es rechazado por pi con un error.

**Gravedad:** Media. Falta una interacción principal y hay una vía de error plausible.

**Recomendación:** Enviar `prompt` con `streamingBehavior` (o `steer`/`follow_up`) mientras el agente trabaja, y dejar pasar siempre los comandos de extensión. Borrar `working` solo en `agent_settled`. Leer `queue_update` para mostrar lo que está encolado.

### A8. Sin handshake de versión

**Evidencia**
- `src/main` nunca ejecuta `--version` ni compara versiones. El único texto de versión es un mensaje de error: `gentle-shell-desktop@5ab4a00:src/main/adapters/launcherLocator.ts:26-28`.
- El protocolo no tiene campo de versión ([04-rpc-contract.md: Versionado](../04-rpc-contract.md#hay-un-handshake-de-versión)).

**Impacto:** Un gentle-pi más antiguo se degrada en silencio. Por ejemplo, la pestaña Helpers se queda vacía sin 3.7.0 (`gentle-shell-desktop@5ab4a00:README.md:89-91`). Los problemas de desfase (A2, A5) solo se detectan por sus síntomas.

**Gravedad:** Media. Falta una salvaguarda en una frontera entre repositorios.

**Recomendación:** Ejecutar `gentle-shell --version` una vez por arranque (`gentle-shell@ac67159:bin/gentle-shell.mjs:1217-1219`), mostrar las versiones y avisar por debajo de un mínimo. A más largo plazo, proponer en upstream un registro de capacidades versionado ([gap G10](../04-rpc-contract.md#carencias-que-necesita-el-escritorio)).

### A9. El aprovisionamiento del lanzador en el primer arranque no muestra progreso

**Evidencia**
- En el primer arranque con un home aislado o `--home`, el lanzador instala los paquetes complementarios de gentle-ai antes de arrancar pi, todavía en `ac67159`: `gentle-shell@ac67159:bin/gentle-shell.mjs:1114-1140`, `:1265-1268`.
- El progreso solo va a stderr: `:819`, `:1139-1140`, `:1160`.
- Cada hijo puede tardar hasta 15 minutos: `:1089`.
- El escritorio registra el stderr del hijo en su propia consola y nunca lo muestra: `gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:292-295`, `gentle-shell-desktop@5ab4a00:src/main/index.ts:42-44`.
- `isolated` es el valor por defecto cuando no se encuentra pi: `gentle-shell-desktop@5ab4a00:src/main/domain/home/home.ts:17-19`, `gentle-shell-desktop@5ab4a00:src/main/adapters/setupService.ts:24`.
- La aplicación lanza un chat nuevo en cuanto se abre: `gentle-shell-desktop@5ab4a00:src/renderer/app/App.tsx:9`, `:35`.
- Cambiar de chat detiene al hijo tras 3 s: `gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:57`, `:213-235`.

**Impacto:** `Inference:` (no ejecutado):
- Un usuario nuevo sin pi ve un chat inactivo durante minutos, sin señal de que se esté trabajando.
- Un prompt enviado mientras tanto espera en la tubería de stdin.
- Cambiar de chat durante el aprovisionamiento mata al lanzador. Este trata la señal como una interrupción y lo reintenta en la siguiente ejecución (`gentle-shell@ac67159:bin/gentle-shell.mjs:1102-1113`).

**Gravedad:** Media. Una primera experiencia degradada en el camino por defecto.

**Recomendación:** Ejecutar `gentle-shell setup` (o un equivalente) como un paso visible en la pantalla de primer arranque, o mostrar las líneas de stderr del lanzador mientras no haya llegado todavía ningún registro RPC. No lanzar automáticamente un chat antes de que el usuario actúe.

### A10. Los chats nuevos se ejecutan en el directorio de trabajo de la aplicación

**Evidencia**
- `PiSession` admite `cwd` (`gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:15`, `:135`), pero `ChatHost` nunca lo pasa (`gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts:159-166`).
- El lanzador de procesos hereda entonces el directorio de trabajo del proceso de Electron (`gentle-shell-desktop@5ab4a00:src/main/adapters/nodeProcessSpawner.ts:10`), y el lanzador también (`gentle-shell@ac67159:bin/gentle-shell.mjs:1396`).
- pi crea una sesión nueva en `process.cwd()`: `pi@a13d35a:packages/coding-agent/src/main.ts:448`, `:591`, `:693`.
- pi reabre una sesión en el cwd de su cabecera: `pi@a13d35a:packages/coding-agent/src/core/session-manager.ts:1782`.

**Impacto:** Los chats nuevos trabajan en el directorio desde el que se haya arrancado la aplicación, sea cual sea. No hay forma de elegir una carpeta de proyecto. La barra de estado de la maqueta muestra un cwd ([gap G7](../04-rpc-contract.md#carencias-que-necesita-el-escritorio)). `UNVERIFIED:` no se comprobó el directorio de trabajo de una aplicación de macOS lanzada desde Finder.

**Gravedad:** Media. Contexto erróneo para las operaciones de archivos y herramientas del agente.

**Recomendación:** Añadir a "New chat" la elección de una carpeta de proyecto y pasarla como `cwd`. Mostrar el cwd de cada chat (`ChatSummary.cwd` ya existe, `gentle-shell-desktop@5ab4a00:src/shared/bridge-types.ts:26-27`).

### A11. Ciclo de vida de la lista de chats y de la selección

**Evidencia**
- **La barra lateral se carga una sola vez.** Llama a `listChats()` al montarse y nunca más: `gentle-shell-desktop@5ab4a00:src/renderer/features/chats/ChatsContainer.tsx:29-44`.
- **"New chat" puede no hacer nada.** La selección de chat nuevo es una única constante, `NEW_CHAT`, y "New chat" la vuelve a establecer (`gentle-shell-desktop@5ab4a00:src/renderer/app/App.tsx:9`, `:58-60`). El efecto de apertura depende de ese objeto (`gentle-shell-desktop@5ab4a00:src/renderer/features/conversation/ConversationContainer.tsx:81-95`).
- **Un chat arranca al iniciar la aplicación.** `App` selecciona un chat nuevo al montarse (`gentle-shell-desktop@5ab4a00:src/renderer/app/App.tsx:35`).

**Impacto:** `Inference:` (no ejecutado):
- Los chats creados en la aplicación nunca aparecen en la barra lateral hasta un reinicio.
- Pulsar "New chat" mientras hay un chat nuevo abierto no hace nada, porque React omite una actualización al mismo valor de estado, así que no se puede iniciar un segundo chat nuevo sin abrir antes otro chat.
- Cada arranque lanza un hijo, aunque solo sea para navegar.

**Gravedad:** Media. Datos erróneos o ausentes en la barra lateral.

**Recomendación:** Refrescar la lista tras `newChat` y tras cada turno completado (o enviar los cambios de la lista desde el proceso principal). Crear un objeto de selección nuevo (o un contador) por cada clic en "New chat". Lanzar el proceso en el primer envío en lugar de al montarse.

### A12. Timeouts de los diálogos no modelados

**Evidencia**
- El códec decodifica `timeout` (`gentle-shell-desktop@5ab4a00:src/main/domain/rpc/codec.ts:161`, `:172`, `:183`), pero el reducer y el tipo `Dialog` lo descartan: `gentle-shell-desktop@5ab4a00:src/main/domain/rpc/chatReducer.ts:167-179`, `gentle-shell-desktop@5ab4a00:src/shared/bridge-types.ts:70-82`.
- pi resuelve por su cuenta un diálogo que ha agotado su tiempo (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-mode.ts:115-120`) y descarta en silencio una respuesta tardía ([Correlación y errores](../04-rpc-contract.md#correlación-y-errores)).

**Impacto:** `Inference:` (no ejecutado) la tarjeta sigue en pantalla después de que pi haya pasado a otra cosa, y la respuesta del usuario se ignora sin ninguna indicación.

**Gravedad:** Baja. Un desencadenante limitado: solo los diálogos que establecen un timeout.

**Recomendación:** Llevar `timeout` a `Dialog`, mostrar una cuenta atrás y retirar la tarjeta cuando expire.

### A13. El hilo del chat anterior sigue visible durante el cambio

**Evidencia**
- La sesión antigua se detiene por completo antes de construir la nueva. `performStart` espera primero a `this.current?.stop()`: `gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts:156-159`.
- `stop()` espera a `exited`, o mata el proceso tras un periodo de gracia de 3 s y vuelve a esperar: `gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.ts:57`, `:213-235`.
- `exited` se resuelve con el evento `'close'` del hijo (`gentle-shell-desktop@5ab4a00:src/main/adapters/nodeProcessSpawner.ts:33-42`). Node emite `'close'` después de que se hayan cerrado los flujos de stdio del hijo (https://nodejs.org/api/child_process.html#event-close). Las líneas de stdout se procesan de forma síncrona en `data` y `end` (`gentle-shell-desktop@5ab4a00:src/main/adapters/nodeProcessSpawner.ts:74-88`). Por tanto, no llega ningún evento de stdout del hijo antiguo después de que `stop()` se resuelva.
- `ChatHost` nunca desvincula los listeners `state` y `error` de la sesión antigua (`gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts:167-168`), pero después de que `stop()` se resuelva al hijo antiguo no le queda salida que emitir.
- El renderer no restablece el hilo en un cambio. El efecto de apertura solo borra el error del puente y sustituye `chatState` cuando se resuelve la llamada de apertura: `gentle-shell-desktop@5ab4a00:src/renderer/features/conversation/ConversationContainer.tsx:81-95`. El título de la cabecera sigue a la nueva selección de inmediato (`:118`).
- La llamada de apertura se resuelve después de la parada antigua, la búsqueda con `listAll()` para un chat existente, el lanzamiento y, para un chat existente, la carga del historial: `gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts:103-107`, `:172-184`.

**Impacto:** `Inference:` (no ejecutado) tras hacer clic en otro chat, los mensajes del chat anterior siguen en pantalla bajo el título del chat nuevo hasta que la nueva sesión envía un estado o se resuelve la llamada de apertura. Los envíos de la sesión antigua durante su parada siguen actualizando esa vista obsoleta (`gentle-shell-desktop@5ab4a00:src/renderer/features/conversation/ConversationContainer.tsx:60-67`). Un evento tardío de la sesión antigua no puede sobrescribir el estado del chat nuevo, porque la nueva sesión no existe hasta que la antigua se ha detenido.

**Gravedad:** Baja. Estética y transitoria: se muestra el hilo equivocado, pero no se mezcla estado entre chats.

**Recomendación:** Restablecer `chatState` (o mostrar un estado de carga) cuando cambie `activeChat`. Etiquetar los envíos con un id de chat cuando llegue el soporte de varios chats (A3).

### A14. Endurecimiento del preload y del IPC

**Evidencia**
- `sandbox: false` (sandbox del sistema operativo de Chromium desactivado, distinto de `contextIsolation`, que solo separa el renderer del contexto del preload/Node): `gentle-shell-desktop@5ab4a00:src/main/index.ts:85`.
- Los handlers de IPC usan los argumentos del renderer tal cual, sin comprobaciones de tipo ni comprobación del emisor: `gentle-shell-desktop@5ab4a00:src/main/ipc/registerHandlers.ts:28-37`.
- La CSP de producción permite `'unsafe-eval'` y carga las fuentes desde Google en tiempo de ejecución: `gentle-shell-desktop@5ab4a00:src/renderer/index.html:5-16`.
- No existe ninguna protección `will-navigate` (buscar `will-navigate` en `src/` no devuelve nada).
- Mitigaciones existentes:
  - `contextIsolation: true` y `nodeIntegration: false` (aislamiento del renderer respecto a Node a través del puente del preload, no el sandbox del sistema operativo de Chromium): `gentle-shell-desktop@5ab4a00:src/main/index.ts:83-84`.
  - Se deniegan todas las ventanas nuevas: `:97-102`.
  - El Markdown se sanea con DOMPurify: `gentle-shell-desktop@5ab4a00:src/renderer/shared/markdown/renderMarkdown.ts:58-72`.

**Impacto:** No se identificó ninguna vía de ataque, pero el renderer muestra la salida del modelo y el puente llega a un proceso que ejecuta herramientas. La defensa en profundidad es escasa. Un arranque sin conexión también pierde las fuentes.

**Gravedad:** Baja. Ninguna vía de ataque identificada.

**Recomendación:**
- Validar los argumentos de IPC en `registerHandlers`.
- Habilitar el sandbox. `UNVERIFIED:` no se comprobó con la documentación de Electron si el preload ESM (`preload/index.mjs`, `gentle-shell-desktop@5ab4a00:src/main/index.ts:82`) lo impide.
- Eliminar `'unsafe-eval'` de la CSP de producción e incluir las fuentes en el bundle.
- Añadir un handler `will-navigate` que deniegue la navegación.

### A15. Recurso silencioso al puente simulado en los builds empaquetados

**Evidencia**
- `useBridge()` devuelve el simulado siempre que falta `window.gentle`, sin comprobar el entorno: `gentle-shell-desktop@5ab4a00:src/renderer/shared/bridge/useBridge.ts:10-12`.
- La comprobación de smoke pasa si el body contiene "Chats", que la UI simulada también renderiza: `gentle-shell-desktop@5ab4a00:scripts/smoke-electron.mjs:39-56`.
- M1 ya sufrió un fallo del preload que dejó una ventana en blanco: `gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m1-chat-core.md:56`.

**Impacto:** `Inference:` (no ejecutado) si el preload falla en un build empaquetado, el usuario ve chats falsos y respuestas falsas en streaming en lugar de un error, y la comprobación de smoke sigue pasando.

**Gravedad:** Media. Muestra datos erróneos sin ninguna señal.

**Recomendación:** Usar el simulado solo en el build `dev:web` (por ejemplo, tras un flag de `import.meta.env`). Mostrar un error explícito cuando falte el puente en Electron. Hacer que la comprobación de smoke verifique que existe `window.gentle`.

### A16. Carencias de cobertura de tests y de CI

**Evidencia**
- **Sin CI.** `.github/` solo contiene plantillas de issues (listado de archivos en `5ab4a00`).
- **Fixtures que no proceden de una salida real.** Codifican las suposiciones del escritorio, no la salida de gentle-shell (A5).
- **Sin tests para:**
  - la raíz de composición y el camino de salida: `src/main/index.ts`;
  - los caminos de Windows en `launcherLocator`;
  - `HelpersSummary`: no se encontró ningún archivo de test dedicado ni ninguna aserción sobre su texto; solo se renderiza dentro de `HelpersContainer.test.tsx`.

  Esta lista procede de un escaneo de tests hermanos con `fd`, seguido de una búsqueda en los tests de los padres.
- **Sin archivo de test dedicado, pero cubiertos a través de los padres:**
  - `ChatListItem`, por `gentle-shell-desktop@5ab4a00:src/renderer/features/chats/components/ChatList.test.tsx:22-53`;
  - `HelperListItem`, por `gentle-shell-desktop@5ab4a00:src/renderer/features/helpers/components/HelperList.test.tsx`;
  - `HelperThreadItem`, por `gentle-shell-desktop@5ab4a00:src/renderer/features/helpers/components/HelperThread.test.tsx`;
  - `HelpersFooter` (Back to chat, Show tool details, Stop deshabilitado), por `gentle-shell-desktop@5ab4a00:src/renderer/features/helpers/HelpersContainer.test.tsx:93-131`;
  - `HelpersStrip`, por `gentle-shell-desktop@5ab4a00:src/renderer/features/conversation/ConversationContainer.test.tsx:264`;
  - los átomos (`Button`, `Pill`, `TextField`), renderizados por los componentes que los usan;
  - `nodeProcessSpawner`, por `gentle-shell-desktop@5ab4a00:src/main/domain/session/PiSession.test.ts:130-140`.
- **Ningún test automatizado se ejecuta contra un gentle-shell real.** Al cierre de M1 el chat real no se había ejercitado en absoluto: `gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m1-chat-core.md:65`. M2 registró más tarde ejecuciones manuales de extremo a extremo contra un pi real, incluido el home real del mantenedor (`gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m2-helpers.md:57`, `:64`). Esas ejecuciones no forman parte de la batería de tests.

**Impacto:** Las regresiones llegan a `main` sin comprobar. El desfase del contrato con gentle-shell pasa los tests (A5).

**Gravedad:** Media. Falta una salvaguarda.

**Recomendación:** Añadir un workflow de CI (`pnpm test`, `pnpm typecheck`, `pnpm build` y `smoke:electron` bajo xvfb en Linux), con un job de Windows una vez corregido A4. Grabar los fixtures a partir de una ejecución real de gentle-shell. Añadir un test de contrato que cargue el ejemplo de actividad publicado por gentle-shell.

### A17. Desviación respecto a las reglas de estructura declaradas

**Evidencia**
- **Imports de Node en el dominio.** `src/main/domain/home/home.ts` importa `node:fs`, `node:os` y `node:path` (`gentle-shell-desktop@5ab4a00:src/main/domain/home/home.ts:1-3`), pese a "no Electron or Node imports allowed here" (`gentle-shell-desktop@5ab4a00:src/main/domain/index.ts:1-4`). `src/README.md` enuncia la regla más estrecha de que el dominio se mantenga "free of Electron imports" (`gentle-shell-desktop@5ab4a00:src/README.md:45-51`), que `home.ts` no incumple.
- **Un módulo compartido con un solo consumidor.** `renderer/shared/markdown` tiene un solo consumidor (`MessageBubble`) y se justifica por un uso "later" en los helpers (`gentle-shell-desktop@5ab4a00:src/renderer/shared/markdown/Markdown.tsx:11-14`). `src/README.md:34-35` dice "Nothing moves there speculatively".
- **Una nota que no existe.** `App.tsx` cita una nota "Selected chat" en el documento de M1 (`gentle-shell-desktop@5ab4a00:src/renderer/app/App.tsx:21-23`). Esa nota no está en `odd/tasks/desktop-m1-chat-core.md`. `ConversationContainer.tsx` cita el documento de M1 en general para "no global store for M1" (`gentle-shell-desktop@5ab4a00:src/renderer/features/conversation/ConversationContainer.tsx:13-14`), y tampoco se encontró allí tal afirmación.
- **Un marcador de posición obsoleto.** `SessionPlaceholder` y su comentario "placeholder for T3" siguen presentes: `gentle-shell-desktop@5ab4a00:src/main/domain/index.ts:8-9`, `:16-18`.

**Impacto:** Pequeño, pero estas reglas son las que se pide seguir a quienes contribuyen.

**Gravedad:** Baja.

**Recomendación:** Trasladar las búsquedas de `fs`/`homedir` detrás de un puerto o a un adaptador. O bien trasladar Markdown a `conversation`, o bien registrar la excepción. Corregir la referencia colgante. Eliminar el marcador de posición.

### A18. Descubrimiento del lanzador y cobertura de plataformas

**Evidencia**
- Las aplicaciones abiertas desde Finder no tienen el `PATH` de la shell, así que no se encuentra el lanzador: `gentle-shell-desktop@5ab4a00:README.md:52-58`.
- `dev:local-pi` usa la sintaxis POSIX `${VAR:-default}`: `gentle-shell-desktop@5ab4a00:package.json:23`. El issue #25 del escritorio (abierto) informa de que falla en Windows PowerShell. La PR abierta #27 (head `f42c3bd`, sin fusionar a fecha de 2026-10-03; cierra #25) sustituye el script por `node scripts/dev-local-pi.mjs`, que resuelve `GENTLE_SHELL_BIN` o la ruta por defecto y lanza `electron-vite dev` con `shell` en win32.
- Solo se ha probado macOS con Apple silicon: `gentle-shell-desktop@5ab4a00:README.md:7`.
- Sin firma ni notarización: `gentle-shell-desktop@5ab4a00:electron-builder.yml:30`, `gentle-shell-desktop@5ab4a00:README.md:64`.

**Impacto:** Una aplicación de macOS empaquetada falla en un arranque normal salvo que se inicie desde una terminal o se le proporcione `GENTLE_SHELL_BIN`. `Inference:` `dev:local-pi` falla bajo `cmd.exe` de Windows.

**Gravedad:** Baja. Documentado, y tiene soluciones alternativas.

**Recomendación:** Resolver el `PATH` de la shell de inicio de sesión al arrancar en macOS, o permitir que el usuario elija la ruta del lanzador en la aplicación y guardarla. Hacer que `dev:local-pi` sea multiplataforma (la PR abierta #27 lo propone). Requisitos de plataforma de las piezas upstream: [10-platforms.md](../10-platforms.md).

### A19. Dos elecciones de home persistidas

**Evidencia**
- El escritorio guarda su propio `{home}` en `userData/config.json`: `gentle-shell-desktop@5ab4a00:src/main/adapters/appConfigStore.ts:20-42`.
- gentle-shell guarda una elección de home en `~/.gentle-shell/config.json` y la usa cuando no se pasa ningún flag: `gentle-shell@ac67159:lib/gentle-shell-launcher.ts:218-224`, `:241-243`.
- El escritorio siempre pasa un flag: `gentle-shell-desktop@5ab4a00:src/main/domain/home/home.ts:33-37`.

**Impacto:** `Inference:` el `gentle-shell` de la terminal y el escritorio pueden usar homes distintos, así que un chat iniciado en uno no aparece en el otro.

**Gravedad:** Baja.

**Recomendación:** Leer la elección guardada de gentle-shell como valor por defecto para el primer arranque del escritorio, o escribir la elección del escritorio a través del propio `gentle-shell`. Esto requiere una decisión del mantenedor (ver el [índice de ADR](adr/README.md#sin-decidir--no-registrado)).

## Riesgos para escalar la UI

Se derivan de los hallazgos. No son defectos independientes.

| Superficie prevista | Hallazgos que la bloquean | Nota |
|---|---|---|
| Varios chats a la vez (estados de la barra lateral de la maqueta, notificaciones) | A3, A1, A11 | Necesita un registro de sesiones y envíos con ámbito de chat antes de cualquier trabajo de UI. |
| Panel de ODD (M3) | A3, A8 | Necesita un estado estructurado de ODD, que RPC no proporciona ([gap G2](../04-rpc-contract.md#carencias-que-necesita-el-escritorio)). |
| Stop de un helper | A5 | Necesita un comando RPC en upstream ([gap G1](../04-rpc-contract.md#carencias-que-necesita-el-escritorio)). Antes, el parser del escritorio debe ser correcto. |
| Pantallas de proveedores y extensiones (M4) | A2, A8 | O bien más pi en el mismo proceso (lo que empeora A1 y A2), o bien comandos RPC nuevos ([gaps G3–G5](../04-rpc-contract.md#carencias-que-necesita-el-escritorio)). |
| Releases para Windows y Linux | A4, A16, A18 | Sin CI y sin plataformas probadas aparte de macOS. Detalle por plataforma: [10-platforms.md](../10-platforms.md). |
| Servicio host para clientes de navegador y móviles ([propuesta 0004](../07-proposals/0004-host-service.md), **[community]**, sin decidir) | A3, A1, A8, A14, A5, A10, A15 | Necesita antes el trabajo de varios chats (A3, A1), un handshake de versión (A8), autenticación y validación de argumentos (A14), la corrección del parser de actividad (A5), un `cwd` por chat (A10) y una elección explícita del puente en lugar del recurso silencioso al simulado (A15). Detalle: [11, Qué debe cambiar primero](../11-host-service.md#qué-debe-cambiar-primero); [12, Autenticación y origen](../12-host-protocol.md#autenticación-y-origen). |
## Recomendaciones y orden

Dentro de cada grupo, el orden es la secuencia sugerida.

### 1. Desbloquear el uso de varios chats

1. **A3:** registro de sesiones indexado por el id de sesión de pi; `chatId` en cada envío y cada comando; ids de mensaje estables.
2. **A11:** refrescar la lista de chats; selección de chat nuevo por clic; lanzar en el primer envío.
3. **A1:** dejar de mutar `PI_CODING_AGENT_DIR`; como mínimo, serializar `listAll()`.

### 2. Corregir errores funcionales

1. **A5:** alinear los estados de los helpers y hacer opcional `callId`; fixtures reales.
2. **A7:** steer y follow-up mientras el agente trabaja; borrar `working` en `agent_settled`.
3. **A15:** limitar el puente simulado a `dev:web`; la comprobación de smoke verifica `window.gentle`.
4. **A10:** carpeta de proyecto por cada chat nuevo.
5. **A8:** leer y mostrar las versiones al arrancar; avisar por debajo de los mínimos.
6. **A2:** alinear o eliminar la dependencia de pi en el mismo proceso.
7. **A6, A12, A13, A19:** hilo en vivo a partir de los eventos de pi; timeouts de los diálogos; restablecer el hilo al cambiar de chat; alineación de la elección de home.

### 3. Plataforma

1. **A4:** lanzamiento de `.cmd` en Windows a través de `cmd.exe` con los tokens entrecomillados (reproducir primero; la PR abierta #26 no entrecomilla).
2. **A16:** CI con tests, typecheck, build y smoke; añadir Windows una vez resuelto A4.
3. **A9:** aprovisionamiento visible en el primer arranque.
4. **A18:** resolución del `PATH` en macOS o una ruta del lanzador guardada; scripts multiplataforma.

### 4. Higiene

- **A14:** validación de los argumentos de IPC, sandbox, CSP sin `'unsafe-eval'`, fuentes incluidas en el bundle, protección `will-navigate`.
- **A17:** correcciones de la desviación de estructura.

## Hallazgos añadidos tras la actualización

Añadidos el 2026-10-03, después de que el trabajo sobre los scrollbars de la [maqueta conceptual v2](https://github.com/matraket/gentle-shell-desktop/blob/d119d0a7a928821c40fff41ad1b1ddc73eaa1834/docs/assets/mockup-v2/gs-mockup-corpus.html) en una sesión de la comunidad los sacara a la luz. Se añaden aquí al final para que las citas por número de línea a las secciones anteriores sigan siendo válidas; pertenecen al grupo Higiene de [Recomendaciones y orden](#recomendaciones-y-orden).

### A20. Chromium ignora las reglas de scrollbar de WebKit

**Evidencia**
- El escritorio fija las propiedades estándar en todos los elementos: `scrollbar-width: thin` y `scrollbar-color: var(--line-strong) transparent` (`gentle-shell-desktop@5ab4a00:src/renderer/shared/theme/tokens.css:48-52`). El mismo archivo también da estilo a `::-webkit-scrollbar` con un tamaño de 8px, pista transparente, thumb redondeado y hover en `--purple` (`:54-72`). Ambos llegaron en el commit `3456eef` (PR #20, "match scrollbars to dark theme").
- MDN: "If an element's computed `scrollbar-color` and `scrollbar-width` values are anything other than `auto`, they will override `::-webkit-scrollbar-*` styling." (<https://developer.mozilla.org/en-US/docs/Web/CSS/::-webkit-scrollbar>, consultado el 2026-10-03). Chrome admite ambas propiedades estándar desde Chrome 121 (<https://developer.chrome.com/docs/css-ui/scrollbar-styling>).
- El escritorio fija Electron 44.4.3 (`gentle-shell-desktop@5ab4a00:pnpm-lock.yaml:1601`), cuyas notas de versión indican Chromium `152.0.7977.54` (notas de la versión v44.4.3 de Electron en GitHub, leídas el 2026-10-03).
- Una prueba con Chromium 149 headless en la sesión comunitaria de la maqueta mostró que un elemento con ambas propiedades estándar pinta el thumb estándar e ignora las reglas de WebKit (informe de la sesión, 2026-10-03).

**Impacto:** `Inference:` (no ejecutado en el escritorio) en la aplicación empaquetada nunca se aplican el thumb redondeado de 8px ni el hover en `--purple` de `:54-72`; solo se dibuja el scrollbar estándar fino en `--line-strong`. La intención del PR se cumple solo en parte.

**Severidad:** Baja (efecto estético).

**Recomendación:** Mantener un único mecanismo por motor: aplicar las reglas `::-webkit-scrollbar` dentro de `@supports selector(::-webkit-scrollbar)` y las propiedades estándar dentro de `@supports not selector(::-webkit-scrollbar)`, como hace la maqueta conceptual v2. Verificarlo en la aplicación empaquetada.

### A21. Thumb del scrollbar por debajo del contraste no textual de 3:1

**Evidencia**
- El color del thumb es `--line-strong` `#563040` (`gentle-shell-desktop@5ab4a00:src/renderer/shared/theme/tokens.css:13`, usado en `:51` y `:64`) sobre `--bg` `#060407`, `--panel` `#100a0f` y `--raised` `#180e15` (`:9-11`).
- Relaciones de contraste WCAG 2 calculadas con la fórmula de luminancia relativa de WCAG: 1.84:1 sobre `--bg`, 1.76:1 sobre `--panel`, 1.70:1 sobre `--raised`. El color de hover `--purple` `#c96aa2` (`:23`) da 5.45–5.90:1, pero según A20 la regla de hover no se aplica en Chromium.
- El criterio de conformidad 1.4.11 (Non-text Contrast) de WCAG 2.2 pide al menos 3:1 para la información visual necesaria para identificar componentes de la interfaz (<https://www.w3.org/TR/WCAG22/#non-text-contrast>). El criterio exime a los componentes cuya apariencia decide el agente de usuario; aquí aplica porque el escritorio da estilo al scrollbar.

**Impacto:** el thumb que indica la posición de desplazamiento se ve con dificultad sobre todos los fondos de panel, más aún para usuarios con baja visión.

**Severidad:** Baja según los criterios de esta auditoría, que no valoran la accesibilidad (ver Método y alcance). `Inference:` una revisión de accesibilidad probablemente la valoraría más alta.

**Recomendación:** Usar un color de thumb basado solo en tokens con al menos 3:1. La maqueta conceptual v2 usa `color-mix(in srgb, var(--line-strong), var(--purple) 50%)`, que se renderiza como `#904d71` y da 3.39:1, 3.25:1 y 3.13:1 sobre los tres fondos (calculado con la misma fórmula). Mantener `--purple` para hover y foco.
