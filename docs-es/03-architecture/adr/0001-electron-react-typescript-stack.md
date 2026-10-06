> Traducción al español de `docs/03-architecture/adr/0001-electron-react-typescript-stack.md` (commit `d27baba`). Documento de lectura; la versión de referencia es la inglesa.

# 0001. Electron, React y TypeScript como pila del escritorio

> Estado: borrador (draft).

## Contexto

Gentle Shell solo existía dentro de la UI de terminal de pi. El objetivo era una ventana de chat para personas que no quieren una terminal (`odd/tasks/desktop-m1-chat-core.md:9-11`). pi es un programa Node (`odd/tasks/desktop-m1-chat-core.md:18`).

## Decisión

- **Shell:** Electron + React, "chosen by the maintainer on 2026-09-21" (`odd/tasks/desktop-m1-chat-core.md:18`).
- **Pila:** Electron + React + TypeScript (strict), Vite mediante `electron-vite`, pnpm y `electron-builder` para builds de desarrollo sin firmar (`odd/tasks/desktop-m1-chat-core.md:26`).
- **Tests:** vitest, con un entorno Node para el código del proceso principal y del protocolo, y jsdom para el renderer (`odd/tasks/desktop-m1-chat-core.md:27`).

## Consecuencias

- **Tres procesos.** La aplicación se ejecuta como proceso principal, preload y renderer, cada uno construido como su propio bundle (`electron.vite.config.ts:5-40`; [0002](0002-process-roles-and-typed-preload-bridge.md)).
- **Node en el proceso principal.** El proceso principal puede lanzar hijos e importar paquetes de Node, que es lo que hace posible la lista de sesiones en el mismo proceso ([0006](0006-in-process-session-list.md)).
- **Tamaño del paquete.** El build de macOS sin firmar ocupaba 156 MiB al cierre de M1 (`odd/tasks/desktop-m1-chat-core.md:61`).
- **Plataformas.** Solo se ha probado macOS con Apple silicon (`README.md:7`).

## Estado

aceptada (accepted), registrada en `odd/tasks/desktop-m1-chat-core.md:18`, `:26`
