> Traducción al español de `docs/07-proposals/0001-agent-flow-graph.md` (árbol de trabajo tras la actualización del 2026-10-03). Documento de lectura; la versión de referencia es la inglesa.

# 0001. El flujo de agentes como grafo

> Estado: propuesta (proposed).

| Campo | Valor |
|---|---|
| Autor | Matrak (comunidad) |
| Fuente | Conversación con Matrak, 2026-10-01 (no publicada); [issue #28, "Author's framing: philosophy"](https://github.com/Gentleman-Programming/gentle-shell-desktop/issues/28) |
| Estado | `proposed` (solo el mantenedor la pasa a `accepted` o `declined`) |
| Principios | vision P10 **[community]**; debe respetar vision P4 **[maintainer]** |

## Problema

Un chat puede iniciar varios helpers, y los helpers pueden hacer preguntas al padre y devolverle resultados. Hoy ese flujo se muestra como una lista plana:

- El panel de Helpers del escritorio enumera los helpers del chat y un hilo cada vez (`gentle-shell-desktop@5ab4a00:src/renderer/features/helpers/HelpersContainer.tsx`; [screens SCR-03](../06-ux/screens.md#scr-03-panel-de-helpers)).
- La maqueta conceptual (mockup) muestra la misma lista, más filas de helpers bajo el mensaje que los inició (`gs-mockup.html:545-550`, `:572-578`).
- La propia superposición de gentle-shell es una lista junto a un hilo ([inventory A3](../05-capability-inventory.md#helpers-subagentes)).

Una lista responde a "qué se está ejecutando". No muestra **quién delegó qué, desde qué mensaje, en qué orden y qué se devolvió**. `Inference:` esa relación es la parte del flujo de trabajo que peor muestra una terminal, lo que la convierte en candidata para vision P10.

## Propuesta

Una vista de grafo del flujo de agentes por chat:

- **Nodos:** el agente principal del chat, cada helper y (cuando se conoce) el mensaje del usuario que dio lugar a una delegación.
- **Aristas:** delegación (el padre inicia un helper); pregunta y respuesta (el helper pregunta al padre, inventory A5); resultado devuelto (inventory A7); redirección enviada (inventory A6).
- **Estado del nodo:** queued, running, waiting, done, failed, con el tiempo transcurrido; al seleccionar un nodo se abre su hilo en el panel de Helpers existente.
- **Tiempo:** nodos ordenados por hora de inicio, de modo que el grafo también se lee como una línea temporal.

**Alcance.** Un chat cada vez. El mantenedor decidió "Never a global list: the parent-child relation stays direct" (`gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m2-helpers.md:7`; [ADR 0011](../03-architecture/adr/0011-helpers-scoped-per-chat.md)). Un grafo entre chats (por ejemplo, de los mensajes `orchestrator_*` entre sesiones, inventory A9) chocaría con esa decisión; se deja como pregunta abierta, no como parte de esta propuesta.

## Requisitos del runtime

| Necesidad | ¿Disponible hoy? | Evidencia | Carencia |
|---|---|---|---|
| Lista de los helpers del chat con estado y marcas de tiempo | Sí, sobre el host interactivo: `gentle-agents.activity/v1` tiene `id`, `agent`, `label`, `status`, `createdAt`, `startedAt`, `endedAt` | [04, añadidos de gentle-shell](../04-rpc-contract.md#añadidos-de-gentle-shell-sobre-rpc) | Primero, las discrepancias del parser del escritorio ([audit A5](../03-architecture/audit.md#a5-el-conjunto-de-estados-de-los-helpers-y-los-elementos-de-herramienta-no-coinciden-con-gentle-shell)) |
| Qué sesión o tarea inició un helper | No: `TaskRecord` tiene `parentSessionId` (`gentle-shell@ac67159:lib/agents-protocol.ts:124`), pero la carga lo omite deliberadamente (`gentle-shell@ac67159:docs/gentle-agents-activity.md:62`; el esquema de actividad no cambia desde 3.7.0 (`1162ce9`) hasta la release 4.0.0 (`1f35ab1`) y `main` (`ac67159`)) | — | Campo nuevo. `Inference:` la misma vía que gap G8 (un cambio en la carga de `setWidget` en gentle-shell) |
| Qué mensaje del usuario dio lugar a una delegación | No: la carga no tiene vínculo con el mensaje (`gentle-shell-desktop@5ab4a00:src/renderer/features/conversation/components/HelpersStrip.tsx:9-16`) | — | Campo nuevo (gentle-shell); el escritorio también necesita ID de mensaje estables ([audit A3](../03-architecture/audit.md#a3-host-de-sesión-única-con-ids-de-mensaje-posicionales)) |
| Helpers iniciados por helpers | `Inference:` (leído, no ejecutado) no. Cada helper es un proceso de pi aparte (`--mode rpc --session-dir <agent home>/gentle-agents/sessions`, `gentle-shell@ac67159:lib/agents-runner.ts:258-259`, `:501-502`), lanzado con `GENTLE_PI_AGENTS_CHILD=1` (`:216`, `:473`); `agentsEnabled` devuelve false para él (`gentle-shell@ac67159:extensions/gentle-agents.ts:151-152`), y `gentleAgents` retorna pronto en un proceso así (`:338-345`), después de registrar como mucho la herramienta de mensajería del hijo `subagent_parent_message` (`:195-196`) y antes de que se registren las herramientas `subagent_*` (`:1402-1403`) | — | Ninguna mientras esto se mantenga; solo se necesita un ID de tarea padre si se añade la delegación anidada |
| Aristas de pregunta, respuesta, resultado y redirección | En parte: los diálogos de los hijos en modo tarea llegan al padre como diálogos ordinarios, sin vínculo con el helper (inventory A5); los resultados llegan como mensajes personalizados `gentle-agents.result` (inventory A7), que el escritorio descarta ([audit A6](../03-architecture/audit.md#a6-el-reducer-descarta-de-la-vista-en-vivo-los-mensajes-que-no-son-del-asistente)); desde gentle-shell 4.0.0 (#1631), un padre inactivo se despierta después con un mensaje con rol de usuario generado por el sistema, que no lleva ningún ID de tarea (`gentle-shell@ac67159:extensions/gentle-agents.ts:65`, `:691`; inventory A7); la redirección es una herramienta del modelo (inventory A6) | inventory A5–A7 | ID del helper en las solicitudes de diálogo (nuevo); el escritorio debe conservar los mensajes personalizados |
| Modelo, tokens y coste por nodo | No: omitidos de la carga | `gentle-shell@ac67159:docs/gentle-agents-activity.md:62`; inventory A2 | gap G8 |
| Helpers terminados de sesiones anteriores | No sobre RPC; en disco en `<agent home>/gentle-agents/tasks/` | inventory A12 | gap G8 |
| Varios chats, cada uno con su propio grafo | No: host de una sola sesión | [audit A3](../03-architecture/audit.md#a3-host-de-sesión-única-con-ids-de-mensaje-posicionales) | gap G9 (trabajo del escritorio) |

## Precedentes en el ecosistema

- **Superposición de agentes de gentle-shell** (`/gentle:agents`, `alt+a`): vista dividida de las tareas y del hilo seleccionado, Follow, Open session, Stop y un selector de Scope entre "this session's direct active children and all open orchestrators" (`gentle-shell@ac67159:docs/gentle-shell.md:226-227`). Una lista, no un grafo; solo TUI sobre RPC ([inventory A3](../05-capability-inventory.md#helpers-subagentes)).
- **Árbol de sesión de pi** (`/tree`): navega por las ramas de una sesión como un árbol (inventory S8, `pi@a13d35a:packages/coding-agent/src/modes/interactive/interactive-mode.ts:3224`). Un árbol de las entradas de una conversación, no de agentes.
- No se encontró ninguna vista de grafo de agentes. `rg -il '\bgraph\b'` sobre `extensions/`, `lib/`, `docs/` y `README.md` de `gentle-shell@ac67159` solo da usos no relacionados (el grafo de contribuidores de GitHub, el grafo de autoridad de revisión, el grafo de módulos de pi), los mismos archivos que en `1162ce9`. `rg -il 'agent graph|graph view|flow graph'` sobre `gentle-shell@ac67159`, `pi@a13d35a:packages/coding-agent/src` y `gentle-ai@ff77164` da 0 coincidencias (ejecutado de nuevo el 2026-10-03).

## Preguntas abiertas

- ¿Es un grafo por chat lo bastante útil frente a la lista existente como para justificar los campos upstream?
- ¿Debería aparecer alguna vez la mensajería entre sesiones (inventory A9), dado vision P4?
- ¿Primero el grafo o la línea temporal? Una línea temporal necesita solo los campos disponibles hoy.
