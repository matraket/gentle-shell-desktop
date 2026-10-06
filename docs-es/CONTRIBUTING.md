> Traducción al español de `CONTRIBUTING.md` (árbol de trabajo tras la actualización del 2026-10-03). Documento de lectura; la versión de referencia es la inglesa.

# Contribuir

> Estado: borrador, propuesta de la comunidad para el proceso de contribución; se cita la práctica del mantenedor donde está registrada (draft (community proposal for the contribution process; maintainer practice cited where recorded)).

Gentle Desktop es una versión preliminar temprana: M1 (núcleo del chat) y M2 (helpers por chat) están terminados (`README.md:3`). Esta guía ofrece el camino corto hacia una contribución útil y enlaza con el [corpus de documentación](README.md) para el detalle.

## Cómo leer esta guía

| Etiqueta | Significado |
|---|---|
| **[maintainer]** | Los mensajes de Discord de Alan Buscaglia y los documentos del repositorio de escritorio escritos por el mantenedor (`README.md`, `odd/tasks/desktop-m1-*.md`, `odd/tasks/desktop-m2-*.md`): intención declarada o práctica registrada. |
| **[community proposal]** | Esta guía, otras páginas del corpus y los mensajes de Discord de miembros distintos del mantenedor: propuesto, no decidido. |
| **[upstream]** | Los propios archivos de los repositorios upstream (repositorios de origen): reglas que el grupo del escritorio no controla. |

Son las mismas etiquetas, con las mismas fuentes, que la tabla de etiquetas de [08 §Cómo leer esta página](08-team.md#cómo-leer-esta-página).

Las citas `path:line` apuntan a archivos de este repositorio en `main` `5ab4a00` (el corpus las escribe como `gentle-shell-desktop@5ab4a00:path:line`); los archivos citados no han cambiado en la rama del corpus. `Inference:` marca razonamiento, no un hecho declarado. Los IDs de otras páginas del corpus llevan su página (`audit A4`, `inventory C20`, `governance D7`, `QW-11`), siguiendo la [convención de IDs del corpus](README.md#cómo-leerlo); M1 y M2 sin calificador son los hitos del mantenedor.

Aplicar la práctica del mantenedor a las pull requests de la comunidad es en sí mismo una **[community proposal]** ([08 §Flujo de contribución](08-team.md#flujo-de-contribución)). Las preguntas abiertas de gobernanza se listan al [final de esta guía](#preguntas-abiertas).

## Antes de empezar

1. **Leer el corpus.** Empezar por la [visión](00-vision.md) y el [glosario](01-glossary.md), y después seguir el orden de lectura de [docs/README.md](README.md#cómo-leerlo).
2. **Elegir un área.** [08 §Áreas de responsabilidad](08-team.md#áreas-de-responsabilidad) lista siete áreas con su alcance; los responsables se proponen a sí mismos, el grupo los confirma y el mantenedor puede vetarlos (governance D12, **[community proposal]**).
3. **Elegir una tarea.** Los [quick wins](09-roadmap.md#quick-wins) (mejoras rápidas) afectan solo al escritorio, no necesitan ninguna decisión abierta y cada uno corrige un hallazgo citado (**[community proposal]**).
4. **Hablar primero.** La comunidad se coordina en el hilo de Discord "Gentle Desktop"; los issues de GitHub están habilitados, las Discussions no ([08 §Canales de comunicación](08-team.md#canales-de-comunicación)). Anunciar qué tarea se toma antes de empezar es una **[community proposal]**.

El proceso del mantenedor es "present a roadmap, which goes into the repo; divide tasks; present PRs" (governance D1, **[maintainer]**, Discord, Alan Buscaglia, 2026-09-27; [08 §Cómo se toman las decisiones](08-team.md#cómo-se-toman-las-decisiones)).

## Dónde corresponde un cambio

No todos los cambios corresponden a este repositorio. [02 §Dónde corresponde cada cambio](02-ecosystem.md#dónde-corresponde-cada-cambio) encamina cada tipo de cambio; esa tabla está etiquetada como `Inference:` en su fuente, y también este resumen:

| Si el cambio… | Corresponde a |
|---|---|
| Añade o modifica un comando RPC, un evento o la forma de una respuesta | pi (`earendil-works/pi`) |
| Publica datos nuevos de una funcionalidad de gentle-shell, o hace que un comando de gentle-shell funcione bajo RPC, o modifica el lanzador | gentle-shell |
| Permite al host actuar sobre una funcionalidad de gentle-shell | gentle-shell, a través de un canal de entrada: pi ya encamina el texto del host hacia los comandos de extensión y los hooks, así que solo un tipo de comando RPC nuevo necesitaría a pi (etiquetado como `Inference:` en 02); qué canal usar es una pregunta abierta ([ADR: Sin decidir](03-architecture/adr/README.md#sin-decidir--no-registrado)) |
| Cambia qué paquetes complementarios recibe un home | gentle-ai, y después una subida de la versión fijada en gentle-pi |
| Renderiza o actúa sobre datos que ya circulan por el canal, o cambia el proceso, el IPC o el empaquetado del escritorio | Este repositorio |

Los repositorios upstream tienen sus propias reglas **[upstream]**; hay que seguirlas allí, no aquí:

- **pi:** los issues y las PR de contribuidores nuevos se cierran automáticamente por defecto, y no se acepta ninguna PR sin la aprobación previa del mantenedor (`lgtm`) (`pi@a13d35a:CONTRIBUTING.md:23`, `:31-34`, `:58`; pi 1.0.0). Resumen en [04 §Cómo proponer cambios del contrato en upstream](04-rpc-contract.md#cómo-proponer-cambios-del-contrato-en-upstream).
- **gentle-shell:** no existe ningún `CONTRIBUTING.md` en `ac67159` (`main`, versión de paquete 4.0.0); tiene formularios de issue para bugs y funcionalidades ([04 §Cómo proponer cambios del contrato en upstream](04-rpc-contract.md#cómo-proponer-cambios-del-contrato-en-upstream)).
- **gentle-ai:** "No PR without an issue. No exceptions." (`gentle-ai@ff77164:CONTRIBUTING.md:24-26`; v4.0.0). El trabajo solo puede empezar cuando el issue tiene `status:approved` (`:31`), y la CI rechaza automáticamente las PR no vinculadas a un issue aprobado (`:35`).

## Proponer ideas

Las ideas que van más allá de la paridad con gentle-shell se redactan como propuestas en [docs/07-proposals/](07-proposals/README.md#proceso): un archivo por idea con estado `proposed`, abierto como pull request y añadido al índice. Solo el mantenedor pasa una propuesta a `accepted` o `declined` (governance D7, **[community proposal]**). La visión del mantenedor se queda en [00-vision.md](00-vision.md) y no se edita para incluir ideas de la comunidad (`docs/README.md:37`).

## Flujo de trabajo

El mantenedor construyó M1 y M2 con esta práctica **[maintainer]**. Usarla para el trabajo de la comunidad es una **[community proposal]**.

| Práctica | Registrada en |
|---|---|
| Un documento de funcionalidad (feature document) de ODD por hito en `odd/tasks/`, con objetivo, alcance, restricciones, tareas, ruta, commits, comprobaciones y evidencia de revisión | `odd/tasks/desktop-m1-chat-core.md:3-75`; `odd/tasks/desktop-m2-helpers.md:5-53` |
| TDD estricto con vitest: "RED observed before implementation, GREEN, REFACTOR"; entorno Node para el proceso principal y el protocolo, jsdom para el renderer | `odd/tasks/desktop-m1-chat-core.md:27`; `odd/tasks/desktop-m2-helpers.md:26` |
| Estructura: Scope Rule, Screaming Architecture, contenedor/presentacional, diseño atómico bajo `shared/ui`, proceso principal hexagonal; el porqué de la forma del árbol está en `src/README.md` | `odd/tasks/desktop-m1-chat-core.md:29`; `src/README.md:5-51` |
| Reglas de React 19: imports con nombre, sin memoización manual, ref como prop | `odd/tasks/desktop-m1-chat-core.md:29` |
| Verificación en navegador del trabajo de UI a medida que se incorpora, mediante `pnpm dev:web` con el puente simulado, guardando capturas de pantalla como evidencia | `odd/tasks/desktop-m1-chat-core.md:29`; `odd/tasks/desktop-m2-helpers.md:26` |
| Comprobaciones en los criterios de aceptación: ambos hitos exigen `pnpm test`, `pnpm typecheck`, `pnpm build`; M1 añade que `pnpm package` produzca un build sin firmar; M2 añade `pnpm smoke:electron`, que M1 también ejecutó en la tarea T6 y en su cierre | `odd/tasks/desktop-m1-chat-core.md:50`, `:61`, `:65`; `odd/tasks/desktop-m2-helpers.md:43` |
| Artefactos técnicos en inglés, registro neutro | `odd/tasks/desktop-m1-chat-core.md:28` |
| Receipt-driven development (RDD) activado, consentimiento de revisión concedido de antemano por el mantenedor | `odd/tasks/desktop-m1-chat-core.md:31`; `odd/tasks/desktop-m2-helpers.md:26` |

Notas:

- El ajuste de TDD estricto está registrado con la fuente "user-level CLAUDE.md" (`odd/tasks/desktop-m1-chat-core.md:27`), no como una política del repositorio. `Inference:` ese archivo es la configuración propia del mantenedor, porque el mismo documento registra sus instrucciones para el hito (`:29`); no dice de quién es el archivo ([08 §Flujo de contribución](08-team.md#flujo-de-contribución) lo interpreta del mismo modo). Si vincula a quienes contribuyen es una cuestión [abierta](#preguntas-abiertas).
- `Inference:` el consentimiento de RDD concedido de antemano cubre los propios hitos del mantenedor; nada dice si las PR de la comunidad pasan por RDD ([08 §Preguntas abiertas](08-team.md#preguntas-abiertas)).
- Todavía no hay CI, así que nada ejecuta estas comprobaciones por quien contribuye (audit A16, [auditoría](03-architecture/audit.md#a16-carencias-de-cobertura-de-tests-y-de-ci)). **[community proposal]**: quienes contribuyen ejecutarían estas comprobaciones localmente y pegarían los resultados en la PR.

## Ramas, commits y pull requests

**Práctica registrada [maintainer]:**

- Conventional Commits; sin atribución a IA (`odd/tasks/desktop-m1-chat-core.md:28`).
- Cadena de ramas de funcionalidad: M1 registra la estrategia de entrega `ask-on-risk` con la estrategia de cadena `feature-branch-chain` "cached from this session" (`odd/tasks/desktop-m1-chat-core.md:30`). Una rama de seguimiento (`feat/desktop-m1-chat-core`) tiene ramas de porción (`feat/desktop-m1-1-scaffold`, …); la PR de la primera porción apunta a la rama de seguimiento, las porciones posteriores apuntan a la porción anterior, y solo la rama de seguimiento se fusiona en `main`. No fusionar nunca una rama hija con `--delete-branch` hasta que la cadena esté completa (misma línea).
- M2 llama a su cadena una "cached choice" (`odd/tasks/desktop-m2-helpers.md:3`). Su línea de previsión dice "~900 authored changed lines (…) → feature-branch-chain" (`odd/tasks/desktop-m2-helpers.md:28`); ninguno de los dos documentos establece una regla de tamaño para cuándo usar una cadena.
- El documento de M1 registra las etiquetas `type:feature` y `size:exception` en la PR #4, la primera porción (`odd/tasks/desktop-m1-chat-core.md:32`). La API de GitHub (`gh pr list`, 2026-10-01) también muestra etiquetas `type:*`, y `size:exception` en algunas, en las PR #3 a #18; eso es estado de GitHub, no una práctica registrada en el repositorio.
- La cadena de M1 se fusionó en la rama de seguimiento y después en `main` por indicación del mantenedor (`odd/tasks/desktop-m1-chat-core.md:71`).

**Para las contribuciones de la comunidad [community proposal]:**

- Un quick win o un cambio coherente por PR, con sus tests y su documentación en la misma PR.
- No está decidido cuándo usar una cadena de ramas de funcionalidad: 08 pregunta si el grupo la adopta para todos los hitos o solo para los grandes ([preguntas abiertas](#preguntas-abiertas); [08 §Preguntas abiertas](08-team.md#preguntas-abiertas)).
- Los cambios del corpus se hacen como una pull request contra el documento (`docs/README.md:35-37`).
- La documentación del código que acompaña a un cambio (`src/README.md`, la sección de desarrollo del README) la escribe quien hace ese cambio ([08 §Documentación y comunidad](08-team.md#documentación-y-comunidad)).

## Entorno de desarrollo

**Requisitos** (`README.md:9-19`):

- Node.js 22.19 o posterior y pnpm 11 (`README.md:11`). `package.json` no declara ningún campo `engines` ni `packageManager`, así que nada impone estas versiones.
- El lanzador `gentle-shell`, distribuido con gentle-pi 3.7.0 o posterior (`README.md:12-17`); la versión actual del paquete es 4.0.0 (`gentle-shell@ac67159:package.json:3`):

  ```sh
  npm install -g gentle-pi
  gentle-shell --version
  ```

- Un proveedor de modelos con sesión iniciada mediante pi o `gentle-shell --isolated` (`README.md:21-30`).

**Ejecutar desde el código fuente** (`README.md:34-40`). El paso de descarga de Electron procede del README, no de un script de `package.json`:

```sh
pnpm install
node node_modules/electron/install.js   # downloads the Electron binary; pnpm may skip it
pnpm dev
```

**Scripts** (`package.json:10-24`; descripciones tomadas de `README.md:95-108`, `:116`):

| Comando | Qué hace |
|---|---|
| `pnpm dev` | Ejecuta la aplicación Electron + React |
| `pnpm dev:web` | Ejecuta solo el renderer en una pestaña del navegador, http://localhost:5173, con un puente simulado (`odd/tasks/desktop-m1-chat-core.md:29`) |
| `pnpm dev:local-pi` | Ejecuta la aplicación contra un checkout local de gentle-pi (por defecto `../gentle-pi-worktrees/desktop-integration`). Usa sintaxis de shell POSIX (`package.json:23`); la PR abierta #27 (sin fusionar a fecha de 2026-10-03) lo hace multiplataforma |
| `pnpm test` / `pnpm test:watch` | Ejecuta la batería de vitest una vez / en modo watch |
| `pnpm typecheck` | Comprueba los tipos del proceso principal, el preload y el renderer |
| `pnpm build` | Construye el proceso principal, el preload y el renderer |
| `pnpm smoke:electron` | Construye, lanza la entrada principal empaquetada mediante Playwright y verifica que aparece la ventana |
| `pnpm package`, `package:mac`, `package:win`, `package:linux` | Construye una aplicación sin firmar en `release/` |

`package.json` también define `pnpm preview` (`electron-vite preview`, `package.json:14`); el README no lo describe.

**Variables de entorno:**

| Variable | Efecto | Fuente |
|---|---|---|
| `GENTLE_SHELL_BIN` | Ruta al lanzador (el `bin/gentle-shell.mjs` de un checkout de gentle-pi u otro ejecutable de gentle-shell); en caso contrario se usa `gentle-shell` del `PATH` | `README.md:110`; `src/main/adapters/launcherLocator.ts` |
| `GENTLE_SHELL_INTERACTIVE_HOST=1` | La establece la aplicación en el proceso de pi que lanza, para que gentle-pi publique la actividad de los helpers y habilite los diálogos RPC; no hay que establecerla manualmente | `README.md:89-91`, `:112`; `odd/tasks/desktop-m2-helpers.md:11` |

Solo se ha probado macOS (Apple silicon); los builds de Windows y Linux están configurados pero no probados (`README.md:7`). Para la configuración por plataforma de pi, gentle-shell, gentle-ai y engram, y los problemas conocidos de Windows (audit A4, A18), ver [docs/10-platforms.md](10-platforms.md).

## Informar de errores

- Usar el formulario de informe de errores de los issues de GitHub (`README.md:66`). Pide una búsqueda de duplicados, una comprobación de datos sensibles, los pasos para reproducir, el comportamiento esperado y el real, las versiones y el sistema operativo, y aplica las etiquetas `bug` y `status:needs-review` (`.github/ISSUE_TEMPLATE/bug_report.yml:1-91`).
- **Problema conocido:** ambos formularios de issue se copiaron de gentle-pi y todavía lo nombran (`.github/ISSUE_TEMPLATE/bug_report.yml:2`, `:30`, `:57`; `feature_request.yml:2`). Corregirlos es el quick win de la hoja de ruta [QW-11](09-roadmap.md#qw-11-formularios-de-issues-y-contributing). Hasta entonces, **[community proposal]**, rellenar el formulario así (los formularios se quedan como están):
  - *Problem* (`bug_report.yml:26-32`): donde dice gentle-pi, describir el efecto en Gentle Desktop. Poner el commit del escritorio (o la versión de la aplicación) en su primera línea; el formulario no tiene ningún campo para ello.
  - *gentle-pi version* (obligatorio, `bug_report.yml:54-60`): la versión del paquete gentle-pi que distribuye el lanzador `gentle-shell` en uso, o su commit si el lanzador se ejecuta desde un checkout (`GENTLE_SHELL_BIN`).
  - *Pi version* (obligatorio, `bug_report.yml:62-68`): la versión de pi. `gentle-shell --version` imprime las versiones de gentle-shell, de pi y del home (`README.md:16`); pegar también esa salida en *Problem*.
- Consultar primero las [limitaciones conocidas](https://github.com/Gentleman-Programming/gentle-shell-desktop/blob/5ab4a00b0aefc249460dcf8d0bcef9adac495fd4/README.md#known-limitations): por ejemplo, el Stop de los helpers está deshabilitado a propósito (`README.md:62`).
- Un error en el propio pi o en gentle-shell corresponde a ese repositorio ([Dónde corresponde un cambio](#dónde-corresponde-un-cambio)).

## Preguntas abiertas

Ninguna fuente las responde; esta guía no las responde ([08 §Preguntas abiertas](08-team.md#preguntas-abiertas)):

- Quién revisa y fusiona las PR de la comunidad.
- Si las PR de la comunidad pasan por RDD, y con el consentimiento de quién.
- Si el TDD estricto es una regla del repositorio para quienes contribuyen.
- Si el grupo adopta la cadena de ramas de funcionalidad para todos los hitos, o solo para los hitos grandes.
