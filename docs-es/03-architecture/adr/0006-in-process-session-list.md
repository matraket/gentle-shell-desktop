> Traducción al español de `docs/03-architecture/adr/0006-in-process-session-list.md` (commit `d27baba`). Documento de lectura; la versión de referencia es la inglesa.

# 0006. Listar los chats en el mismo proceso con `SessionManager.listAll()` de pi

> Estado: borrador (draft).

## Contexto

`SessionManager.listAll()` de `@earendil-works/pi-coding-agent` devuelve id, cwd, nombre, fecha de creación, fecha de modificación, número de mensajes y primer mensaje (`odd/tasks/desktop-m1-chat-core.md:16`).

## Decisión

T3 lista las sesiones "with `SessionManager.listAll()` under the resolved home" y las expone como `sessions.list` (`odd/tasks/desktop-m1-chat-core.md:39`).

## Consecuencias

- **Un segundo camino hacia pi.** El escritorio tiene un segundo camino de datos hacia pi además de RPC, con su propia versión de pi: 0.85.1 bloqueada (`package.json:42`; `pnpm-lock.yaml:323`), frente a como mínimo 0.99.1 sobre RPC.
- **Una variable global del proceso.** `listAll()` lee el directorio de agente de `PI_CODING_AGENT_DIR`, así que el adaptador establece esa variable global del proceso en torno a cada llamada. Su comentario lo registra como "a real, accepted M1 limitation" (`src/main/adapters/piSessionStore.ts:18-25`).
- Ver [audit A1](../audit.md#a1-dos-caminos-de-datos-hacia-pi-y-una-mutación-global-de-pi_coding_agent_dir) y [audit A2](../audit.md#a2-desfase-de-versión-de-pi-entre-los-dos-caminos).

## Estado

aceptada (accepted), registrada en `odd/tasks/desktop-m1-chat-core.md:39`
