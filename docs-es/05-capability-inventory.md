> Traducción al español de `docs/05-capability-inventory.md` (árbol de trabajo tras la actualización del 2026-10-03). Documento de lectura; la versión de referencia es la inglesa.

# Inventario de capacidades

> Estado: borrador (draft).

Cada capacidad de gentle-shell que necesita una superficie en la aplicación de escritorio, y cómo llegar a ella. La experiencia de gentle-shell es el modo interactivo (TUI) de pi más las extensiones de gentle-shell, así que este inventario tiene dos partes: [el núcleo de pi](#núcleo-de-pi-v100), el runtime con el que habla el escritorio a través de gentle-shell, y [gentle-shell y gentle-ai](#gentle-shell-y-gentle-ai), lo que gentle-shell añade por encima.

## Resumen de cobertura

Filas por grupo, contadas mecánicamente a partir de las tablas de capacidades de más abajo (primera palabra de las celdas "Estado en el escritorio" y "Expuesto sobre RPC"), recontadas por última vez el 2026-10-03 tras la actualización a pi 1.0.0 y al `main` de gentle-shell en `ac67159` (versión de paquete 4.0.0). Volver a contar cuando cambie una fila.

| Parte | Grupo | Filas | Escritorio done | partial | missing | n/a | RPC yes | partial | no | host-side | spawn | n/a |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| núcleo de pi | Sesiones | 19 | 1 | 2 | 16 | 0 | 5 | 4 | 5 | 1 | 4 | 0 |
| núcleo de pi | Conversación y entrada | 21 | 5 | 4 | 11 | 1 | 15 | 1 | 0 | 4 | 0 | 1 |
| núcleo de pi | Contexto, compactación y reintento | 6 | 0 | 0 | 6 | 0 | 4 | 1 | 1 | 0 | 0 | 0 |
| núcleo de pi | Modelos, razonamiento y proveedores | 13 | 0 | 1 | 12 | 0 | 3 | 2 | 7 | 0 | 1 | 0 |
| núcleo de pi | Extensiones, paquetes, skills, prompts, temas y MCP | 9 | 0 | 0 | 9 | 0 | 0 | 3 | 4 | 0 | 2 | 0 |
| núcleo de pi | Confianza del proyecto | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| núcleo de pi | Visualización y terminal | 8 | 0 | 2 | 3 | 3 | 0 | 0 | 1 | 2 | 1 | 4 |
| núcleo de pi | Ayuda y diagnóstico | 4 | 0 | 0 | 4 | 0 | 0 | 0 | 4 | 0 | 0 | 0 |
| **núcleo de pi** | **Total** | **81** | **6** | **9** | **62** | **4** | **27** | **11** | **23** | **7** | **8** | **5** |
| gentle-shell | Lanzador y homes | 12 | 1 | 3 | 5 | 3 | 0 | 0 | 5 | 0 | 5 | 2 |
| gentle-shell | Experiencia del shell | 19 | 0 | 3 | 15 | 1 | 4 | 10 | 4 | 1 | 0 | 0 |
| gentle-shell | Helpers (subagentes) | 12 | 0 | 5 | 7 | 0 | 3 | 5 | 4 | 0 | 0 | 0 |
| gentle-shell | Flujo de trabajo ODD y seguimiento de tareas | 4 | 0 | 0 | 3 | 1 | 1 | 2 | 0 | 1 | 0 | 0 |
| gentle-shell | Revisión y RDD | 5 | 0 | 2 | 3 | 0 | 2 | 2 | 1 | 0 | 0 | 0 |
| gentle-shell | Perfiles, modelos y persona | 4 | 0 | 1 | 3 | 0 | 1 | 0 | 3 | 0 | 0 | 0 |
| gentle-shell | Seguridad y permisos | 6 | 1 | 0 | 3 | 2 | 3 | 0 | 2 | 0 | 0 | 1 |
| gentle-shell | Integraciones, skills, memoria y diagnóstico | 10 | 0 | 1 | 9 | 0 | 2 | 8 | 0 | 0 | 0 | 0 |
| gentle-ai | gentle-ai fuera de la sesión | 5 | 0 | 0 | 5 | 0 | 0 | 0 | 5 | 0 | 0 | 0 |
| **gentle-shell + gentle-ai** | **Total** | **77** | **2** | **15** | **53** | **7** | **16** | **27** | **24** | **2** | **5** | **3** |

## De un vistazo (núcleo de pi)

| Pregunta | Respuesta |
|---|---|
| ¿Cuántas capacidades tiene el núcleo de pi? | 81 filas en 8 grupos, que cubren 24 comandos slash integrados, 1 comando oculto operativo (`/debug`), 2 comandos de extensiones integradas, 43 atajos de teclado de la aplicación, 47 atajos de teclado de la TUI, 40 indicadores de CLI, 8 subcomandos de CLI y 55 ajustes de primer nivel. |
| ¿Cuántas cubre el escritorio? | **done** 6, **partial** 9, **missing** 62, **n/a** 4 (mecánica de terminal sin significado en una GUI). |
| ¿A cuántas puede llegar hoy el escritorio sobre RPC? | **yes** 27, **partial** 11, **no** 23, **host-side** 7, solo **spawn** 8, **n/a** 5. |
| Hallazgos más importantes del núcleo de pi para el escritorio | 1) La redirección (steer) y los mensajes de seguimiento (follow-up) están plenamente disponibles sobre RPC, pero el escritorio rechaza la entrada mientras hay una ejecución activa (C4). 2) Los comandos slash integrados no existen sobre RPC (C12). 3) Bajo `--mode rpc`, un proyecto sin decidir queda en silencio como no confiable (T1). 4) La lista de sesiones del escritorio ignora los directorios de sesión personalizados (S17). 5) Reabrir una sesión cuyo cwd almacenado ya no existe hace que pi termine con código 1 bajo RPC (S3). |

Los recuentos son totales de las tablas de más abajo; volver a contarlos cuando cambie una fila.

## Método

### Fuentes

| Fuente | Qué se enumeró | Fijado en |
|---|---|---|
| pi 1.0.0 (`@earendil-works/pi-coding-agent`) | Comandos slash integrados, despacho interactivo, atajos de teclado, indicadores y subcomandos de CLI, esquema de ajustes, menú de ajustes, extensiones integradas, manejadores de comandos RPC | `pi@a13d35a` (actualización del 2026-10-03; el SHA fijado anterior, pi 0.99.1 `pi@d86654a`, solo se cita en comparaciones de versiones). Todos los recuentos de [Evidencia de completitud](#evidencia-de-completitud) se volvieron a comprobar en `a13d35a` y no cambian. |
| pi 0.85.1 | Solo las diferencias que importan para la lista de sesiones del escritorio en el mismo proceso | `pi@d981de1` |
| Gentle Desktop | El estado en el escritorio de cada fila de capacidad, leyendo `src/` y mediante búsquedas por palabra clave (lista más abajo) | `gentle-shell-desktop@5ab4a00` (`src/` es idéntico en `docs/corpus`, comprobado con `git diff --quiet main HEAD -- src`) |
| `04-rpc-contract.md` | La columna "Expuesto sobre RPC" y los IDs de carencia (gap) G1–G10 | este corpus |

`Inference:` gentle-shell ejecuta el modo interactivo de pi, así que cada capacidad del núcleo de pi de más abajo está disponible en gentle-shell salvo que una extensión de gentle-shell la sobrescriba o la oculte. Comprobar las sobrescrituras corresponde a la parte de gentle-shell (C5b).

### Claves de cita

Las filas usan claves cortas para seguir siendo legibles. Cada clave se expande a un prefijo completo `repo@sha:path`.

| Clave | Se expande a |
|---|---|
| `IM:` | `pi@a13d35a:packages/coding-agent/src/modes/interactive/interactive-mode.ts:` |
| `SC:` | `pi@a13d35a:packages/coding-agent/src/core/slash-commands.ts:` |
| `KB:` | `pi@a13d35a:packages/coding-agent/src/core/keybindings.ts:` |
| `TKB:` | `pi@a13d35a:packages/tui/src/keybindings.ts:` |
| `ARGS:` | `pi@a13d35a:packages/coding-agent/src/cli/args.ts:` |
| `SM:` | `pi@a13d35a:packages/coding-agent/src/core/settings-manager.ts:` |
| `RPCT:` | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-types.ts:` |
| `RPCM:` | `pi@a13d35a:packages/coding-agent/src/modes/rpc/rpc-mode.ts:` |
| `PISRC:` | `pi@a13d35a:packages/coding-agent/src/` (cualquier otro archivo fuente) |
| `PIDOC:` | `pi@a13d35a:packages/coding-agent/docs/` |
| `D:` | `gentle-shell-desktop@5ab4a00:src/` |
| `04` | [`04-rpc-contract.md`](04-rpc-contract.md) de este corpus |

### Evidencia de completitud

| Categoría | Enumerado a partir de | Recuento | Cobertura |
|---|---|---|---|
| Comandos slash integrados | Array `BUILTIN_SLASH_COMMANDS`, `SC:19-44` | 24 | Los 24 tienen fila. Contrastado con el despacho en `IM:3146-3285`. |
| Comandos slash ocultos | Ramas de despacho en `IM:3261-3275` que no están en el array | 3 | `/debug` tiene fila (H2). `/arminsayshi` y `/dementedelves` quedan excluidos: solo renderizan un componente (`IM:3266`, `:3271`) y no son capacidades. |
| Comandos de extensiones integradas | `builtInExtensions` (`PISRC:extensions/index.ts:7-13`) y las llamadas a `registerCommand` en `PISRC:extensions/` | 2 | `/llama` (M9) y `/mcp` (E8). Las otras dos extensiones integradas, `codemode` y `tool-search`, registran herramientas, no comandos. |
| Atajos de teclado de la aplicación | Interfaz `AppKeybindings`, `KB:15-57` | 43 | Los 43 están mapeados en [Cobertura de atajos de teclado](#cobertura-de-atajos-de-teclado). |
| Atajos de teclado de la TUI | Entradas `"tui.*": {` en `TKB:72-209` | 47 | Agrupados por familia en [Cobertura de atajos de teclado](#cobertura-de-atajos-de-teclado). |
| Indicadores de CLI | Ramas `arg === "--…"` distintas en `ARGS:82-235` | 40 | Los 40 están mapeados en [Cobertura de indicadores de CLI](#cobertura-de-indicadores-de-cli). Texto de ayuda en `ARGS:289-332`. |
| Subcomandos de CLI | Bloque de ayuda `Commands:`, `ARGS:277-286` | 8 | Los 8 están mapeados en [Cobertura de indicadores de CLI](#cobertura-de-indicadores-de-cli). |
| Claves de ajustes | `interface Settings`, `SM:133-189` | 55 | Las 55 figuran en [Cobertura de ajustes](#cobertura-de-ajustes). Formas anidadas en `SM:18-131`. |
| Elementos del menú de ajustes | Entradas `id:` en `PISRC:modes/interactive/components/settings-selector.ts` y los setters a los que llama `showSettingsSelector` (`IM:4822-5066`) | 34 elementos de primer nivel | Cada setter corresponde a una clave en [Cobertura de ajustes](#cobertura-de-ajustes). |
| Comandos RPC | `04` §Commands (33 comandos) | 33 | Cada comando RPC que usa al menos una fila se cita por su nombre. |

### Búsquedas en el escritorio

Un estado en el escritorio **missing** cita una de estas búsquedas. Cada una ejecuta `rg -i <pattern> src -g '!*.test.*' -g '!__fixtures__'` en `gentle-shell-desktop@5ab4a00`.

| ID | Patrón | Resultado |
|---|---|---|
| Q1 | `set_model\|get_available_models\|cycle_model` | 0 resultados |
| Q2 | `thinking_level\|thinkingLevel` | 0 resultados |
| Q3 | `login\|logout\|auth` | Solo la detección de `auth.json` en el primer arranque (`D:main/domain/home/home.ts:86`); los demás resultados son la palabra "authoritative" en comentarios |
| Q4 | `compact` | Solo comentarios (`D:main/domain/rpc/types.ts:17`, `:20`; `D:renderer/features/conversation/components/HelpersStrip.tsx:10`) |
| Q5 | `fork\|clone\|get_tree` | 2 resultados no relacionados (`D:renderer/shared/bridge/mockBridge.ts:176`, `:195`) |
| Q6 | `set_session_name\|rename\|sessionName\|session_info_changed` | 0 resultados |
| Q7 | `export_html\|exportTo` | 0 resultados |
| Q8 | `bash` | Solo comentarios y un token de tema (`D:main/domain/rpc/types.ts:17`, `:20`, `:62`) |
| Q9 | `steer\|follow_up\|followUp\|clear_queue` | 0 resultados |
| Q10 | `image` | `D:main/domain/rpc/history.ts:13` omite las partes de imagen; `D:renderer/shared/markdown/renderMarkdown.ts:19` es un comentario del sanitizador |
| Q11 | `get_session_stats\|cost\|contextUsage` | 1 comentario no relacionado (`D:main/adapters/piSessionStore.ts:6`) |
| Q12 | `get_commands\|slash` | 0 resultados |
| Q13 | `skill` | 0 resultados |
| Q14 | `trust` | 1 comentario no relacionado (`D:renderer/shared/markdown/renderMarkdown.ts:6`) |
| Q15 | `scoped` | 0 resultados |
| Q16 | `mcp` | 0 resultados |
| Q17 | `clipboard\|copy\|writeText\|get_last_assistant_text` | No relacionados (`D:main/domain/rpc/chatReducer.ts:285-287`, texto (copy) del primer arranque) |
| Q18 | `retry` | Solo la decodificación de `willRetry` (`D:main/domain/rpc/codec.ts:94`) y el botón Retry del primer arranque |
| Q19 | `theme` | Solo tokens fijos en el código (`D:renderer/shared/theme/tokens.css:2-5`, `D:renderer/shared/theme/theme.ts:6`) |
| Q20 | `install\|uninstall\|package` | Solo comentarios (`D:main/ports/index.ts:57-59`, `D:main/domain/rpc/types.ts:8-12`) |
| Q21 | `settings` | Solo el puerto `HomeSettings` (`D:main/ports/index.ts:85`) |
| Q22 | `abort_bash\|abort_retry\|set_auto` | 0 resultados |
| Q23 | `navigate\|branch` | 1 comentario no relacionado (`D:main/domain/rpc/chatReducer.ts:13`) |
| Q24 | `keybind\|shortcut\|hotkey` | 1 comentario sobre el atajo Escape para abortar (`D:renderer/features/conversation/components/Composer.tsx:20`) |
| Q25 | `search\|delete\|mermaid` | No hay cuadro de búsqueda, ni acción de borrado, ni renderizador de Mermaid; los resultados son un parser de consultas de URL, la limpieza de listeners y claves JSON de temas |

### Cómo mantenerlo al día

1. Volver a ejecutar las enumeraciones de [Evidencia de completitud](#evidencia-de-completitud) en el nuevo SHA de pi y comparar los recuentos.
2. Volver a ejecutar Q1–Q25 en el nuevo SHA del escritorio; un resultado que no sea un comentario cambia el estado de una fila.
3. Actualizar los totales de [De un vistazo](#de-un-vistazo-núcleo-de-pi).

## Columnas

| Columna | Significado |
|---|---|
| Capacidad | Lo que puede hacer el usuario. ID en negrita para referencias cruzadas. |
| En la CLI | Comando, tecla, indicador o ajuste en la TUI de pi, con cita. Las teclas son los valores por defecto de pi; "Win/WSL" marca el valor por defecto alternativo que usa pi en Windows y WSL (`KB:62-67`). |
| Expuesto sobre RPC | **yes** / **partial** / **no**, con el comando RPC o el ID de carencia. **host-side**: el escritorio puede implementarlo a partir de datos que ya tiene. **spawn**: solo como indicador de lanzamiento o variable de entorno. |
| Estado en el escritorio | **done** / **partial** / **missing**, citando `D:` o un ID de búsqueda. **n/a**: mecánica de terminal sin significado en una GUI. |
| Superficie en el escritorio | Idea breve y neutral de la superficie de la GUI. Siempre `Inference:`; la maqueta conceptual (mockup) es intención, no especificación. |
| Dependencia de upstream | Cambio necesario en upstream (repositorio de origen), o "none". |
| Prioridad | `TBD`: la priorización es una decisión posterior del equipo. |

## Núcleo de pi (v1.0.0)

### Sesiones

| Capacidad | En la CLI | Expuesto sobre RPC | Estado en el escritorio | Superficie en el escritorio | Dependencia de upstream | Prioridad |
|---|---|---|---|---|---|---|
| **S1** Iniciar una sesión nueva | `/new` (`IM:3245`); `app.session.new`, sin asignar por defecto (`KB:146`) | yes: `new_session` (`RPCT:27`) | partial: "New chat" lanza un proceso nuevo sin `--session` (`D:main/domain/session/ChatHost.ts:110-113`) en lugar de `new_session`; no se pasa ningún `cwd` a la sesión (`D:main/domain/session/ChatHost.ts:159-166`) | Inference: "New chat" con un selector de carpeta | none | TBD |
| **S2** Continuar la última sesión de esta carpeta | `--continue`, `-c` (`ARGS:110`, `:296`) | spawn only | missing: el argv del escritorio no tiene `--continue` (`D:main/domain/session/PiSession.ts:127-133`) | Inference: "Continue last chat" por proyecto | none | TBD |
| **S3** Reanudar una sesión guardada | `/resume` abre el selector (`IM:3276`, manejador `IM:5632`); `--resume`, `-r` (`ARGS:112`, `:297`); `--session <path\|id>` (`ARGS:133`, `:298`); `app.session.resume`, sin asignar (`KB:149`) | partial: `switch_session` necesita una ruta (`RPCT:61`); ningún comando lista sesiones | done: lista de la barra lateral a partir de `SessionManager.listAll()` en el mismo proceso (`D:main/adapters/piSessionStore.ts:29-35`); se reabre mediante `--session <path>` al lanzar (`D:main/domain/session/ChatHost.ts:100-108`). Salvedad: bajo RPC, un cwd de sesión almacenado que ya no existe hace que pi termine con código 1 (`PISRC:main.ts:694-705`) | Inference: lista de chats en la barra lateral (existe) | Inference: un comando de listado eliminaría la importación de pi en el mismo proceso | TBD |
| **S4** Buscar, filtrar y ordenar sesiones | Búsqueda y teclas del selector: filtro de nombradas `ctrl+n` (`KB:122`), ordenar `ctrl+s` (`KB:170`), mostrar ruta `ctrl+p` (`KB:166`); `PIDOC:sessions.md:18` | host-side (sobre la lista propia del escritorio) | missing: Q25 | Inference: cuadro de búsqueda y conmutador "named only" en la barra lateral | none | TBD |
| **S5** Nombrar o renombrar una sesión | `/name [name]` (`IM:3194`, manejador `IM:6587`); `--name`, `-n` (`ARGS:125`, `:303`); renombrar en el selector `ctrl+r` (`KB:174`) | partial: `set_session_name` solo renombra la sesión cargada (`RPCT:68`); evento `session_info_changed` | missing: Q6. La barra lateral muestra el nombre cuando existe (`D:main/domain/session/sessionList.ts:40-41`) | Inference: renombrado en línea en la barra lateral y la cabecera | Inference: renombrar una sesión que no está cargada necesita un comando nuevo o acceso directo al archivo | TBD |
| **S6** Borrar una sesión | Borrar en el selector `ctrl+d` (`KB:178`); `ctrl+backspace` cuando la consulta está vacía (`KB:182`) | no: no hay comando de borrado en `RPCT:20-74` | missing: Q25 | Inference: "Delete chat" en el menú de la barra lateral | pi: comando de borrado, o eliminación del archivo por el escritorio (Inference) | TBD |
| **S7** Información y estadísticas de la sesión | `/session` muestra archivo, ID, número de mensajes, tokens y coste (`IM:3199`, manejador `IM:6612`; `PIDOC:sessions.md:16`) | yes: `get_state` (`RPCT:30`), `get_session_stats` (`RPCT:59`) | missing: Q11; `get_state` está tipado (`D:main/domain/rpc/types.ts:32`) pero nunca se envía | Inference: panel de detalles del chat | none (ver G7) | TBD |
| **S8** Navegar por el árbol de la sesión | `/tree` (`IM:3224`, manejador `IM:5483`); doble Escape en un editor vacío cuando `doubleEscapeAction` es `tree`, el valor por defecto (`IM:3020-3034`, `SM:169`); `app.session.tree`, sin asignar (`KB:147`); teclas y filtros del árbol (`KB:150-157`, `:210-237`); `treeFilterMode` (`SM:170`) | partial: lectura con `get_tree` (`RPCT:66`) y `get_entries` (`RPCT:65`); ningún comando mueve la hoja activa dentro del mismo archivo (comprobado `RPCT:20-74`) | missing: Q5, Q23 | Inference: vista de ramas de la conversación | pi: comando de navegación del árbol | TBD |
| **S9** Etiquetar entradas del árbol | `app.tree.editLabel` `shift+l` (`KB:158`); `app.tree.toggleLabelTimestamp` `shift+t` (`KB:162`) | no: no hay comando de etiquetas en `RPCT:20-74` | missing: Q23 | Inference: añadir un marcador a un mensaje | pi: comando de etiquetas | TBD |
| **S10** Resumir una rama al abandonarla | Se ofrece durante la navegación por el árbol (`PIDOC:sessions.md:32`); `branchSummary.reserveTokens`, `branchSummary.skipPrompt` (`SM:35-38`) | no: depende de S8; solo aparecen los eventos `summarization_retry_*` (`04` §Events) | missing: Q23 | Inference: pregunta "Summarize the branch you leave?" | pi (con S8) | TBD |
| **S11** Bifurcar desde un mensaje anterior del usuario | `/fork` (`IM:3214`, manejador `IM:5424`); doble Escape cuando `doubleEscapeAction` es `fork`; `app.session.fork`, sin asignar (`KB:148`); `--fork <path\|id>` (`ARGS:137`, `:300`) | yes: `get_fork_messages` (`RPCT:64`), `fork` (`RPCT:62`). Efecto secundario: cancela todos los helpers (`04` G1) | missing: Q5 | Inference: "Branch from here" en un mensaje del usuario | none | TBD |
| **S12** Clonar la sesión | `/clone` (`IM:3219`, manejador `IM:5462`) | yes: `clone` (`RPCT:63`). Mismo efecto secundario que S11 | missing: Q5 | Inference: "Duplicate chat" | none | TBD |
| **S13** Exportar una sesión | `/export [path]`, HTML por defecto o `.jsonl` (`IM:3168`, `IM:6439-6450`); `--export <file>` (`ARGS:174`, `:323`) | partial: solo `export_html` (`RPCT:60`, `RPCM:598-601`); no hay comando de exportación a JSONL | missing: Q7 | Inference: "Export…" con elección de formato | pi para JSONL; Inference: el escritorio conoce la ruta de la sesión y podría copiar el archivo por sí mismo | TBD |
| **S14** Importar una sesión desde JSONL | `/import <path>` llama a `runtimeHost.importFromJsonl` (`IM:3173`, `IM:6486-6506`) | no: no hay comando de importación. Inference: `switch_session` al archivo puede cubrir una parte, sin verificar | missing: Q6, Q7 | Inference: "Open session file…" | pi | TBD |
| **S15** Compartir una sesión | `/share` sube a Radius o a un gist secreto de GitHub (`IM:3178`, manejador `IM:6530`; `PIDOC:usage.md:82`); URL base del visor `PI_SHARE_VIEWER_URL` (`ARGS:447`) | no | missing: Q7 | Inference: "Share link…" con un aviso de privacidad | pi | TBD |
| **S16** Sesión efímera | `--no-session` (`ARGS:131`, `:302`) | spawn only | missing: el argv no tiene ese indicador (`D:main/domain/session/PiSession.ts:127-133`) | Inference: "Private chat (not saved)" | none | TBD |
| **S17** Ubicación de almacenamiento de las sesiones | `--session-dir` (`ARGS:139`, `:301`); `sessionDir` (`SM:179`); `PI_CODING_AGENT_SESSION_DIR` (`ARGS:443`) | spawn only | partial: la lista llama a `SessionManager.listAll()` sin directorio (`D:main/adapters/piSessionStore.ts:35`), y `listAll()` sin directorio lee `<agent-dir>/sessions` (`PISRC:core/session-manager.ts:1949`, `PISRC:config.ts:607-608`). Inference: las sesiones guardadas en un directorio personalizado no aparecen en la barra lateral | Inference: no hace falta nada más allá de respetar el ajuste | none | TBD |
| **S18** Abrir o crear una sesión por ID exacto | `--session-id <id>` (`ARGS:135`, `:299`) | spawn only | missing: el argv no tiene ese indicador (`D:main/domain/session/PiSession.ts:127-133`) | Inference: no hace falta; como mucho, enlaces profundos | none | TBD |
| **S19** Copiar el último mensaje del asistente | `/copy` (`IM:3189`, manejador `IM:6556`); `app.message.copy` `ctrl+x` copia la selección o el último mensaje (`KB:130`) | yes: `get_last_assistant_text` (`RPCT:67`); portapapeles en el lado del host | missing: Q17 | Inference: botón de copiar en cada mensaje | none | TBD |

### Conversación y entrada

| Capacidad | En la CLI | Expuesto sobre RPC | Estado en el escritorio | Superficie en el escritorio | Dependencia de upstream | Prioridad |
|---|---|---|---|---|---|---|
| **C1** Enviar un prompt | `enter` (`TKB:144`); manejador de envío `IM:3140-3339` | yes: `prompt` (`RPCT:22`) | done: `D:main/domain/session/PiSession.ts:184`, `D:renderer/features/conversation/components/Composer.tsx:34` | Compositor (existe) | none | TBD |
| **C2** Escribir un prompt de varias líneas | `shift+enter`, `ctrl+j` (`TKB:143`) | host-side | done: Shift+Enter inserta un salto de línea (`D:renderer/features/conversation/components/Composer.tsx:16-17`) | Compositor (existe) | none | TBD |
| **C3** Detener la ejecución en curso | `escape` (`KB:93`); durante el streaming aborta y devuelve al editor los mensajes encolados (`IM:3011-3013`) | yes: `abort` (`RPCT:25`) | done: Escape envía `abort` (`D:renderer/features/conversation/components/Composer.tsx:30`, `D:main/domain/session/PiSession.ts:189`) | Botón Stop y Escape (existen) | none | TBD |
| **C4** Redirigir una tarea en ejecución | `enter` durante el streaming envía `prompt` con `streamingBehavior: "steer"` (`IM:3317-3324`); la entrada durante la compactación se encola (`IM:3305-3315`) | yes: `steer` (`RPCT:23`) o `prompt` + `streamingBehavior` (`RPCT:22`) | missing: un prompt enviado mientras trabaja se rechaza con "Gentle is still working" (`D:main/domain/session/PiSession.ts:169-180`); Q9 | Inference: el compositor sigue utilizable mientras trabaja; el mensaje se muestra como "queued" | none | TBD |
| **C5** Encolar un mensaje de seguimiento | `app.message.followUp` `alt+enter`, Win/WSL `ctrl+q` (`KB:134`; manejador `IM:4388`) | yes: `follow_up` (`RPCT:24`) | missing: Q9 | Inference: "Send after this finishes" | none | TBD |
| **C6** Editar los mensajes encolados | `app.message.dequeue` `alt+up`, Win/WSL `alt+q` (`KB:138`; manejador `IM:4420`) | yes: `clear_queue` devuelve los mensajes eliminados (`RPCT:26`); evento `queue_update` (`04` §Events) | missing: Q9 | Inference: chips de mensajes encolados con editar y quitar | none | TBD |
| **C7** Elegir el modo de entrega de la cola | `steeringMode`, `followUpMode`: `"all"` o `"one-at-a-time"` (`SM:140-141`); elementos de `/settings` `steering-mode`, `follow-up-mode` | yes: `set_steering_mode`, `set_follow_up_mode` (`RPCT:43-44`), lectura mediante `get_state`; el setter escribe el ajuste (`PISRC:core/agent-session.ts:2655`) | missing: Q9 | Inference: conmutador en los ajustes | none | TBD |
| **C8** Ejecutar un comando de shell | `!cmd` añade la salida al contexto, `!!cmd` la deja fuera (`IM:3287-3303`); Escape lo aborta (`IM:3014-3015`); `shellPath`, `shellCommandPrefix` (`SM:149`, `:152`) | yes: `bash` con `excludeFromContext` (`RPCT:55`), `abort_bash` (`RPCT:56`), `bash_execution_update` | missing: Q8 | Inference: modo "Run command" en el compositor | none | TBD |
| **C9** Adjuntar imágenes | Pegar con `app.clipboard.pasteImage` `ctrl+v`, Win/WSL `alt+v` (`KB:142`; `PISRC:modes/interactive/components/custom-editor.ts:95`); arrastrar a una terminal compatible (`PIDOC:usage.md:19`); `images.autoResize`, `images.blockImages` (`SM:67-70`) | yes: `images` en `prompt`, `steer`, `follow_up` (`RPCT:22-24`) | missing: compositor solo de texto; el historial omite las partes de imagen (`D:main/domain/rpc/history.ts:13`); Q10 | Inference: pegar o soltar imágenes en el compositor | none | TBD |
| **C10** Referenciar archivos con `@` | `@` busca archivos, `tab` completa rutas (`PIDOC:usage.md:17-18`; proveedor de autocompletado `IM:807`); `autocompleteMaxVisible` (`SM:174`); argumentos de CLI `@file` (`ARGS:235-236`) | host-side: no hay comando de búsqueda de archivos; Inference: el escritorio tiene acceso al sistema de archivos | missing: no hay autocompletado en `D:renderer/features/conversation/components/Composer.tsx` | Inference: selector de archivos con `@` en el compositor | none | TBD |
| **C11** Ejecutar comandos de extensiones, plantillas y skills | `/<name>` escrito en el editor | yes: `prompt` ejecuta comandos de extensiones y expande plantillas y skills (`PIDOC:rpc-commands.md:31-33`) | partial: cualquier texto, incluido `/…`, se envía como `prompt` (`D:main/domain/session/PiSession.ts:184`); no hay descubrimiento (C12) | Inference: funciona hoy si se escribe | none | TBD |
| **C12** Descubrir comandos con `/` | Escribir `/` abre un menú con los integrados más los comandos de recursos (`PIDOC:usage.md:46`; integrados añadidos en `IM:700-716`) | partial: `get_commands` solo lista comandos de extensiones, plantillas de prompt y skills (`RPCM:680-710`). Los integrados solo existen en modo interactivo: `BUILTIN_SLASH_COMMANDS` solo lo usan `IM:116`, `:700`, `:716`. Inference: un integrado como `/model` enviado mediante `prompt` llega al modelo como texto plano | missing: Q12 | Inference: paleta de comandos | pi, si los integrados deben ser accesibles sobre RPC | TBD |
| **C13** Abrir un editor externo | `app.editor.external` `ctrl+g` (`KB:126`; manejador `IM:4509`); `externalEditor` (`SM:148`) | host-side | missing: Q24 | Inference: poco valor en un compositor de GUI | none | TBD |
| **C14** Editar texto en el prompt | 23 acciones `tui.editor.*`: movimientos del cursor, saltos de palabra, cortar y pegar (kill and yank), deshacer, historial de prompts (`TKB:72-142`; valor por defecto de deshacer sobrescrito en `KB:77-80`) | host-side | partial: solo la edición nativa del textarea; no hay historial de prompts (`D:renderer/features/conversation/components/Composer.tsx`) | Inference: historial de prompts con Arriba/Abajo | none | TBD |
| **C15** Vaciar el editor o salir | `app.clear` `ctrl+c` (`KB:94`; `IM:4189`); dos veces sale; `app.exit` `ctrl+d` en un editor vacío (`KB:95`; `IM:4199`); `/quit` (`IM:3281`) | yes: cerrar stdin apaga pi (`04` §Startup and shutdown) | done: cerrar la aplicación detiene la sesión (`D:main/domain/session/ChatHost.ts:137-140`) | Cierre de ventana (existe) | none | TBD |
| **C16** Suspender en segundo plano | `app.suspend` `ctrl+z`, ninguno en Windows (`KB:96-99`; `IM:4351`) | n/a | n/a: control de trabajos de la terminal | — | none | TBD |
| **C17** Ver las llamadas a herramientas y sus resultados | Se muestran en línea; `app.tools.expand` `ctrl+o` alterna la salida (`KB:117`; `IM:4470`) | yes: `tool_execution_*`, deltas `toolcall_*` (`04` §Events) | missing: los eventos de herramientas solo incrementan un contador de actividad (`D:main/domain/rpc/chatReducer.ts:65-67`); las partes de herramientas no se renderizan (`D:main/domain/rpc/history.ts:15-17`) | Inference: tarjetas de herramientas plegables | none | TBD |
| **C18** Ver el razonamiento | `app.thinking.toggle` `ctrl+t` (`KB:118`; `IM:4502`); `hideThinkingBlock` (`SM:146`) | yes: deltas `thinking_*` (`04` §`message_update` delta types) | missing: el razonamiento no se renderiza (`D:main/domain/rpc/history.ts:15-17`) | Inference: bloque "thinking" plegable | none | TBD |
| **C19** Responder a diálogos de extensiones | Diálogos `select`, `confirm`, `input`, `editor` de las extensiones | yes: `extension_ui_request` / `extension_ui_response` (`04` §Extension UI requests) | done: tarjetas de diálogo para los cuatro tipos (`D:renderer/features/conversation/components/DialogCard.tsx:39-45`) | Tarjetas de pregunta (existen) | none | TBD |
| **C20** Ver avisos, estado y widgets de extensiones | `notify`, `setStatus`, `setWidget`, `setTitle` | yes, como peticiones de tipo dispara y olvida (`04` §Extension UI requests) | partial: solo se interpreta el widget `gentle-agents`; `notify` y el resto se ignoran (`D:main/domain/rpc/chatReducer.ts:180-184`) | Inference: notificaciones para los avisos, chips de estado | none | TBD |
| **C21** Leer Markdown y diagramas renderizados | Renderizado de Markdown; `markdown.codeBlockIndent`, `markdown.mermaid` (`SM:85-88`) | yes: texto de los mensajes | partial: el Markdown se renderiza (`D:renderer/shared/markdown/renderMarkdown.ts:65`); no hay Mermaid (Q25) | Inference: renderizado de Mermaid en los mensajes | none | TBD |

### Contexto, compactación y reintento

| Capacidad | En la CLI | Expuesto sobre RPC | Estado en el escritorio | Superficie en el escritorio | Dependencia de upstream | Prioridad |
|---|---|---|---|---|---|---|
| **K1** Compactar manualmente | `/compact [instructions]` (`IM:3250`, manejador `IM:7010`) | yes: `compact` con `customInstructions` (`RPCT:47`) | missing: Q4 | Inference: acción "Compact now" con instrucciones opcionales | none | TBD |
| **K2** Compactación automática | `compaction.enabled`, `reserveTokens`, `keepRecentTokens`, `modelOverrides` (`SM:28-33`); elemento de `/settings` `autocompact` | partial: `set_auto_compaction` solo alterna `enabled` (`RPCT:48`); eventos `compaction_start` / `compaction_end` | missing: los eventos de compactación no se decodifican (`D:main/domain/rpc/types.ts:17`); Q4 | Inference: estado "Compacting…" en el chat | pi, para los umbrales sobre RPC | TBD |
| **K3** Ver el uso de contexto | Porcentaje de contexto en el pie (`PISRC:modes/interactive/components/footer.ts:159-162`) | yes, solo por consulta: `get_session_stats.contextUsage` (`04` G7) | missing: Q11 | Inference: % de ctx en la barra de estado | none (G7) | TBD |
| **K4** Ver tokens y coste | Uso y coste en el pie (`PISRC:modes/interactive/components/footer.ts:159`); `/session` (S7) | yes, solo por consulta: `get_session_stats` (`RPCT:59`) | missing: Q11 | Inference: coste en la barra de estado | none (G7) | TBD |
| **K5** Reintentar automáticamente los errores transitorios | `retry.enabled`, `maxRetries`, `baseDelayMs`, `maxAgentDelayMs`, `provider.*` (`SM:40-52`); Escape aborta un reintento pendiente (`IM:3677`) | yes: `set_auto_retry` (`RPCT:51`), `abort_retry` (`RPCT:52`), eventos `auto_retry_*` | missing: Q18, Q22. El escritorio desactiva `working` en `agent_end` incluso cuando sigue un reintento (`04` observación de compatibilidad 3) | Inference: banner "Retrying in 4 s… Cancel" | none | TBD |
| **K6** Archivos de contexto y prompt de sistema | `AGENTS.md`, `CLAUDE.md`, `AGENTS.override.md`, `SYSTEM.md`, `APPEND_SYSTEM.md` (`PIDOC:configuration.md:18-20`, `:32-33`, `:41-47`); `--system-prompt`, `--append-system-prompt`, `--no-context-files` (`ARGS:120-124`, `:204`) | no: ningún comando lista los archivos de contexto cargados (comprobado `RPCT:20-74`); los indicadores son solo de lanzamiento | missing: el argv no tiene esos indicadores (`D:main/domain/session/PiSession.ts:127-133`) | Inference: lista "Loaded instructions" por chat | pi, para listar el contexto cargado | TBD |

### Modelos, razonamiento y proveedores

| Capacidad | En la CLI | Expuesto sobre RPC | Estado en el escritorio | Superficie en el escritorio | Dependencia de upstream | Prioridad |
|---|---|---|---|---|---|---|
| **M1** Seleccionar un modelo | `/model [provider/model]` (`IM:3156`, manejador `IM:5116`); `app.model.select` `ctrl+l` (`KB:116`); `--model`, `--provider` (`ARGS:114-117`, `:289-290`); desde 1.0.0, `--provider` sin `--model` es un error en lugar de ignorarse (`PISRC:main.ts:469-474`; `pi@a13d35a:packages/coding-agent/CHANGELOG.md:38`) | yes: `get_available_models` (`RPCT:35`), `set_model` (`RPCT:33`) | missing: Q1 | Inference: selector de modelo en la barra de estado | none | TBD |
| **M2** Establecer el modelo por defecto | El camino "set as default" del selector de modelo llama a `setModel(model, { persist })` (`IM:5267-5274`); `defaultProvider`, `defaultModel` (`SM:135-136`) | no: G4 | missing: Q1 | Inference: "Default model for new chats" en Providers | pi (G4) | TBD |
| **M3** Rotar entre modelos | `app.model.cycleForward` `ctrl+p`, `app.model.cycleBackward` `shift+ctrl+p`, Win/WSL `alt+p` (`KB:108-115`; `IM:4451`) | partial: `cycle_model` no tiene campo de dirección (`RPCT:34`) | missing: Q1 | Inference: atajo de teclado en la aplicación | none | TBD |
| **M4** Elegir los modelos para rotar | `/scoped-models` (`IM:3151`); `--models <patterns>` (`ARGS:141`, `:304`); `enabledModels` (`SM:167`); teclas del selector `app.models.*` (`KB:186-209`) | no: ningún comando establece el ámbito; `cycle_model` solo informa de `isScoped` (`04` §Commands) | missing: Q15 | Inference: favoritos en el selector de modelo | pi | TBD |
| **M5** Establecer el nivel de razonamiento | `/thinking [level]` (`IM:3162`, manejador `IM:5067`); `app.thinking.cycle` `shift+tab` (`KB:100-103`; `IM:4440`); `--thinking` con `off, minimal, low, medium, high, xhigh, max` (`ARGS:157`, `:312`); sufijo `:<thinking>` en `--model` (`ARGS:290`) | yes: `set_thinking_level`, `cycle_thinking_level`, `get_available_thinking_levels` (`RPCT:38-40`); evento `thinking_level_changed` | missing: Q2 | Inference: control de "effort" en la barra de estado | none | TBD |
| **M6** Establecer el nivel de razonamiento por defecto | El selector de razonamiento `app.thinking.save` `ctrl+s` (`KB:104-107`; `PISRC:modes/interactive/components/thinking-selector.ts:131`) persiste `defaultThinkingLevel` (`PISRC:core/agent-session.ts:2575-2576`); `modelThinkingLevels` por modelo (`SM:138`), elemento de `/settings` `model-thinking` | no: el `set_thinking_level` de RPC no pasa `persist` (`RPCM:498`) | missing: Q2 | Inference: esfuerzo por defecto en los ajustes | pi (misma forma que G4) | TBD |
| **M7** Iniciar sesión en un proveedor | `/login [provider]`, OAuth o clave de API (`IM:3234`, manejador `IM:5775-5829`; `PIDOC:providers.md:12`). Desde 1.0.0, el selector de nivel superior termina con "Sign in with Radius", y tras un inicio de sesión con Radius pi ofrece añadir el servidor MCP de Radius al `mcp.json` global y recarga (`IM:5810-5829`, `:6276`, `:6296-6340`; `pi@a13d35a:packages/coding-agent/CHANGELOG.md:25`) | no: G3 | missing: el primer arranque solo comprueba que exista `auth.json` (`D:main/domain/home/home.ts:86`); Q3 | Inference: pantalla Providers con botones de inicio de sesión | pi (G3) | TBD |
| **M8** Cerrar sesión en un proveedor | `/logout` (`IM:3240`, manejador `IM:5930`) | no: G3 | missing: Q3 | Inference: "Sign out" por proveedor | pi (G3) | TBD |
| **M9** Proveedores personalizados y modelos locales | `<agent-dir>/models.json` (`PIDOC:configuration.md:16`); `/llama` gestiona los modelos del router de llama.cpp (`PISRC:extensions/llama/index.ts:183`) | partial: `/llama` solo avisa fuera de la TUI (`PISRC:extensions/llama/index.ts:185-188`); `models.json` es solo un archivo | missing: el primer arranque solo comprueba que exista `models.json` (`D:main/domain/home/home.ts:87`) | Inference: sección "Local models" en Providers | pi | TBD |
| **M10** Usar claves de API del entorno | Variables de entorno y comandos de claves de los proveedores (`PIDOC:providers.md:20-85`); `--api-key` (`ARGS:118`, `:291`) | spawn only | partial: el hijo hereda el entorno del escritorio (`04` §Process chain, paso 3); no hay UI | Inference: campos de clave de API en Providers | none | TBD |
| **M11** Listar modelos desde el shell | `--list-models [search]` (`ARGS:206`, `:324`) | yes: `get_available_models` (`RPCT:35`) | missing: Q1 | Inference: cubierto por M1 | none | TBD |
| **M12** Inspeccionar credenciales desde el shell | `pi auth check`, `print-api-key`, `print-bearer-token` (`ARGS:284`; `PISRC:cli/auth-command.ts:52-56`) | no | missing: Q3 | Inference: "Check connection" por proveedor | pi (G3) | TBD |
| **M13** Ajustar el comportamiento de red | `transport`, `httpProxy`, `httpIdleTimeoutMs`, `websocketConnectTimeoutMs`, `cacheWarming` (`SM:139`, `:180-183`); elementos de `/settings` `transport`, `http-idle-timeout`, `cache-warming-mode` | no | missing: Q21 | Inference: ajustes avanzados | pi | TBD |

### Extensiones, paquetes, skills, prompts, temas y MCP

| Capacidad | En la CLI | Expuesto sobre RPC | Estado en el escritorio | Superficie en el escritorio | Dependencia de upstream | Prioridad |
|---|---|---|---|---|---|---|
| **E1** Instalar, actualizar, eliminar y listar paquetes | `pi install`, `remove`, `uninstall`, `update`, `list` (`ARGS:278-282`; `PISRC:package-manager-cli.ts:267-273`); `-l` escribe en el ámbito del proyecto (`PIDOC:packages.md:19`); `packages` (`SM:159`) | no: G5 | missing: Q20 | Inference: pantalla Extensions (maqueta) | pi (G5) | TBD |
| **E2** Habilitar o deshabilitar recursos de paquetes | TUI `pi config [-l]`, Tab cambia el ámbito (`ARGS:283`; `PISRC:package-manager-cli.ts:796`); filtros por paquete (`SM:122-131`); las extensiones integradas se pueden deshabilitar ahí (`PIDOC:mcp.md:242`) | no: G5 | missing: Q20 | Inference: conmutadores por recurso con ámbito | pi (G5) | TBD |
| **E3** Cargar extensiones para una ejecución | `--extension`, `-e` (`ARGS:176`, `:313`); `--no-extensions`, `-ne` (`ARGS:179`, `:314`); rutas locales `extensions` (`SM:160`) | spawn only | missing: el argv no tiene esos indicadores (`D:main/domain/session/PiSession.ts:127-133`) | Inference: opción para desarrolladores | none | TBD |
| **E4** Usar skills | `/skill:name` cuando `enableSkillCommands` está activado (`SM:164`; `PIDOC:slash-commands.md:58`); `--skill`, `--no-skills` (`ARGS:181`, `:198`); rutas `skills` (`SM:161`) | partial: se invocan mediante `prompt`, las lista `get_commands` | missing: Q13 | Inference: lista de skills en Extensions y en la paleta de comandos | none | TBD |
| **E5** Usar plantillas de prompt | `/<template>` (`PIDOC:slash-commands.md:57`); `--prompt-template`, `--no-prompt-templates` (`ARGS:184`, `:200`); rutas `prompts` (`SM:162`) | partial: se invocan mediante `prompt`, las lista `get_commands` | missing: Q12, Q25 | Inference: plantillas en la paleta de comandos | none | TBD |
| **E6** Elegir un tema | Theme en `/settings`: un tema, o un par claro/oscuro (`PISRC:modes/interactive/components/settings-selector.ts:331-391`); `theme` (`SM:142`); integrados `system` (por defecto), `dark`, `light` (`PIDOC:themes.md:7`); `--theme`, `--use-theme`, `--no-themes` (`ARGS:187-203`) | no: bajo RPC `setTheme()` devuelve `{success:false}` y `getAllThemes()` devuelve `[]` (`04` §What RPC mode drops) | missing: los tokens son fijos en el código (`D:renderer/shared/theme/tokens.css:2-5`); Q19 | Inference: selector de tema en Extensions | pi: datos de temas sobre RPC | TBD |
| **E7** Recargar recursos | `/reload` recarga atajos de teclado, extensiones, skills, prompts, temas y archivos de contexto (`IM:3256`, manejador `IM:6349`; `SC:42`); desde 0.99.2 también habilita las herramientas añadidas recientemente a `defaultTools` (`PIDOC:settings.md:56`; `pi@a13d35a:packages/coding-agent/CHANGELOG.md:64`) | no: no hay comando de recarga en `RPCT:20-74` | missing: Q21 | Inference: "Reload" tras instalar una extensión | pi | TBD |
| **E8** Gestionar servidores MCP | Comando de extensión integrada `/mcp` (`PISRC:extensions/mcp/index.ts:1097`); `pi mcp add`, `remove`, `list`, `login`, `logout` (`ARGS:285`; `PIDOC:mcp.md:82`); `mcp.json` (`PIDOC:configuration.md:15`). Desde 0.99.2, los nombres de herramientas y de espacios de nombres de MCP sustituyen `-` por `_` (`mcp__my-server__x` pasa a ser `mcp__my_server__x`) (`pi@a13d35a:packages/coding-agent/CHANGELOG.md:87`) | partial: `/mcp` mediante `prompt`; fuera de la TUI informa del estado con `notify` en lugar del gestor (`PISRC:extensions/mcp/index.ts:1124-1125`) | missing: Q16; `notify` se ignora (C20). En los homes aprovisionados por gentle-shell 3.7.0, el `/mcp` integrado puede quedar sustituido; gentle-shell 4.0.0 aprovisiona con gentle-ai v4.0.0, que ya no instala ese sustituto (ver [filas del núcleo de pi que gentle-shell cambia](#filas-del-núcleo-de-pi-que-gentle-shell-cambia)) | Inference: sección MCP en Extensions | pi, para el estado estructurado de MCP | TBD |
| **E9** Elegir las herramientas disponibles | `--tools`, `-t`; `--exclude-tools`, `-xt`; `--no-tools`, `-nt`; `--no-builtin-tools`, `-nbt` (`ARGS:143-156`, `:306-311`); `defaultTools` (`SM:168`); nombres de las herramientas integradas (`ARGS:449-457`) | spawn only: ningún comando cambia las herramientas (comprobado `RPCT:20-74`) | missing: el argv no tiene esos indicadores (`D:main/domain/session/PiSession.ts:127-133`) | Inference: conmutadores de herramientas por chat | pi | TBD |

### Confianza del proyecto

| Capacidad | En la CLI | Expuesto sobre RPC | Estado en el escritorio | Superficie en el escritorio | Dependencia de upstream | Prioridad |
|---|---|---|---|---|---|---|
| **T1** Decidir si confiar en un proyecto | Pregunta al arrancar; `/trust` guarda una decisión (`IM:3229`, manejador `IM:5240`); `--approve`, `-a` y `--no-approve`, `-na` (`ARGS:229-232`, `:327-328`); `defaultProjectTrust` `ask`/`always`/`never`, solo global (`SM:151`, `:110`) | no. Bajo RPC no hay UI (`hasUI` solo es true en modo interactivo, `PISRC:main.ts:770`), así que un proyecto sin decidir se resuelve como **no confiable** salvo que `--approve`/`--no-approve` lo sobrescriba, el proyecto no tenga recursos que requieran confianza (entonces es confiable directamente, `PISRC:core/project-trust.ts:47-52`; comprobación en `PISRC:core/trust-manager.ts:186`), una extensión responda a `project_trust`, haya una decisión almacenada o el valor por defecto sea `always` (`PISRC:core/project-trust.ts:54-88`). Los paquetes del proyecto solo se cargan después de resolver la confianza (`PIDOC:packages.md:19-21`) | missing: Q14 | Inference: pregunta de confianza al abrir una carpeta nueva | pi (comando o diálogo de confianza). gentle-shell no gestiona `project_trust` (Y5) | TBD |

### Visualización y terminal

Son sobre todo mecánica de terminal. Para el escritorio solo importan como información de diseño.

| Capacidad | En la CLI | Expuesto sobre RPC | Estado en el escritorio | Superficie en el escritorio | Dependencia de upstream | Prioridad |
|---|---|---|---|---|---|---|
| **U1** TUI normal o a pantalla completa | `--tui-mode` (`ARGS:213`, `:326`); `tuiMode`, `fullscreenExitOutput`, `fullscreenScrollbar`, `fullscreenCopyOnSelect`, `fullscreenWheelScrollLines` (`SM:184-188`). La pantalla completa es el valor por defecto desde 1.0.0; en 0.99.1 era `regular` (`SM:184`, `:1349`; `PIDOC:settings.md:94`; `pi@a13d35a:packages/coding-agent/CHANGELOG.md:24`) | n/a | n/a | — | none | TBD |
| **U2** Buscar en la transcripción y saltar entre prompts | `tui.altScreen.*`: buscar, coincidencia siguiente/anterior, prompt anterior/siguiente, paginación (`TKB:160-209`; sobrescrituras `KB:81-92`) | host-side | missing: Q25 | Inference: buscar en el chat | none | TBD |
| **U3** Opciones de renderizado de la terminal | `terminal.*` (`SM:57-65`); `editorPaddingX`, `outputPad`, `showHardwareCursor` (`SM:172-175`) | n/a | n/a | — | none | TBD |
| **U4** Cabecera de arranque y registro de cambios | `quietStartup`, `true`/`false`, más `"header"` (conservar solo la cabecera de arranque) desde 1.0.0 (`SM:111-112`, `:150`; `PIDOC:settings.md:93`); `--verbose` (`ARGS:227`, `:325`); `/changelog` (`IM:3204`, manejador `IM:6693`); `collapseChangelog` (`SM:154`) | no | missing: Q21 | Inference: "What's new" tras una actualización | pi | TBD |
| **U5** Ayuda de atajos | `/hotkeys` (`IM:3209`, manejador `IM:6728`) | host-side | partial: pistas fijas en el compositor (`D:renderer/features/conversation/components/Composer.tsx:61`) | Inference: hoja de atajos | none | TBD |
| **U6** Atajos de teclado personalizados | `<agent-dir>/keybindings.json` (`KB:380`) | n/a | n/a: el escritorio tiene sus propios atajos (Q24) | — | none | TBD |
| **U7** Configuración inicial | Pide el tema y el consentimiento de analítica (`PISRC:modes/interactive/components/first-time-setup.ts`; se ejecuta en `PISRC:main.ts:674-675`) | n/a: solo en modo interactivo | partial: el primer arranque del escritorio hace otra pregunta, la elección de home (`D:renderer/features/first-run/components/FirstRun.tsx`) | Inference: añadir pasos de tema y analítica | none | TBD |
| **U8** Telemetría, analítica y modo sin conexión | `enableInstallTelemetry`, `enableAnalytics` (`SM:155-156`); `PI_TELEMETRY`, `PI_OFFLINE` (`ARGS:445-446`); `--offline` (`ARGS:233`, `:329`) | spawn only | missing: Q21 | Inference: ajustes de privacidad | none | TBD |

### Ayuda y diagnóstico

| Capacidad | En la CLI | Expuesto sobre RPC | Estado en el escritorio | Superficie en el escritorio | Dependencia de upstream | Prioridad |
|---|---|---|---|---|---|---|
| **H1** Informar de un bug a los desarrolladores de pi | `/bug [description]` (`IM:3183`, manejador `IM:6541`; `PIDOC:sessions.md:62-66`) | no | missing: no hay acción de informe de bugs en `D:` | Inference: "Report a problem" (alcance por decidir: pi frente a gentle-shell frente al escritorio) | pi | TBD |
| **H2** Volcar el estado de depuración | `/debug` escribe las líneas renderizadas y los mensajes en `pi-debug.log` (`IM:3261`, manejador `IM:6860`; `PIDOC:usage.md:92`). Oculto: no está en `BUILTIN_SLASH_COMMANDS` | no | missing: el stderr del hijo solo se registra (`04` §Framing) | Inference: "Copy diagnostics" | pi | TBD |
| **H3** Actualizar pi, las extensiones o los catálogos de modelos | `pi update [source\|self\|pi]` (`ARGS:281`) | no | missing: Q20 | Inference: aviso de actualización | pi | TBD |
| **H4** Mostrar la versión | `--version`, `-v` (`ARGS:93`) | no: G10 | missing: no hay comprobación de versión (`04` §Versioning) | Inference: cuadro About | pi (G10) | TBD |

### Cobertura de atajos de teclado

Los 43 atajos de teclado de la aplicación de `KB:15-57`, con su fila.

| IDs de atajo | Fila |
|---|---|
| `app.interrupt` | C3 |
| `app.clear`, `app.exit` | C15 |
| `app.suspend` | C16 |
| `app.thinking.cycle` | M5 |
| `app.thinking.save` | M6 |
| `app.model.cycleForward`, `app.model.cycleBackward` | M3 |
| `app.model.select` | M1 |
| `app.tools.expand` | C17 |
| `app.thinking.toggle` | C18 |
| `app.editor.external` | C13 |
| `app.message.copy` | S19 |
| `app.message.followUp` | C5 |
| `app.message.dequeue` | C6 |
| `app.clipboard.pasteImage` | C9 |
| `app.session.new` | S1 |
| `app.session.tree` | S8 |
| `app.session.fork` | S11 |
| `app.session.resume` | S3 |
| `app.session.toggleNamedFilter`, `app.session.togglePath`, `app.session.toggleSort` | S4 |
| `app.session.rename` | S5 |
| `app.session.delete`, `app.session.deleteNoninvasive` | S6 |
| `app.tree.foldOrUp`, `app.tree.unfoldOrDown`, `app.tree.filter.default`, `app.tree.filter.noTools`, `app.tree.filter.userOnly`, `app.tree.filter.labeledOnly`, `app.tree.filter.all`, `app.tree.filter.cycleForward`, `app.tree.filter.cycleBackward` | S8 |
| `app.tree.editLabel`, `app.tree.toggleLabelTimestamp` | S9 |
| `app.models.save`, `app.models.enableAll`, `app.models.clearAll`, `app.models.toggleProvider`, `app.models.reorderUp`, `app.models.reorderDown` | M4 |

Los 47 atajos de teclado de la TUI de `TKB:72-209`, por familia:

| Familia | IDs | Fila |
|---|---|---|
| `tui.editor.*` | 23: `cursorUp`, `cursorDown`, `historyPrevious`, `historyNext`, `cursorLeft`, `cursorRight`, `cursorWordLeft`, `cursorWordRight`, `cursorLineStart`, `cursorLineEnd`, `jumpForward`, `jumpBackward`, `pageUp`, `pageDown`, `deleteCharBackward`, `deleteCharForward`, `deleteWordBackward`, `deleteWordForward`, `deleteToLineStart`, `deleteToLineEnd`, `yank`, `yankPop`, `undo` | C14 |
| `tui.input.*` | 4: `newLine` (C2), `submit` (C1), `tab` (C10), `copy` (S19) | según se indica |
| `tui.select.*` | 6: `up`, `down`, `pageUp`, `pageDown`, `confirm`, `cancel` | Navegación de selectores dentro de S3, S8, M1, M4 y C19 |
| `tui.altScreen.*` | 14: `pageUp`, `pageDown`, `halfPageUp`, `halfPageDown`, `lineUp`, `lineDown`, `previousPrompt`, `nextPrompt`, `search`, `searchNext`, `searchPrevious`, `searchClose`, `top`, `bottom` | U2 |

Los IDs `app.*` son idénticos en pi 0.85.1 (comprobado con `diff`).

### Cobertura de indicadores de CLI

Los 40 indicadores que se interpretan en `ARGS:82-235`. El escritorio solo pasa a pi `--mode rpc` y `--session <path>`, a través del lanzador (`D:main/domain/session/PiSession.ts:127-133`).

| Indicadores | Fila |
|---|---|
| `--help`, `-h`; `--version`, `-v` | H4 (versión); la ayuda no tiene equivalente en la GUI |
| `--mode`; `--print`, `-p` | No interactivos. `--mode rpc` es como el escritorio ejecuta pi (`04`). |
| `--continue`, `-c` | S2 |
| `--resume`, `-r`; `--session` | S3 |
| `--session-id` | S18 |
| `--fork` | S11 |
| `--session-dir` | S17 |
| `--no-session` | S16 |
| `--name`, `-n` | S5 |
| `--export` | S13 |
| `--provider`; `--model` | M1 |
| `--api-key` | M10 |
| `--models` | M4 |
| `--thinking` | M5 |
| `--list-models` | M11 |
| `--system-prompt`; `--append-system-prompt`; `--no-context-files`, `-nc` | K6 |
| `--tools`, `-t`; `--exclude-tools`, `-xt`; `--no-tools`, `-nt`; `--no-builtin-tools`, `-nbt` | E9 |
| `--extension`, `-e`; `--no-extensions`, `-ne` | E3 |
| `--skill`; `--no-skills`, `-ns` | E4 |
| `--prompt-template`; `--no-prompt-templates`, `-np` | E5 |
| `--theme`; `--use-theme`; `--no-themes` | E6 |
| `--approve`, `-a`; `--no-approve`, `-na` | T1 |
| `--tui-mode` | U1 |
| `--verbose` | U4 |
| `--offline` | U8 |

También se interpretan: `--` termina el análisis de opciones (`ARGS:82`); los argumentos `@file` adjuntan archivos (`ARGS:235-236`, C10); los `--flags` desconocidos se conservan para las extensiones (`ARGS:237-250`).

Los 8 subcomandos de `ARGS:277-286`: `install`, `remove`, `uninstall`, `update`, `list` (E1; `update` también H3), `config` (E2), `auth` (M12), `mcp` (E8).

### Cobertura de ajustes

Las 55 claves de primer nivel de `interface Settings` (`SM:133-189`). Los ajustes viven en `<agent-dir>/settings.json` (global) y `.pi/settings.json` (proyecto), y la capa del proyecto se fusiona en profundidad sobre la global (`SM:249-253`, `:300-301`). **Menú** significa un elemento de `/settings`: el menú llama exactamente a los setters de `IM:4822-5066`, así que una clave marcada como "archivo" no tiene elemento de menú. **Escritorio:** el escritorio no lee ni escribe ningún ajuste de pi (Q21).

| Clave | Se establece en la TUI mediante | RPC | Fila |
|---|---|---|---|
| `lastChangelogVersion` | interno | no | U4 |
| `defaultProvider`, `defaultModel` | selector de modelo "set as default" | no (G4) | M2 |
| `defaultThinkingLevel` | selector de razonamiento `ctrl+s` | no | M6 |
| `modelThinkingLevels` | menú `model-thinking` | no | M6 |
| `transport` | menú `transport` | no | M13 |
| `steeringMode`, `followUpMode` | menú `steering-mode`, `follow-up-mode` | yes | C7 |
| `theme` | menú `theme` | no | E6 |
| `compaction` | menú `autocompact` (solo `enabled`) | partial: `set_auto_compaction` | K2 |
| `branchSummary` | archivo | no | S10 |
| `retry` | archivo | partial: `set_auto_retry` | K5 |
| `hideThinkingBlock` | menú `hide-thinking`; `ctrl+t` | host-side | C18 |
| `showCacheMissNotices` | menú `cache-miss-notices` | no | C20 |
| `externalEditor` | archivo | host-side | C13 |
| `shellPath`, `shellCommandPrefix` | archivo | no | C8 |
| `quietStartup` | menú `quiet-startup` (`true`, `header`, `false`) | n/a | U4 |
| `defaultProjectTrust` | menú `default-project-trust` (solo global) | no | T1 |
| `npmCommand` | archivo | no | E1 |
| `collapseChangelog` | menú `collapse-changelog` | n/a | U4 |
| `enableInstallTelemetry` | menú `install-telemetry` | no | U8 |
| `enableAnalytics` | configuración inicial | no | U7, U8 |
| `trackingId`, `deviceId` | interno, generado | no | U8 |
| `packages` | `pi install` / `remove` / `config` | no (G5) | E1, E2 |
| `extensions` | archivo; `pi config` | no (G5) | E2, E3 |
| `skills` | archivo; `pi config` | no | E4 |
| `prompts` | archivo; `pi config` | no | E5 |
| `themes` | archivo; `pi config` | no | E6 |
| `enableSkillCommands` | menú `skill-commands` | no | E4 |
| `terminal` | menú `show-images`, `image-width-cells`, `clear-on-shrink`, `terminal-progress` | n/a | U3 |
| `images` | menú `auto-resize-images`, `block-images` | no | C9 |
| `enabledModels` | `/scoped-models`; `--models` | no | M4 |
| `defaultTools` | archivo; indicadores de herramientas | no | E9 |
| `doubleEscapeAction` | menú `double-escape-action` | n/a | S8, S11 |
| `treeFilterMode` | menú `tree-filter-mode` | n/a | S8 |
| `thinkingBudgets` | archivo | no | M6 |
| `editorPaddingX`, `outputPad`, `showHardwareCursor` | menú `editor-padding`, `output-padding`, `show-hardware-cursor` | n/a | U3 |
| `autocompleteMaxVisible` | menú `autocomplete-max-visible` | n/a | C10 |
| `markdown` | menú `mermaid-rendering` | host-side | C21 |
| `warnings` | menú `warnings` (elemento de submenú `anthropic-extra-usage`) | no | C20 |
| `codemode` | archivo | no | E2 (extensión integrada) |
| `sessionDir` | archivo; `--session-dir` | no | S17 |
| `httpProxy`, `httpIdleTimeoutMs`, `websocketConnectTimeoutMs` | archivo; menú `http-idle-timeout` | no | M13 |
| `cacheWarming` | menú `cache-warming-mode` (solo global) | no | M13 |
| `tuiMode`, `fullscreenExitOutput`, `fullscreenScrollbar`, `fullscreenCopyOnSelect`, `fullscreenWheelScrollLines` | menú `tui-mode`, `fullscreen-*` | n/a | U1 |

Inference: aparte de C7, K2 y K5, pi no ofrece ninguna forma de leer o escribir ajustes sobre RPC. Una pantalla de ajustes en el escritorio necesitaría un cambio en pi o ediciones directas de `settings.json`.

### Diferencias entre pi 0.85.1 y 0.99.1 que importan al escritorio

El escritorio importa pi 0.85.1 en el mismo proceso solo para listar sesiones (`04` §Effective versions). Estas comprobaciones cubren ese camino. Comparan contra 0.99.1; `session-manager.ts` es idéntico byte a byte en 1.0.0 (`git diff --stat d86654a a13d35a` está vacío para él), así que también son válidas contra 1.0.0, salvo que `getSessionsDir` se trasladó a `pi@a13d35a:packages/coding-agent/src/config.ts:607-608`.

| Área | Hallazgo | Evidencia |
|---|---|---|
| Formato del archivo de sesión | La misma versión: `CURRENT_SESSION_VERSION = 3` en ambas. | `pi@d981de1:packages/coding-agent/src/core/session-manager.ts:30`; `pi@d86654a:packages/coding-agent/src/core/session-manager.ts:41` |
| Forma de `SessionInfo` que devuelve `listAll()` | Idéntica (comprobado con `diff` de la interfaz). Esto resuelve, para los campos que usa la lista, la cuestión del formato de sesión que quedó como `UNVERIFIED` en la observación de compatibilidad 7 de `04`. | `pi@d981de1:…/session-manager.ts:174`; `pi@d86654a:…/session-manager.ts:229` |
| `listAll()` sin directorio | Ambas leen solo `<agent-dir>/sessions` e ignoran `sessionDir` y `PI_CODING_AGENT_SESSION_DIR`. Ver S17. 0.99.1 añade un `AbortSignal` opcional. | `pi@d981de1:…/session-manager.ts:1685-1700`; `pi@d86654a:…/session-manager.ts:1921-1949`; `getSessionsDir` en `pi@d981de1:packages/coding-agent/src/config.ts:572-573` y `pi@d86654a:packages/coding-agent/src/config.ts:600-601` |
| Comandos slash integrados | 0.99.1 añade `/bug` (H1); ningún otro cambio. No está en el camino 0.85.1 del escritorio. | `diff` de las entradas `name:` en `SC:19-44` y el archivo de 0.85.1 |
| Atajos de teclado de la aplicación | Sin cambios. | `diff` de `KB:15-57` y el archivo de 0.85.1 |

`UNVERIFIED:` si 0.99.1 escribe tipos de entrada de sesión que 0.85.1 leería de otra forma al calcular `firstMessage` o `name`. Solo se compararon la constante de versión y la forma de `SessionInfo`.

## gentle-shell y gentle-ai

Todo lo que gentle-shell (`main` en `ac67159`, paquete npm `gentle-pi` 4.0.0) añade sobre pi (versión mínima 0.99.1, desarrollado contra 1.0.0; `GS:package.json:78`, `:95-97`), más las capacidades de gentle-ai que llegan a una sesión de gentle-shell o a un usuario del escritorio. Las columnas y las palabras de estado son las mismas que en [Columnas](#columnas).

### De un vistazo (gentle-shell y gentle-ai)

| Pregunta | Respuesta |
|---|---|
| ¿Qué añade gentle-shell? | Un lanzador (homes, configuración, carga de paquetes), 18 puntos de entrada de extensiones con 28 comandos slash, 9 atajos (uno de ellos solo cuando `GENTLE_PI_STATS_VIEW_KEY` está definido), 23 herramientas de modelo nuevas, 6 herramientas integradas registradas de nuevo, 1 indicador de CLI, 1 proveedor y 4 renderizadores de mensajes, más 3 temas, 12 skills y 1 plantilla de prompt. 77 filas en 9 grupos más abajo, 5 de ellas para gentle-ai. |
| ¿Cuánto llega a un host RPC? | Muy poco como **datos**. Casi todos los comandos se ejecutan a través de `prompt`, pero la mayoría solo responde con `notify`, que el escritorio ignora (C20), y todo panel construido sobre `ctx.ui.custom()` o sobre una API exclusiva de la TUI se pierde bajo RPC (`04` §What RPC mode drops). |
| Hallazgos más importantes para el escritorio | 1) `/gentle:profiles` y `/gentle:models` abren ambos paneles `ctx.ui.custom()` y después leen `result.type`, así que ninguno de los dos paneles llega a un host RPC; `Inference:` (no ejecutado) probablemente cada manejador lanza un `TypeError` (P1, P3). 2) YOLO y el permiso de revisión "allow for this session" requieren `ctx.mode === "tui"`, así que una sesión de escritorio nunca puede activarlos (Y4, R3). 3) La salida de los comandos es solo `notify`; gestionar `notify` (C20) desbloquea de una vez la mayoría de los comandos `/gentle:*` (V18). 4) El escritorio descarta los mensajes personalizados (comprobación previa de la revisión, resultados de los helpers) porque solo conserva los mensajes `assistant` (V17, A7); desde 4.0.0, a un padre inactivo lo despierta en su lugar un mensaje con rol de usuario (A7). 5) El primer chat en un home aislado nuevo se bloquea mientras el lanzador instala los paquetes complementarios, y el escritorio no muestra ningún progreso (L5). 6) gentle-shell no gestiona `project_trust`, así que T1 se mantiene tal como está escrito. |

### Método (parte de gentle-shell)

**Fuentes.** Actualizadas el 2026-10-03. El `main` de gentle-shell en `ac67159` (paquete `gentle-pi`, versión 4.0.0; 19 commits después del commit de la release 4.0.0 `1f35ab1`, y los hechos de esos commits se marcan como posteriores a la release): `bin/`, `lib/`, cada archivo bajo `extensions/`, `themes/`, `skills/`, `prompts/`, `assets/`, y la documentación `readme-reference.md`, `gentle-shell.md`, `prompt-history.md`, `yolo-mode.md`. gentle-ai `ff77164` (v4.0.0): `internal/app/app.go`, `internal/cli/review_mode.go`, `internal/cli/telemetry.go`, `internal/cli/review_facade.go`, `internal/agents/pi/adapter.go`, `internal/components/engram/inject.go`. Escritorio `5ab4a00` `src/`. Los SHAs fijados anteriores, gentle-shell `1162ce9` (3.7.0) y gentle-ai `6dee8f8` (v3.7.0), solo se citan en comparaciones de versiones.

**Versión (gentle-ai).** gentle-shell 4.0.0 fija un gentle-ai local al paquete **v4.0.0** (`INSTALLER_VERSION = "4.0.0"`, `GS:scripts/gentle-ai-installer.mjs:39`). La etiqueta `v4.0.0` (objeto de etiqueta anotada `89921f9`) apunta al commit `ff77164` (`GS:scripts/gentle-ai-installer.mjs:48-50`), citado como `GAI:`; v4.0.0 trasladó la ruta del módulo de Go a `/v4` (`GS:scripts/gentle-ai-installer.mjs:45-46`, `:51`). El SHA fijado anterior del corpus `gentle-ai@b388eb3` es un ancestro de `ff77164` (`git merge-base --is-ancestor b388eb3 ff77164` tiene éxito), y los `adapter.go`, `app.go`, `review_mode.go`, `telemetry.go` y `rdd_mode.go` citados aquí son idénticos byte a byte entre ambos. gentle-shell 3.7.0 fijaba **v3.7.0** (`gentle-shell@1162ce9:scripts/gentle-ai-installer.mjs:39`), commit `6dee8f8`, que no es un ancestro de `ff77164`; `gentle-ai@6dee8f8` solo se cita donde v3.7.0 difiere de una forma que importa.

**Claves de cita** (además de las claves de [Claves de cita](#claves-de-cita)):

| Clave | Se expande a |
|---|---|
| `GSX:` | `gentle-shell@ac67159:extensions/` |
| `GSL:` | `gentle-shell@ac67159:lib/` |
| `GS:` | `gentle-shell@ac67159:` (cualquier otra ruta) |
| `RR:` | `gentle-shell@ac67159:docs/readme-reference.md:` |
| `GSD:` | `gentle-shell@ac67159:docs/gentle-shell.md:` |
| `GAI:` | `gentle-ai@ff77164:` |

**Cómo se decidió la exposición sobre RPC.** Bajo `--mode rpc`, pi vincula las extensiones con el contexto de UI de RPC y `mode: "rpc"` (`RPCM:318-321`), así que `ctx.hasUI` es **true** y `ctx.mode` es `"rpc"` (`PISRC:core/extensions/runner.ts:564-567`, `:620-622`). Por tanto, una condición sobre `ctx.hasUI` se cumple bajo RPC; una condición sobre `ctx.mode === "tui"`, no. `isInteractiveRpcHost` añade `GENTLE_SHELL_INTERACTIVE_HOST=1` (`GSL:rpc-host.ts:15-26`). Cada fila comprueba qué condición se aplica y si la funcionalidad usa `ctx.ui.custom()`, `setFooter`, `setHeader`, `setEditorComponent` o un `setWidget` con factoría de componentes, todos ellos perdidos bajo RPC (`04` §What RPC mode drops).

#### Evidencia de completitud

| Categoría | Enumerado con | Recuento | Cobertura |
|---|---|---|---|
| Puntos de entrada de extensiones | `pi.extensions: ["./extensions"]` (`GS:package.json:61-63`); `extensions/*.ts` de primer nivel más `extensions/history/index.ts` | 18 | Los 18 están mapeados en [Cobertura de extensiones](#cobertura-de-extensiones). 4.0.0 añade `gentle-stats.ts`. |
| Comandos slash | `rg -c '\.registerCommand\('` sobre `extensions/` y `lib/` | 26 puntos de llamada, 28 nombres | Los 28 nombres están mapeados en [Cobertura de comandos y atajos](#cobertura-de-comandos-y-atajos). 4.0.0 añade `/gentle:stats` (`GSX:gentle-stats.ts:86-89`). Un punto registra `gentle:install-delegation` y `gentle:install-review` en un bucle (`GSX:gentle-ai.ts:9902-9915`); tres puntos auxiliares registran cuatro comandos del banner (`GSX:startup-banner.ts:642-645`). |
| Atajos | `rg '\.registerShortcut\('` | 10 resultados, 9 llamadas | Los 9 están mapeados. El décimo resultado es un comentario (`GSX:gentle-shell.ts:523`). El atajo de `/gentle:stats` solo se registra cuando `GENTLE_PI_STATS_VIEW_KEY` está definido (`GSX:gentle-stats.ts:22-26`, `:90-96`). |
| Herramientas de modelo | `rg '\.registerTool\('` más el auxiliar `tool()` (`GSX:gentle-agents.ts:1402-1429`) y el bucle de herramientas silenciosas (`GSX:quiet-tools.ts:812-814`) | 23 nombres nuevos, 6 integradas registradas de nuevo (`bash` ya no se registra de nuevo en 4.0.0), 1 envoltorio de codemode (`GSL:codemode-renderer.ts:180`) | Todas mapeadas en [Cobertura de herramientas](#cobertura-de-herramientas). |
| Indicadores de CLI registrados por extensiones | `rg '\.registerFlag\('` | 1 | `--no-skill-registry` (I3). |
| Proveedores | `rg '\.registerProvider\('` | 1 | `nan` (I6). |
| Renderizadores de mensajes | `rg '\.registerMessageRenderer\('` | 4 | `gentle-pi.review-preflight` (V17), `gentle-agents.message`, `gentle-agents.orchestrator-message`, `gentle-agents.result` (A7, A9). |
| Indicadores y subcomandos del lanzador | `parseLauncherArgs` (`GSL:gentle-shell-launcher.ts:41-165`) y `helpText()` (`:1146-1189`) | 7 indicadores (`--link`, `--isolated`, `--home`, `--package-root`, `--help`/`-h`, `--version`, `--`), 2 subcomandos propios (`home`, `setup`), 7 subcomandos de pi reenviados (`PI_SUBCOMMANDS`, `:12`) | Filas L1–L8. |
| Temas, skills, prompts | `themes/*.json`, `name:` de `skills/*/SKILL.md`, `prompts/*.md` | 3, 12, 1 | V10, I1, I2. |
| Gestión de `project_trust` | `rg 'project_trust\|defaultProjectTrust\|--approve'` sobre todo el checkout de gentle-shell | 0 resultados | Y5. |

#### Búsquedas en el escritorio (parte de gentle-shell)

La misma forma de comando que en [Búsquedas en el escritorio](#búsquedas-en-el-escritorio), en `gentle-shell-desktop@5ab4a00`.

| ID | Patrón | Resultado |
|---|---|---|
| Q26 | `gentle:` | 0 resultados |
| Q27 | `profile` | 0 resultados |
| Q28 | `yolo\|persona` | 0 resultados |
| Q29 | `review\|rdd\|receipt` | Solo la palabra "preview" en comentarios (`D:renderer/shared/bridge/mockBridge.ts:26`, `:30`, `:72`, `:87`) |
| Q30 | `todo` | 0 resultados |
| Q31 | `usage` | 0 resultados |
| Q32 | `\bodd\b` | Solo comentarios que citan los propios archivos `odd/tasks/*.md` del escritorio (p. ej., `D:main/domain/session/PiSession.ts:61`) |
| Q33 | `memory\|engram` | 4 resultados, solo comentarios (`D:main/domain/rpc/chatReducer.ts:210`; `D:renderer/shared/bridge/mockBridge.ts:24`, `:271`; `D:renderer/shared/bridge/useBridge.ts:7`) |
| Q34 | `worktree` | 0 resultados |
| Q35 | `telemetry\|doctor` | 0 resultados |
| Q36 | `vim\|banner\|customize\|palette` | 0 resultados |
| Q37 | `subagent_\|orchestrator` | 0 resultados |
| Q38 | `setup\|provision` | Solo el `SetupService` propio del escritorio para la elección de home (`D:main/adapters/setupService.ts:15-41`, `D:main/ports/index.ts:89-97`) |
| Q39 | `history` | Solo la carga del historial con `get_messages` (`D:main/domain/session/ChatHost.ts:11-22`, `D:main/domain/rpc/history.ts`); no hay historial de prompts |

### Lanzador y homes

| Capacidad | En la CLI | Expuesto sobre RPC | Estado en el escritorio | Superficie en el escritorio | Dependencia de upstream | Prioridad |
|---|---|---|---|---|---|---|
| **L1** Elegir el home del agente | `--link` (`PI_CODING_AGENT_DIR` o `~/.pi/agent`), `--isolated` (`GENTLE_SHELL_HOME` o `~/.gentle-shell/agent`, el valor por defecto), `--home <path>`; mutuamente excluyentes (`GSL:gentle-shell-launcher.ts:80-118`, `:154-162`, `:191-225`; `RR:260-272`). Desde 4.0.0, el lanzador también pasa al hijo el home de pi propio del usuario como `GENTLE_SHELL_USER_PI_HOME` (gana un valor heredado; si no, `PI_CODING_AGENT_DIR`; si no, `~/.pi/agent`), que lee `/gentle:stats` (V19) (`GSL:gentle-shell-launcher.ts:197-205`, `:958-963`) | spawn only (`04` §Process chain, paso 2) | done: elección en el primer arranque, persistida por el escritorio, pasada como `--link`/`--isolated`, o `--home` cuando `GENTLE_SHELL_HOME` está definido (`D:main/domain/home/home.ts:33-37`, `D:main/adapters/setupService.ts:21-38`). Salvedad: el lanzador lee `GENTLE_SHELL_HOME` como el directorio aislado (`GSL:gentle-shell-launcher.ts:207-209`), mientras que el escritorio lo convierte en modo ruta; el modo ruta se niega a aprovisionar automáticamente un directorio no vacío que no le pertenece (`GS:bin/gentle-shell.mjs:1124-1131`) | Primer arranque (existe) | none | TBD |
| **L2** Persistir la elección de home para la terminal | `gentle-shell home [link\|isolated\|<path>]` lee o escribe `~/.gentle-shell/config.json` (`GS:bin/gentle-shell.mjs:364-385`; `GSL:gentle-shell-launcher.ts:241-243`; `RR:274-276`) | no: comando aparte del lanzador, ejecutado por fuera del canal | partial: el escritorio mantiene su propia elección y siempre pasa un indicador de home, y un indicador prevalece sobre la configuración del lanzador (`GSL:gentle-shell-launcher.ts:214-222`). `Inference:` la aplicación ignora la elección `gentle-shell home` de un usuario de terminal | Inference: opción "Same home as my terminal" | none | TBD |
| **L3** Mostrar las versiones | `gentle-shell --version` imprime `gentle-shell <v>`, `pi <v>`, `home <mode> <dir>` (`GSL:gentle-shell-launcher.ts:90-93`, `:1138-1144`; `GS:bin/gentle-shell.mjs:1217-1219`) | no: G10 | missing: no hay comprobación de versión (`04` §Versioning) | Inference: cuadro About | none (G10) | TBD |
| **L4** Aprovisionar los paquetes complementarios | `gentle-shell [home selector] setup [--dry-run]` ejecuta el gentle-ai local al paquete como `install --agent pi --scope global` (`GSL:gentle-shell-launcher.ts:143-146`, `:1167-1169`; `GS:bin/gentle-shell.mjs:821`, `:944-954`; `RR:284-304`). Necesita el gentle-ai fijado ≥ 3.6.0 (`GSL:gentle-shell-launcher.ts:428`) | no | missing: Q38 | Inference: "Repair companions" en Extensions | none | TBD |
| **L5** Aprovisionamiento automático en el primer arranque y resincronización | Un lanzamiento simple contra un home aislado o `--home` (nunca `--link`, nunca un subcomando de pi) ejecuta el flujo de configuración cuando el home nunca se aprovisionó o cambiaron el gentle-ai fijado o la versión de gentle-pi; marcador `provisioned` en `config.json`; bloqueo `<home>/.gentle-shell-setup.lock`; tiempo límite del hijo de 15 minutos; exclusión con `GENTLE_SHELL_NO_AUTO_SETUP=1` (`GS:bin/gentle-shell.mjs:1114-1178`, `:1265-1278`; `RR:348-364`) | spawn: se ejecuta antes de que arranque pi; toda la salida del hijo va a stderr, así que el stdout de RPC queda limpio (`GS:bin/gentle-shell.mjs:1160`; `RR:354`) | partial: todo lanzamiento aislado pasa por él, pero el escritorio solo registra stderr (`04` §Framing). `Inference:` el primer chat en un home aislado nuevo espera a una instalación de gentle-ai sin ningún progreso visible | Inference: progreso "Setting up Gentle…" en el primer lanzamiento | Inference: una señal de progreso de la configuración legible por máquina (gentle-shell) | TBD |
| **L6** Valores por defecto de un home aislado nuevo | Escribe `"tuiMode": "fullscreen"`, `"theme": "Gentleman-Cute"` (si no hay ninguno), el marcador de propiedad `.gentle-shell-home` y una pista en stderr (`GS:bin/gentle-shell.mjs:1238-1243`; `RR:350`); deshabilita el `codemode` integrado de pi en los homes que pertenecen a gentle-shell (`GS:bin/gentle-shell.mjs:1279-1292`) | spawn | n/a: ocurre dentro del lanzador | — | none | TBD |
| **L7** Ejecutar comandos de paquetes de pi contra el home resuelto | `gentle-shell install\|remove\|uninstall\|update\|list\|config\|auth` reenviados a pi sin inyección de paquetes (`GSL:gentle-shell-launcher.ts:12`, `:1171-1180`; `RR:278-282`). `mcp` no está en `PI_SUBCOMMANDS` | no: G5 | missing: Q20 | Inference: pantalla Extensions | pi (G5), o llamadas al lanzador por fuera del canal (Inference) | TBD |
| **L8** Cargar gentle-pi y tomar el control de una copia en conflicto | Sin ninguna declaración de gentle-pi en los ajustes, inyecta solo `-e <package root>`, y pi descubre las extensiones, skills, prompts y temas del paquete; la toma de control añade `--no-extensions`, luego `-e` por cada otro paquete de los ajustes y cada entrada de extensión suelta, y luego `-e <package root>`; una declaración coincidente no recibe inyección (`GSL:gentle-shell-launcher.ts:916-952`). `--package-root <dir>` fuerza una toma de control en modo `--link` (`GSL:gentle-shell-launcher.ts:125-133`; `GS:bin/gentle-shell.mjs:1294-1303`; `RR:344`). `RR:328` y `RR:335` todavía describen un `--theme <root>/themes --skill <root>/skills --prompt-template <root>/prompts` adicional; ese texto está desfasado respecto al código | spawn | missing: el argv no tiene `--package-root` (`D:main/domain/session/PiSession.ts:127-133`) | Inference: opción para desarrolladores | none | TBD |
| **L9** Elegir el runtime de pi | `GENTLE_SHELL_PI`, luego el pi incluido en el paquete y luego `pi` en `PATH`; mínimo 0.99.1; `.cmd`/`.bat` se ejecutan a través de `cmd.exe` en win32 (`GSL:gentle-shell-launcher.ts:368-379`, `:392`; `RR:306-314`, `:366-368`) | spawn | partial: el hijo hereda el entorno del escritorio, así que `GENTLE_SHELL_PI` funciona; no hay UI ni traducción de errores (`04` §Process chain) | Inference: línea "pi runtime" en el diagnóstico | none | TBD |
| **L10** Pista para reanudar al salir | Imprime `To resume in gentle-shell:` después de la pista de pi (`GSL:gentle-shell-resume-hint.ts:17`, `:169`; `GSX:resume-hint.ts:38-40` requiere `ctx.mode === "tui"`) | n/a: solo al salir de la TUI | n/a: la barra lateral reabre los chats (S3) | — | none | TBD |
| **L11** Puente (bridge) del ciclo de vida de Herdr | Carga automáticamente `extensions/herdr-agent-state.ts` dentro de Herdr; se omite para RPC y sin TTY (`GS:bin/gentle-shell.mjs:186-199`; `RR:378-386`) | n/a | n/a: integración con un multiplexor de terminal | — | none | TBD |
| **L12** Actualizar gentle-shell | No hay comprobación de actualizaciones: `rg` de comprobaciones de actualización en `bin/`, `lib/`, `extensions/` no encuentra ninguna; la documentación llama a la resolución del runtime "not an auto-updater" (`RR:312`). Actualizar es `npm i -g gentle-pi`, tras lo cual L5 resincroniza el home (`RR:352`) | no | missing: no hay comprobación de versión (L3), así que no hay nada con lo que comparar | Inference: aviso "Update available" | Inference: una fuente de versión (G10) | TBD |

### Experiencia del shell

| Capacidad | En la CLI | Expuesto sobre RPC | Estado en el escritorio | Superficie en el escritorio | Dependencia de upstream | Prioridad |
|---|---|---|---|---|---|---|
| **V1** Marco del prompt con etiqueta de trabajando, en cola y fase | `GentlePromptEditor` mediante `setEditorComponent` (`GSX:gentle-shell.ts:1104-1120`); pétalo, etiqueta `working`/`queued`, etiqueta de fase de ODD; el marco sigue el estilo de tarjeta, el marco redondeado `neon` o el prompt pintado `float` (`GSD:51-62`) | partial: `setEditorComponent` se descarta; el estado de cola está disponible como `queue_update` (`04` §Events); la fase, como en O2 | partial: el compositor solo conoce `working` (`D:main/domain/session/PiSession.ts:169-180`) | Inference: chip de estado en el compositor | none (cola); G2 (fase) | TBD |
| **V2** Cabecera y barra de estado compacta | Cabecera a pantalla completa (140 columnas o más): marca, cwd, rama, número de cambios sin confirmar, `model · effort · profile`, indicador de contexto, coste con `sub`, uso por modelo; su ubicación es configurable, encima de la entrada o debajo de la entrada como un pie flotante que además agrupa los cambios capturados y los estados de las integraciones. Por debajo de 140 columnas, la pantalla completa no tiene barra lateral, y el modo normal mantiene la barra compacta de una línea con los estados de las extensiones y el nombre de la sesión (`GSX:gentle-shell.ts:1789-1874`; `GSD:24-49`, `:37-38`). `GENTLE_PI_SHELL=0` restaura el pie de pi (`GSL:shell-bar.ts:107-111`) | partial: `setFooter` se descarta. Modelo y esfuerzo: `get_state`; coste y contexto: `get_session_stats`; cwd, rama, perfil: nada (`04` G6, G7) | missing: Q11, Q27, Q31 | Inference: barra de estado (maqueta) | gentle-shell (G6), pi (G7) | TBD |
| **V3** Tarjeta de estado | Primera tarjeta de la columna derecha de la pantalla completa (Status → Changes → TODO): Proyecto (cwd, rama, nombre de la sesión, perfil activo), Cambios, Integraciones (`setStatus` de otras extensiones) (`GSD:33-34`) | partial: `setStatus` llega al host (`04` §Extension UI requests); el resto, como V2 | missing: `setStatus` se ignora (`D:main/domain/rpc/chatReducer.ts:183`) | Inference: panel lateral | como V2 | TBD |
| **V4** Uso de la suscripción | `/gentle:usage`, `alt+u` (`GENTLE_PI_SHELL_USAGE_KEY`) (`GSX:gentle-shell.ts:1345-1346`, `:1633-1665`); proveedores Codex, Claude, NaN y cualquier fuente `gentle-pi:usage-source/v1` (`GSD:105-140`) | no: el panel es `ctx.ui.custom()` (`GSX:gentle-shell.ts:1634`). `Inference:` el uso se sigue obteniendo al iniciar la sesión bajo RPC, porque solo se comprueba `ctx.hasUI` (`GSX:gentle-shell.ts:1774`, `:1875`) | missing: Q31 | Inference: medidores de uso en Providers y en la barra de estado | gentle-shell: publicar el uso como datos | TBD |
| **V5** Cambios capturados | `/gentle:changes`, `alt+g` (`GENTLE_PI_SHELL_CHANGES_KEY`); widget `gentle-shell-changes`; superposición de diff a dos paneles (`GSX:gentle-shell.ts:1163-1166`, `:1333-1343`, `:1925-1945`; `GSD:64-97`). La evidencia se guarda como entradas de sesión `gentle-pi.session-change/v1` (`GSL:session-change-capture.ts:28`; `GSD:84`) | partial: la superposición y el widget son exclusivos de la TUI. `Inference:` la evidencia en bruto se puede leer con `get_entries` y `entry_appended` (`04` §Commands, §Events) | missing: Q34 | Inference: vista "Changes" con diffs por worktree | Inference: un esquema de entradas documentado (gentle-shell) | TBD |
| **V6** Registrar un worktree de la sesión | Herramienta de modelo `session_worktree_register` (`GSX:gentle-shell.ts:1748-1751`); entradas `gentle-pi.session-worktree/v1` (`GSL:session-worktree-registry.ts:114`) | yes: eventos de herramientas | missing: las llamadas a herramientas no se renderizan (C17) | Inference: lista de worktrees en Changes | none | TBD |
| **V7** Paleta de comandos | `/gentle:commands`, `alt+k` (`GENTLE_PI_COMMANDS_KEY`); grupos seleccionados Configuration, Session, Diagnostics, Skills (`GSX:gentle-shell.ts:1169`, `:1946-1956`; `GSL:command-palette.ts:353-357`; `GSL:command-palette-catalog.ts:19-59`) | partial: la paleta es `ctx.ui.custom()` (`GSX:gentle-shell.ts:1321`); los comandos que lista se ejecutan a través de `prompt` y aparecen en `get_commands` (`04`) | missing: Q12, Q36 | Inference: paleta de comandos que reutilice los grupos y etiquetas seleccionados | none | TBD |
| **V8** Personalización visual | `/gentle:customize`: Animations, Banner, Themes, Editor (Vim, YOLO), History, Layout, Cards (`neon`/`float`; en 4.0.0 el estilo también abarca los paneles Agents, Todos y Status, el prompt y la cabecera/el pie), Sections, Profiles (perfiles visuales), Reset (`GSX:gentle-shell.ts:1957-1963`; `GSL:visual-customize-view.ts:32`; `GSD:158-176`); archivos `visual-customization.json`, `visual-profiles.json`, `card-style.json` (`GSL:visual-profiles.ts:104`; `GSL:card-style-policy.ts:12`) | no: el comando se niega salvo que `ctx.mode === "tui"` (`GSX:gentle-shell.ts:1960-1961`) | missing: los tokens son fijos en el código (Q19, Q36) | Inference: ajustes de Appearance | none | TBD |
| **V9** Modo de animación | `/gentle:animations [status\|quality\|performance\|potato]`; `animations.json` (`GSX:gentle-shell.ts:2296-2324`; `RR:967-979`) | partial: el comando se ejecuta (`select`, `notify`); solo afecta al renderizado de la TUI | n/a: animación de terminal. `Inference:` corresponde a un ajuste de movimiento reducido | — | none | TBD |
| **V10** Temas incluidos | `Gentle`, `Gentleman-Cute`, `Gentleman-Sexy` (`GS:themes/`; `GS:package.json:64-66`); el valor por defecto para los homes aislados es `Gentleman-Cute` (L6) | no: E6 | partial: una copia fija en el código, `D:renderer/shared/theme/gentleman-cute.json` (Q19) | Inference: selector de tema | pi (E6), o leer directamente los archivos JSON (Inference) | TBD |
| **V11** Banner de arranque | `/gentle:banner`, `/gentle:toggle-rose`, `/gentle:toggle-text-logo`, `/gentle:banner-color` (`pink`, `cyan`, `yellow`, `green`); `banner.json` (`GSX:startup-banner.ts:590-645`; `RR:999`). Cabecera dibujada con `setHeader` (`GSX:startup-banner.ts:750`) | partial: los comandos se ejecutan (`select`, `notify`); la cabecera se descarta | missing: Q36 | Inference: pantalla de bienvenida, poco valor | none | TBD |
| **V12** Edición del prompt con Vim | `/gentle:vim [status\|enable\|disable]`; `vim.json` (`GSX:gentle-shell.ts:2272-2294`; `RR:981-997`). El adaptador del editor solo admite los pares de paquetes de pi auditados `0.99.1`, `0.99.2` y `1.0.0` (`RR:997`; `GSD:199`) | partial: el comando se ejecuta; el editor es exclusivo de la TUI | missing: Q36 | Inference: modo Vim opcional en el compositor | none | TBD |
| **V13** Comportamiento de Esc | Abortar envía los mensajes encolados cuando la ejecución se asienta; doble Esc para cancelar, de activación voluntaria (opt-in); doble Esc en reposo borra un borrador (`GSX:gentle-shell.ts:2390-2417`; `RR:935-965`); `/gentle:double-esc-cancel [status\|enable\|disable]`, `double-esc-cancel.json`, `GENTLE_PI_DOUBLE_ESC_CANCEL` (`GSX:gentle-shell.ts:1124`, `:2330-2359`) | host-side | partial: Escape aborta (C3); el encolado no está admitido (C4) | Inference: la misma semántica en el compositor | none | TBD |
| **V14** Historial de prompts | `/history`, `ctrl+shift+r` (`GSX:history/index.ts:94`, `:1410-1418`); la captura es de activación voluntaria mediante `/gentle:customize` → History, `history-capture.json` o `GENTLE_PI_HISTORY_CAPTURE` (`GS:docs/prompt-history.md:8-56`) | partial: el selector es `ctx.ui.custom()` (`GSX:history/index.ts:1193`). `Inference:` la captura sigue ejecutándose bajo RPC cuando está activada, a través de `before_agent_start` (`GSX:history/index.ts:1376`) | missing: Q39 | Inference: historial con flecha arriba y búsqueda en el compositor | none | TBD |
| **V15** Tarjetas de herramientas silenciosas y tarjeta Code | Vuelve a registrar `read`, `grep`, `find`, `ls`, `edit`, `write` con renderizadores de tarjeta; desde 4.0.0, `bash` se deja a la herramienta nativa de pi, que conserva el `shellPath` y los prefijos configurados (`RR:142`; `GSD:152` todavía enumera `bash`, desactualizado respecto al código); `GENTLE_PI_QUIET_TOOLS=0` lo desactiva; tarjeta compacta de `codemode` (`GSX:quiet-tools.ts:25-39`, `:792-815`; `GSL:codemode-renderer.ts:180`; `GSD:152`, `:178-185`). También incluye `@heyhuynhgiabuu/pi-pretty` 0.6.27 (`GSX:pi-pretty.ts`; `GS:package.json:75`). `UNVERIFIED:` qué registra pi-pretty; el paquete no está instalado en el checkout de referencia | yes para los eventos de herramientas (C17); el renderizado es exclusivo de la TUI | missing: C17 | Inference: tarjetas de herramientas | none | TBD |
| **V16** Tarjetas de notificación | Los avisos de Gentle siguen el estilo de tarjeta seleccionado, `neon` (marco redondeado) o `float` (panel con fondo de tono) (`GSD:142-156`) | yes: peticiones `notify` | missing: C20 | Inference: notificaciones | none | TBD |
| **V17** Tarjeta de comprobación previa de la revisión y aviso de binario de desarrollo | Renderizador de mensajes para `gentle-pi.review-preflight` (`GSX:gentle-shell.ts:1347`, `:1627-1632`); widget de binario de desarrollo `gentle-shell-dev-binary` (`GSX:gentle-shell.ts:1348`, `:1890-1895`) | partial: la comprobación previa llega como mensaje personalizado (R2). La tarjeta del binario de desarrollo es un widget con factoría de componentes, que se descarta bajo RPC; en el `main` de gentle-shell (`ac67159`), después de la release 4.0.0 (#1652), el `notify` de respaldo solo se envía cuando el shell está desactivado (`GENTLE_PI_SHELL=0`, o dentro de un helper) (`GSX:gentle-ai.ts:9706-9710`; `GSL:shell-bar.ts:107-111`), mientras que una comprobación de sobrescritura fallida sigue enviando un `notify` bajo `ctx.hasUI` (`GSX:gentle-ai.ts:9711-9713`). `Inference:` por defecto un host RPC no recibe ningún aviso de binario de desarrollo salvo que esa comprobación falle; en la release 4.0.0 y en 3.7.0, una sobrescritura activa o no válida siempre llegaba como `notify` (`gentle-shell@1f35ab1:extensions/gentle-ai.ts:9368-9370`; `gentle-shell@1162ce9:extensions/gentle-ai.ts:9369-9370`) | missing: los mensajes que no son del asistente se descartan (`D:main/domain/rpc/chatReducer.ts:81-82`; `D:main/domain/rpc/history.ts:18`); `notify` se ignora (C20) | Inference: tarjeta de recordatorio en el chat; banner de advertencia | none | TBD |
| **V18** Salida de los comandos | La mayoría de los comandos `/gentle:*` responden solo con `ctx.ui.notify` (87 llamadas en `GSX:gentle-ai.ts`, 29 en `GSX:gentle-shell.ts`, contadas con `rg -o 'ctx\.ui\.notify'`) | yes: `notify` | missing: C20 | Inference: una notificación o tarjeta de resultado por comando | none | TBD |
| **V19** Estadísticas de uso | `/gentle:stats`, nuevo en 4.0.0: un panel que ocupa toda la terminal sobre el historial local de sesiones de pi, con las pestañas Overview (mapa de calor de actividad, modelo favorito, tokens, rachas), Models (tokens, coste, mensajes y proporción por modelo) y Session. Lee los archivos de sesión de primer nivel del home activo y del home de pi propio del usuario (`GENTLE_SHELL_USER_PI_HOME`, o si no `~/.pi/agent`), no persiste nada nuevo y excluye las ejecuciones de helpers; no hay atajo por defecto, `GENTLE_PI_STATS_VIEW_KEY` asigna uno (`GSX:gentle-stats.ts:10-32`, `:86-96`; `GSD:256-278`) | no: el panel es `ctx.ui.custom()`, y fuera de la TUI el comando solo envía el `notify` "The stats overlay requires TUI mode." (`GSX:gentle-stats.ts:49-56`) | missing: Q11, Q31; `notify` se ignora (C20) | Inference: vista del historial de uso junto a las estadísticas de la sesión (S7, K4) | none. `Inference:` el panel solo lee archivos de sesión que pi ya escribe (`GSX:gentle-stats.ts:10-12`), así que el escritorio podría agregar esos mismos archivos por sí mismo | TBD |

### Helpers (subagentes)

| Capacidad | En la CLI | Expuesto sobre RPC | Estado en el escritorio | Superficie en el escritorio | Dependencia de upstream | Prioridad |
|---|---|---|---|---|---|---|
| **A1** Delegar trabajo en un helper | Herramientas de modelo `subagent_list_agents`, `subagent_run` (`agent`, `task`, `label?`, `context?`, `workspace_root?` o `repository_root?`, `mode?`), `subagent_continue` (`GSX:gentle-agents.ts:62`, `:1527-1537`, `:1613-1616`; `GSD:218`). El modo en segundo plano necesita un padre vivo interactivo o RPC (`GSX:gentle-agents.ts:1191`, `:1329`; `RR:910-912`). `GENTLE_PI_AGENTS=0` lo deshabilita (`GSX:gentle-agents.ts:151-154`) | yes: herramientas de modelo, más el envío de actividad bajo el host interactivo (`04` §gentle-shell additions) | partial: lista e hilo de Helpers (`D:renderer/features/helpers/HelpersContainer.tsx`), con las carencias del parser de las observaciones 2 y 6 de `04` y de [audit A5](03-architecture/audit.md#a5-el-conjunto-de-estados-de-los-helpers-y-los-elementos-de-herramienta-no-coinciden-con-gentle-shell). gentle-shell publica `completed` y `timed_out` (`GSL:agents-protocol.ts:9-17`); el escritorio descarta una tarea con cualquiera de esos estados (`D:main/domain/rpc/helpersActivity.ts:21`, `:139-141`). `Inference:` (no ejecutado) una tarea vista por primera vez en ejecución se conserva por la fusión de retención y se convierte en `done` (`D:main/domain/rpc/chatReducer.ts:225-240`), así que un helper que agotó su tiempo se muestra como terminado; solo falta una tarea vista por primera vez ya terminada. `Inference:` (no ejecutado) se descarta todo elemento de herramienta real, porque el escritorio exige un `callId` que el publicador nunca envía (`D:main/domain/rpc/helpersActivity.ts:107-118`; `GSL:agents-rpc-publisher.ts:97-105`) | Pestaña Helpers (existe) | none | TBD |
| **A2** Seguir los helpers en vivo | Tarjeta de agentes encima del editor con `model · effort`, tokens, coste, tiempo transcurrido (`GSX:gentle-agents.ts:1172`; `GSD:205-212`); `ctrl+shift+a` la pliega (`GENTLE_PI_AGENTS_KEY`) (`GSL:agents-keys.ts:7`, `:17-21`; `GSX:gentle-agents.ts:1635-1644`) | partial: `gentle-agents.activity/v1` omite `model`, `tokens`, `cost` (nota sobre la carga en `04`) | partial: la lista y el hilo existen; no hay modelo, tokens ni coste; el hilo no muestra filas de herramientas y un helper que agotó su tiempo se muestra como terminado (A1) | Franja de Helpers (existe) | gentle-shell: añadir campos (G8) | TBD |
| **A3** Superposición de agentes | `/gentle:agents`, `alt+a` (`GENTLE_PI_AGENTS_VIEW_KEY`): ámbito Current y All-sessions, Follow, abrir la transcripción de la sesión en `$EDITOR`, hilo a pantalla completa (`GSX:gentle-agents.ts:55`, `:1646-1655`; `GSL:agents-keys.ts:8`, `:11-15`; `GSD:226-231`) | no: retorna antes de tiempo con "requires TUI mode" cuando `ctx.mode !== "tui"` (`GSX:gentle-agents.ts:1081-1086`) | partial: la pestaña Helpers solo cubre la sesión actual | Inference: ámbito "All sessions"; abrir la transcripción | gentle-shell (G8) | TBD |
| **A4** Detener helpers | `alt+s` (`GENTLE_PI_AGENTS_STOP_KEY`) detiene los helpers propios activos o en cola; **Stop** de la superposición (`s`) (`GSL:agents-keys.ts:9`, `:23-27`; `GSX:gentle-agents.ts:1656-1662`); herramienta de modelo `subagent_cancel` (`:1602`) | no: G1 | missing: Stop está deshabilitado (`D:renderer/features/helpers/components/HelpersFooter.tsx:16`, `:36`) | Botón Stop (maqueta) | gentle-shell y un canal de entrada (G1) | TBD |
| **A5** Responder a la pregunta de un helper | El `select`/`confirm`/`input`/`editor` de un hijo en modo tarea llega al padre como un diálogo normal; la pregunta de un hijo en segundo plano se descarta (`GSD:214`). Las consultas del hijo mediante `subagent_parent_message` se responden con `subagent_reply` (`GSX:gentle-agents.ts:195-198`, `:1595`; `GSD:224`) | yes: los diálogos de un hijo en modo tarea aparecen como diálogos del padre; las respuestas, solo a través del modelo | partial: se responden como tarjetas de diálogo normales (C19), sin vínculo con el helper (Inference) | Inference: tarjeta de pregunta dentro del hilo del helper | none | TBD |
| **A6** Redirigir o continuar un helper | Herramientas de modelo `subagent_send_message`, `subagent_continue` (`GSX:gentle-agents.ts:1608`, `:1613`) | partial: solo pidiéndoselo al modelo mediante `prompt` | missing: Q37 | Inference: cuadro de mensaje en el hilo del helper | canal de entrada (forma de G1) | TBD |
| **A7** Recibir resultados en segundo plano | Mensaje personalizado `gentle-agents.result`. Un padre ocupado lo recibe como una redirección (steer) que inicia un turno; desde 4.0.0, un padre inactivo lo almacena sin iniciar un turno y después lo despierta un mensaje con rol de usuario, "[System-generated Gentle Agents notification, not written by the user] …", enviado con `sendUserMessage(..., {deliverAs: "steer"})`. Tarjetas Agent result y Stale agent result (`GSX:gentle-agents.ts:56`, `:63-65`, `:686-712`, `:720`, `:939-963`; `GSD:223`) | partial: eventos de mensajes personalizados; el despertar es un mensaje de usuario normal | missing: los mensajes que no son del asistente se descartan (`D:main/domain/rpc/chatReducer.ts:81-82`). `Inference:` (no ejecutado) el despertar en vivo también se descarta, pero al reabrir un chat el historial conserva los mensajes de usuario (`D:main/domain/rpc/history.ts:37-38`), así que el texto del despertar aparece como una burbuja de usuario sin el resultado | Inference: tarjeta de resultado en el chat | none | TBD |
| **A8** Política de subagentes en segundo plano | `/gentle:background-subagents [status\|enable\|disable]`; el `.pi/gentle-ai/background-subagents.json` del proyecto prevalece sobre el global `<configHome>/background-subagents.json`, que prevalece sobre `GENTLE_PI_BACKGROUND_SUBAGENTS`; valor por defecto `off` (`GSX:gentle-ai.ts:10152-10178`; `RR:908-933`) | partial: se ejecuta a través de `prompt`; sin argumento abre un `select`; el informe es `notify` | missing: Q26 | Inference: conmutador en los ajustes con la fuente que decide | none | TBD |
| **A9** Enviar mensajes a otras sesiones abiertas | Herramientas de modelo `orchestrator_session_id`, `orchestrator_list`, `orchestrator_send_message`; consentimiento Allow once / Allow for this session / Deny (`GSX:gentle-agents.ts:1432-1464`; `GSL:session-messaging-grants.ts:81`; `GSD:219`) | yes: el consentimiento es un `select` siempre que `ctx.hasUI` | partial: el consentimiento se puede responder como tarjeta de diálogo (C19); no hay vista de las otras sesiones | Inference: tarjeta de consentimiento que nombre a la otra sesión | none | TBD |
| **A10** Helpers en otro repositorio | `subagent_run.repository_root` con un permiso interactivo (`GSL:foreign-target-grants.ts:21`; `GSD:221`) | no: se rechaza cuando `ctx.mode !== "tui"` (`GSX:gentle-agents.ts:1218`) | missing: Q37 | Inference: diálogo de permiso | gentle-shell | TBD |
| **A11** Definiciones de helpers y agentes empaquetados | Agentes en Markdown en `<agent home>/agents/`, `<agent home>/subagents/`, `<cwd>/.pi/agents/`, `<cwd>/.pi/subagents/` (`GSL:agents-config.ts:214-217`). El home del agente es `GENTLE_PI_AGENT_HOME`, luego `PI_CODING_AGENT_DIR` y luego `~/.pi/agent` (`GSL:agent-home.ts:6-8`; `GSD:203`), y el lanzador asigna ambas variables al home resuelto (`GSL:gentle-shell-launcher.ts:958-963`), así que con `--isolated` viven bajo `~/.gentle-shell/agent` (L1). Claves de `subagents.json` `default_model`, `default_effort`, `default_mode`, `model_profiles`, `stall_timeout_ms`, `tool_stall_timeout_ms`, `max_concurrency`, `history_max_tasks` (`GSD:201-203`); `/gentle:install-delegation`, `/gentle:install-review` con `--force` (`GSX:gentle-ai.ts:9902-9915`; `RR:606-611`) | partial: los comandos de instalación a través de `prompt` (solo `notify`); las definiciones son archivos | missing: Q37 | Inference: lista de helpers en Extensions | none | TBD |
| **A12** Historial y transcripciones de los helpers | Tareas terminadas en `<agent home>/gentle-agents/tasks/`, sesiones hijas en `<agent home>/gentle-agents/sessions/`, home del agente como en A11 (`GSL:agents-history.ts:18-19`; `GSX:gentle-agents.ts:124-126`, `:351-357`; `GSD:233` muestra el valor por defecto `~/.pi/agent`) | no: G8 | missing: Q37 | Inference: vista "Why did it do that?" (propuesta de la comunidad, [issue #28, "Author's framing: philosophy"](https://github.com/Gentleman-Programming/gentle-shell-desktop/issues/28)) | gentle-shell (G8) | TBD |

### Flujo de trabajo ODD y seguimiento de tareas

| Capacidad | En la CLI | Expuesto sobre RPC | Estado en el escritorio | Superficie en el escritorio | Dependencia de upstream | Prioridad |
|---|---|---|---|---|---|---|
| **O1** ODD en cada petición | Prompt del harness con los 7 pasos de ODD (autorizar, explorar, resolver la incertidumbre, clasificar, registrar, implementar, cerrar) (`GSX:gentle-ai.ts:1239-1266`), añadido en `before_agent_start` (`GSX:gentle-ai.ts:9751-9757`; `GSD:282`) | yes: el hook no tiene condición de modo (`GSX:gentle-ai.ts:9751-9757`) | n/a: se ejecuta dentro de gentle-shell | Inference: no hace falta | none | TBD |
| **O2** Fase de ODD | Se infiere de la actividad de las herramientas (`GSX:gentle-shell.ts:2375-2387`) y la refina la herramienta de modelo `gentle_odd_phase` con `authorizing`, `exploring`, `researching`, `deciding`, `planning`, `implementing`, `checking`, `closing` o `clear` (`GSX:gentle-ai.ts:9329-9383`; `GSL:odd-phase.ts:16-25`) | partial: G2. Los informes explícitos llegan como `tool_execution_*`; las fases inferidas se quedan en el editor de la TUI. `Inference:` la inferencia también se ejecuta bajo el host RPC interactivo (condición `isInteractiveMode`, `GSX:gentle-shell.ts:2383`), pero nada la publica | missing: Q32; los eventos de herramientas no se renderizan (C17) | Indicador de pasos de ODD (maqueta). `Inference:` los cinco pasos de la maqueta (Explore→Plan→Build→Verify→Deliver) necesitan una correspondencia con estas ocho fases | gentle-shell (G2) | TBD |
| **O3** Documentos de funcionalidad (feature documents) | `odd/tasks/<feature-name>.md` escrito por el modelo y la réplica en Engram `odd/<feature-name>/tasks` (`GSX:gentle-ai.ts:1258`). Ningún código de gentle-shell los lee ni los escribe: `rg 'odd/tasks'` en `extensions/` y `lib/` solo encuentra esa línea del prompt y un comentario | host-side: `Inference:` el escritorio puede leer los archivos del proyecto; el formato no está especificado (G2) | missing: Q32 | Tareas del panel de ODD con evidencia de commits y tests (maqueta) | gentle-shell: un formato estructurado (G2) | TBD |
| **O4** Lista de tareas | Herramienta de modelo `todo` (`write`, `add`, `update`, `clear`, `list`); widget de tarjeta `gentle-todo`; `ctrl+shift+t` lo pliega (`GENTLE_PI_TODO_KEY`); las tareas abiertas se inyectan en cada turno; `stale` en ámbar tras 2 turnos sin tocar; `GENTLE_PI_TODO=0` lo deshabilita (`GSX:gentle-todo.ts:31-32`, `:61-71`, `:168-182`, `:211-219`, `:236-245`; `GSL:shell-todo.ts:86-87`; `GSD:236-254`) | partial: el widget usa una factoría de componentes (tabla de exclusivos de la TUI de `04`). El estado completo viaja en cada resultado de la herramienta `todo` como `details.gentleTodo` (`GSX:gentle-todo.ts:207`) | missing: Q30 | Lista de tareas del panel de ODD (maqueta) | none (Inference: interpretar los resultados de la herramienta) | TBD |

### Revisión y RDD

| Capacidad | En la CLI | Expuesto sobre RPC | Estado en el escritorio | Superficie en el escritorio | Dependencia de upstream | Prioridad |
|---|---|---|---|---|---|---|
| **R1** Activar o desactivar receipt-driven development | `/gentle:review-mode [status\|enable\|disable]` ejecuta el `gentle-ai review mode` nativo con `--scope clone`, así que `enable` no puede sobrescribir una desactivación global (`GSX:gentle-ai.ts:10053-10100`). CLI nativa: `gentle-ai review mode <enable\|disable\|status> [--cwd] [--scope global\|clone] [--expected-revision] [--json]`; activado por defecto (`GAI:internal/cli/review_mode.go:48-77`; la misma línea de uso en `gentle-ai@6dee8f8:internal/cli/review_mode.go:48`). En v4.0.0, como en v3.7.0, un modo sin establecer se resuelve como activado (`GAI:internal/reviewtransaction/rdd_mode.go:698-701`; `GAI:README.md:151`; `gentle-ai@6dee8f8:internal/reviewtransaction/rdd_mode.go:698-701`; `gentle-ai@6dee8f8:README.md:134`). Nuevo en v4.0.0: en un sistema de archivos que no puede conservar modos POSIX privados ("WSL DrvFS without the metadata option, exFAT, and SMB without POSIX extensions"), `review mode` se niega con un error que indica el remontaje o el traslado en lugar de una reparación con `chmod` (`GAI:internal/cli/review_mode.go:276-307`). gentle-shell lo contradice: su README dice "RDD is opt-in" (`GS:README.md:291`) y su código dice "RDD is off by default until explicitly enabled" (`GSX:gentle-ai.ts:5376`), y un comentario de código dice que gentle-ai v2.4.0 "made receipt-driven development opt-in" (`GSL:native-review-cli.ts:866-867`) | partial: se ejecuta a través de `prompt`; el resultado es `notify` | missing: Q29 | `ODD · RDD on` en la barra de estado (maqueta) | none. `Inference:` el escritorio puede leer `gentle-ai review mode status --json` por fuera del canal | TBD |
| **R2** Recordatorio de comprobación previa de la revisión | En `agent_end`, con una mutación propia sin revisar y una transición `review.start`, envía el mensaje personalizado `gentle-pi.review-preflight` como turno de seguimiento (`GSX:gentle-ai.ts:9815-9851`) | yes: condicionado a `ctx.hasUI`, que es true bajo RPC (`GSX:gentle-ai.ts:9823`) | missing: los mensajes que no son del asistente se descartan (`D:main/domain/rpc/chatReducer.ts:81-82`) | Inference: tarjeta de recordatorio | none | TBD |
| **R3** Consentimiento de la revisión | TUI: un panel personalizado; otros modos: `select` con granted, declined o allow for this session (`GSL:review-consent-ui.ts:73-105`). El host solo lo presenta cuando puede capturar una identidad de sesión, lo que requiere `ctx.mode === "tui"` (`GSL:review-session-standing-permission.ts:144-162`; `GSX:gentle-ai.ts:9629-9648`) | partial (`Inference:`, no ejecutado): bajo RPC se omite el consentimiento en el lado del host; el sobre vuelve al modelo, al que se le indica que use `ask_user_choice` o que lo transmita como texto (`GS:assets/orchestrator.md:82`). "Allow for this session" no está disponible | partial: un diálogo `ask_user_choice` se renderizaría como tarjeta (C19) | Inference: tarjeta de consentimiento con beneficios y consecuencias | gentle-shell: identidad de sesión en RPC | TBD |
| **R4** Permiso de revisión de la sesión | `/gentle:review-session-permission [status\|revoke]`; clave de estado `gentle-review-session-permission` (`GSX:gentle-ai.ts:6185`, `:9262-9270`, `:10029-10051`) | no: informa de que requiere la TUI interactiva (`GSX:gentle-ai.ts:10044`) | missing: Q29 | Inference: indicador junto a RDD | gentle-shell | TBD |
| **R5** Herramientas de revisión nativa | Herramientas de modelo `gentle_review`, `gentle_review_capture`, `gentle_review_capture_group`, `gentle_review_scope` (`GSX:gentle-ai.ts:9396`, `:9439`, `:9479`, `:9525`); RECOVER y REPAIR_LEGACY_ALIAS necesitan un `confirm` nuevo y fallan de forma cerrada sin UI (`GSX:gentle-ai.ts:5778-5779`, `:8410-8411`) | yes: eventos de herramientas; los diálogos `confirm` llegan al host | partial: las tarjetas de confirmación funcionan (C19); faltan las tarjetas de herramientas (C17) | Inference: cronología de la revisión en el panel de ODD | none | TBD |

### Perfiles, modelos y persona

| Capacidad | En la CLI | Expuesto sobre RPC | Estado en el escritorio | Superficie en el escritorio | Dependencia de upstream | Prioridad |
|---|---|---|---|---|---|---|
| **P1** Perfiles de agente-modelo | Panel `/gentle:profiles`: `enter` aplicar, `c` crear, `s` instantánea, `d` duplicar, `r` renombrar, `x` borrar, `e` exportar, `i` importar, `p` fijación local, `P` declaración del repositorio; `~/.pi/gentle-ai/profiles.json`, `profiles.export.json`; la clave `orchestrator` escribe `defaultProvider`, `defaultModel`, `defaultThinkingLevel` (`GSX:gentle-ai.ts:9924-9929`, `:4070`; `RR:759-820`) | no: G6. `Inference:` (no ejecutado) el manejador lee `result.type` después de que `ctx.ui.custom()` devuelva `undefined`, y lanza una excepción (`GSX:gentle-ai.ts:4732-4739`). Antes de eso, cuando falta `profiles.json`, escribe un perfil `current` inicial y envía un `notify` (`GSX:gentle-ai.ts:4702-4712`), así que el archivo se crea aunque el panel falle. En el `main` de gentle-shell (`ac67159`), después de la release 4.0.0 (#1349), aplicar un perfil pide primero un `confirm` con el diff del enrutamiento (variantes vacía, solo de orquestador y poblada, `GSX:gentle-ai.ts:4220-4300`); `confirm` llega a un host RPC, pero solo desde dentro del panel, así que allí también es inalcanzable | missing: Q27 | Pantalla Profiles; perfil en la barra de estado (maqueta) | gentle-shell (G6) | TBD |
| **P2** Fijación de perfiles por repositorio | Local `<git-common-dir>/gentle-ai/profile-pin.json` (`p`), del repositorio `<worktree-root>/.pi/gentle-ai/profile.json` (`P`); se muestran como `name (local)` o `name (repo)` (`RR:822-869`) | no: G6 | missing: Q27 | Inference: conmutador de fijación por proyecto | none. `Inference:` ambos archivos tienen una forma JSON documentada que el escritorio podría leer (`RR:835-841`) | TBD |
| **P3** Modelo y esfuerzo por helper | Panel `/gentle:models`: `x` exportar, `r` restaurar, `u` capturar en el perfil actual, `ctrl+s` guardar; `~/.pi/gentle-ai/models.json`, `models.export.json`; escribe `<cwd>/.pi/subagents.json` o `<agent home>/subagents.json`, home del agente como en A11 (`GSX:gentle-ai.ts:2414-2418`, `:260-262`, `:9917-9922`, `:3327`; `RR:709-757`) | no: `Inference:` (no ejecutado) el mismo fallo que P1: `result.type` se lee justo después de `ctx.ui.custom()` (`GSX:gentle-ai.ts:3365-3366`) | missing: Q27 | Inference: tabla de modelo y esfuerzo por helper | gentle-shell | TBD |
| **P4** Persona | `/gentle:persona` (`gentleman` o `neutral`); `~/.pi/gentle-ai/persona.json`, sobrescritura por proyecto `.pi/gentle-ai/persona.json` (`GSX:gentle-ai.ts:9931-9936`, `:4754-4773`; `RR:684-707`) | yes: un `select` y luego `notify` (`04` §gentle-shell additions) | partial: funciona si se escribe (C11) y se responde como tarjeta de diálogo (C19); la confirmación se descarta (C20); Q28 | Inference: selector de persona en los ajustes | none | TBD |

### Seguridad y permisos

| Capacidad | En la CLI | Expuesto sobre RPC | Estado en el escritorio | Superficie en el escritorio | Dependencia de upstream | Prioridad |
|---|---|---|---|---|---|---|
| **Y1** Confirmar comandos de shell arriesgados | Las llamadas a `bash` se clasifican como permitir, confirmar o bloquear; confirmar usa `ctx.ui.confirm`; sin UI el comando se bloquea (`GSX:gentle-ai.ts:1814-1864`). Configuración: `runtime-guardrails.json` global y del proyecto, `GENTLE_PI_AUTONOMOUS_MODE` (`GSX:gentle-ai.ts:1499-1534`) | yes: diálogo `confirm` | done: tarjetas de confirmación (`D:renderer/features/conversation/components/DialogCard.tsx:39-45`) | Tarjeta de confirmación (existe) | none | TBD |
| **Y2** Bloquear rutas sensibles | `read`/`write`/`edit` sobre rutas sensibles se bloquean con un motivo (`GSX:gentle-ai.ts:1564-1694`, `:9871-9875`) | yes: el motivo está en el resultado de la herramienta | missing: los resultados de las herramientas no se renderizan (C17) | Inference: tarjeta de herramienta bloqueada | none | TBD |
| **Y3** Seguridad de los hijos | Los helpers bloquean los comandos destructivos reconocidos (`GSX:child-safety.ts:4-21`) y descartan los bloques de contexto exclusivos del orquestador (`GSX:child-context.ts:9-26`) | n/a: dentro de los helpers | n/a | — | none | TBD |
| **Y4** Permiso YOLO de la sesión | `/gentle:yolo [enable\|disable\|status]`; `/gentle:customize` → Editor; indicador `gentle:yolo` mediante `setStatus` y `setWidget` (`GSL:yolo-session-policy.ts:5-6`, `:105-108`, `:213-240`; `GS:docs/yolo-mode.md:1-30`) | no (`Inference:`, no ejecutado): la activación captura una identidad de sesión que requiere `ctx.mode === "tui"` (`GSL:yolo-session-policy.ts:115-118`, `GSL:review-session-standing-permission.ts:144-162`), así que `enable` informa "activation requires an interactive primary TUI session" (`GSL:yolo-session-policy.ts:171-173`). Esto acota la fila de YOLO de `04`: el indicador puede llegar a un host, pero nunca como activo | missing: Q28 | Inference: conmutador de YOLO con la misma advertencia | gentle-shell: identidad de sesión en RPC | TBD |
| **Y5** Confianza del proyecto | gentle-shell no añade nada: no hay manejador de `project_trust`, ni `--approve`, ni escritura de `defaultProjectTrust` (0 resultados, ver [Evidencia de completitud](#evidencia-de-completitud-1)). Las fijaciones de perfil evitan a propósito los ajustes del proyecto para que pi no pida confianza (`RR:867`) | no: T1 se aplica sin cambios | missing: Q14 | como T1 | como T1 | TBD |
| **Y6** Mantenerse dentro de la raíz del proyecto | Una línea del prompt del orquestador: mantener el trabajo de la sesión dentro de la raíz del proyecto y de los worktrees registrados del mismo clon, y preguntar antes de cualquier lectura o escritura fuera de ella, indicando la ruta absoluta de destino (`GS:assets/orchestrator.md:86`). Añadida en el `main` de gentle-shell (`ac67159`) después de la release 4.0.0, por #1520, solo como un cambio de prompt: el commit `e2d85a4` solo modifica `assets/orchestrator.md`, y ningún código lo impone | yes (`Inference:`): el prompt del orquestador se añade en `before_agent_start`, que no tiene condición de modo (O1) | n/a: una instrucción para el modelo, no una funcionalidad del host | Inference: presentarla como orientación, no como un sandbox impuesto | none. `Inference:` imponerla sería un cambio de gentle-shell | TBD |

### Integraciones, skills, memoria y diagnóstico

| Capacidad | En la CLI | Expuesto sobre RPC | Estado en el escritorio | Superficie en el escritorio | Dependencia de upstream | Prioridad |
|---|---|---|---|---|---|---|
| **I1** Skills empaquetadas | 12 skills: `gentle-ai`, `gentle-ai-branch-pr`, `gentle-ai-chained-pr`, `gentle-ai-cognitive-doc-design`, `gentle-ai-comment-writer`, `gentle-ai-issue-creation`, `gentle-ai-judgment-day`, `gentle-ai-rdd-defect-workflow`, `gentle-ai-skill-creator`, `gentle-ai-skill-improver`, `gentle-ai-skill-registry`, `gentle-ai-work-unit-commits` (`GS:skills/*/SKILL.md`, líneas `name:`) | partial: como E4 | missing: Q13 | Inference: lista de skills en Extensions | none | TBD |
| **I2** Plantilla de prompt | `/skill-creation` (`GS:prompts/skill-creation.md:1-5`) | partial: como E5 | missing: Q12 | Inference: paleta de comandos | none | TBD |
| **I3** Registro de skills | `.atl/skill-registry.md` se actualiza al iniciar la sesión y mediante un observador de archivos. En el `main` de gentle-shell (`ac67159`), después de la release 4.0.0 (#1679), las escrituras automáticas omiten los destinos rastreados por Git y emiten una advertencia (`GSX:skill-registry.ts:365-380`; `RR:663-664`); la regla de ignorado `*` de `.atl/.gitignore`, que deja sin cambios el `.gitignore` raíz, ya existía en el código de 3.7.0 (`gentle-shell@1162ce9:extensions/skill-registry.ts:316-334`) y ahora está documentada (`RR:662`); `/skill-registry:refresh` regenera de forma deliberada, incluso cuando está rastreado; indicador `--no-skill-registry`, `GENTLE_PI_NO_SKILL_REGISTRY=1` (`GSX:skill-registry.ts:27`, `:560-595`, `:625-683`; `RR:615-682`) | partial: la actualización se ejecuta sin interfaz; el comando se ejecuta a través de `prompt` (solo `notify`); el indicador es solo de lanzamiento | missing: Q13 | Inference: acción "Refresh skills" | none | TBD |
| **I4** Memoria | No incluida; el paquete `npm:gentle-engram` lo instala la configuración (L4; `GAI:internal/agents/pi/adapter.go:32`, `:65-70`; `RR:1022-1034`). `/gentle:doctor` informa de si las herramientas de Engram están activas (`GSX:gentle-ai.ts:10006`) | yes: `Inference:` las herramientas de memoria son herramientas de modelo normales | missing: Q33 | Inference: indicador de memoria | none | TBD |
| **I5** Herramienta CodeGraph | Herramienta de modelo `codegraph` (`GSX:codegraph-tools.ts:280-300`, `:323`) | yes: eventos de herramientas | missing: C17 | Inference: tarjeta de herramienta | none | TBD |
| **I6** Proveedor NaN | Proveedor `nan`, URL base `https://api.nan.builders/v1`, clave de API de NaN (`GSX:nan-provider.ts:5`; `GSL:nan-provider.ts:5-6`, `:160-164`) | partial: modelos mediante `get_available_models`; el inicio de sesión es G3 | missing: M7 | Inference: entrada de proveedor en Providers | pi (G3) | TBD |
| **I7** Estado y diagnóstico (doctor) | `/gentle:status`, `/gentle:doctor` (`GSX:gentle-ai.ts:9998-10027`, `:10180-10206`) | partial: se ejecutan a través de `prompt`; la salida es solo `notify` | missing: Q35 | Inference: panel Diagnostics | none | TBD |
| **I8** Sobrescritura del binario de desarrollo de gentle-ai | `/gentle:dev-binary [status\|<absolute path>\|off]`, `GENTLE_PI_GENTLE_AI_DEV_BINARY`, `dev-binary.json` (`GSX:gentle-ai.ts:9973-9996`; `GSL:gentle-ai-binary.ts:58`) | partial: solo `notify` | missing: Q26 | Inference: ajuste para desarrolladores | none | TBD |
| **I9** Telemetría | `/gentle:telemetry [status\|enable\|disable\|preview]` transmite `gentle-ai telemetry <op> --json` (`GSX:gentle-ai.ts:10102-10150`); métricas de runtime y un disparador al iniciar la sesión; exclusiones `DO_NOT_TRACK=1`, `GENTLE_AI_TELEMETRY=0`, `CI=true` (`GSX:runtime-metrics.ts:13-17`; `GSL:telemetry-trigger.ts:63-75`; `RR:1036-1050`) | partial: solo `notify`; las exclusiones por entorno son solo de lanzamiento | missing: Q35 | Inference: ajustes de privacidad (con U8) | none | TBD |
| **I10** Preguntas estructuradas | `ask_user_question` (1–4 preguntas, 2–4 opciones, selección múltiple, descripciones, vistas previas) y `ask_user_choice` (`GSX:ask-user-question.ts:243-268`; `GSX:ask-user-choice.ts:217-231`) | partial: un `select` por pregunta; se pierden las descripciones, las vistas previas y la fila de texto libre "Type something." (`GSX:ask-user-question.ts:133-160`); necesita el host interactivo (`04`) | partial: cada pregunta se renderiza como una tarjeta de diálogo `select` (C19); no se muestran las descripciones, las vistas previas ni la fila de texto libre que se pierden sobre RPC | Tarjetas de pregunta (existen); Inference: mostrar las descripciones de las opciones | gentle-shell: carga de diálogo más rica | TBD |

### gentle-ai fuera de la sesión

Solo lo que toca un usuario de gentle-shell o del escritorio. gentle-ai también configura otros agentes (Claude Code, Codex, OpenCode, Cursor, Gemini y más, `GAI:internal/agents/`); ese soporte queda fuera de alcance aquí.

| Capacidad | En la CLI | Expuesto sobre RPC | Estado en el escritorio | Superficie en el escritorio | Dependencia de upstream | Prioridad |
|---|---|---|---|---|---|---|
| **GA1** Instalar y sincronizar la pila de pi | `gentle-ai install --agent pi --scope global`, `gentle-ai sync` (`GAI:internal/app/app.go:145-154`, `:306`, `:320`). Paquetes gestionados en v4.0.0: `npm:gentle-pi`, `npm:gentle-engram`, `npm:pi-web-access`, `npm:pi-btw` (`GAI:internal/agents/pi/adapter.go:65-70`). `npm:pi-mcp-adapter` está retirado: "Gentle AI therefore never installs the adapter and removes it wherever it finds it" (`GAI:internal/agents/pi/adapter.go:22-29`); la desinstalación también lo elimina (`:78-83`). El adaptador apunta a `APPEND_SYSTEM.md` (archivo del prompt de sistema) y a `mcp.json` en el directorio de agente de pi (`:33-34`, `:310-327`). `ProvisionEngramMCP`, ejecutado por el componente Engram al instalar y al sincronizar, elimina el adaptador de `settings.json` y de `<agentDir>/npm/package.json`, y fusiona los servidores de un `mcp-adapter.json` antiguo (legacy) en `mcp.json`, creando `mcp.json` solo cuando hay un servidor que migrar; nunca añade un servidor de Engram (`:435-470`, `:523-529`; `GAI:internal/components/engram/inject.go:693-694`). `InstallCommand` sigue ejecutando `pi-engram init` (`:285-297`). En v3.7.0, que instalaba gentle-shell 3.7.0, la lista todavía incluía `pi-mcp-adapter` y el adaptador indicaba que no escribía `mcp.json` (`gentle-ai@6dee8f8:internal/agents/pi/adapter.go:57-63`, `:398-399`) | no | missing: Q38 | Inference: mediante L4 | none | TBD |
| **GA2** Fachada de revisión | `gentle-ai review <acknowledge-approved\|capture-result\|…\|assess\|start\|validate\|status\|…>` (`GAI:internal/cli/review_facade.go:598`); la usa R5 | no: solo se llega a ella a través de las herramientas de gentle-shell | missing: Q29 | Inference: `review status` / `assess` de solo lectura para la barra de estado | none | TBD |
| **GA3** CLI de telemetría | `gentle-ai telemetry <status\|policy\|enable\|disable\|preview\|trigger\|runtime> [--json]` (`GAI:internal/cli/telemetry.go:62-80`) | no | missing: Q35 | Inference: ajustes de privacidad | none | TBD |
| **GA4** CLI del registro de skills y de CodeGraph | `gentle-ai skill-registry <refresh\|list>`, `gentle-ai codegraph` (`GAI:internal/app/app.go:120-123`, `:375-382`) | no | missing: Q13 | Inference: cubierto por I3, I5 | none | TBD |
| **GA5** Versión, actualización, desinstalación, restauración, diagnóstico | `gentle-ai version`, `update`, `upgrade`, `uninstall`, `restore`, `doctor` (`GAI:internal/app/app.go:104-106`, `:114`, `:155`, `:302-304`, `:331-333`) | no | missing: Q35 | Inference: panel Diagnostics | none | TBD |

### Filas del núcleo de pi que gentle-shell cambia

| Fila de pi | Qué cambia gentle-shell | Evidencia |
|---|---|---|
| C3, C4, C14 | Esc envía los mensajes encolados tras un aborto; doble Esc de activación voluntaria; modo Vim; historial de prompts (V12, V13, V14). | `GSX:gentle-shell.ts:2390-2417`; `RR:935-997` |
| C17 | 6 herramientas integradas se vuelven a registrar con renderizadores de tarjeta (`bash` sigue siendo la herramienta nativa de pi desde 4.0.0); `codemode` recibe una tarjeta compacta (V15). | `GSX:quiet-tools.ts:25-39`, `:812-814`; `GSL:codemode-renderer.ts:180` |
| K3, K4 | El pie de pi se sustituye por la cabecera y la barra del shell (V2). | `GSX:gentle-shell.ts:1789` |
| E2, E9 | El lanzador deshabilita el `codemode` integrado de pi en los homes que le pertenecen (L6). | `GS:bin/gentle-shell.mjs:1279-1292` |
| E6, U1 | Se incluyen 3 temas; los homes aislados nuevos usan por defecto `Gentleman-Cute` y pantalla completa (V10, L6). `Inference:` la pantalla completa también es el valor por defecto propio de pi desde 1.0.0 (U1), así que la escritura de `tuiMode` solo importa en pi 0.99.x. | `GS:package.json:64-66`; `RR:350` |
| E1 | Los comandos de paquetes se ejecutan contra el home resuelto (L7). | `GSL:gentle-shell-launcher.ts:12` |
| M9 | Añade el proveedor `nan` (I6). | `GSX:nan-provider.ts:5` |
| E8 | La configuración de gentle-shell 4.0.0 instala gentle-ai v4.0.0, que nunca instala `npm:pi-mcp-adapter` y lo elimina de `settings.json` y de `<agentDir>/npm/package.json` cuando se ejecuta su paso de Engram (L4, GA1). pi documenta que una extensión instalada que registra `/mcp`, con `pi-mcp-adapter` como ejemplo, sustituye el soporte MCP integrado. `Inference:` el comportamiento del `/mcp` integrado de E8 se aplica en un home aprovisionado en 4.0.0. En 3.7.0, la configuración instalaba gentle-ai v3.7.0, cuyos paquetes gestionados incluían el adaptador, y la limpieza posterior a la configuración de gentle-shell (sin cambios en 4.0.0) solo elimina `@juicesharp/rpiv-ask-user-question` y `gentle-pi`, así que esos homes lo conservaron. `UNVERIFIED:` si un home así pierde el adaptador en su resincronización con 4.0.0 (ver [Preguntas abiertas](#preguntas-abiertas)), y si `pi-mcp-adapter` registra `/mcp` (no está instalado en ningún checkout de referencia). | `GAI:internal/agents/pi/adapter.go:22-29`, `:65-70`, `:435-470`; `gentle-ai@6dee8f8:internal/agents/pi/adapter.go:57-63`, `:440`; `GSL:gentle-shell-launcher.ts:562-565`; `PIDOC:mcp.md:242`; `PISRC:extensions/index.ts:9-13` |
| U4 | La cabecera de arranque se sustituye por el banner (V11). | `GSX:startup-banner.ts:750` |
| T1 | Sin cambios (Y5). | — |

### Cobertura de extensiones

| Punto de entrada de extensión | Filas |
|---|---|
| `ask-user-choice.ts`, `ask-user-question.ts` | I10 |
| `child-context.ts`, `child-safety.ts` | Y3 |
| `codegraph-tools.ts` | I5 |
| `gentle-agents.ts` | A1–A7, A9, A10, A12; parte de A8 y A11 (lee la política de segundo plano y carga las definiciones de helpers, mientras que sus comandos se registran en `gentle-ai.ts`, `GSX:gentle-ai.ts:10152`, `:9902-9915`) |
| `gentle-ai.ts` | O1, O2, R1–R5, P1, P3, P4, Y1, Y2, A8, A11, I4, I7, I8, I9 |
| `gentle-shell.ts` | V1–V9, V12–V14, V17, O2, V6 |
| `gentle-stats.ts` | V19 |
| `gentle-todo.ts` | O4 |
| `history/index.ts` | V14 |
| `nan-provider.ts` | I6 |
| `pi-pretty.ts` | V15 |
| `quiet-tools.ts` | V15 |
| `resume-hint.ts` | L10 |
| `runtime-metrics.ts` | I9 |
| `skill-registry.ts` | I3 |
| `startup-banner.ts` | V11 |
| `lib/yolo-session-policy.ts` (registrado desde `gentle-ai.ts:8925`) | Y4 |

### Cobertura de comandos y atajos

| Comando o atajo | Tecla por defecto / sobrescritura por entorno | Fila |
|---|---|---|
| `/gentle:agents` | `alt+a` (`GENTLE_PI_AGENTS_VIEW_KEY`) | A3 |
| (detener helpers) | `alt+s` (`GENTLE_PI_AGENTS_STOP_KEY`) | A4 |
| (plegar la tarjeta de agentes) | `ctrl+shift+a` (`GENTLE_PI_AGENTS_KEY`) | A2 |
| `/gentle:usage` | `alt+u` (`GENTLE_PI_SHELL_USAGE_KEY`) | V4 |
| `/gentle:changes` | `alt+g` (`GENTLE_PI_SHELL_CHANGES_KEY`) | V5 |
| `/gentle:commands` | `alt+k` (`GENTLE_PI_COMMANDS_KEY`) | V7 |
| (plegar la tarjeta de tareas) | `ctrl+shift+t` (`GENTLE_PI_TODO_KEY`) | O4 |
| `/history` | `ctrl+shift+r` (fijo) | V14 |
| `/gentle:customize` | — | V8 |
| `/gentle:animations` | — | V9 |
| `/gentle:vim` | — | V12 |
| `/gentle:double-esc-cancel` | — | V13 |
| `/gentle:banner`, `/gentle:toggle-rose`, `/gentle:toggle-text-logo`, `/gentle:banner-color` | — | V11 |
| `/gentle:background-subagents` | — | A8 |
| `/gentle:install-delegation`, `/gentle:install-review` | — | A11 |
| `/gentle:review-mode` | — | R1 |
| `/gentle:review-session-permission` | — | R4 |
| `/gentle:profiles` | — | P1, P2 |
| `/gentle:models` | — | P3 |
| `/gentle:persona` | — | P4 |
| `/gentle:yolo` | — | Y4 |
| `/skill-registry:refresh` | — | I3 |
| `/gentle:status`, `/gentle:doctor` | — | I7 |
| `/gentle:dev-binary` | — | I8 |
| `/gentle:telemetry` | — | I9 |
| `/gentle:stats` | ninguna por defecto; definir `GENTLE_PI_STATS_VIEW_KEY` | V19 |

28 nombres de comando y 9 atajos, uno de ellos (`/gentle:stats`) registrado solo cuando `GENTLE_PI_STATS_VIEW_KEY` está definido (`GSX:gentle-stats.ts:22-26`, `:90-96`). Las teclas son los valores por defecto; `off` o un valor vacío deshabilita cada tecla que admite sobrescritura (`GSL:agents-keys.ts:11-27`; `GSX:gentle-shell.ts:1219-1229`; `GSL:command-palette.ts:353-357`; `GSX:gentle-todo.ts:67-71`). Los atajos son asignaciones de teclas de la terminal, así que ninguno llega a un host RPC; el escritorio necesita los suyos propios.

### Cobertura de herramientas

| Herramientas | Fila |
|---|---|
| `subagent_list_agents`, `subagent_run`, `subagent_status`, `subagent_result`, `subagent_list_tasks`, `subagent_continue` | A1 |
| `subagent_cancel` | A4 |
| `subagent_reply`, `subagent_parent_message` | A5 |
| `subagent_send_message` | A6 |
| `orchestrator_session_id`, `orchestrator_list`, `orchestrator_send_message` | A9 |
| `gentle_odd_phase` | O2 |
| `todo` | O4 |
| `gentle_review`, `gentle_review_capture`, `gentle_review_capture_group`, `gentle_review_scope` | R5 |
| `session_worktree_register` | V6 |
| `ask_user_question`, `ask_user_choice` | I10 |
| `codegraph` | I5 |
| Registradas de nuevo: `read`, `grep`, `find`, `ls`, `edit`, `write`; envuelta: `codemode` (`bash` es la herramienta nativa de pi desde 4.0.0) | V15 |

### Ajustes de los que es responsable gentle-shell

Todos viven bajo el home de configuración `GENTLE_PI_CONFIG_HOME`, por defecto `~/.pi/gentle-ai` (`GSL:agent-home.ts:14-16`). El lanzador define `PI_CODING_AGENT_DIR`, `GENTLE_PI_AGENT_HOME` y, desde 4.0.0, `GENTLE_SHELL_USER_PI_HOME` para el hijo, pero no `GENTLE_PI_CONFIG_HOME` (`GSL:gentle-shell-launcher.ts:958-963`). `Inference:` estos ajustes se comparten entre las sesiones `--link`, `--isolated` y `--home`, a diferencia de los propios ajustes de pi.

| Archivo (bajo el home de configuración salvo que se indique) | Lo establece | Fila |
|---|---|---|
| `persona.json`; del proyecto `.pi/gentle-ai/persona.json` | `/gentle:persona` | P4 |
| `models.json`, `models.export.json` | `/gentle:models` | P3 |
| `profiles.json`, `profiles.export.json`; `<git-common-dir>/gentle-ai/profile-pin.json`; `<worktree>/.pi/gentle-ai/profile.json` | `/gentle:profiles` | P1, P2 |
| `background-subagents.json`; del proyecto `.pi/gentle-ai/background-subagents.json` | `/gentle:background-subagents` | A8 |
| `double-esc-cancel.json` | `/gentle:double-esc-cancel` | V13 |
| `animations.json` | `/gentle:animations` | V9 |
| `vim.json` | `/gentle:vim` | V12 |
| `banner.json` | `/gentle:banner` y los conmutadores | V11 |
| `card-style.json`, `visual-customization.json`, `visual-profiles.json` | `/gentle:customize` | V8 |
| `history-capture.json` | `/gentle:customize` → History | V14 |
| `runtime-guardrails.json`; del proyecto `.pi/gentle-ai/runtime-guardrails.json` | solo archivo | Y1 |
| `dev-binary.json` | `/gentle:dev-binary` | I8 |
| `~/.gentle-shell/config.json` (`home`, `provisioned`) | `gentle-shell home`, L5 | L2, L5 |

### Preguntas abiertas

- `UNVERIFIED:` si `/gentle:profiles` y `/gentle:models` lanzan realmente una excepción bajo RPC. El camino de código está leído, no ejecutado (P1, P3).
- `UNVERIFIED:` qué registra `@heyhuynhgiabuu/pi-pretty` 0.6.27 (V15).
- `UNVERIFIED:` cuánto tarda en la práctica un aprovisionamiento en el primer arranque (L5).
- `UNVERIFIED:` si el `gentle-ai install --agent pi --scope global` de `gentle-shell setup` (sin indicadores de componentes, `GS:bin/gentle-shell.mjs:821`) selecciona el componente Engram de gentle-ai, el único llamador de `ProvisionEngramMCP` (`GAI:internal/components/engram/inject.go:693-694`). Esto decide si un home aprovisionado por 3.7.0 pierde `pi-mcp-adapter` al resincronizar (fila E8 en [filas del núcleo de pi que gentle-shell cambia](#filas-del-núcleo-de-pi-que-gentle-shell-cambia)).
