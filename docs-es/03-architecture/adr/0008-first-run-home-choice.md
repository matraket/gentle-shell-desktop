> Traducción al español de `docs/03-architecture/adr/0008-first-run-home-choice.md` (commit `d27baba`). Documento de lectura; la versión de referencia es la inglesa.

# 0008. Elección de home en el primer arranque: vincular a pi o mantener un home separado

> Estado: borrador (draft).

## Contexto

Los usuarios pueden tener ya una configuración de pi en `~/.pi/agent` con inicios de sesión y sesiones. El lanzador gentle-shell admite `--link` e `--isolated` (`odd/tasks/desktop-m1-chat-core.md:17`).

## Decisión

T5 (`odd/tasks/desktop-m1-chat-core.md:41`, `:49`):

1. Detectar `~/.pi/agent`.
2. Si existe, ofrecer "Use my pi setup" o "Keep it separate". Omitir la pantalla cuando no se encuentra pi.
3. Guardar la elección en la configuración `userData` de la aplicación.
4. Pasarla al lanzador como `--link` o `--isolated`.

## Consecuencias

- **Valores por defecto.** Sin ninguna elección guardada, la aplicación usa `isolated` (`src/main/domain/home/home.ts:17-19`).
- **Sobrescritura.** `GENTLE_SHELL_HOME` prevalece sobre ambos modos con `--home <dir>` (`src/main/domain/home/home.ts:33-37`).
- **Sin necesidad de reiniciar.** Los flags de home se vuelven a leer en cada lanzamiento (`src/main/adapters/homeSettings.ts:5-17`). El directorio de listado se resuelve de nuevo en cada llamada de listado (`src/main/adapters/piSessionStore.ts:44-58`, conectado en `src/main/index.ts:63`).
- **Dos elecciones guardadas.** gentle-shell guarda su propia elección de home en otro lugar ([audit A19](../audit.md#a19-dos-elecciones-de-home-persistidas)).
- **El primer arranque en un home aislado** desencadena el aprovisionamiento del lanzador sin progreso visible ([audit A9](../audit.md#a9-el-aprovisionamiento-del-lanzador-en-el-primer-arranque-no-muestra-progreso)).

## Estado

aceptada (accepted), registrada en `odd/tasks/desktop-m1-chat-core.md:41`, `:49`; `README.md:25-30`, `:42`
