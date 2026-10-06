> Traducción al español de `docs/07-proposals/0003-post-hoc-audit-by-questions.md` (árbol de trabajo tras la actualización del 2026-10-03). Documento de lectura; la versión de referencia es la inglesa.

# 0003. Auditoría a posteriori mediante preguntas

> Estado: propuesta (proposed).

| Campo | Valor |
|---|---|
| Autor | Matrak (comunidad) |
| Fuente | Conversación con Matrak, 2026-10-01 (no publicada); [issue #28, "Author's framing: philosophy"](https://github.com/Gentleman-Programming/gentle-shell-desktop/issues/28) |
| Estado | `proposed` (solo el mantenedor la pasa a `accepted` o `declined`) |
| Principios | vision P10 **[community]** (preguntar a un helper que ha terminado por qué; P10 se refiere a un helper, no a la sesión principal, desde la revisión del 2026-10-03); respalda vision P7 **[maintainer]** (mockup intent), **[gentle-shell]** y vision P9 **[community]** |

## Problema

Cuando un helper (un subagente en el que el agente principal ha delegado) termina, el usuario ve el resultado: un helper "done", su respuesta en el chat, una tarea con un commit. No le resulta fácil preguntar a ese helper **"¿por qué lo hiciste de esta manera y no de aquella?"**

- Preguntar en el chat principal añade la pregunta a la conversación de trabajo y puede iniciar trabajo nuevo. `Inference:` además, el agente principal respondería a partir de su propio contexto, que contiene el resultado del helper pero no sus pasos.
- El razonamiento y los pasos del helper no están disponibles para el escritorio una vez que termina: la carga de actividad conserva los últimos 40 elementos del hilo y omite la ruta de la transcripción y el resultado ([gap G8](../04-rpc-contract.md#carencias-que-necesita-el-escritorio)).
- El escritorio no representa las llamadas a herramientas ni el razonamiento, ni siquiera del agente principal (inventory C17, C18).

`Inference:` poder interrogar a un helper que ha terminado convierte "el agente dice que ha terminado" en algo que el usuario puede comprobar, lo que sirve a vision P7 (evidencias visibles) y a vision P9 (aprender del trabajo). En el hilo de la comunidad se planteó una preocupación relacionada: un agente puede afirmar que ha tenido éxito sin que nadie lo verifique (Discord, Rafael The Hutt, 2026-09-27); ese hilo propone una solución distinta (gentle-mesh), de la que esta propuesta no depende.

## Propuesta

**Alcance principal (vision P10):** en un helper que ha terminado, una acción **Ask why** abre una conversación lateral. **Extensión más allá de vision P10 [community]:** la misma acción en un turno terminado del agente principal. P10 la deja fuera, porque a la sesión principal se le puede preguntar sin más ([issue #28, "Author's framing: review of the vision (2026-10-03)"](https://github.com/Gentleman-Programming/gentle-shell-desktop/issues/28), punto 1); se mantiene solo como variante opcional, y su fila de requisitos más abajo está marcada como "Extensión".

1. Parte de la propia transcripción de ese helper (su tarea, sus pasos, sus llamadas a herramientas, su resultado).
2. El usuario hace preguntas; el helper responde a partir de su transcripción y cita los pasos a los que se refiere.
3. No cambia el chat principal, el repositorio ni el registro original del helper. `Inference:` esto necesita una ejecución de solo lectura (sin herramientas de escritura ni de shell).
4. El intercambio puede guardarse junto al nodo original o descartarse.

## Requisitos del runtime

| Necesidad | ¿Disponible hoy? | Evidencia | Carencia |
|---|---|---|---|
| La transcripción completa y el resultado de un helper | No sobre RPC: la carga omite `sessionPath` y `result`; los hilos conservan 40 elementos (el esquema de actividad no cambia desde 3.7.0 (`1162ce9`) hasta la release 4.0.0 (`1f35ab1`) y `main` (`ac67159`)) | `gentle-shell@ac67159:docs/gentle-agents-activity.md:62`, `:79` | **gap G8** |
| Helpers terminados, a posteriori | En disco: un JSON por tarea en `<agent home>/gentle-agents/tasks/` (se conservan las `history_max_tasks` más recientes, 200 por defecto). Cada helper es su propia sesión de pi: un proceso de pi aparte que se ejecuta con `--mode rpc --session-dir <agent home>/gentle-agents/sessions` | `gentle-shell@ac67159:docs/gentle-shell.md:233`; `gentle-shell@ac67159:lib/agents-runner.ts:258-259`, `:501-502`; `gentle-shell@ac67159:extensions/gentle-agents.ts:124-127`, `:1266`; inventory A12 | `Inference:` el escritorio podría leerlos en el lado del host. `UNVERIFIED:` el formato JSON de las tareas no está documentado como estable |
| Reanudar un helper terminado con una pregunta | Solo como herramienta del modelo del agente principal: `subagent_continue` "Resume a finished subagent task in its own session with a follow-up prompt" rechaza una tarea que no ha terminado o que no tiene ruta de sesión y, en caso contrario, la vuelve a lanzar con `--session <sessionPath>`. Los procesos de helper (`GENTLE_PI_AGENTS_CHILD=1`) no la registran | `gentle-shell@ac67159:extensions/gentle-agents.ts:1613-1615`, `:1622`, `:1631`, `:152`, `:338-345`; `gentle-shell@ac67159:lib/agents-runner.ts:261`; `gentle-shell@ac67159:docs/gentle-shell.md:218`, `:233` | Canal de entrada del host (forma de gap G1). Un helper reanudado conserva sus herramientas normales, así que no es de solo lectura (`Inference:`) |
| Una ejecución de solo lectura sobre una sesión guardada | `Inference:` (no ejecutado): lanzar un proceso de pi aparte sobre el archivo de sesión del helper con `--session <path>`, que "Opens by file path" (`pi@a13d35a:packages/coding-agent/docs/cli.md:90-91`; inventory S3), y herramientas restringidas con `--tools` o `--no-tools` (inventory E9). Ambos son indicadores solo de lanzamiento. `UNVERIFIED:` que pi vuelva a abrir de este modo el archivo de sesión de un helper; no ejecutado | inventory S3, E9; [vision §Principios de producto, "Preguntar a un helper que ha terminado"](../00-vision.md#principios-de-producto) | Trabajo del escritorio, más una decisión sobre si esto es aceptable fuera de los flujos propios de gentle-shell |
| **Extensión** (más allá de vision P10, **[community]**): preguntar sobre el agente principal sin tocar el chat | En parte: `fork` y `clone` existen sobre RPC, pero en la sesión activa cancelan todos los helpers como efecto secundario | inventory S11, S12; [gap G1](../04-rpc-contract.md#carencias-que-necesita-el-escritorio) | `Inference:` un proceso aparte evita el efecto secundario |
| El razonamiento del helper | En parte: los elementos de razonamiento están en el hilo del helper (límite de 40 elementos). Para la extensión al turno principal: sí (deltas `thinking_*`), no se representa | `gentle-shell@ac67159:docs/gentle-agents-activity.md:64`, `:79`; inventory C18; [gap G8](../04-rpc-contract.md#carencias-que-necesita-el-escritorio) | Solo el escritorio para lo que contiene el hilo; los elementos más antiguos necesitan gap G8 |
| Vincular las respuestas con la evidencia de ODD (tarea, commit, revisión) | Sin estado estructurado de ODD | inventory O3, R5; [gap G2](../04-rpc-contract.md#carencias-que-necesita-el-escritorio) | gap G2 |
| Varias conversaciones laterales a la vez | No: host de una sola sesión | [audit A3](../03-architecture/audit.md#a3-host-de-sesión-única-con-ids-de-mensaje-posicionales) | gap G9 (trabajo del escritorio) |

## Precedentes en el ecosistema

- **`subagent_continue` y `subagent_result`:** las tareas terminadas "come back on demand for `subagent_result` and `subagent_continue`" (`gentle-shell@ac67159:docs/gentle-shell.md:233`; herramientas en `gentle-shell@ac67159:extensions/gentle-agents.ts:1578`, `:1613-1615`). Es el mecanismo existente más cercano, dirigido por el modelo del agente principal.
- **Open session en la superposición de agentes:** "Open writes a markdown transcript for `$EDITOR`, not a resumed child session" (`gentle-shell@ac67159:docs/gentle-shell.md:227`). Una transcripción de solo lectura, solo TUI.
- **fork, clone y tree de pi:** ramificar desde un mensaje anterior o duplicar una sesión (inventory S8, S11, S12), lo que mantiene intacto el original.
- **export de pi:** `/export` escribe una sesión como HTML o JSONL (inventory S13).

## Preguntas abiertas

- ¿"Ask why" debería usar la propia sesión del helper (`subagent_continue`, mismo modelo y contexto) o un lector nuevo sobre la transcripción?
- ¿Es la ejecución de solo lectura un requisito estricto, o basta con una advertencia?
- ¿Dónde deberían vivir las respuestas guardadas: en el chat, junto al helper o en el documento de funcionalidad (feature document)?
- ¿Se desea siquiera la extensión al turno principal, dado que vision P10 solo cubre los helpers que han terminado?
