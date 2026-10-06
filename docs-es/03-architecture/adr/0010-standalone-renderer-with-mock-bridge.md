> Traducción al español de `docs/03-architecture/adr/0010-standalone-renderer-with-mock-bridge.md` (commit `d27baba`). Documento de lectura; la versión de referencia es la inglesa.

# 0010. Ejecutar el renderer de forma autónoma contra un puente simulado

> Estado: borrador (draft).

## Contexto

El mantenedor pidió que la UI se verificara en un navegador a medida que se incorpora el trabajo (`odd/tasks/desktop-m1-chat-core.md:29`). La automatización del navegador no puede conectarse a un `BrowserWindow` de Electron (`vite.web.config.ts:5-7`).

## Decisión

El renderer se ejecuta de forma autónoma con un puente simulado mediante `pnpm dev:web`, y la UI se maneja con herramientas de navegador, guardando capturas de pantalla como evidencia (`odd/tasks/desktop-m1-chat-core.md:29`). M2 amplió el simulado con un escenario de helpers (`odd/tasks/desktop-m2-helpers.md:19`).

## Consecuencias

- **Un único camino de código.** `useBridge()` devuelve `window.gentle` cuando está presente y `mockBridge` en caso contrario, así que el mismo código se ejecuta en ambos modos (`src/renderer/shared/bridge/useBridge.ts:4-12`).
- **Tamaño del simulado.** El simulado tiene 489 líneas y debe seguir el ritmo del puente real.
- **Los datos reales se desvían.** El simulado codifica las propias suposiciones del escritorio, como el estado `done` y `callId`. Ver [audit A5](../audit.md#a5-el-conjunto-de-estados-de-los-helpers-y-los-elementos-de-herramienta-no-coinciden-con-gentle-shell).
- **Sin protección.** El recurso al simulado no tiene ninguna protección por entorno ([audit A15](../audit.md#a15-recurso-silencioso-al-puente-simulado-en-los-builds-empaquetados)).

## Estado

aceptada (accepted), registrada en `odd/tasks/desktop-m1-chat-core.md:29`; `odd/tasks/desktop-m2-helpers.md:19`
