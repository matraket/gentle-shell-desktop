> Traducción al español de `docs/03-architecture/adr/0007-text-only-chat-view.md` (commit `d27baba`). Documento de lectura; la versión de referencia es la inglesa.

# 0007. La vista de chat muestra solo el texto del usuario y del asistente

> Estado: borrador (draft).

## Contexto

El escritorio se dirige a personas que quieren sacar el trabajo adelante, no mirar una terminal (`odd/tasks/desktop-m1-chat-core.md:11`).

## Decisión

- **Alcance.** M1 es una conversación en texto plano: "No tool output, no thinking shown" (`odd/tasks/desktop-m1-chat-core.md:7`).
- **Reducer.** El reducer de T2 "keeps only user/assistant text, working state, and dialogs" (`odd/tasks/desktop-m1-chat-core.md:38`).
- **Aceptación.** "thinking and tool events never appear" (`odd/tasks/desktop-m1-chat-core.md:47`).

## Consecuencias

- **Qué ocurre con el resto.** Los eventos de herramientas y de razonamiento solo incrementan un contador `activity` (`src/main/domain/rpc/chatReducer.ts:61-68`, `:93-104`), y el historial los descarta (`src/main/domain/rpc/history.ts:11-19`).
- **Qué añadió M2.** La actividad de los subagentes, en una pestaña Helpers separada ([0011](0011-helpers-scoped-per-chat.md)).
- **Efecto secundario.** Los eventos de mensaje que no son del asistente se ignoran en vivo ([audit A6](../audit.md#a6-el-reducer-descarta-de-la-vista-en-vivo-los-mensajes-que-no-son-del-asistente)).

## Cambio posterior

- **Las respuestas del asistente se renderizan como Markdown saneado.** Las tareas de seguimiento de las ejecuciones reales de M2 registran "#16 `53497af` sanitized Markdown replies" (`odd/tasks/desktop-m2-helpers.md:63`). El código interpreta el texto del asistente con `marked` y lo sanea con DOMPurify (`src/renderer/shared/markdown/renderMarkdown.ts:65-72`). `MessageBubble` renderiza el texto del usuario como texto plano y el texto del asistente a través de `Markdown` (`src/renderer/features/conversation/components/MessageBubble.tsx:20`).
- **Qué no cambió.** La vista sigue mostrando solo el texto del usuario y del asistente; los eventos de herramientas y de razonamiento siguen fuera de ella. Solo se modificó la renderización en "texto plano" del texto del asistente.

## Estado

aceptada, modificada en parte (accepted, amended in part), registrada en `odd/tasks/desktop-m1-chat-core.md:7`, `:38`, `:47`; la renderización en texto plano de las respuestas del asistente fue modificada por `odd/tasks/desktop-m2-helpers.md:63`
