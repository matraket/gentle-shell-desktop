> Traducción al español de `docs/06-ux/principles.md` (árbol de trabajo tras la actualización del 2026-10-03). Documento de lectura; la versión de referencia es la inglesa.

# Principios de UX

> Estado: borrador (draft).

Estos principios convierten los [principios de producto](../00-vision.md#principios-de-producto) (vision P1–P10) en reglas para las pantallas. Cada uno nombra el principio de producto al que sirve y conserva la etiqueta de procedencia de ese principio. Esta página no añade ninguna afirmación del mantenedor: una regla etiquetada **[community]** se propone para su validación por el mantenedor, igual que vision P9 y P10.

## De un vistazo

| # | Principio de UX | Sirve a | Procedencia | ¿Se cumple hoy en el escritorio? |
|---|---|---|---|---|
| U1 | Hablar con claridad | vision P2 | **[maintainer]** (mockup intent) | Sí, en los textos que existen |
| U2 | Ocultar el detalle técnico hasta que se pida | vision P2, P7 | **[maintainer]** (mockup intent; alcance de milestone M1 y M2), **[gentle-shell]** | En parte: la salida de herramientas y el razonamiento no se muestran en absoluto |
| U3 | Pedir atención solo cuando haga falta | vision P5 | **[maintainer]** (mockup intent), **[gentle-shell]** | No: un chat cada vez |
| U4 | Mantener los helpers con su chat | vision P4 | **[maintainer]** | Sí |
| U5 | Permitir al usuario detener, redirigir y decidir | vision P6 | **[gentle-shell]**, **[maintainer]** (mockup intent) | En parte: solo detener la ejecución principal y responder preguntas |
| U6 | Mostrar el flujo de trabajo y sus evidencias | vision P7, P1 | **[maintainer]** (mockup intent), **[gentle-shell]** | No |
| U7 | Decir dónde está cada cosa; no editar nunca en silencio la configuración del usuario | vision P3 | **[maintainer]**, **[gentle-shell]** | En parte: solo en el primer arranque |
| U8 | Gestionar la configuración en la aplicación | vision P8 | **[maintainer]** (mockup intent, milestone M4 planificado) | No |
| U9 | Enseñar mientras se trabaja | vision P9 | **[community]** | No evaluado |
| U10 | Paridad de teclado con la CLI | vision P1, P6 | **[community]** | En parte: tres atajos |
| U11 | Accesible por defecto | vision P2 | **[community]**, respaldado por el marcado de la maqueta | En parte |
| U12 | Ir más allá de la terminal solo mediante propuestas | vision P10 | **[community]** | n/a |

**Claves de cita.** `D:` es `gentle-shell-desktop@5ab4a00:src/`. `gs-mockup.html:<line>` es el DOM guardado de la maqueta conceptual (mockup) (intención, no especificación). Los ID se repiten entre documentos (inventory A1–A12 y U1–U8, audit A1–A21, U1–U12 de esta página), así que todo ID de otro documento va cualificado: `inventory C4` es una fila del [inventario de capacidades](../05-capability-inventory.md), `inventory Q29` una de sus [búsquedas en el escritorio](../05-capability-inventory.md#búsquedas-en-el-escritorio), `gap G1` una [carencia (gap) del RPC](../04-rpc-contract.md#carencias-que-necesita-el-escritorio), `audit A3` un [hallazgo de la auditoría](../03-architecture/audit.md#hallazgos), `vision P2` y `vision Q5` un [principio de producto](../00-vision.md#principios-de-producto) y una [pregunta abierta](../00-vision.md#preguntas-abiertas-para-el-mantenedor). Un cualificador abarca los ID que se enumeran tras él (`vision P2, P7`). `milestone M1` es un hito del escritorio, no una fila del inventario. U1–U12 sin cualificar son los principios de esta página. Las pantallas que aplican cada regla están en [screens.md](screens.md).

## U1. Hablar con claridad

**Regla.** Nombrar las cosas por lo que hacen para el usuario: "Gentle", "Helpers", "needs you", "Where we are". Mantener los nombres internos (métodos RPC, rutas de archivo, nombres de herramientas) fuera de los textos principales.

- **Sirve a:** vision P2 **[maintainer]** (mockup intent).
- **Evidencia:** textos de la maqueta `gs-mockup.html:486` ("needs you"), `:522` ("Helpers"), `:617` ("Where we are"), `:565` ("Tell Gentle what you need…").
- **Hoy:** el escritorio reutiliza estos textos: el texto de ejemplo del compositor (`D:renderer/features/conversation/components/Composer.tsx:51`), el hilo vacío "Start a conversation with Gentle." (`D:renderer/features/conversation/components/MessageThread.tsx:39`), la etiqueta "needs you" (`D:renderer/features/chats/components/ChatListItem.tsx:14`).
- **Comprobación para una pantalla nueva:** ¿podría una persona que nunca ha abierto una terminal leer todas las etiquetas principales?

## U2. Ocultar el detalle técnico hasta que se pida

**Regla.** Mostrar primero los resultados. Poner las llamadas a herramientas, el razonamiento, las rutas de archivo y las versiones detrás de un conmutador, en una línea secundaria o en los bordes de la ventana (barra de estado, texto pequeño en monoespaciado).

- **Sirve a:** vision P2 **[maintainer]** (mockup intent para la redacción; alcance de milestone M1 y M2), vision P7 **[maintainer]** (mockup intent), **[gentle-shell]**.
- **Evidencia:** alcance de milestone M1 "No tool output, no thinking shown" (`gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m1-chat-core.md:7`); "Show tool details" sin marcar en la maqueta (`gs-mockup.html:600`); rutas en monoespaciado pequeño bajo un título (`gs-mockup.html:613`, `:674`, `:683`).
- **Hoy:** el pie de Helpers tiene el mismo conmutador sin marcar (`D:renderer/features/helpers/components/HelpersFooter.tsx:28-31`). En el chat principal, las llamadas a herramientas (inventory C17) y el razonamiento (inventory C18) no se representan en absoluto, así que todavía no hay nada que desvelar.
- **Tensión.** U2 dice "ocultar", U6 dice "mostrar evidencias". `Inference:` la maqueta lo resuelve mostrando la evidencia como una línea de resumen breve ("commit 3f1c2a9 · tests green", `gs-mockup.html:630`) y dejando el detalle a un clic.

## U3. Pedir atención solo cuando haga falta

**Regla.** Pueden ejecutarse varios chats a la vez. Un chat muestra su estado en la barra lateral; la aplicación solo interrumpe cuando un chat necesita una decisión o termina algo que el usuario está esperando.

- **Sirve a:** vision P5 **[maintainer]** (mockup intent), **[gentle-shell]**.
- **Evidencia:** estados de la barra lateral `gs-mockup.html:481` (working), `:486` (needs you), `:491` (hora); notificaciones "Helper finished" y "Gentle needs a decision" (`gs-mockup.html:828`, `:833`); campana `gs-mockup.html:470`.
- **Hoy:** el elemento de la lista de chats puede mostrar `idle`, `working` o `needs you` (`D:renderer/features/chats/components/ChatListItem.tsx:11-15`), pero el proceso principal siempre informa `idle` (`D:main/domain/session/sessionList.ts:35`); solo el puente simulado produce los otros dos (`D:renderer/shared/bridge/mockBridge.ts:57`, `:65`). No hay notificaciones.
- **Bloqueado por:** host de una sola sesión (audit A3, gap G9); ciclo de vida de la lista de chats (audit A11); `notify` ignorado (inventory C20).

## U4. Mantener los helpers con su chat

**Regla.** Un helper se muestra dentro del chat que lo inició, idealmente bajo el mensaje que lo inició. Sin lista global de helpers.

- **Sirve a:** vision P4 **[maintainer]**: "Never a global list: the parent-child relation stays direct (maintainer decision, 2026-09-21)" (`gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m2-helpers.md:7`; [ADR 0011](../03-architecture/adr/0011-helpers-scoped-per-chat.md)).
- **Evidencia:** helpers bajo el mensaje (`gs-mockup.html:545-550`); pestaña Helpers por chat (`gs-mockup.html:520-523`, `:571-606`).
- **Hoy:** pestaña Helpers por chat (`D:renderer/features/conversation/components/ConversationHeader.tsx:28-37`). Las filas bajo el mensaje se sustituyen por una franja de todo el chat porque la carga de actividad no tiene vínculo con el mensaje (`D:renderer/features/conversation/components/HelpersStrip.tsx:9-16`).
- **Restricción para las propuestas:** una vista entre chats, como un grafo de todas las sesiones ([proposal 0001](../07-proposals/0001-agent-flow-graph.md)), choca con esta decisión salvo que el mantenedor la revise.

## U5. Permitir al usuario detener, redirigir y decidir

**Regla.** Todo agente en ejecución tiene una forma visible de detenerlo. El usuario responde a las preguntas en el sitio, siempre puede responder con sus propias palabras y decide qué se entrega.

- **Sirve a:** vision P6 **[gentle-shell]**, **[maintainer]** (mockup intent).
- **Evidencia:** "Esc to stop the agent" (`gs-mockup.html:568`); Stop del helper (`gs-mockup.html:603`); tarjeta de pregunta con "Let me explain" (`gs-mockup.html:553-558`); "You still decide what happens next in your repository." (`gentle-shell@ac67159:README.md:137`).
- **Hoy:** Escape aborta la ejecución principal (inventory C3); las tarjetas de diálogo responden a los cuatro tipos de diálogo (inventory C19, `D:renderer/features/conversation/components/DialogCard.tsx:39-45`). El Stop del helper está deshabilitado (`D:renderer/features/helpers/components/HelpersFooter.tsx:36`). El compositor es de solo lectura mientras el agente trabaja (`D:renderer/features/conversation/components/Composer.tsx:53`), así que no es posible redirigir (steer) (inventory C4).
- **Bloqueado por:** gap G1 (detener helpers); audit A7 (redirigir y el mensaje de seguimiento (follow-up) existen sobre RPC, pero el escritorio los rechaza). Está abierto si un prompt enviado mientras el agente trabaja debe ponerse en cola, redirigir o rechazarse ([vision Q5](../00-vision.md#preguntas-abiertas-para-el-mantenedor)).

## U6. Mostrar el flujo de trabajo y sus evidencias

**Regla.** Mostrar dónde está el trabajo (fase), qué está planificado (tareas), qué lo demuestra (commits, pruebas, comprobaciones) y el estado de la revisión. Una evidencia es un hecho con una fuente, no una afirmación.

- **Sirve a:** vision P7, P1 **[maintainer]** (mockup intent), **[gentle-shell]** ("A workflow you can inspect.", `gentle-shell@ac67159:README.md:35`).
- **Evidencia:** panel de ODD (`gs-mockup.html:610-647`); `ODD · RDD on` (`gs-mockup.html:822`).
- **Hoy:** no hay panel de ODD ni estado de RDD (inventory O2–O4, R1; inventory Q29–Q32).
- **Bloqueado por:** gap G2 (estado estructurado de ODD), gap G7 (datos de estado).

## U7. Decir dónde está cada cosa; no editar nunca en silencio la configuración del usuario

**Regla.** Cuando una pantalla lee o escribe la configuración del usuario, dice qué carpeta o archivo, y si es el pi del usuario o el espacio propio de la aplicación.

- **Sirve a:** vision P3 **[maintainer]**, **[gentle-shell]**.
- **Evidencia:** "Your pi settings are never edited" (`gs-mockup.html:672`); "Where this lives" (`gs-mockup.html:734-739`); ámbito de la extensión (`gs-mockup.html:802-807`); "never edits your vanilla pi setup" (`gentle-shell-desktop@5ab4a00:README.md:19`).
- **Hoy:** el primer arranque muestra el directorio detectado (`D:renderer/features/first-run/components/FirstRun.tsx:45`). Dos elecciones de home persistidas pueden discrepar (audit A19). `Inference:` la aplicación ignora la elección de `gentle-shell home` de un usuario de terminal, porque la aplicación siempre pasa un indicador de home y un indicador prevalece sobre la configuración del lanzador (launcher) (inventory L2).

## U8. Gestionar la configuración en la aplicación

**Regla.** Los inicios de sesión, el modelo por defecto, las extensiones y su ámbito se gestionan en la ventana, no solo en una terminal.

- **Sirve a:** vision P8 **[maintainer]** (mockup intent, milestone M4 planificado: `gentle-shell-desktop@5ab4a00:README.md:63`).
- **Evidencia:** pantallas Providers y Extensions (`gs-mockup.html:692-742`, `:745-810`).
- **Hoy:** no implementado (inventory M7, M8, E1, E2 missing).
- **Bloqueado por:** gap G3, G4, G5; la elección entre solo RPC y pi en el mismo proceso ([vision Q4](../00-vision.md#preguntas-abiertas-para-el-mantenedor), audit A1, A2).

## U9. Enseñar mientras se trabaja

**Regla (propuesta).** La aplicación explica qué está haciendo el agente y por qué, en frases breves y claras, para que el usuario aprenda el flujo de trabajo al observarlo.

- **Sirve a:** vision P9 **[community]**, respaldado por **[gentle-shell]** para la persona ("senior architect and teacher", `gentle-shell@ac67159:docs/readme-reference.md:103`).
- **Evidencia en la maqueta** (`Inference:` leído como enseñanza, no declarado como tal): el agente narra su plan (`gs-mockup.html:535-536`, `:543`); metadatos de los pasos como "5 tasks", "tests · review" (`gs-mockup.html:620`, `:622`).
- **Estado:** propuesto. No es intención del mantenedor hasta que se valide ([vision Q9](../00-vision.md#preguntas-abiertas-para-el-mantenedor)).

## U10. Paridad de teclado con la CLI

**Regla (propuesta).** Las acciones frecuentes de la CLI tienen un atajo en el escritorio: enviar, nueva línea, detener y, con el tiempo, modelo y esfuerzo, paleta de comandos, vista de helpers, detener helpers.

- **Sirve a:** vision P1, P6 **[community]**.
- **Por qué:** los 9 atajos de gentle-shell (uno de ellos, para `/gentle:stats`, solo cuando `GENTLE_PI_STATS_VIEW_KEY` está definido) y los atajos de teclado de pi son asignaciones de teclas de la terminal; ninguno llega a un host RPC, así que "el escritorio necesita los suyos propios" ([inventario, cobertura de comandos y atajos](../05-capability-inventory.md#cobertura-de-comandos-y-atajos)).
- **Evidencia:** la maqueta muestra tres indicaciones (`gs-mockup.html:568`); el escritorio implementa las mismas tres (`D:renderer/features/conversation/components/Composer.tsx:30-37`, `:61`).
- **No es paridad de asignaciones.** `Inference:` no es obligatorio reproducir las teclas exactas de la terminal; varias (`ctrl+c`, `ctrl+d`, `ctrl+z`) significan otras cosas en una aplicación de escritorio. Qué acciones tienen atajos es una decisión de diseño del equipo.

## U11. Accesible por defecto

**Regla (propuesta).** Todo control es un botón o una entrada reales, alcanzable con el teclado y con un anillo de foco visible; las regiones activas (live regions) anuncian la actividad nueva; el movimiento puede reducirse; el diseño funciona con anchos estrechos.

- **Sirve a:** vision P2 **[community]**. La accesibilidad se nombró como área de competencia para el grupo de trabajo (Discord, Matrak, 2026-09-27).
- **Evidencia en la maqueta** (marcado, no una regla declarada): `role="tablist"` (`gs-mockup.html:520`); `aria-live="polite"` en el hilo del helper y en las notificaciones (`:587`, `:825`); `role="switch"` con `aria-checked` (`:766`); contorno de foco (`:124`); puntos de ruptura en 1100 px y 640 px (`:437-456`).
- **Hoy:** los elementos de chat son botones para su uso con teclado y lector de pantalla (`D:renderer/features/chats/components/ChatListItem.tsx:23-26`); los errores usan `role="status"` (`D:renderer/features/conversation/components/StatusLine.tsx:14`); los campos de texto eliminan el contorno al recibir el foco y usan en su lugar un color de borde (`D:renderer/shared/ui/atoms/TextField.css:17-20`). La auditoría no cubrió la accesibilidad ([auditoría, método y alcance](../03-architecture/audit.md#método-y-alcance)).
- **Relacionado:** los modos de animación de gentle-shell (inventory V9). `Inference:` corresponden a un ajuste de movimiento reducido.

## U12. Ir más allá de la terminal solo mediante propuestas

**Regla (propuesta).** Una funcionalidad sin equivalente en gentle-shell o pi (por ejemplo, una vista de grafo) empieza como un archivo en [07-proposals](../07-proposals/README.md). Solo llega a una pantalla después de que el mantenedor la acepte.

- **Sirve a:** vision P10 **[community]**.
- **Por qué:** mantiene el trabajo de paridad (el inventario) separado de las ideas nuevas, y mantiene la intención del mantenedor separada del encuadre de la comunidad ([issue #28, "Author's framing: corpus rules"](https://github.com/Gentleman-Programming/gentle-shell-desktop/issues/28), regla 5).

## Preguntas abiertas

- ¿Se aceptan U9–U12 como principios? Dependen de [vision Q9 y Q11](../00-vision.md#preguntas-abiertas-para-el-mantenedor).
- U3 depende de la decisión sobre varios chats ([vision Q3](../00-vision.md#preguntas-abiertas-para-el-mantenedor)).

## Fuentes leídas

`docs/00-vision.md`; `gs-mockup.html` L4–909; `gentle-shell-desktop@5ab4a00`: `odd/tasks/desktop-m1-chat-core.md`, `odd/tasks/desktop-m2-helpers.md`, `README.md`, `src/renderer/**`, `src/main/domain/session/sessionList.ts`; `gentle-shell@ac67159:README.md`, `docs/readme-reference.md` (`main` de gentle-shell en `ac67159`, versión de paquete 4.0.0; actualizados el 2026-10-03); `docs/05-capability-inventory.md` (cobertura de comandos y atajos); hilo de Discord (copia guardada).
