> Traducción al español de `docs/03-architecture/adr/0011-helpers-scoped-per-chat.md` (commit `d27baba`). Documento de lectura; la versión de referencia es la inglesa.

# 0011. Los helpers tienen como ámbito el chat que los inició

> Estado: borrador (draft).

## Contexto

gentle-agents ejecuta subagentes ("helpers") y, con un host interactivo, publica su actividad sobre RPC como `gentle-agents.activity/v1` (`odd/tasks/desktop-m2-helpers.md:9-12`).

## Decisión

Cada chat tiene una pestaña Helpers que muestra solo los subagentes que inició ese chat. Es "Never a global list: the parent-child relation stays direct" (decisión del mantenedor, 2026-09-21; `odd/tasks/desktop-m2-helpers.md:7`). El reducer mantiene `helpers` por chat e ignora las demás claves de widget (`odd/tasks/desktop-m2-helpers.md:16`). Detener helpers queda fuera de alcance hasta que gentle-agents exponga un comando RPC (`odd/tasks/desktop-m2-helpers.md:22`).

## Consecuencias

- **Dónde vive el estado.** El estado de los helpers forma parte de `ChatState` (`src/shared/bridge-types.ts:128`). El renderer lo muestra en `features/helpers`, que solo se abre desde `conversation` (`src/README.md:28-32`).
- **Stop deshabilitado.** El botón Stop está deshabilitado (`src/renderer/features/helpers/components/HelpersFooter.tsx:36-38`; `README.md:62`).
- **Retención.** Los helpers terminados se conservan mediante una fusión de retención, porque gentle-agents los descarta de las tramas (`odd/tasks/desktop-m2-helpers.md:57`; `src/main/domain/rpc/chatReducer.ts:209-229`).

## Estado

aceptada (accepted), registrada en `odd/tasks/desktop-m2-helpers.md:7`, `:16`, `:22`
