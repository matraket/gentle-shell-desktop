> Traducción al español de `docs/03-architecture/adr/0005-gentle-shell-rpc-child-process.md` (commit `d27baba`). Documento de lectura; la versión de referencia es la inglesa.

# 0005. Comunicarse con Gentle Shell a través de un proceso hijo `gentle-shell --mode rpc`

> Estado: borrador (draft).

## Contexto

pi ofrece `--mode rpc` con comandos, eventos y diálogos de extensión (`odd/tasks/desktop-m1-chat-core.md:15`). El lanzador gentle-shell acepta `[--link|--isolated|--home <dir>] --mode rpc`, reenvía los flags a pi y establece `PI_CODING_AGENT_DIR` (`odd/tasks/desktop-m1-chat-core.md:17`).

## Decisión

La conversación se ejecuta "through `gentle-shell --mode rpc`" (`odd/tasks/desktop-m1-chat-core.md:7`). T2 define un `PiSession` que:

- lanza `gentle-shell --mode rpc` con los flags de home elegidos;
- transmite los eventos en streaming;
- envía `prompt`, `abort` y `extension_ui_response`;
- se cierra limpiamente.

Fuente: `odd/tasks/desktop-m1-chat-core.md:38`. Las entradas JS del lanzador se ejecutan bajo Electron con `ELECTRON_RUN_AS_NODE=1` y `process.execPath`, nunca como un lanzamiento de Electron sin más (`odd/tasks/desktop-m1-chat-core.md:39`).

## Consecuencias

- **Protocolo.** El contrato es el protocolo RPC de pi, con las extensiones de gentle-shell por encima ([04-rpc-contract.md](../../04-rpc-contract.md)).
- **Lanzador externo.** El lanzador se encuentra en el `PATH` o mediante `GENTLE_SHELL_BIN` (`src/main/adapters/launcherLocator.ts:16-31`). M1 también dice que "Electron's bundled Node runs [pi] in the main process without a sidecar" (`odd/tasks/desktop-m1-chat-core.md:18`), pero el código ejecuta un lanzador externo. Ver [Sin decidir](README.md#sin-decidir--no-registrado).
- **Problemas conocidos.** El lanzamiento de `.cmd` en Windows ([audit A4](../audit.md#a4-lanzador-cmd-de-windows-lanzado-sin-shell)) y la falta de un handshake de versión ([audit A8](../audit.md#a8-sin-handshake-de-versión)).

## Estado

aceptada (accepted), registrada en `odd/tasks/desktop-m1-chat-core.md:7`, `:38-39`
