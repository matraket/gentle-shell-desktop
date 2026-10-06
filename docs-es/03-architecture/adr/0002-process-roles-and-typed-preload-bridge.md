> Traducción al español de `docs/03-architecture/adr/0002-process-roles-and-typed-preload-bridge.md` (commit `d27baba`). Documento de lectura; la versión de referencia es la inglesa.

# 0002. Roles de los procesos y un puente de preload tipado y mínimo

> Estado: borrador (draft).

## Contexto

Electron ejecuta tres contextos de JavaScript que no pueden compartir estado en tiempo de ejecución, solo tipos (`src/README.md:7-10`).

## Decisión

Cada proceso tiene un único rol (`odd/tasks/desktop-m1-chat-core.md:26`):

- El **proceso principal** es responsable de los procesos hijo y de la lista de sesiones.
- El **renderer** es solo UI.
- El **preload** expone "a typed, minimal bridge".

El contrato compartido por los tres vive en `src/shared/bridge-types.ts` (`src/README.md:12-16`).

## Consecuencias

- **El puente.** El renderer solo llega al proceso principal a través de `window.gentle` (`GentleBridge`): 8 canales de petición y 2 canales de envío (`src/shared/bridge-types.ts:273-295`; `src/shared/ipc-channels.ts:8-23`).
- **Preload testeable.** `createBridge` recibe un objeto IPC inyectado, así que se prueba sin Electron (`src/preload/bridge.ts:10-19`).
- **Carencias.** Los envíos no llevan id de chat, y los argumentos de IPC no se validan. Ver [audit A3](../audit.md#a3-host-de-sesión-única-con-ids-de-mensaje-posicionales) y [audit A14](../audit.md#a14-endurecimiento-del-preload-y-del-ipc).

## Estado

aceptada (accepted), registrada en `odd/tasks/desktop-m1-chat-core.md:26`, `src/README.md:5-19`
