> Traducción al español de `docs/07-proposals/0002-interact-with-running-node.md` (árbol de trabajo tras la actualización del 2026-10-03). Documento de lectura; la versión de referencia es la inglesa.

# 0002. Interactuar con un nodo en ejecución

> Estado: propuesta (proposed).

| Campo | Valor |
|---|---|
| Autor | Matrak (comunidad) |
| Fuente | Conversación con Matrak, 2026-10-01 (no publicada); [issue #28, "Author's framing: philosophy"](https://github.com/Gentleman-Programming/gentle-shell-desktop/issues/28) |
| Estado | `proposed` (solo el mantenedor la pasa a `accepted` o `declined`) |
| Principios | vision P10 **[community]**; amplía vision P6 **[gentle-shell]**, **[maintainer]** (mockup intent) |

## Problema

Una vez que un agente está en ejecución, el usuario del escritorio solo puede observarlo:

- El agente principal puede detenerse con Escape, pero el compositor es de solo lectura mientras trabaja, así que no se le puede redirigir (steer) (`gentle-shell-desktop@5ab4a00:src/renderer/features/conversation/components/Composer.tsx:53`; [inventory C4](../05-capability-inventory.md#conversación-y-entrada); [audit A7](../03-architecture/audit.md#a7-prompts-rechazados-mientras-el-agente-trabaja-pese-a-existir-steer-y-follow-up)).
- Un helper no puede detenerse: el botón Stop está deshabilitado (`gentle-shell-desktop@5ab4a00:src/renderer/features/helpers/components/HelpersFooter.tsx:36`).
- Un helper no puede redirigirse, y sus preguntas llegan como tarjetas de diálogo ordinarias sin vínculo con el helper que preguntó ([inventory A5, A6](../05-capability-inventory.md#helpers-subagentes)).

En la terminal de gentle-shell, el usuario puede detener helpers desde la superposición o con un atajo (inventory A4), y el modelo puede redirigirlos con una herramienta (inventory A6). El escritorio no ofrece ninguna de las dos cosas.

## Propuesta

Seleccionar cualquier nodo en ejecución (el agente principal o un helper) y actuar sobre él en el sitio:

| Acción | Agente principal | Helper |
|---|---|---|
| **Detener** | Existe (Escape, inventory C3) | Botón Stop en el hilo del helper (maqueta conceptual (mockup) `gs-mockup.html:603`) |
| **Redirigir** ("cambiar de rumbo antes del siguiente paso") | El compositor sigue siendo utilizable mientras trabaja; el mensaje se marca como redirección o en cola | Cuadro de mensaje en el hilo del helper |
| **Responder a su pregunta** | Tarjeta de pregunta en el chat (existe, inventory C19) | Tarjeta de pregunta dentro del hilo del helper, con el nombre del helper |
| **Inspeccionar** | Paso actual, llamadas a herramientas, razonamiento (detrás de un conmutador, UX U2) | Paso actual y llamadas a herramientas (existe en parte) |

El texto de redirección va solo al nodo seleccionado. El usuario ve el mensaje en el hilo de ese nodo, de modo que el registro muestra quién redirigió qué.

## Requisitos del runtime

| Necesidad | ¿Disponible hoy? | Evidencia | Carencia |
|---|---|---|---|
| Detener el agente principal | Sí: `abort` | inventory C3 | — |
| Redirigir o poner en cola para el agente principal | Sí sobre RPC: `steer`, `follow_up`, `clear_queue`, `queue_update` | inventory C4–C6 | Solo el escritorio (audit A7). Comportamiento por decidir: [vision Q5](../00-vision.md#preguntas-abiertas-para-el-mantenedor) |
| Detener un helper | Sin comando del host; `subagent_cancel` es una herramienta del modelo. `Inference:` `abort` cancela solo los helpers en primer plano, así que un helper en segundo plano no puede detenerse sobre RPC | [gap G1](../04-rpc-contract.md#carencias-que-necesita-el-escritorio) | **gap G1** (gentle-shell, más un canal de entrada del host) |
| Redirigir un helper | Solo pidiéndoselo al modelo: `subagent_send_message` "Steer a running subagent with a message delivered before its next model call" es una herramienta del modelo (`gentle-shell@ac67159:extensions/gentle-agents.ts:1608`) | inventory A6 | Canal de entrada del host (misma forma que gap G1) |
| Responder a la pregunta de un helper en su hilo | En parte: el diálogo de un hijo en modo tarea llega al padre como un diálogo ordinario; la pregunta de un hijo en segundo plano se descarta (`gentle-shell@ac67159:docs/gentle-shell.md:214`) | inventory A5 | ID del helper en la solicitud de diálogo (nuevo, gentle-shell). `UNVERIFIED:` si el diálogo reenviado lleva alguna identidad del hijo; no comprobado en el código |
| Responder a la consulta `subagent_parent_message` de un helper | Solo a través del modelo: `subagent_reply`, una respuesta, en 30 segundos (`gentle-shell@ac67159:docs/gentle-shell.md:224`) | inventory A5 | Canal de entrada del host |
| Inspeccionar los pasos de un helper | En parte: los elementos del hilo están en la carga de actividad, pero los elementos de herramienta de gentle-shell no llevan `callId`, que el escritorio exige, así que `Inference:` (no ejecutado) se descarta todo elemento de herramienta | [audit A5](../03-architecture/audit.md#a5-el-conjunto-de-estados-de-los-helpers-y-los-elementos-de-herramienta-no-coinciden-con-gentle-shell) | Primero, una corrección en el escritorio |
| Inspeccionar las llamadas a herramientas y el razonamiento del agente principal | Sí sobre RPC: deltas `tool_execution_*`, `thinking_*` | inventory C17, C18 | Solo el escritorio |

`Inference:` (a partir de [04, responsabilidad de las carencias](../04-rpc-contract.md#carencias-que-necesita-el-escritorio)) gentle-shell puede enviar datos nuevos al host sin cambiar pi, pero las *acciones* del host sobre los helpers necesitan un canal de entrada. pi ya encamina el texto del host hacia el código de las extensiones; entre otros caminos, `prompt` llega a los comandos de extensión y a los manejadores `input`, `steer` y `follow_up` llegan a los manejadores `input`, `bash` llega a los manejadores `user_bash`, y las respuestas a diálogos responden a los diálogos ([04 §Canales del host y de las extensiones](../04-rpc-contract.md#canales-del-host-y-de-las-extensiones)). Un comando `/gentle:*` o un manejador `input` que detenga o redirija un helper por su ID es una forma candidata y no necesita ningún cambio en pi; no está diseñada ni acordada upstream (repositorio de origen), y qué canal usar está abierto ([ADR: Sin decidir](../03-architecture/adr/README.md#sin-decidir--no-registrado)).

## Precedentes en el ecosistema

- **Stop en la superposición de agentes de gentle-shell:** **Stop** (`s`) para las tareas activas propias, y `alt+s` para detener los helpers activos o en cola actuales (`gentle-shell@ac67159:docs/gentle-shell.md:227`, `:232`; inventory A4). Solo TUI.
- **Redirigir un helper:** `subagent_send_message` (`gentle-shell@ac67159:extensions/gentle-agents.ts:1608-1610`; `gentle-shell@ac67159:docs/gentle-shell.md:218`, "steer a running child").
- **Redirigir el agente principal:** pi envía Enter durante el streaming como `prompt` con `streamingBehavior: "steer"` (`pi@a13d35a:packages/coding-agent/src/modes/interactive/interactive-mode.ts:3317-3324`; inventory C4).
- **Responder a la pregunta de un helper:** los diálogos de los hijos en modo tarea aparecen como diálogos del padre (`gentle-shell@ac67159:docs/gentle-shell.md:214`).

## Preguntas abiertas

- ¿Redirigir un helper debería pasar por el agente padre (para que lo sepa) o ir directamente al helper?
- ¿Qué debería hacer un prompt enviado mientras el agente principal trabaja: redirigir, ponerse en cola o rechazarse ([vision Q5](../00-vision.md#preguntas-abiertas-para-el-mantenedor))?
- ¿Debería Stop sobre un helper pedir confirmación, como hace `alt+s` en la terminal?
