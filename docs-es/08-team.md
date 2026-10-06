> Traducción al español de `docs/08-team.md` (árbol de trabajo tras la actualización del 2026-10-03). Documento de lectura; la versión de referencia es la inglesa.

# Equipo y gobernanza

> Estado: borrador, propuesta de la comunidad pendiente de revisión del grupo y del mantenedor (draft (community proposal, awaiting group and maintainer review)).

> **Borrador de la comunidad.** Esta página propone cómo un grupo de trabajo de la comunidad podría repartirse el trabajo en Gentle Desktop y cómo se toman las decisiones. Nada de lo que aquí figura está decidido hasta que el grupo y el mantenedor estén de acuerdo. No se asigna a ninguna persona a ningún área: todos los responsables son `TBD`, y las personas se propondrán ellas mismas más adelante.

**En un párrafo.** El mantenedor pidió a la comunidad que presentara una hoja de ruta, se repartiera las tareas y presentara PR **[maintainer]** (Discord, Alan Buscaglia, 2026-09-27). Un miembro de la comunidad propuso un grupo de trabajo con áreas de competencia, cada una con un responsable, más una hoja de ruta y un MVP, presentados a los mantenedores como grupo **[community proposal]** (Discord, Matrak, 2026-09-27). Esta página concreta esas áreas a partir de las evidencias del corpus: siete áreas más tres aspectos transversales, con un alcance vinculado a hallazgos de la auditoría, carencias (gaps) del RPC, ADR, filas del inventario y pantallas.

## Cómo leer esta página

| Etiqueta | Fuente | Peso |
|---|---|---|
| **[maintainer]** | Los mensajes de Discord de Alan Buscaglia y los documentos del repositorio del escritorio escritos por el mantenedor (`README.md`, `odd/tasks/desktop-m1-*.md`, `odd/tasks/desktop-m2-*.md`) | Intención declarada o práctica registrada. |
| **[upstream]** | Los propios archivos de los repositorios upstream (repositorio de origen) (pi, gentle-shell) | Reglas que el grupo del escritorio no controla. |
| **[community proposal]** | Esta página, otras páginas del corpus y los mensajes de Discord de miembros distintos del mantenedor | Propuesto. No decidido. |

`Inference:` marca un razonamiento, no un hecho declarado. `UNVERIFIED:` marca una afirmación que se comprobó pero no se confirmó.

**Claves de cita.** `gentle-shell-desktop@5ab4a00:` es la rama `main` del repositorio del escritorio. Las rutas como `03-architecture/audit.md` son páginas del corpus en `docs/`. Las fechas de Discord se han convertido desde el formato `d/m/yy` del hilo (copia guardada del hilo "Gentle Desktop", no está en el repositorio). Los ID de otras páginas llevan su página (`audit A3`, `gap G9`, `inventory C20`, `vision Q1`, `UX U9`, `design D1`, `SCR-01`); un cualificador abarca los ID que le siguen (`audit A3, A11`). M1 y M2 sin cualificar son los hitos del mantenedor, no filas del inventario; D1–D12 son las reglas de gobernanza de esta página.

**ID.** Los ID del corpus se repiten entre páginas, así que esta página siempre los cualifica: `audit A3` ([auditoría](03-architecture/audit.md#resumen)), `gap G1` ([contrato RPC](04-rpc-contract.md#carencias-que-necesita-el-escritorio)), `inventory C17` ([inventario de capacidades](05-capability-inventory.md)), `UX U11` ([principios de UX](06-ux/principles.md)), `design D5` ([diferencias del sistema de diseño](06-ux/design-system.md#diferencias)), `ADR 0005` ([índice de ADR](03-architecture/adr/README.md#índice)), `SCR-03` ([pantallas](06-ux/screens.md#de-un-vistazo)), `vision Q2` ([visión](00-vision.md#preguntas-abiertas-para-el-mantenedor)).

**Los archivos del repositorio no nombran a ningún mantenedor del escritorio** ([02-ecosystem §Responsables](02-ecosystem.md#responsables)). Esta página usa "mantenedor" para Alan Buscaglia, tal como lo etiqueta el hilo de Discord y como los documentos de M1 y M2 se refieren a "Maintainer instructions" y "Maintainer decisions" (`gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m1-chat-core.md:29`, `:75`).

## De un vistazo

| Área | Lidera | Responsable | Número de personas **[community proposal]** |
|---|---|---|---|
| [Núcleo y contrato RPC](#núcleo-y-contrato-rpc) | Proceso principal, host de sesión, análisis del protocolo, IPC; el servicio host propuesto, si se acepta [0004](07-proposals/0004-host-service.md) | `TBD` | 2–3 |
| [Integración upstream](#integración-upstream-pi--gentle-shell--gentle-ai) | Cambios que el escritorio necesita en pi, gentle-shell o gentle-ai | `TBD` | 2–3 |
| [Frontend](#frontend) | Renderer: pantallas y componentes | `TBD` | 2–4 |
| [UX y diseño](#ux-y-diseño) | Principios, especificaciones de pantallas, tokens de diseño | `TBD` | 1–2 |
| [QA y pruebas de extremo a extremo](#qa-y-pruebas-de-extremo-a-extremo) | Fixtures, pruebas de contrato, smoke, comprobaciones con el runtime real | `TBD` | 1–2 |
| [Plataforma y distribución](#plataforma-y-distribución) | Windows/Linux/macOS, empaquetado, infraestructura de CI | `TBD` | 1–2 |
| [Documentación y comunidad](#documentación-y-comunidad) | Este corpus, mantenimiento de la hoja de ruta, documentación para contribuidores, canales | `TBD` | 1–2 |
| [Aspectos transversales](#aspectos-transversales) | Accesibilidad, rendimiento, seguridad | `TBD` un custodio para cada uno | 0 dedicadas |

Los rangos de número de personas son una propuesta. Cada uno se deriva de la cantidad de evidencias dentro del alcance (recuentos más abajo), no de quién está disponible. `Inference:` una persona puede cubrir más de un área mientras el grupo sea pequeño.

## Áreas de responsabilidad

Las siete áreas proceden del esqueleto de esta página. El mensaje de Matrak nombró "UX, accesibilidad, performance, diseño" como ejemplos de áreas (Discord, Matrak, 2026-09-27). Este borrador fusiona UX y diseño en un área, porque el corpus cubre ambos en una carpeta ([06-ux](06-ux)). Trata la accesibilidad y el rendimiento como [aspectos transversales](#aspectos-transversales) en lugar de áreas, porque cada uno afecta a todas las áreas y la auditoría no cubrió ninguno de los dos (`03-architecture/audit.md:18`), así que todavía no hay evidencias para dimensionar un área aparte.

### Cómo se asignan las filas del inventario

**[community proposal]** El [inventario de capacidades](05-capability-inventory.md#resumen-de-cobertura) tiene 158 filas (81 de pi core, 77 de gentle-shell y gentle-ai; recontadas tras la actualización del 2026-10-03, que añadió inventory V19 e Y6). Su columna "Exposed over RPC" decide quién lidera una fila:

| "Exposed over RPC" | Filas | Lidera | Colabora |
|---|---|---|---|
| yes | 43 | Núcleo (conectar los datos) | Frontend (mostrarlos) |
| partial | 38 | Núcleo | Integración upstream (la parte que falta), Frontend |
| no | 47 | Integración upstream | Núcleo, Frontend una vez que llegue el cambio upstream |
| host-side | 9 | Frontend | Núcleo |
| spawn | 13 | Núcleo (argumentos de lanzamiento) | Plataforma |
| n/a | 8 | ninguna para siete filas de mecánica de la terminal (inventory C16, U1, U3, U6, L10, L11, Y3; [screens §Filas sin pantalla](06-ux/screens.md#filas-sin-pantalla)); inventory U7 se integra en SCR-09, así que la muestra Frontend | — |

Los recuentos son los totales del [resumen de cobertura](05-capability-inventory.md#resumen-de-cobertura). Por separado, 56 de las 158 filas tienen una celda "Upstream dependency" que no empieza por "none". Regla de recuento de esta página: dividir cada fila por los `|` no escapados, tomar la sexta celda y comprobar si empieza por "none". Cinco filas cuya celda empieza por "none" también nombran una carencia: inventory V1 ("none (queue); G2 (phase)") depende de gap G2 para parte de la fila, e inventory S7, K3, K4 ("none (G7)", "none (see G7)") y L3 ("none (G10)") apuntan a una carencia. Si también se cuenta inventory V1, el resultado es 57; si se cuenta cada celda que nombra una carencia, es 61. Volver a contar cuando cambie el inventario.

### Núcleo y contrato RPC

**Alcance**
- **Proceso principal y host de sesión.** El proceso principal hexagonal y el puente (bridge) de preload tipado: ADR [0002](03-architecture/adr/0002-process-roles-and-typed-preload-bridge.md), [0003](03-architecture/adr/0003-hexagonal-main-process.md), [0005](03-architecture/adr/0005-gentle-shell-rpc-child-process.md), [0006](03-architecture/adr/0006-in-process-session-list.md), [0011](03-architecture/adr/0011-helpers-scoped-per-chat.md), [0012](03-architecture/adr/0012-interactive-host-env-flag.md).
- **Varios chats.** Audit A3 (Alta), A11, A1, en el orden que recomienda la auditoría ([audit §1. Desbloquear el uso de varios chats](03-architecture/audit.md#1-desbloquear-el-uso-de-varios-chats)); gap G9 es trabajo del escritorio, no un cambio upstream ([04 §Carencias que necesita el escritorio](04-rpc-contract.md#carencias-que-necesita-el-escritorio)).
- **Corrección de la capa de protocolo.** Audit A2, A5 (con Integración upstream), A6, A7, A8, A10, A12, A13 (con Frontend), A19 (con Integración upstream).
- **Endurecimiento del IPC.** Audit A14 (ver [seguridad](#aspectos-transversales)).
- **Reglas de estructura en `src/main`.** La parte de audit A17 relativa al proceso principal (importaciones de `home.ts`, marcador de posición obsoleto).
- **Inventario.** Filas expuestas sobre RPC como yes, partial o spawn ([tabla de asignación](#cómo-se-asignan-las-filas-del-inventario)). Se reparten entre 14 de los 17 grupos del inventario; los mayores son Conversation and input (16), Shell experience (14), Sessions (13), Integrations, skills, memory and diagnostics (10) y Helpers (8) (yes + partial + spawn por grupo en el [resumen de cobertura](05-capability-inventory.md#resumen-de-cobertura)).
- **Arquitectura sin decidir.** Prepara las evidencias para siete de los nueve candidatos de [ADR "Undecided / not recorded"](03-architecture/adr/README.md#sin-decidir--no-registrado): un hijo por chat frente a un host compartido, solo RPC frente a mixto, prompt mientras trabaja, política de compatibilidad de versiones (vision Q3–Q6), el canal del host hacia las funcionalidades de gentle-shell (con Integración upstream, ya que cada alternativa modifica pi o gentle-shell), y la ubicación del proceso y la ubicación de la configuración del servicio host (con Plataforma). Los decide el mantenedor ([gobernanza](#cómo-se-toman-las-decisiones)). **[community proposal]** Si el mantenedor acepta la [propuesta 0004](07-proposals/0004-host-service.md), Núcleo también es responsable del propio servicio host: registro de sesiones, raíz de composición y el [protocolo del host](12-host-protocol.md) ([11](11-host-service.md); sus requisitos del runtime B1–B6 son en su mayoría el trabajo de varios chats y de corrección descrito arriba).

**Fuera de alcance**
- Representación y diseño visual: Frontend y UX.
- Cualquier cambio en la unión `RpcCommand` de pi o en gentle-shell: Integración upstream.
- Empaquetado y lanzamiento específico de cada sistema operativo (audit A4): Plataforma.

**Responsable:** `TBD`.

**Número de personas: 2–3** **[community proposal]**. Justificación: 14 hallazgos de la auditoría están en este alcance (audit A1, A2, A3, A5, A6, A7, A8, A10, A11, A12, A13, A14, A17 en parte, A19; regla de recuento: todo hallazgo nombrado en el alcance anterior, incluidos los compartidos y los parciales, como en las demás áreas), entre ellos el único hallazgo Alta que bloquea varias superficies (audit A3 es un bloqueo principal de SCR-01 y SCR-06 en [screens §De un vistazo](06-ux/screens.md#de-un-vistazo); [audit §Riesgos para escalar la UI](03-architecture/audit.md#riesgos-para-escalar-la-ui) lo vincula con varios chats a la vez y con el panel de ODD), más 94 filas del inventario marcadas yes, partial o spawn. `Inference:` la secuencia de varios chats es en serie (audit A3, luego A11, luego A1), así que más de tres personas se esperarían unas a otras.

**Interfaces**
- Frontend: los tipos del puente de preload (`src/shared/bridge-types.ts`, ADR 0002) son el contrato entre ambos.
- Integración upstream: handshake de versión (gap G10, audit A8), estados reales de los helpers (audit A5).
- QA: fixtures y pruebas de contrato para el parser.

**Competencias:** proceso principal de Electron e IPC; TypeScript estricto; procesos hijo de Node y JSON delimitado por líneas; arquitectura hexagonal; vitest en el entorno de Node (`gentle-shell-desktop@5ab4a00:package.json:15`, `:39`; `gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m1-chat-core.md:26-27`); lectura de los tipos RPC de pi (`pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts`, pi 1.0.0).

### Integración upstream (pi / gentle-shell / gentle-ai)

gentle-pi y gentle-shell son un único paquete (`gentle-shell@ac67159:package.json`, `main` de gentle-shell, versión de paquete 4.0.0; [02-ecosystem](02-ecosystem.md)), así que esta área se titula por repositorio: pi, gentle-shell (paquete `gentle-pi`) y gentle-ai.

**Alcance**
- **Carencias del RPC que necesitan un cambio upstream.** Gaps G1–G8 y G10. `Inference` (a partir de [02 §Dónde corresponde cada cambio](02-ecosystem.md#dónde-corresponde-cada-cambio), etiquetado a su vez como `Inference`): gaps G3, G4, G5 y G10 corresponden a pi; gaps G2, G6, G7 y G8 a gentle-shell; gap G1 a gentle-shell; el canal (las entradas de extensión existentes de pi, un tipo de comando nuevo de pi o un canal propio de gentle-shell) está abierto ([ADR: Sin decidir](03-architecture/adr/README.md#sin-decidir--no-registrado)).
- **Comandos de gentle-shell que fallan bajo RPC.** Inventory P1, P3, Y4, R3 ([02 §Dónde corresponde cada cambio](02-ecosystem.md#dónde-corresponde-cada-cambio)).
- **Comportamiento del lanzador (launcher).** Progreso de la configuración legible por máquina para audit A9 (inventory L5), semántica del home para audit A19.
- **gentle-ai fuera de la sesión.** Inventory GA1–GA5 ([05](05-capability-inventory.md#gentle-ai-fuera-de-la-sesión)).
- **Inventario.** Las 47 filas marcadas "no" sobre RPC ([tabla de asignación](#cómo-se-asignan-las-filas-del-inventario)).
- **Requisitos previos pendientes.** "Real data requires gentle-pi with `rpc-interactive-host` (gentle-shell #1328, #1329, P3 pending)" **[maintainer]** (`gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m2-helpers.md:59`). "P3" ahí es un elemento de trabajo de gentle-pi que el documento de M2 no define más (`:69` nombra "the P3 branch"); no es inventory P3.
- **Seguir el proceso de cada repositorio.** pi exige la aprobación previa del mantenedor antes de una PR, mediante una issue de Contribution Proposal **[upstream]** (`pi@a13d35a:.github/ISSUE_TEMPLATE/contribution.yml:1`; `pi@a13d35a:CONTRIBUTING.md:31-34`, `:58`; [04 §Cómo proponer cambios del contrato en upstream](04-rpc-contract.md#cómo-proponer-cambios-del-contrato-en-upstream)). gentle-shell no tiene `CONTRIBUTING.md` en `ac67159` y usa un formulario de solicitud de funcionalidad ([04](04-rpc-contract.md#gentle-shell-gentleman-programminggentle-shell-paquete-gentle-pi-responsable-de-los-añadidos-a-nivel-de-extensión)).

**Fuera de alcance**
- Consumir en el escritorio una nueva capacidad upstream: Núcleo y Frontend.
- Proyectos de la comunidad fuera del ecosistema fijado, como gentle-mesh ([02 §Proyectos de la comunidad fuera de alcance](02-ecosystem.md#proyectos-de-la-comunidad-fuera-de-alcance)).
- Decidir el diseño upstream. Lo deciden los mantenedores upstream.

**Responsable:** `TBD`.

**Número de personas: 2–3** **[community proposal]**. Justificación: 9 carencias upstream en dos repositorios con reglas de contribución distintas, 47 filas del inventario marcadas "no" y una base de código en Go (gentle-ai) junto a dos en TypeScript. `Inference:` el ritmo está condicionado por la revisión upstream (pi cierra automáticamente por defecto las PR de contribuidores nuevos, `pi@a13d35a:CONTRIBUTING.md:23`), así que más personas no acelerarían esta área.

**Interfaces**
- Núcleo: acuerda cada nuevo comando, evento o forma de carga antes de proponerlo upstream.
- Documentación y comunidad: enlaza las issues upstream desde la hoja de ruta.
- QA: pruebas de contrato frente a los esquemas upstream publicados (por ejemplo `gentle-agents.activity/v1`, [04 §Versionado y compatibilidad](04-rpc-contract.md#versionado-y-compatibilidad)).

**Competencias:** TypeScript en pi (`packages/coding-agent`) y en las extensiones de gentle-shell; Go para gentle-ai (el inventario cita fuentes en Go bajo su clave `GAI:`, `gentle-ai@ff77164:internal/...`, gentle-ai v4.0.0, [05 §Método (parte de gentle-shell)](05-capability-inventory.md#método-parte-de-gentle-shell); [02 §Versiones y compatibilidad](02-ecosystem.md#versiones-y-compatibilidad)); el modo RPC y la UI de extensiones de pi; redactar issues upstream breves y bien fundamentadas.

### Frontend

**Alcance**
- **Pantallas.** Implementar [SCR-01 a SCR-19](06-ux/screens.md#de-un-vistazo). Tres existen en parte (SCR-01, SCR-02, SCR-03) y SCR-09 existe en parte; las otras 15 no existen.
- **Arquitectura del renderer.** ADR [0004](03-architecture/adr/0004-renderer-scope-rule-and-screaming-architecture.md) (Scope Rule, Screaming Architecture, contenedor/presentacional, `shared/ui` atómico), [0007](03-architecture/adr/0007-text-only-chat-view.md), [0010](03-architecture/adr/0010-standalone-renderer-with-mock-bridge.md).
- **Hallazgos de la auditoría.** Audit A15 (recurso silencioso al puente simulado; con Plataforma), la parte de audit A17 relativa al renderer (`shared/markdown` con un único consumidor, referencia colgante a una nota), audit A13 (con Núcleo).
- **Inventario.** Filas host-side (9) y la mitad de superficie de cada fila que conecta Núcleo. Ejemplos nombrados en [02](02-ecosystem.md#dónde-corresponde-cada-cambio): notificaciones de `notify` (inventory C20), tarjetas de herramienta (inventory C17), redirección (inventory C4).
- **Implementación del tema.** ADR [0009](03-architecture/adr/0009-hardcoded-gentleman-cute-theme.md) y las correcciones de tokens de design D1–D12, una vez que UX las decida.

**Fuera de alcance**
- Qué debe mostrar una pantalla y cómo se lee: UX y diseño.
- Análisis del protocolo y estado de la sesión: Núcleo.

**Responsable:** `TBD`.

**Número de personas: 2–4** **[community proposal]**. Justificación: 19 pantallas, 15 de ellas sin empezar; las pantallas de la maqueta (SCR-01 a SCR-09) y las derivadas del inventario (SCR-10 a SCR-19) pueden avanzar en paralelo una vez que se despejen sus bloqueos. `Inference:` la mayoría de las pantallas nuevas están bloqueadas por carencias (por ejemplo SCR-04 por gap G2, SCR-07 por gaps G3 y G4), así que el extremo superior solo compensa una vez que Integración upstream entregue.

**Interfaces**
- Núcleo: el contrato del puente.
- UX: especificaciones de pantallas y tokens.
- QA: pruebas de componentes y evidencias de verificación en navegador.

**Competencias:** React 19 (`gentle-shell-desktop@5ab4a00:package.json:45-46`) con las reglas `react-19` del mantenedor (importaciones con nombre, sin memoización manual, ref como prop) **[maintainer]** (`gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m1-chat-core.md:29`); TypeScript estricto; Vite y `electron-vite`; vitest con jsdom y Testing Library (`gentle-shell-desktop@5ab4a00:package.json:26-27`, `:35`); propiedades personalizadas de CSS.

### UX y diseño

**Alcance**
- **Principios.** UX [U1–U12](06-ux/principles.md#de-un-vistazo); UX U9, U10, U11 y U12 están etiquetados como community.
- **Especificaciones de pantallas y arquitectura de la información.** [Pantallas](06-ux/screens.md) y sus [preguntas abiertas](06-ux/screens.md#preguntas-abiertas) (qué pantallas derivadas están dentro del alcance, el panel de progreso del trabajo, una o varias pantallas de configuración).
- **Sistema de diseño.** Diferencias de tokens y componentes design D1–D12 ([sistema de diseño](06-ux/design-system.md#diferencias)) y cambio de tema ([§Temas](06-ux/design-system.md#temas)).
- **Preguntas de encuadre del producto** que llevar al mantenedor: vision Q1 (accesible frente a completo) y vision Q8 (perfiles).
- **Encuadre de UX de las propuestas de la comunidad** [0001](07-proposals/0001-agent-flow-graph.md)–[0003](07-proposals/0003-post-hoc-audit-by-questions.md), hasta que el mantenedor las acepte o las rechace.

**Fuera de alcance**
- Implementación: Frontend.
- Tratar los datos de ejemplo de la maqueta como requisitos. La maqueta es intención, no especificación ([vision §Cómo leer esta página](00-vision.md#cómo-leer-esta-página)).

**Responsable:** `TBD`.

**Número de personas: 1–2** **[community proposal]**. Justificación: 12 principios y 12 diferencias de diseño ya documentados; el trabajo abierto son 19 especificaciones de pantallas y tres preguntas abiertas a nivel de pantalla. `Inference:` una o dos personas mantienen coherente la voz del producto (vision P2, UX U1).

**Interfaces**
- Frontend: especificaciones y tokens.
- Custodio de accesibilidad: UX U10 y U11.
- Mantenedor: valida los principios y el encuadre del producto.

**Competencias:** diseño de interacción y visual; leer la maqueta conceptual (mockup) (`gs-mockup.html`) como intención; tokens de diseño; fundamentos de accesibilidad (UX U11); familiaridad con la TUI de gentle-shell, para que la paridad se juzgue a partir del producto real.

### QA y pruebas de extremo a extremo

**Alcance**
- **Audit A16.** Sin CI, fixtures no tomados de salidas reales, sin pruebas para la raíz de composición, las rutas del lanzador en Windows y `HelpersSummary`, y sin ejecución automatizada contra un gentle-shell real ([audit A16](03-architecture/audit.md#a16-carencias-de-cobertura-de-tests-y-de-ci)).
- **Fixtures reales y pruebas de contrato.** Grabar fixtures a partir de una ejecución real de gentle-shell; añadir una prueba de contrato frente al ejemplo de actividad publicado (recomendación de audit A16; vinculado a audit A5).
- **Reproducciones.** Reproducir audit A4 en Windows antes de cualquier corrección (recomendación de la auditoría [§3. Plataforma](03-architecture/audit.md#3-plataforma)); el issue #23 del escritorio informa del fallo con pasos de reproducción, pero los autores del corpus no lo han reproducido (audit A4).
- **Comprobaciones smoke y en navegador.** `pnpm smoke:electron` arranca la entrada principal empaquetada mediante Playwright (`gentle-shell-desktop@5ab4a00:README.md:107`); verificación en navegador del trabajo de UI con capturas de pantalla como evidencia **[maintainer]** (`gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m1-chat-core.md:29`).

**Fuera de alcance**
- Escribir las pruebas unitarias de cada funcionalidad. Con TDD estricto, eso lo hace cada autor ([flujo de contribución](#flujo-de-contribución)).
- Runners de CI y matriz de compilación: Plataforma.

**Responsable:** `TBD`.

**Número de personas: 1–2** **[community proposal]**. Justificación: un hallazgo Media de la auditoría (audit A16) con varias partes, más fixtures del runtime real y la reproducción en Windows. La batería existente ya es grande (286 pruebas al cierre de M2, `gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m2-helpers.md:59`), así que la carencia es la cobertura del comportamiento real, no el volumen.

**Interfaces**
- Plataforma: los trabajos de CI ejecutan las baterías de QA.
- Integración upstream: esquemas y salidas reales que grabar.
- Núcleo y Frontend: puntos de inserción para pruebas.

**Competencias:** vitest (`gentle-shell-desktop@5ab4a00:package.json:39`); Playwright (`:36`); pruebas de Electron; ejecutar gentle-shell en local con un home aislado (`gentle-shell-desktop@5ab4a00:README.md:29`); entornos de prueba de Windows y Linux.

### Plataforma y distribución

**Alcance**
- **Hallazgos de la auditoría y riesgos de plataforma.** Audit A4 (Alta: lanzamiento de `.cmd` en Windows), audit A9 (progreso del aprovisionamiento en el primer arranque; con Integración upstream), audit A18 (descubrimiento del lanzador y cobertura de plataformas), audit A15 (puente simulado en compilaciones empaquetadas; con Frontend); la matriz de soporte, las topologías de WSL y los riesgos PLAT-01 a PLAT-11 en [10-platforms.md](10-platforms.md#riesgos). Dos PR upstream abiertas son contribuciones externas en este alcance, sin fusionar a fecha de 2026-10-03: #26 (creación de procesos en Windows, audit A4; deja las rutas sin entrecomillar, PLAT-02) y #27 (`dev:local-pi` multiplataforma, audit A18). Revisarlas corresponde a esta área; contribuir con una PR no convierte a nadie en responsable del área.
- **Infraestructura de CI.** El flujo de trabajo que recomienda audit A16, con un trabajo de Windows una vez que llegue audit A4 ([audit §3. Plataforma](03-architecture/audit.md#3-plataforma)).
- **Empaquetado.** Destinos de `electron-builder` para macOS, Windows y Linux (`gentle-shell-desktop@5ab4a00:package.json:18-21`). Solo se ha probado macOS (Apple silicon), y no hay compilaciones firmadas (`gentle-shell-desktop@5ab4a00:README.md:7`). **[community proposal]** Si se acepta la [propuesta 0004](07-proposals/0004-host-service.md), también el empaquetado del servicio host, su ciclo de vida por sistema operativo y su ubicación en Windows o en WSL ([10, Servicio host](10-platforms.md#servicio-host-propuesta-0004); CT-03, CT-04 en [13](13-clients-and-topologies.md#preguntas-abiertas); PLAT-12 a PLAT-14).
- **Distribución del runtime.** Prepara las evidencias para la cuestión sin decidir de "runtime incluido frente a externo" (vision Q2, [ADR not recorded](03-architecture/adr/README.md#sin-decidir--no-registrado)). La decide el mantenedor.

**Fuera de alcance**
- Comportamiento del lanzador dentro de gentle-shell: Integración upstream.
- Contenido de las pruebas: QA.

**Responsable:** `TBD`.

**Número de personas: 1–2** **[community proposal]**. Justificación: cuatro hallazgos de la auditoría (uno Alta), 11 riesgos de plataforma (PLAT-01 a PLAT-11; tres calificados como Alta, dos de ellos solo para un público o una topología), tres sistemas operativos de destino con uno probado y sin CI. `Inference:` el acceso a máquinas Windows y Linux importa más que el número de personas.

**Interfaces**
- QA: trabajos de CI.
- Núcleo: argumentos de lanzamiento y descubrimiento del lanzador (filas del inventario marcadas "spawn").
- Integración upstream: salida del aprovisionamiento del lanzador (audit A9).

**Competencias:** `electron-builder` y `electron-vite` (`gentle-shell-desktop@5ab4a00:package.json:33-34`); `child_process` de Node en Windows; `PATH` de macOS y firma de aplicaciones; configuración de CI (todavía no existe ningún flujo de trabajo, así que no se ha elegido proveedor de CI; audit A16).

### Documentación y comunidad

**Alcance**
- **Este corpus.** De `docs/00` a `docs/10`, el índice de ADR y el índice de propuestas. Mantener actualizado el inventario ([05 §Cómo mantenerlo al día](05-capability-inventory.md#cómo-mantenerlo-al-día)).
- **Mantenimiento de la hoja de ruta.** [09-roadmap](09-roadmap.md) se deriva de las otras páginas ([issue #28, "Author's framing: scope of the corpus"](https://github.com/Gentleman-Programming/gentle-shell-desktop/issues/28)). Presentarla es el paso 1 del proceso del mantenedor **[maintainer]** (Discord, Alan Buscaglia, 2026-09-27).
- **Infraestructura para contribuidores.** No hay archivo `CONTRIBUTING` en `main` ([issue #28, "Author's framing: facts checked before writing"](https://github.com/Gentleman-Programming/gentle-shell-desktop/issues/28)). Los formularios de issues siguen nombrando gentle-pi (`gentle-shell-desktop@5ab4a00:.github/ISSUE_TEMPLATE/bug_report.yml:2`, `feature_request.yml:2`).
- **Canales.** Mantener actualizados los [canales de comunicación](#canales-de-comunicación), incluida la solicitud de Discussions.
- **El registro de propuestas.** El [índice y la lista "mencionado, no propuesto"](07-proposals/README.md#mencionado-en-la-comunidad-no-propuesto).

**Fuera de alcance**
- Decidir qué entra en la visión, en la hoja de ruta o en el estado de una propuesta: el mantenedor ([gobernanza](#cómo-se-toman-las-decisiones)).
- La documentación del código que acompaña al cambio (`src/README.md`, sección de desarrollo del README): el autor de ese cambio.

**Responsable:** `TBD`.

**Número de personas: 1–2** **[community proposal]**. Justificación: ya existen nueve archivos Markdown de primer nivel (ocho páginas numeradas y el índice `README.md`) y tres carpetas (`03-architecture`, `06-ux`, `07-proposals`) que contienen cinco páginas más, 12 ADR, tres propuestas y dos índices; el trabajo abierto es el mantenimiento, la documentación para contribuidores y dos formularios de issues desfasados.

**Interfaces:** todas las áreas (cada página tiene un área de referencia: 03 y 04 con Núcleo, 05 con Núcleo e Integración upstream, 06 con UX, 10 con Plataforma y distribución). Mantenedor: validación de la visión y de la hoja de ruta.

**Competencias:** redacción técnica en inglés, registro neutro **[maintainer]** (`gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m1-chat-core.md:28`); disciplina de citas ([issue #28, "Author's framing: corpus rules"](https://github.com/Gentleman-Programming/gentle-shell-desktop/issues/28), regla 1); Markdown y Mermaid; formularios de issues de GitHub.

### Aspectos transversales

**[community proposal]** Cada aspecto tiene un custodio (`TBD`) que comprueba el trabajo de cada área en relación con él. Un custodio no es un equipo aparte.

| Aspecto | Evidencias hoy | Comprobaciones del custodio | Áreas principales |
|---|---|---|---|
| **Accesibilidad** | Nombrada como área por Matrak (Discord, 2026-09-27). Regla propuesta UX [U11](06-ux/principles.md#u11-accesible-por-defecto) y paridad de teclado UX [U10](06-ux/principles.md#u10-paridad-de-teclado-con-la-cli), ambas **[community]**. No cubierta por la auditoría (`03-architecture/audit.md:18`). | Alcance por teclado, foco, regiones activas, movimiento reducido (regla UX U11). | UX, Frontend, QA |
| **Rendimiento** | Nombrado como área por Matrak (Discord, 2026-09-27). El rendimiento de representación y el tamaño de la aplicación empaquetada no están cubiertos por la auditoría (`03-architecture/audit.md:18`). No existe ninguna medición en el corpus. | `Inference:` primero una línea base (arranque, chats largos, muchos helpers), ya que todavía no se ha medido nada. | Núcleo, Frontend, Plataforma |
| **Seguridad** | Audit A14 (validación del IPC, sandbox, CSP sin `'unsafe-eval'`, protección `will-navigate`) y audit A15 (puente simulado en compilaciones empaquetadas). **[community proposal]** Si se acepta la [propuesta 0004](07-proposals/0004-host-service.md): la autenticación y la validación de argumentos del servicio host (requisito B4 de la propuesta 0004), las comprobaciones de `Origin` ([0004, Propuesta](07-proposals/0004-host-service.md#propuesta)), el modelo de autenticación más allá de loopback (HP-02) y una credencial en loopback (HP-07) ([12, Autenticación y origen](12-host-protocol.md#autenticación-y-origen)). | Superficie del IPC y comportamiento de la compilación empaquetada; para el servicio host, cada socket de escucha y sus credenciales. | Núcleo, Plataforma, Frontend |

## Interés expresado en el hilo

**No son asignaciones.** Lo que dijo cada persona, citado del hilo de Discord. Los responsables siguen siendo `TBD` hasta que las personas se propongan.

| Quién | Fecha | Qué dijo |
|---|---|---|
| memoTux | 2026-09-26, 2026-09-29, 2026-09-30 | "Presente."; propuso el proceso de [§Cómo se toman las decisiones](#cómo-se-toman-las-decisiones); compartió una hoja de ruta extraída del repositorio; dijo que elaboraría una propuesta de hoja de ruta. |
| SteLMV | 2026-09-26 | "Me sumo de igual forma en ambos casos" (me uno en cualquier caso). |
| basb7 | 2026-09-26 | Había enviado al mantenedor una demo alfa construida con Tauri + Rust; "interesado en seguir con el desarrollo de gentle desktop"; "el lunes me pongo al día para empezar a aportar" (el lunes me pondré al día para empezar a contribuir). |
| MAYLOVE | 2026-09-26 | Probó en Windows e informó de `spawn EINVAL` (audit A4); "carga sesiones bien" (carga bien las sesiones). |
| eSagraDEV | 2026-09-26, 2026-09-27 | "luego me pongo a testear y a ver que podemos mejorarle" (lo probaré y veré qué podemos mejorar); "como hacemos pa contribuir" (cómo contribuimos). |
| Mauroo | 2026-09-27 | "Yo me sumo !" (me apunto). |
| vudumstead | 2026-09-27 | "voy apoyar" (voy a apoyar). |
| Erick | 2026-09-27 | "me hare el tiempo ... para poder dar mi aporte" (sacaré tiempo para contribuir). |
| Matrak | 2026-09-26, 2026-09-27, 2026-09-30 | Propuso "armar un grupo de trabajo y postularnos como grupo a Alan" (formar un grupo de trabajo y presentarnos como grupo a Alan) (09-26); propuso áreas de competencia con responsables (09-27); se ofreció a revisar la hoja de ruta de memoTux y darle su opinión (09-30). |
| gc | 2026-09-29 | Dijo que está desarrollando una versión de escritorio (interfaz en Electron, pi/gentle-shell por debajo). No expresó una oferta de contribuir; memoTux le invitó a hacerlo el 2026-09-30 ("Si lo que tu ya tienes puedes aportarlo para la comunidad, bienvenido es"). |

## Cómo se toman las decisiones

| # | Regla | Etiqueta | Fuente |
|---|---|---|---|
| D1 | El proceso es: presentar una hoja de ruta, que entra en el repositorio; repartir las tareas; presentar PR. | **[maintainer]** | Discord, Alan Buscaglia, 2026-09-27: "1- juntensen presenten un roadmap y lo metemos en el repo 2- dividan tareas 3- presenten prs" |
| D2 | La hoja de ruta es una lista de hitos; la implementación se discute dentro del grupo. | **[community proposal]** (consejo de Gentleman Staff) | Discord, dnlrsls, 2026-09-26 |
| D3 | El grupo analiza lo que compartió el mantenedor, propone una hoja de ruta (siguiendo la sugerencia de dnlrsls), fusiona las propuestas en una común y, después, los miembros se comprometen con una tarea concreta. | **[community proposal]** | Discord, memoTux, 2026-09-26 |
| D4 | El grupo se reúne en directo, define áreas de competencia con un responsable, una hoja de ruta y un MVP, y se presenta a los mantenedores como grupo. El proyecto se mantiene alineado con la filosofía del mantenedor. | **[community proposal]** | Discord, Matrak, 2026-09-27 |
| D5 | La cadena de M1 del propio mantenedor se fusionó en su rama de seguimiento y después en `main` por instrucción suya. Ninguna fuente indica cómo se revisan y fusionan las PR de la comunidad ([preguntas abiertas](#preguntas-abiertas)). | **[maintainer]** (práctica registrada, su propia cadena) | `gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m1-chat-core.md:71` ("Maintainer instruction: #4 to #9 merged into the tracker"; tracker #3 fusionada en `main` "(maintainer instruction)"), `:75` |
| D6 | El mantenedor valida la [visión](00-vision.md) línea a línea; hasta entonces es un borrador. | **[community proposal]** | `00-vision.md:3-5` |
| D7 | Las ideas que van más allá de la paridad se redactan como propuestas; solo el mantenedor pasa una propuesta a `accepted` o `declined`. | **[community proposal]** | [07-proposals §Proceso](07-proposals/README.md#proceso); vision P10 |
| D8 | Las cuestiones de arquitectura que el repositorio deja abiertas reciben un ADR solo después de una decisión del mantenedor. | **[community proposal]** | [ADR "Undecided / not recorded"](03-architecture/adr/README.md#sin-decidir--no-registrado) |
| D9 | Un cambio que corresponde a upstream va a ese repositorio mediante su propio proceso: los cambios del protocolo RPC a pi, los datos a nivel de extensión y las correcciones del RPC a gentle-shell, la pila de complementos gestionada a gentle-ai. | **[community proposal]**; el enrutamiento es `Inference:` como en su fuente | [02 §Dónde corresponde cada cambio](02-ecosystem.md#dónde-corresponde-cada-cambio) |
| D10 | Las PR de pi necesitan la aprobación previa del mantenedor (`lgtm`). Por separado, en "Where can I learn about plans?", el archivo dice que Earendil usa RFC para discutir los cambios grandes; eso describe la práctica upstream, no una regla para contribuidores. | **[upstream]** | `pi@a13d35a:CONTRIBUTING.md:31-34`, `:58`; `:99-102` |
| D11 | Cada responsable de área decide dentro del alcance del área; todo lo que cambie la visión, el propósito de una pantalla, un ADR o la interfaz de otra área va al grupo y, después, al mantenedor. | **[community proposal]** | Esta página |
| D12 | Los responsables se proponen ellos mismos; el grupo lo confirma; el mantenedor puede vetarlo. | **[community proposal]** | Esta página; los responsables son `TBD` |

## Papel del mantenedor

| Responsabilidad | Etiqueta | Fuente |
|---|---|---|
| Fija la intención del producto mediante el repositorio y la maqueta conceptual; remitió a la maqueta cuando se le preguntó por sus ideas, objetivos y límites. | **[maintainer]** | Discord, Alan Buscaglia, 2026-09-26; [visión](00-vision.md#cómo-leer-esta-página) |
| Incorpora la hoja de ruta al repositorio una vez que el grupo la presenta. | **[maintainer]** | Discord, Alan Buscaglia, 2026-09-27 |
| Hizo fusionar su propia cadena de M1 en la rama de seguimiento y después en `main` por instrucción suya. La revisión y la fusión de las PR de la comunidad son una [pregunta abierta](#preguntas-abiertas). | **[maintainer]** (práctica registrada, su propia cadena) | `gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m1-chat-core.md:71`, `:75` |
| Dio instrucciones sobre la verificación y la estructura del código para M1 (comprobaciones en navegador, reglas de React y de estructura). | **[maintainer]** | `gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m1-chat-core.md:29` |
| Valida la visión, responde a vision Q1–Q13, decide los candidatos a ADR abiertos, acepta o rechaza propuestas. | **[community proposal]** | `00-vision.md:3-5`; [07-proposals §Proceso](07-proposals/README.md#proceso) |
| gentle-shell "is built by Alan Buscaglia"; gentle-ai es "Built by Alan Buscaglia (Gentleman Programming)" y lo enumera bajo "Maintainer" en CONTRIBUTORS. | **[upstream]** para la autoría | `gentle-shell@ac67159:README.md:351`; `gentle-ai@ff77164:README.md:306`, `CONTRIBUTORS.md:5-9`; [02 §Responsables](02-ecosystem.md#responsables) |

`Inference:` como el mantenedor también construye gentle-shell, el área de Integración upstream a menudo hablará con él en un segundo papel.

## Flujo de contribución

Los documentos de M1 y M2 del mantenedor registran cómo se construyó el código existente **[maintainer]**. Aplicar la misma práctica a las PR de la comunidad es una **[community proposal]**.

| Práctica | Registrada en |
|---|---|
| Documento de funcionalidad (feature document) por hito en `odd/tasks/`, con tareas, ruta, commits, comprobaciones y evidencias de revisión | `gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m1-chat-core.md:54-61`; `odd/tasks/desktop-m2-helpers.md:47-53` |
| TDD estricto con vitest: RED antes de la implementación, GREEN, REFACTOR | `gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m1-chat-core.md:27`; `odd/tasks/desktop-m2-helpers.md:26` |
| Scope Rule, Screaming Architecture, contenedor/presentacional, `shared/ui` atómico, proceso principal hexagonal | `gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m1-chat-core.md:29`; `odd/tasks/desktop-m2-helpers.md:26`; ADR [0003](03-architecture/adr/0003-hexagonal-main-process.md), [0004](03-architecture/adr/0004-renderer-scope-rule-and-screaming-architecture.md) |
| Verificación en navegador del trabajo de UI a medida que llega | `gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m1-chat-core.md:29`; `odd/tasks/desktop-m2-helpers.md:26` |
| Artefactos en inglés, registro neutro; Conventional Commits; sin atribución a IA | `gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m1-chat-core.md:28` |
| Cadena de ramas de funcionalidad: las PR de cada porción apuntan a la porción anterior, solo la rama de seguimiento se fusiona en `main`; nunca `--delete-branch` a mitad de la cadena | `gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m1-chat-core.md:30`; `odd/tasks/desktop-m2-helpers.md:3`, `:26` |
| Desarrollo dirigido por recibos (receipt-driven development, RDD) activado, con el consentimiento de revisión concedido de antemano por el mantenedor. `Inference:` los documentos de M1 y M2 cubren solo sus propios hitos, así que el consentimiento concedido de antemano consta solo para ese trabajo | `gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m1-chat-core.md:31`; `odd/tasks/desktop-m2-helpers.md:26` |
| Errores notificados mediante el formulario de informe de errores | `gentle-shell-desktop@5ab4a00:README.md:66` |

**Carencias de este flujo hoy.** Ninguna CI ejecuta estas comprobaciones (audit A16), no hay guía para contribuidores ([issue #28, "Author's framing: facts checked before writing"](https://github.com/Gentleman-Programming/gentle-shell-desktop/issues/28)) y el ajuste de TDD estricto consta como procedente de la configuración del agente a nivel de usuario del mantenedor (`gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m1-chat-core.md:27`), no de una política del repositorio. Ver [preguntas abiertas](#preguntas-abiertas).

## Canales de comunicación

| Canal | Estado | Fuente |
|---|---|---|
| Hilo de Discord "Gentle Desktop" (servidor de Gentleman Programming, canal gentle-shell) | **En uso.** Allí se publicaron el proceso del mantenedor y las propuestas de este grupo. | Hilo de Discord, de 2026-09-26 a 2026-09-30 |
| Sala de voz en directo en Discord | **Propuesta** para una reunión de presentación del grupo; el hilo no fija ninguna fecha. Dos miembros ya hablaron en un canal en directo. | Discord, Matrak, 2026-09-26 y 2026-09-27 ("lo que estuvimos hablando @memoTux y yo en un canal en vivo") |
| GitHub Discussions en `Gentleman-Programming/gentle-shell-desktop` | **Solicitado, no habilitado.** memoTux pidió al mantenedor que habilitara Discussions para que la conversación sobre la hoja de ruta tuviera lugar allí (Discord, memoTux, 2026-09-29). `gh api repos/Gentleman-Programming/gentle-shell-desktop --jq .has_discussions` devolvió `false` el 2026-10-01. | Discord, memoTux, 2026-09-29; API de GitHub, 2026-10-01 |
| Issues y PR de GitHub en el mismo repositorio | **En uso.** Las issues están habilitadas (`has_issues: true`, API de GitHub, 2026-10-01); la issue de planificación de M2 es la #2; M1 y M2 se entregaron como cadenas de PR. | `gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m2-helpers.md:3`, `:59`; `odd/tasks/desktop-m1-chat-core.md:75` |
| Gestores de incidencias upstream (pi, gentle-shell) | Para los cambios que corresponden a upstream (regla D9). pi remite las preguntas a Discord, no a las issues. | [04 §Cómo proponer cambios del contrato en upstream](04-rpc-contract.md#cómo-proponer-cambios-del-contrato-en-upstream); `pi@a13d35a:.github/ISSUE_TEMPLATE/config.yml:1-5` |

## Preguntas abiertas

- ¿Quién revisa y fusiona las PR de la comunidad? Las fuentes solo registran que la cadena de M1 del propio mantenedor se fusionó por instrucción suya (`odd/tasks/desktop-m1-chat-core.md:71`); las evidencias de revisión que registran los documentos de M1 y M2 son linajes de RDD (por ejemplo `odd/tasks/desktop-m1-chat-core.md:67`), y no se nombra a ningún revisor humano.
- ¿Quién es responsable de la política de RDD para las PR de la comunidad? El documento de M1 registra "consent for review is pre-granted by the maintainer" (`odd/tasks/desktop-m1-chat-core.md:31`). `Inference:` eso cubre sus propios hitos; nada dice si las PR de la comunidad pasan por RDD, ni con el consentimiento de quién.
- ¿Es el TDD estricto una regla del repositorio para los contribuidores o un ajuste personal del mantenedor? Hoy consta como procedente de su configuración a nivel de usuario (`odd/tasks/desktop-m1-chat-core.md:27`).
- ¿Cómo se coordinan las áreas con los mantenedores upstream? ¿Un contacto por repositorio a través de Integración upstream, o cada área abre sus propias issues upstream?
- ¿Quiere el mantenedor un único contacto del grupo, o que cada responsable de área hable con él directamente?
- ¿Se habilitarán las Discussions y, en ese caso, qué conversaciones pasarán allí desde Discord?
- ¿Quién fusiona cuando el mantenedor no está disponible? Ninguna fuente nombra a un comantenedor ni a un revisor delegado.
- ¿Adopta el grupo la cadena de ramas de funcionalidad para cada hito, o solo para los hitos grandes? M2 eligió una cadena a partir de una previsión de unas 900 líneas cambiadas (`odd/tasks/desktop-m2-helpers.md:28`).
- ¿Bastan los custodios de accesibilidad y rendimiento, o quiere el grupo que sean áreas completas una vez que haya evidencias para dimensionarlas?

## Fuentes leídas

[issue #28](https://github.com/Gentleman-Programming/gentle-shell-desktop/issues/28) (secciones "Author's framing"); hilo de Discord "Gentle Desktop" (Discord de Gentleman Programming); `docs/00-vision.md`; `docs/02-ecosystem.md`; `docs/03-architecture/audit.md`; `docs/03-architecture/adr/README.md`; `docs/04-rpc-contract.md`; `docs/05-capability-inventory.md` (resumen de cobertura, columnas, ID de fila); `docs/06-ux/screens.md`; `docs/06-ux/principles.md` (encabezados y U10–U11); `docs/06-ux/design-system.md` (encabezados y filas D); `docs/07-proposals/README.md`; `docs/10-platforms.md` (riesgos); actualizado el 2026-10-03 frente a pi `a13d35a` (1.0.0), el `main` de gentle-shell en `ac67159` (versión de paquete 4.0.0), gentle-ai `ff77164` (v4.0.0) y las PR #26 y #27 del escritorio en GitHub; `gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m1-chat-core.md`, `odd/tasks/desktop-m2-helpers.md`, `README.md`, `package.json`, `.github/ISSUE_TEMPLATE/`; API de GitHub para `Gentleman-Programming/gentle-shell-desktop` (solo lectura, 2026-10-01).
