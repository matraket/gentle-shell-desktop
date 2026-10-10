> Traducción al español de `docs/06-ux/design-system.md` (árbol de trabajo tras la actualización del 2026-10-03). Documento de lectura; la versión de referencia es la inglesa.

# Sistema de diseño

> Estado: borrador (draft).

El escritorio tiene un tema fijo en el código, Gentleman-Cute, en forma de 16 tokens de color y 3 tokens de fuente en CSS (`D:renderer/shared/theme/tokens.css:8-29`). La maqueta conceptual (mockup) usa los mismos 15 colores con nombres en parte distintos, más un token de radio. gentle-shell incluye tres temas; hoy el escritorio no puede cambiar entre ellos. Los componentes de UI compartidos son tres átomos: Button, Pill y TextField.

**Claves de cita.** `D:` es `gentle-shell-desktop@5ab4a00:src/`. `GS:` es `gentle-shell@ac67159:` (`main` de gentle-shell, versión de paquete 4.0.0; `themes/` y las líneas citadas de `package.json` no han cambiado desde `1162ce9`, 3.7.0). `gs-mockup.html:<line>` es el DOM guardado de la maqueta conceptual (intención, no especificación). Todos los valores que siguen se copiaron de la línea citada.

## Tokens

### Tokens de color, uno junto a otro

"Variable del tema" es la clave `vars` correspondiente en `GS:themes/Gentleman-Cute.json`. Los valores son hexadecimales sin distinción entre mayúsculas y minúsculas; los archivos CSS usan minúsculas, y el JSON y `theme.ts`, mayúsculas.

| Función | `tokens.css` del escritorio | Clave de `theme.ts` del escritorio | CSS de la maqueta | Variable del tema (Gentleman-Cute) |
|---|---|---|---|---|
| Fondo de la ventana | `--bg: #060407` (`:9`) | `bg` | `--bg: #060407` (`:6`) | `bg` `#060407` |
| Panel | `--panel: #100a0f` (`:10`) | `panel` | `--panel: #100a0f` (`:7`) | `bgPanel` `#100A0F` |
| Superficie elevada | `--raised: #180e15` (`:11`) | `raised` | `--raised: #180e15` (`:8`) | ninguna (ver [diferencias](#diferencias)) |
| Línea sutil | `--line: #2a1720` (`:12`) | `line` | `--line: #2a1720` (`:9`) | `borderSubtle` `#2A1720` |
| Línea marcada | `--line-strong: #563040` (`:13`) | `lineStrong` | `--line-strong: #563040` (`:10`) | `border` `#563040` |
| Texto | `--text: #f6eff3` (`:14`) | `text` | `--text: #f6eff3` (`:11`) | `text` `#F6EFF3` |
| Texto secundario | `--text-2: #d2cbd0` (`:15`) | `text2` | `--text-2: #d2cbd0` (`:12`) | `pearl` `#D2CBD0` |
| Texto atenuado | `--muted: #a78e9b` (`:16`) | `muted` | `--muted: #a78e9b` (`:13`) | `muted` `#A78E9B` |
| Acento (rosa) | `--accent: #f095c8` (`:17`) | `accent` | `--gold: #f095c8` (`:14`) | `accent` `#F095C8` |
| Acento, activo | `--accent-active: #ffb1dd` (`:18`) | `accentActive` | ninguno | `activePink` `#FFB1DD` |
| Azul | `--blue: #a9c7ee` (`:19`) | `blue` | `--blue: #a9c7ee` (`:15`) | `powderBlue` `#A9C7EE` |
| Verde | `--green: #b4e7c7` (`:20`) | `green` | `--green: #b4e7c7` (`:16`) | `mint` `#B4E7C7` |
| Ámbar | `--amber: #f2b86d` (`:21`) | `amber` | `--amber: #f2b86d` (`:17`) | `peach`, `warning` `#F2B86D` |
| Rojo | `--red: #ff718f` (`:22`) | `red` | `--red: #ff718f` (`:18`) | `error` `#FF718F` |
| Morado | `--purple: #c96aa2` (`:23`) | `purple` | `--purple: #c96aa2` (`:19`) | `deepPink` `#C96AA2` |
| Dorado de títulos | `--champagne: #e0c27a` (`:24`) | `champagne` | `--heading: #e0c27a` (`:20`) | `champagne` `#E0C27A` |

Los números de línea del escritorio están en `D:renderer/shared/theme/tokens.css`; las claves de `theme.ts` están en `D:renderer/shared/theme/theme.ts:7-25`. Los números de línea de la maqueta están en `gs-mockup.html`.

**Variables del tema que el escritorio no usa** (`D:renderer/shared/theme/gentleman-cute.json:4-31`): `bgElement`, `bgSubtle`, `infoBg`, `toolPendingBg` (todas `#100A0F`), `dim` `#76616B`, `softRose` `#D7A0B8`, `sky` `#C4DAF6`, `selection` `#28121E`, `toolSuccessBg` `#151316`, `toolErrorBg` `#261019`. El tema también asigna 55 `colors` semánticos (markdown, sintaxis, niveles de razonamiento, estados de herramienta, diffs) a estas variables (`:32-88`); el escritorio no tiene una capa semántica equivalente.

PR #30 estimó los valores del tema a partir de capturas (`pr30:docs/frontend-renderer-design.md:11-23`); los exactos están en `D:renderer/shared/theme/gentleman-cute.json:4-31` y ya están copiados línea por línea en la tabla anterior. Los valores provisionales y los exactos son cercanos pero ninguno coincide exactamente; trata esta tabla como canónica.

### Tokens de fuente y forma

| Token | Escritorio (`tokens.css`) | Maqueta (`gs-mockup.html`) |
|---|---|---|
| Fuente de presentación | `"Space Grotesk", "Segoe UI", system-ui, sans-serif` (`:26`) | `"Space Grotesk", "Inter", system-ui, sans-serif` (`:21`) |
| Fuente del cuerpo | `"Inter", "Segoe UI", system-ui, sans-serif` (`:27`) | `"Inter", system-ui, -apple-system, sans-serif` (`:22`) |
| Fuente monoespaciada | `"JetBrains Mono", "SFMono-Regular", Consolas, monospace` (`:28`) | `"JetBrains Mono", "SFMono-Regular", Menlo, monospace` (`:23`) |
| Radio | ninguno; valores literales por componente: 4px (`D:renderer/shared/markdown/Markdown.css:21`), 6px (`D:renderer/features/helpers/components/HelperThreadItem.css:86`), 8px, 10px, 12px, 16px, 999px (todas las declaraciones `border-radius` en `D:renderer/**/*.css`) | `--r: 10px` (`:24`), más literales |
| Esquema de color | no declarado (no hay `color-scheme` en `D:renderer/`) | `color-scheme: dark` (`:25`) |
| Espaciado | sin tokens | sin tokens |

Las fuentes se cargan desde Google Fonts en ambos. Escritorio: Space Grotesk 500, 600, 700; Inter 400, 500, 600; JetBrains Mono 400, 500 (`D:renderer/index.html:13-16`). Maqueta: Space Grotesk 500, 600; Inter 400, 500, 600; JetBrains Mono 400, 500 (`gs-mockup.html:3`). Un arranque sin conexión las pierde ([ADR 0009](../03-architecture/adr/0009-hardcoded-gentleman-cute-theme.md), [audit A14](../03-architecture/audit.md#a14-endurecimiento-del-preload-y-del-ipc)).

## Diferencias

| # | Diferencia | Escritorio | Maqueta / tema | Efecto |
|---|---|---|---|---|
| D1 | Nombre del acento | `--accent` | `--gold` (`gs-mockup.html:14`) | Mismo valor; solo cambia el nombre. |
| D2 | Nombre del color de títulos | `--champagne`, sin uso en ningún archivo CSS del escritorio (0 coincidencias de `var(--champagne)` en `D:renderer/`) | `--heading` (`gs-mockup.html:20`) | Mismo valor. |
| D3 | Acento activo | `--accent-active` para el hover del botón principal (`D:renderer/shared/ui/atoms/Button.css:17-19`) | no está en la maqueta; `activePink` en el tema | El escritorio añade un token procedente del tema. |
| D4 | Origen de `--raised` | `#180e15` | igual que la maqueta (`gs-mockup.html:8`); no está en ningún `GS:themes/*.json` (se buscó `180e15`, 0 coincidencias) | `Inference:` el escritorio tomó este valor de la maqueta, no del tema, aunque `tokens.css:4` dice que los valores se copian del tema. |
| D5 | Desviación del fixture | `gentleman-cute.json` asigna `colors.userMessageBg` a `bgElement` y no tiene la variable `userMessageBg` | `GS:themes/Gentleman-Cute.json` añade la variable `userMessageBg: "#2A1523"` y le asigna el color | La copia del escritorio no es idéntica al tema en `ac67159` (comparado con `jq -S` y `diff`; solo difieren estas dos líneas). |
| D6 | Fuentes de reserva | `Segoe UI` en segundo lugar; `Consolas` para monoespaciada | `Inter` en segundo lugar para presentación, `-apple-system` para el cuerpo, `Menlo` para monoespaciada | Distinta fuente de reserva en sistemas sin las fuentes web. |
| D7 | Tamaño de fuente base | no se fija ninguno (`tokens.css` y `App.css` fijan solo `font-family`); los tamaños están en `rem` | `body { font-size: 14px; line-height: 1.5 }` (`gs-mockup.html:35-36`) | `Inference:` el texto del escritorio se representa con el valor por defecto de 16px de Chromium, así que es más grande que en la maqueta. |
| D8 | Color del estado de trabajo | La píldora `working` es ámbar (`D:renderer/shared/ui/atoms/Pill.css:18-21`), usada tanto en la lista de chats de la barra lateral (`D:renderer/features/chats/components/ChatListItem.tsx:7`, `:39`) como en la cabecera del chat (`D:renderer/features/conversation/components/ConversationHeader.tsx:27`) | La píldora de la cabecera del chat es dorada/rosa (`.gs-pill.gs-working`, `gs-mockup.html:162-163`, usada en `:519`); "working" en la barra lateral es texto verde con un punto (`.gs-s.gs-live`, `:144-145`, usado en `:481`) | Mismo estado, colores distintos: una píldora ámbar en el escritorio, dos tratamientos en la maqueta. |
| D9 | Color de needs-you | La píldora `needs-you` es roja (`Pill.css:23-26`) | dorado/rosa (`gs-mockup.html:146`, notificación `:320`) | La maqueta usa el rojo solo para los fallos (`:409`) y para el hover de los botones discretos (`:355`). |
| D10 | Botón principal | fondo de acento (`Button.css:12-15`) | fondo azul (`gs-mockup.html:239`, `:353`) | Distinto color principal. |
| D11 | Burbujas de mensaje | usuario y asistente ambos sobre `--raised`; borde del usuario con acento, borde del asistente con línea (`D:renderer/features/conversation/components/MessageBubble.css:9-20`) | usuario sobre `--raised` con borde `--line-strong`; asistente sobre `--panel` con borde `--line` (`gs-mockup.html:184-185`) | Distinto contraste entre interlocutores. |
| D12 | Esquema de color | no declarado | `color-scheme: dark` | `Inference:` los controles de formulario nativos pueden representarse en claro en el escritorio. |

Estados que coinciden: running = acento/dorado, waiting = azul, done = verde, failed = rojo (`Pill.css:28-46`; `gs-mockup.html:204-206`, `:407-409`).

## Tipografía

| Uso | Escritorio | Maqueta |
|---|---|---|
| Cuerpo | tamaño por defecto del navegador, Inter (`D:renderer/app/App.css:4`) | 14px / 1.5, Inter (`gs-mockup.html:34-36`) |
| Título del chat | Space Grotesk 600, `1rem` (`D:renderer/features/conversation/components/ConversationHeader.css:11-13`) | Space Grotesk 600, 16px (`gs-mockup.html:156`) |
| Título de pantalla | Space Grotesk 600, `1.5rem` en el primer arranque (`D:renderer/features/first-run/components/FirstRun.css:24-26`) | 600 18px para Proveedores y Extensiones (`gs-mockup.html:335`); 600 24px en el primer arranque (`:373`) |
| Etiqueta de sección | — | Space Grotesk 600 12px, mayúsculas, espaciado `.08em` (`gs-mockup.html:250`, `:337`) |
| Texto del mensaje | `0.9rem` / 1.5 (`MessageBubble.css:5-6`) | hereda 14px / 1.55 (`gs-mockup.html:182`) |
| Píldora | Inter 600, `0.75rem` (`Pill.css:6-8`) | 11px (`gs-mockup.html:158`) |
| Botón | Inter 600, `0.875rem` (`Button.css:2-4`) | 500 12px (`gs-mockup.html:351`); enviar 600 13px (`:240`) |
| Campo de texto | Inter `0.9rem` (`D:renderer/shared/ui/atoms/TextField.css:3-4`) | 14px / 1.5 (`gs-mockup.html:235`) |
| Rutas, evidencias, barra de estado | JetBrains Mono `0.75rem`–`0.8rem` en el primer arranque (`FirstRun.css:79-80`, `:142-143`) | JetBrains Mono 11–12px (`gs-mockup.html:285`, `:298`) |

## Componentes

### Componentes compartidos en el escritorio

`D:renderer/shared/ui` contiene tres átomos y nada más (no hay carpeta de moléculas ni de organismos).

| Componente | Archivo | API | Variantes |
|---|---|---|---|
| `Button` | `D:renderer/shared/ui/atoms/Button.tsx:4-24` | props nativas de botón, `variant` | `primary` (por defecto), `ghost` |
| `Pill` | `D:renderer/shared/ui/atoms/Pill.tsx:3-27` | `children`, `tone` | `neutral`, `working`, `needs-you`, `running`, `waiting`, `done`, `failed` |
| `TextField` | `D:renderer/shared/ui/atoms/TextField.tsx:4-34` | props nativas de input o textarea, `multiline` | una línea, varias líneas |

El resto del código compartido del renderer no es un kit de UI: `Markdown` (`D:renderer/shared/markdown/Markdown.tsx`) representa Markdown saneado, y `shared/bridge` y `shared/theme` contienen el hook del puente (bridge) y los tokens. Los componentes de funcionalidad (lista de chats, tarjeta de diálogo, lista e hilo de helpers, opción del primer arranque) viven dentro de sus carpetas de funcionalidad ([ADR 0004](../03-architecture/adr/0004-renderer-scope-rule-and-screaming-architecture.md)).

### Componentes de la maqueta y su equivalente en el escritorio

| Componente de la maqueta | Clase y línea en la maqueta | Equivalente en el escritorio |
|---|---|---|
| Píldora | `.gs-pill` (`gs-mockup.html:157-163`) | átomo `Pill` |
| Distintivo (on, update, local, recommended) | `.gs-badge` (`:346-349`, `:384`) | ninguno; el distintivo "Recommended" del primer arranque es CSS de la funcionalidad (`FirstRun.css:119-126`) |
| Botón (por defecto, principal, discreto) | `.gs-btn` (`:351-355`) | `Button` (`primary`, `ghost`) |
| Interruptor | `.gs-switch` con `role="switch"` (`:356-359`, `:766`) | ninguno |
| Pestañas | `.gs-tabs` (`:392-395`) | pestañas locales de la funcionalidad en `ConversationHeader` |
| Fila de lista (logo, nombre, descripción, acciones) | `.gs-row` (`:339-345`) | ninguno |
| Lista clave-valor | `.gs-kv` (`:365-366`) | ninguno |
| Notificación | `.gs-toast` (`:308-323`) | ninguno |
| Tarjeta de pregunta | `.gs-ask` (`:213-226`) | `DialogCard` (funcionalidad) |
| Fila de helper, elemento de la lista de helpers, elemento del hilo | `.gs-helper`, `.gs-hitem`, `.gs-item` (`:198-209`, `:401-411`, `:421-429`) | `HelperListItem`, `HelperThreadItem` (funcionalidad) |
| Paso, tarea, comprobaciones | `.gs-step`, `.gs-task`, `.gs-checks` (`:263-291`) | ninguno |
| Barra de estado | `.gs-shellbar` (`:294-306`) | ninguno |
| Tarjeta de opción, tarjeta de detección | `.gs-option`, `.gs-found` (`:375-386`) | opción y tarjeta de detección del primer arranque (funcionalidad) |

`Inference:` Interruptor, Distintivo, Fila de lista, Lista clave-valor y Notificación se reutilizan en las pantallas Proveedores, Extensiones y Chats de la maqueta, así que son candidatos para `shared/ui` cuando se construyan esas pantallas.

## Temas

### Temas en gentle-shell

gentle-shell registra su carpeta `themes/` en pi (`GS:package.json:64-66`). Los tres usan el esquema de temas de pi (`vars`, `colors`, `export`).

| Tema | Archivo | `bg` | `accent` | Notas |
|---|---|---|---|---|
| `Gentle` | `GS:themes/Gentle.json` | `#06080f` | `#E0C15A` | Negro azulado con dorado; `text` `#F3F6F9`, `muted` `#5C6170`. |
| `Gentleman-Cute` | `GS:themes/Gentleman-Cute.json` | `#060407` | `#F095C8` | Por defecto para los homes aislados nuevos ([inventory L6](../05-capability-inventory.md#lanzador-y-homes)). El tema fijo en el código del escritorio. |
| `Gentleman-Sexy` | `GS:themes/Gentleman-Sexy.json` | `#060407` | `#F43888` | Los mismos `bg`, `bgPanel`, `border`, `borderSubtle`, `text` y `muted` que Gentleman-Cute (`:5-13`); un acento rosa más intenso (`:15`). |

pi también tiene los temas integrados `system`, `dark` y `light` ([inventory E6](../05-capability-inventory.md#extensiones-paquetes-skills-prompts-temas-y-mcp)). Ninguno de los tres temas de gentle-shell es claro.

### Estado del cambio de tema

**Hoy, fijo en el código.**

- `tokens.css` lo dice: "hardcoded for M1 (reading the live pi theme is out of scope until M4)" (`D:renderer/shared/theme/tokens.css:1-6`). Decisión: [ADR 0009](../03-architecture/adr/0009-hardcoded-gentleman-cute-theme.md), a partir de `gentle-shell-desktop@5ab4a00:odd/tasks/desktop-m1-chat-core.md:22`.
- Hay tres copias de la paleta: `tokens.css`, `theme.ts` y `gentleman-cute.json`. La prueba importa solo el JSON y `theme.ts` (`D:renderer/shared/theme/theme.test.ts:2-3`) y fija cinco valores de `theme.ts` (`accent`, `bg`, `panel`, `text`, `accentActive`) frente al JSON (`:7`, `:15-18`). Nada comprueba `tokens.css`, así que puede desviarse de los otros dos sin que nadie lo note.
- La aplicación solo importa `tokens.css` (`D:renderer/main.tsx:5`). `theme.ts` lo usa la prueba.
- Sobre RPC, pi no expone los temas: `getAllThemes()` devuelve `[]` y `setTheme()` devuelve `{success:false}` ([04, lo que descarta el modo RPC](../04-rpc-contract.md#qué-descarta-el-modo-rpc)).
- El tema de pi elegido por el usuario y los ajustes de apariencia de `/gentle:customize` de gentle-shell no se reflejan (inventory E6, V8, V10).

`Inference:` existen dos vías, ninguna decidida: leer los archivos JSON del tema desde el paquete instalado en el lado del host ([inventory V10](../05-capability-inventory.md#experiencia-del-shell)), o pedir a pi los datos del tema sobre RPC (inventory E6, upstream). Cualquiera de las dos necesita una correspondencia entre los `vars`/`colors` de pi y los tokens del escritorio, que la tabla anterior inicia.

## Preguntas abiertas

- ¿Debería el escritorio seguir el tema de pi del usuario, ofrecer su propio selector o quedarse en Gentleman-Cute?
- ¿Qué valores prevalecen donde la maqueta y el escritorio discrepan (D7–D12)? La maqueta es intención, no especificación, así que esto es una decisión de diseño, no una lista de errores.
- ¿Está dentro del alcance un tema claro? No existe ninguno en gentle-shell.

## Fuentes leídas

`gentle-shell-desktop@5ab4a00`: `src/renderer/shared/theme/{tokens.css,theme.ts,theme.test.ts,gentleman-cute.json}`, `src/renderer/shared/ui/atoms/*`, `src/renderer/index.html`, `src/renderer/main.tsx`, `src/renderer/app/App.css`, CSS de los componentes citados arriba; `gs-mockup.html` L2–457; `gentle-shell@ac67159:themes/*.json`, `package.json` (comprobado de nuevo el 2026-10-03: `git diff 1162ce9 ac67159 -- themes` está vacío).
