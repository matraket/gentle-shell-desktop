> Traducción al español de `docs/07-proposals/README.md` (árbol de trabajo tras la actualización del 2026-10-03). Documento de lectura; la versión de referencia es la inglesa.

# Propuestas

> Estado: borrador (draft).

Ideas de la comunidad que van más allá de la paridad con gentle-shell. Viven aquí, separadas de la [visión](../00-vision.md) del mantenedor, hasta que el mantenedor las acepta ([vision P10](../00-vision.md#principios-de-producto), [UX U12](../06-ux/principles.md#u12-ir-más-allá-de-la-terminal-solo-mediante-propuestas)).

## Índice

| # | Propuesta | Autor | Estado | Principales dependencias del runtime |
|---|---|---|---|---|
| [0001](0001-agent-flow-graph.md) | El flujo de agentes como grafo | Matrak (comunidad) | `proposed` | gap G8, vínculo con el padre y con el mensaje |
| [0002](0002-interact-with-running-node.md) | Interactuar con un nodo en ejecución | Matrak (comunidad) | `proposed` | gap G1, redirección (inventory C4, A6) |
| [0003](0003-post-hoc-audit-by-questions.md) | Auditoría a posteriori mediante preguntas (helpers que han terminado) | Matrak (comunidad) | `proposed` | gap G8, historial de helpers (inventory A12) |
| [0004](0004-host-service.md) | Servicio host local compartido | Matrak (comunidad) | `proposed` | audit A3 y gap G9 (roadmap F1), audit A1, A8, A14 |

Los ID de otros documentos van cualificados porque se repiten (inventory A1–A12 y U1–U8, audit A1–A21, UX U1–U12): `gap G1` procede del [contrato RPC](../04-rpc-contract.md#carencias-que-necesita-el-escritorio), `inventory C4` del [inventario de capacidades](../05-capability-inventory.md), `audit A5` de la [auditoría de arquitectura](../03-architecture/audit.md#hallazgos), `vision P10` y `vision Q5` de la [visión](../00-vision.md), `UX U2` de los [principios de UX](../06-ux/principles.md). Un cualificador abarca los ID que se enumeran tras él (`inventory C4, A6`).

## Proceso
1. **Redactar.** Un archivo por propuesta, `NNNN-short-name.md`, con: Problema, Propuesta, Requisitos del runtime, Precedentes en el ecosistema, Estado, Autor y fuente.
2. **Fundamentar.** Los requisitos del runtime citan las carencias (gaps) del contrato RPC y las filas del inventario de las que dependen. Los precedentes enumeran solo lo que puede verificarse en los repositorios fijados.
3. **Proponer.** Abrir una pull request con el archivo en estado `proposed` y añadirlo al índice.
4. **Decidir.** Solo el mantenedor pasa una propuesta a `accepted` o `declined`. Un miembro de la comunidad nunca cambia ese estado.
5. **Tras la aceptación.** La idea puede pasar a la visión, a las pantallas y a la hoja de ruta. El trabajo upstream (repositorio de origen) que necesite (pi o gentle-shell) sigue [cómo proponer cambios de contrato upstream](../04-rpc-contract.md#cómo-proponer-cambios-del-contrato-en-upstream).

| Estado | Significado | Quién lo fija |
|---|---|---|
| `proposed` | Redactada y abierta a discusión. | Autor |
| `accepted` | El mantenedor la quiere en el producto. | Solo el mantenedor |
| `declined` | El mantenedor no la quiere, por ahora o definitivamente. El archivo se conserva como registro. | Solo el mantenedor |

## Mencionado en la comunidad, no propuesto

Ideas planteadas en el hilo de Discord "Gentle Desktop" sin archivo de propuesta. Se enumeran para que no se pierdan. Enumerarlas no implica respaldarlas, y ninguna de ellas está dentro del alcance. Ver también [términos de la comunidad fuera de alcance](../01-glossary.md#términos-de-la-comunidad-fuera-de-alcance).

| Idea | Planteada por | Fecha | Qué se dijo |
|---|---|---|---|
| Lienzo infinito con agentes | eSagraDEV | 2026-09-26 | Al iniciar un proyecto propio, "un canvan infinito, con agentes, navegador integrado, etc.." |
| Navegador integrado | eSagraDEV | 2026-09-26, 2026-09-27 | El mismo mensaje; más tarde, añadiendo "el navegador integrado de hermes agent" para que pueda usarse desde gentle shell. |
| gentle-mesh para móviles y agentes remotos | memoTux; Rafael The Hutt | 2026-09-26; 2026-09-27 | memoTux: "Gentle Mesh pensamientos para moviles", con interfaces de escritorio y móvil. Rafael: una aplicación multiplataforma y ligera con acceso a agentes remotos mediante VPN, y el protocolo gentle-mesh (`github.com/Rafaeldelinares/gentle-mesh`). Ahora cubierto en parte por [0004](0004-host-service.md#ejecución-remota-opcional-gentle-mesh): ejecución remota opcional detrás del servicio host ([topology T4](../13-clients-and-topologies.md#t4-ejecución-remota-detrás-del-servicio-gentle-mesh-más-adelante)), pendiente de las respuestas de su autor y de la aprobación del mantenedor. |
| Delegación verificable entre agentes | Rafael The Hutt | 2026-09-27 | gentle-mesh RFC-002: delegación con un contrato explícito y una ejecución verificable, frente a la falacia de la "Green Checkbox" (un agente afirma haber tenido éxito y nadie lo comprueba). |
| herdr-web-ui como comparación | Rafael The Hutt | 2026-09-30 | Enlazó `github.com/devswha/herdr-web-ui` y preguntó cómo se compara con gentle-desktop. Evaluado en [0004, Alternativas consideradas y descartadas](0004-host-service.md#alternativas-consideradas-y-descartadas). |

Las fechas se han convertido desde el formato `d/m/yy` del hilo. Fuente: hilo de Discord "Gentle Desktop" (copia guardada, no está en el repositorio).
