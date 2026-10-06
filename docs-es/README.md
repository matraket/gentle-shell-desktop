> Traducción al español de `docs/README.md` (árbol de trabajo tras la actualización del 2026-10-03). Documento de lectura; la versión de referencia es la inglesa.

# Corpus de documentación de Gentle Desktop

Terreno común para todas las personas que trabajan en Gentle Desktop: qué se está construyendo, por qué, cómo funciona hoy, qué hace ya gentle-shell que el escritorio debe exponer y cómo se organiza la comunidad en torno a ello. La hoja de ruta es un documento más entre estos, derivado de los demás.

## Cómo leerlo

1. Empezar por la [visión](00-vision.md) y el [glosario](01-glossary.md).
2. Entender las piezas en el [ecosistema](02-ecosystem.md).
3. Profundizar en la [arquitectura](03-architecture), el [contrato RPC](04-rpc-contract.md) y el [inventario de capacidades](05-capability-inventory.md).
4. Después, [UX](06-ux), [propuestas](07-proposals), [equipo](08-team.md) y la [hoja de ruta](09-roadmap.md).
5. Para el soporte de Windows, macOS, Linux y WSL, leer [plataformas](10-platforms.md) después de la auditoría y la hoja de ruta.

**IDs entre documentos.** Los IDs se repiten entre páginas (inventory A1–A12 y U1–U8, audit A1–A21, UX U1–U12). Dentro de su página de origen un ID se escribe sin calificador; en cualquier otro lugar lleva un calificador: `inventory A5` ([inventario de capacidades](05-capability-inventory.md)), `audit A5` ([auditoría](03-architecture/audit.md)), `UX U3` ([principios de UX](06-ux/principles.md)), `design D3` ([sistema de diseño](06-ux/design-system.md)), `gap G1` ([contrato RPC](04-rpc-contract.md#carencias-que-necesita-el-escritorio)), `vision P2` y `vision Q1` ([visión](00-vision.md)), `ADR 0007` ([ADRs](03-architecture/adr/)), `SCR-03` ([pantallas](06-ux/screens.md)), `governance D7` ([equipo](08-team.md)), `QW-01` ([hoja de ruta](09-roadmap.md)), `PLAT-01` ([plataformas](10-platforms.md)) y `M2 scope D2` (el `odd/tasks/desktop-m2-helpers.md` del mantenedor). Atención a los pares que comparten letra: `inventory Q6` (una búsqueda del escritorio) frente a `vision Q1`, y `milestone M3` (un hito del escritorio) frente a `inventory M3`. Un calificador cubre los IDs que se listan tras él (`audit A3, A11`). Una página puede declarar una forma sin calificador en su propia leyenda, como hace la hoja de ruta con los hitos M1–M6.

## Documentos y estado

| Documento | Propósito | Estado |
|---|---|---|
| [00-vision.md](00-vision.md) | Visión y filosofía del producto (pendiente de validación por el mantenedor) | borrador (pendiente de validación del mantenedor) |
| [01-glossary.md](01-glossary.md) | Vocabulario compartido | borrador |
| [02-ecosystem.md](02-ecosystem.md) | Piezas, responsables y cómo se relacionan con el escritorio | borrador |
| [03-architecture/current.md](03-architecture/current.md) | La arquitectura tal como es hoy | borrador |
| [03-architecture/audit.md](03-architecture/audit.md) | Hallazgos, riesgos y recomendaciones | borrador |
| [03-architecture/adr/](03-architecture/adr) | Registros de decisiones de arquitectura | borrador |
| [04-rpc-contract.md](04-rpc-contract.md) | El contrato escritorio ↔ gentle-shell y sus carencias (gaps) | borrador |
| [05-capability-inventory.md](05-capability-inventory.md) | Cada capacidad de gentle-shell y su superficie en el escritorio | borrador |
| [06-ux/](06-ux) | Principios, pantallas y sistema de diseño | borrador |
| [07-proposals/](07-proposals) | Propuestas de la comunidad más allá de la paridad | borrador |
| [08-team.md](08-team.md) | Áreas de responsabilidad y gobernanza | borrador (propuesta de la comunidad, pendiente de revisión del grupo y del mantenedor) |
| [09-roadmap.md](09-roadmap.md) | Hitos derivados del corpus | borrador (propuesta de la comunidad, pendiente de validación del mantenedor) |
| [10-platforms.md](10-platforms.md) | Soporte de Windows (nativo y WSL), macOS y Linux en todo el ecosistema; qué debe resolver el escritorio y los riesgos | borrador |

Valores de estado: `skeleton` → `draft` → `in review` → `validated`.

## Cómo proponer cambios

Abrir una pull request contra el documento. La visión del mantenedor vive en `00-vision.md`; las ideas nuevas de la comunidad van a `07-proposals/` hasta que el mantenedor las acepte.
