> Traducción al español de `docs/07-proposals/0005-session-process-design.md` (árbol de trabajo tras la actualización del 2026-10-07). Documento de lectura; la versión de referencia es la inglesa.

# 0005. Diseño de procesos de sesión por chat

> Estado: propuesta (proposed).

| Campo | Valor |
|---|---|
| Autor | memoTux (@memotux, comunidad) |
| Fuente | [PR #30](https://github.com/Gentleman-Programming/gentle-shell-desktop/pull/30); numerada como propuesta 0005 por [issue #15](https://github.com/matraket/gentle-shell-desktop/issues/15) |
| Estado | `proposed` (solo el mantenedor la pasa a `accepted` o `declined`) |
| Principios | vision P4 **[maintainer]** (los helpers permanecen ligados al chat que los inició) |

## Problema

Cada sesión de chat pertenece a un host de una sola sesión, así que varios chats no pueden ejecutarse a la vez:

- `ChatHost` es dueño de exactamente un `PiSession` vivo sin registro (`gentle-shell-desktop@5ab4a00:src/main/domain/session/ChatHost.ts:70`; [audit A3](../03-architecture/audit.md#a3-host-de-sesión-única-con-ids-de-mensaje-posicionales)).
- Los ID de mensaje son posicionales, así que los chats concurrentes colisionarían ([audit A3](../03-architecture/audit.md#a3-host-de-sesión-única-con-ids-de-mensaje-posicionales); [gap G9](../04-rpc-contract.md#carencias-que-necesita-el-escritorio)).

PR #30 diseñó el estado objetivo de este host. Esta propuesta registra ese diseño, con una corrección: cada chat son dos procesos del SO, no uno (ver [Propuesta](#propuesta)).

## Propuesta

**[community]** Un supervisor en el proceso main de Electron es dueño de un hijo RPC por chat activo:

```text
Electron main (supervisor: registry, lifecycle, authorization, logs)
  ├── chat A: gentle-shell --mode rpc --> pi (two OS processes)
  └── chat B: gentle-shell --mode rpc --> pi (two OS processes)
```

- **Un hijo por conversación activa.** Cada chat activo recibe su propio hijo RPC de larga vida, propiedad del main y supervisado por él; ningún renderer genera pi (`pr30:docs/pi-electron-session-process-design.md:7`). Un hijo atiende una conversación durante toda su vida y nunca se comparte mediante `switch_session`; reabrir inicia un proceso nuevo (`pr30:docs/pi-electron-session-process-design.md:24`).
- **Dos procesos del SO por chat (corrección).** PR #30 dice un proceso del sistema operativo (`pr30:docs/pi-electron-session-process-design.md:35`; `pr30:docs/system-design.md:108`). Son dos: main genera el lanzador `gentle-shell` (`gentle-shell --mode rpc`), y el lanzador genera pi (`pr30:docs/system-design.md:76-82`). `Inference:` los topes de hijos y las políticas de desalojo deben contar dos procesos por chat, no uno.
- **Descartado: un hijo compartido y pi en el proceso.** Un hijo compartido mediante `switch_session` se descarta salvo que la evidencia de recursos pese más que el aislamiento; pi embebido en main vía SDK se descarta para una integración RPC (`pr30:docs/system-design.md:350-352`).
- **Diferido: host en un Utility Process.** Alojar el registro en un Utility Process se difiere hasta que la carga de trabajo medida o la evidencia de fiabilidad lo justifiquen (`pr30:docs/system-design.md:353`); dónde vive el dueño es [issue #2](https://github.com/matraket/gentle-shell-desktop/issues/2), aún abierto.

## Requisitos del runtime

Lo que el escritorio debe construir antes de que este diseño pueda ejecutarse, en orden de dependencia:

| # | Necesidad | Fuente |
|---|---|---|
| R1 | Un registro de sesiones indexado por ID de conversación: como mucho un hijo activo por ID, sin enrutamiento cruzado, cierre idempotente, solicitudes y diálogos resueltos al salir | `pr30:docs/pi-electron-session-process-design.md:114-121` |
| R2 | Un token de generación o de vínculo (attachment) por hijo, para que la salida tardía de un hijo detenido no actualice un vínculo más nuevo | `pr30:docs/pi-electron-session-process-design.md:168` |
| R3 | Sin dos escritores vivos sobre un mismo archivo de sesión: impedir la doble propiedad dentro de una instancia, o definir un comportamiento explícito de solo lectura o multi-vínculo | `pr30:docs/pi-electron-session-process-design.md:64`, `:123` |
| R4 | Un entorno hijo con lista permitida (allowlist) y un directorio de trabajo explícito, en lugar de heredar todo el entorno ambiente | `pr30:docs/pi-electron-session-process-design.md:176` |
| R5 | Apagado ordenado acotado y una matriz de fallos: cada fallo solo marca su conversación e informa una vez, con diagnósticos redactados | `pr30:docs/pi-electron-session-process-design.md:182-198` |
| R6 | Tests de transporte y de supervisor con hijos falsos, incluido el encuadre solo-LF con U+2028 y U+2029 embebidos | `pr30:docs/pi-electron-session-process-design.md:214-220` |

## Precedentes en el ecosistema

- **pi `--mode rpc`:** una interfaz de control de larga vida como proceso hijo, una tripleta de flujos stdin/stdout/stderr por hijo (`pr30:docs/pi-electron-session-process-design.md:59`). Un hijo por chat se alinea con el protocolo en lugar de multiplexar sesiones mediante `switch_session`.
- **Roles de proceso en Electron:** main supervisa, preload expone una API tipada y estrecha, renderer presenta; los registros del hijo siguen sin ser de confianza (`pr30:docs/pi-electron-session-process-design.md:200-208`). Aquí no se inventa ningún patrón nuevo.

## Relación con la propuesta 0004

Las dos propuestas convergen en un hijo por chat, pero responden a capas distintas: esta va de pi al dueño de la sesión (un hijo supervisado por chat); [0004](0004-host-service.md) va del cliente a un servicio compartido (muchos clientes, un registro). La forma por chat en 0004 sigue propuesta, pendiente de vision Q3. Donde difieren, se aplican las cuestiones de decisión de abajo; esta propuesta no elige la ubicación del host.

## Decisiones abiertas

Cada fila es un issue abierto; ambas alternativas siguen sobre la mesa hasta que decida el mantenedor:

| Issue | Pregunta | Alternativas abiertas |
|---|---|---|
| [issue #2](https://github.com/matraket/gentle-shell-desktop/issues/2) | Dónde vive el dueño de la sesión | Supervisor en main (Utility Process solo con evidencia medida) vs un servicio host, aparte o embebido en main, con un Utility Process como tercera ubicación |
| [issue #3](https://github.com/matraket/gentle-shell-desktop/issues/3) | Qué entorno hereda el hijo | Lista permitida explícita y directorio de trabajo vs heredar todo el entorno |
| [issue #4](https://github.com/matraket/gentle-shell-desktop/issues/4) | Cuántos hijos siguen vivos | Mantener vivos los hijos inactivos, con tope y política de avisar, encolar o desalojar, vs detenerlos y reabrirlos bajo demanda |
| [issue #5](https://github.com/matraket/gentle-shell-desktop/issues/5) | Dos escritores sobre un archivo de sesión | Impedir la doble propiedad dentro de una instancia vs un comportamiento explícito de solo lectura o multi-vínculo |
| [issue #6](https://github.com/matraket/gentle-shell-desktop/issues/6) | Eventos tardíos tras reiniciar un hijo | Token de generación o de vínculo por hijo vs una revisión por chat en cada instantánea |
| [issue #7](https://github.com/matraket/gentle-shell-desktop/issues/7) | Ponerse al día tras reiniciar un servicio | Cursor durable (`get_entries` con `since`), que puede combinarse con las instantáneas, vs instantáneas completas sin cursor en el cliente; cómo el servicio reconstruye su estado desde pi tras un reinicio aún no está escrito |
| [issue #8](https://github.com/matraket/gentle-shell-desktop/issues/8) | Propiedad de los diálogos entre ventanas o clientes | Una ventana es dueña de los diálogos y del cierre vs la primera respuesta gana y la segunda recibe `dialog_not_pending` |
| [issue #9](https://github.com/matraket/gentle-shell-desktop/issues/9) | Validación del remitente IPC | Validar el marco remitente en main vs confiar en la ventana propia de la app y autenticar solo el socket |

## Fuentes

Los prefijos de cita siguen [issue #1](https://github.com/matraket/gentle-shell-desktop/issues/1): `pr30:` se refiere al PR #30.

Signed-off-by: memoTux (@memotux), autor del PR #30.
