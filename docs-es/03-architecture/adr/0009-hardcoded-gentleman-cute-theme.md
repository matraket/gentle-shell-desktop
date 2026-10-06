> Traducción al español de `docs/03-architecture/adr/0009-hardcoded-gentleman-cute-theme.md` (commit `d27baba`). Documento de lectura; la versión de referencia es la inglesa.

# 0009. Fijar en el código los tokens del tema Gentleman-Cute por ahora

> Estado: borrador (draft).

## Contexto

pi tiene temas; gentle-pi distribuye `themes/Gentleman-Cute.json` (`odd/tasks/desktop-m1-chat-core.md:37`).

## Decisión

- **Fuera del alcance de M1:** leer el tema activo de pi. La decisión es "hardcode Gentleman-Cute tokens now" (`odd/tasks/desktop-m1-chat-core.md:22`).
- **En T1:** los tokens de Gentleman-Cute como variables CSS, más las tres familias tipográficas (`odd/tasks/desktop-m1-chat-core.md:37`).

## Consecuencias

- **Dónde vive el tema.** `src/renderer/shared/theme/gentleman-cute.json` y `tokens.css`. El tema de pi del usuario no se refleja.
- **Fuentes.** Se cargan desde Google Fonts en tiempo de ejecución (`src/renderer/index.html:11-16`), así que un arranque sin conexión las pierde ([audit A14](../audit.md#a14-endurecimiento-del-preload-y-del-ipc)).
- **Aplazado, no cerrado.** Leer el tema activo se aplazó. Ningún documento posterior lo decide.

## Estado

aceptada (accepted), registrada en `odd/tasks/desktop-m1-chat-core.md:22`, `:37`
