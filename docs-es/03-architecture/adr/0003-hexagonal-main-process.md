> Traducción al español de `docs/03-architecture/adr/0003-hexagonal-main-process.md` (commit `d27baba`). Documento de lectura; la versión de referencia es la inglesa.

# 0003. Proceso principal hexagonal

> Estado: borrador (draft).

## Contexto

El mantenedor pidió que se aplicaran las reglas de estructura de sus skills, incluido un "hexagonal main process (domain, ports, adapters)" (`odd/tasks/desktop-m1-chat-core.md:29`). M2 mantuvo las mismas restricciones (`odd/tasks/desktop-m2-helpers.md:26`).

## Decisión

El código del proceso principal se divide en tres carpetas (`src/README.md:45-51`):

- `src/main/domain`: tipos y lógica puros.
- `src/main/ports`: las interfaces de las que depende el dominio.
- `src/main/adapters`: las implementaciones en Electron/Node.

El objetivo es un dominio libre de imports de Electron, de modo que el códec RPC y el reducer puedan probarse sin lanzar un `gentle-shell` real (`src/README.md:45-51`).

## Consecuencias

- **Puertos.** Hay cinco: `ProcessSpawner`, `LauncherLocator`, `SessionStore`, `HomeSettings` y `SetupService` (`src/main/ports/index.ts:15-97`). [current.md](../current.md#puertos-y-adaptadores) lista sus adaptadores.
- **Tests basados en fakes.** `PiSession` y `ChatHost` dependen solo de puertos y se prueban con fakes o con un script falso (`src/main/domain/session/PiSession.ts:69-76`).
- **Desviación.** `domain/home/home.ts` importa módulos de Node ([audit A17](../audit.md#a17-desviación-respecto-a-las-reglas-de-estructura-declaradas)).

## Estado

aceptada (accepted), registrada en `odd/tasks/desktop-m1-chat-core.md:29`, `src/README.md:45-51`
