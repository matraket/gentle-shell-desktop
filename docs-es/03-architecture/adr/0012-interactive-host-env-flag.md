> Traducción al español de `docs/03-architecture/adr/0012-interactive-host-env-flag.md` (commit `d27baba`). Documento de lectura; la versión de referencia es la inglesa.

# 0012. Activar las funcionalidades de host interactivo con `GENTLE_SHELL_INTERACTIVE_HOST=1`

> Estado: borrador (draft).

## Contexto

Bajo `--mode rpc`, gentle-pi habilita los diálogos RPC para `ask_user_question` y `ask_user_choice`, y publica la actividad de los subagentes, solo cuando el host declara que es interactivo (`odd/tasks/desktop-m2-helpers.md:11`).

## Decisión

La aplicación establece `GENTLE_SHELL_INTERACTIVE_HOST=1` en el proceso que lanza (`odd/tasks/desktop-m2-helpers.md:11`, `:17`; `README.md:89-91`). En el código, el flag se aplica en último lugar en la fusión del entorno, de modo que nada puede sobrescribirlo (`src/main/domain/session/PiSession.ts:59-67`, `:134`).

## Consecuencias

- **gentle-pi más antiguo.** Con un gentle-pi anterior a 3.7.0, la pestaña Helpers se queda vacía (`README.md:89-91`). El escritorio no lo detecta ([audit A8](../audit.md#a8-sin-handshake-de-versión)).
- **Detalles del contrato.** El valor exacto, las condiciones de activación y el esquema de actividad están en [04-rpc-contract.md](../../04-rpc-contract.md#variables-de-entorno-del-contrato).

## Estado

aceptada (accepted), registrada en `odd/tasks/desktop-m2-helpers.md:11`, `:17`
