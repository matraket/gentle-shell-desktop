> Traducción al español de `docs/03-architecture/adr/0004-renderer-scope-rule-and-screaming-architecture.md` (commit `d27baba`). Documento de lectura; la versión de referencia es la inglesa.

# 0004. Estructura del renderer: Scope Rule, Screaming Architecture, contenedor/presentacional

> Estado: borrador (draft).

## Contexto

El mantenedor pidió que se aplicaran sus skills de React, y que las reglas de estructura de su skill `angular` se aplicaran a React (`odd/tasks/desktop-m1-chat-core.md:29`).

## Decisión

**Reglas de código React:** imports con nombre, sin memoización manual, ref como prop (`odd/tasks/desktop-m1-chat-core.md:29`).

**Reglas de estructura** (`odd/tasks/desktop-m1-chat-core.md:29`; `src/README.md:21-43`):

| Regla | Significado |
|---|---|
| Scope Rule | El código que usa una sola funcionalidad se queda local; el código que usan dos o más va a `shared/`. |
| Screaming Architecture | Las carpetas de funcionalidad se nombran según lo que hace la aplicación. |
| Contenedor/presentacional | `<Feature>Container.tsx` es responsable del estado y llama a `useBridge()`; los componentes bajo `components/` solo reciben props. |
| Diseño atómico | Los átomos reutilizables viven bajo `shared/ui`. |

## Consecuencias

- **Funcionalidades.** `chats`, `conversation`, `first-run` y `helpers`. `helpers` tiene su propia carpeta aunque solo `conversation` lo abre (`src/README.md:28-32`).
- **El puente en un solo lugar.** Las llamadas al puente se quedan en los contenedores, así que los componentes presentacionales se prueban sin Electron (`src/README.md:39-43`).
- **Desviación.** `shared/markdown` tiene un solo consumidor ([audit A17](../audit.md#a17-desviación-respecto-a-las-reglas-de-estructura-declaradas)).

## Estado

aceptada (accepted), registrada en `odd/tasks/desktop-m1-chat-core.md:29`, `src/README.md:21-43`
