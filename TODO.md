# TODO

## Thin-Client / BED Conversion Plan

Convert empyre from a host-driven TUI module into a thin WebSocket client
that runs against bbsengine6's BED daemon. Server runs
`empyre-bed --router empyre.api.handler.MessageRouter`; client connects
with `--bed-host` / `--bed-port` and drives the game through a JSON
request/reply protocol.

### Defaults & decisions (locked in)

- [ ] Add `--thick` flag to `empyre.lib.buildargs`; default `--thick` until Phase 5 is complete, then flip default to `--thin`.
- [ ] Listbox: full port required.
- [ ] Editor: stub for v1 (single string in/out, no multi-frame interaction).
- [ ] Keep both menu-driven thin flow and existing service handlers (Island/Ship/Town/Market/Bank/Channel/Chat) as a non-menu API for bots/tooling on the same BED instance.
- [ ] SSO via bbsengine6 `MemberService`; keep local `AuthService` (moniker+password via `empyre.player.loadplayer` + `checkpassword`) as fallback for legacy empyre-only accounts.
- [ ] Pure JSON wire format for all IO types (no SETBOTTOMBAR binary packet).
- [ ] Server-side cursor tracking for listbox (v1); client-side cursor is a future opt-in.
- [ ] Reconnect via short-lived bearer token issued at `auth` time; no password resend on reconnect.

### Phase 0 — Spec & wire format

- [ ] Write `empyre/BED_PROTOCOL.md` defining every message `type`, request/reply pair, error envelope `{type:"error", code, message}`, listbox frame protocol, cancellation/timeout rules, and the connection section (clients connect to `--bed-host:--bed-port` per `--bed-path`).
- [ ] Add `MessageKind` registry in `empyre.api.handler` mirroring the constants pattern used in `bbsengine6.services`.
- [ ] Extend `databasebuildargs` and `empyre.lib.buildargs` with `--thick/--thin`, `--bed-router`, `--bed-port`. (Client flags `--bed-host`, `--bed-port`, `--bed-path`, `--uri` go in `empyre/client/__main__.py`.)

### Phase 1 — IO shim (`empyre/io_bridge.py`)

- [ ] Re-export every name empyre uses: `echo`, `inputchoice`, `inputstring`, `inputboolean`, `inputinteger`, `inputchar`, `inputdate`, `inputfilename`, `inputpassword`, `screen.setbottombar`, `screen.register_bottombar_fragment`, `screen.unregister_bottombar_fragment`, `listbox.*`, `readfile.display`.
- [ ] Implement **thick mode** as passthrough to `bbsengine6.io.*` (zero regression).
- [ ] Implement **thin mode** that returns a request envelope to the active `MessageRouter` and `await`s the matching `*_reply`.
- [ ] Select shim at `empyre.lib.init(args, thin=...)` time via `sys.modules` swap of `bbsengine6.io`.
- [ ] Cover `echo` end-to-end as the first vertical slice: server emits `echo`, client renders, client sends `echo_ack`.

### Phase 2 — Router rework (`empyre/api/handler.py`)

- [ ] Replace `SessionManager` with `ThinSession` holding `moniker`, `player_moniker`, `pending_request: Dict[request_id, asyncio.Future]`, `render_buffer`, `bottombar_fragments` mirror.
- [ ] Add `IOServiceHandler` that validates `*_reply` types, looks up the future by `request_id`, and resolves it. Owns no game state.
- [ ] Add `GameServiceHandler` (per-session state machine): on `auth` hydrate `ThinSession`, run `empyre.startup.main`, drive `empyre.main.main`'s flow using the IO shim.
- [ ] Add `BedEmpyreRunner` coroutine owning one `ThinSession` per WebSocket (keyed by `id(websocket)`).
- [ ] Rewire `AuthService` to delegate to `bbsengine6.services.member.MemberService` for SSO; keep local `empyre.player.loadplayer` + `checkpassword` fallback.
- [ ] Keep `IslandServiceHandler`, `ShipServiceHandler`, `TownServiceHandler`, `MarketServiceHandler`, `BankServiceHandler`, `ChannelServiceHandler`, `ChatServiceHandler` as the non-menu API for bots/tooling; same `MessageRouter`.

### Phase 3 — Listbox protocol

- [ ] `listbox_open` request: `request_id`, `title`, `items` (or streaming), `columns`, `mode`, `allow_insert`, `allow_edit`, `page_size`, `hotkeys` map.
- [ ] `listbox_append` / `listbox_close` streaming for large result sets.
- [ ] `listbox_reply`: `choice`, `action` (`select`/`insert`/`edit`/`page`/...), `page`, `cancelled`.
- [ ] `readfile.display` reuses streaming pattern: `readfile_open` (path, total_bytes) → `readfile_chunk` (n) → `readfile_close` after last `readfile_reply` carrying `{action, page}`.
- [ ] Server-side cursor tracking (v1 default).

### Phase 4 — Editor stub (v1 only)

- [ ] Single `editor_open` / `editor_reply` round-trip carrying the full text buffer; max_lines cap; cancel supported.
- [ ] No multi-frame interaction, no per-keystroke redraw, no visual mode. Revisit before flipping default to `--thin`.
- [ ] Mark `empyre.instructions` (uses `util.filedisplay`) and any other editor calls as v1 stub.

### Phase 5 — Client implementations

- [ ] `empyre/client/tui.py`: async TUI client. Connect, authenticate, loop on incoming frames, render, read input, send replies. Reuse `bbsengine6.io.getch` semantics with idle-loop notify check via a side task.
- [ ] `empyre/client/headless.py`: scripted client for tests/CI; reads replies from a YAML/JSON script, asserts server render payloads.
- [ ] `empyre/client/__main__.py`: flags `--uri`, `--bed-host`, `--bed-port`, `--bed-path`, `--moniker`, `--password` (or `--password-file`/`--password-env`), `--script`, `--tls/--insecure`, `--reconnect`.

### Phase 6 — Server entry point

- [ ] `empyre-bed` console script in `pyproject.toml`:
      `empyre-bed = "empyre.bed:main"` wrapping `bbsengine6.bed.main` with `--router` defaulted to `empyre.api.handler.MessageRouter`.
- [ ] `python -m empyre` keeps current door-mode behavior when `--thick` (default) is set.

### Phase 7 — Per-module migration (incremental)

Run existing pytest + new thin-mode tests after each step.

- [ ] **echo** — buffer + flush, optional `echo_ack`.
- [ ] **inputstring** — one round-trip per call.
- [ ] **inputboolean** — single keystroke.
- [ ] **inputchoice** — single keystroke + hotkey map.
- [ ] **inputinteger**, **inputchar**, **inputdate**, **inputfilename**, **inputpassword**.
- [ ] **listbox** — `Player.select`, ship select, news listbox, member list.
- [ ] **screen.setbottombar / register_bottombar_fragment** — push-based; mirror the three fragments empyre registers in `lib.init` to the client at `auth` time, re-push on every `register_*` call.
- [ ] **readfile** — streaming listbox-like protocol.

### Phase 8 — Testing & docs

- [ ] `tests/test_thin_io_bridge.py` — shim is a no-op passthrough in `--thick`; emits correct envelopes in `--thin`.
- [ ] `tests/test_bed_empyre_flow.py` — start BED in-process with `empyre.api.handler.MessageRouter`, connect a `headless` client, walk `auth → list players → new player → market → town → combat menu (peek) → quit`.
- [ ] `tests/test_listbox_protocol.py` — listbox_open + listbox_append streaming, cursor moves, page changes, KEY_INSERT, KEY_EDIT, cancel.
- [ ] `tests/test_bed_idempotent_reconnect.py` — disconnect mid-turn, reconnect with bearer token, verify state machine resumes (`engine.__session` row + `ThinSession` rehydration).
- [ ] `tests/test_sso_auth.py` — `auth` via `MemberService` succeeds for known member; legacy fallback works for empyre-only account.
- [ ] Update `empyre.spec` with a "Thin-Client / BED Mode" section.
- [ ] Add `empyre/BED_PROTOCOL.md` (in Phase 0).
- [ ] Add `bbsengine6/handbook/specs/BED_EMPYRE.md`.

### Final command surface (target)

```
# Legacy door (default until Phase 5)
python -m empyre

# Local thin session (tests, dev, single-player)
python -m empyre --thin

# BED server hosting empyre
empyre-bed --host 0.0.0.0 --port 8765

# Connect a TUI client
empyre-client --bed-host bbs.example.com --bed-port 8765 --moniker alice

# Scripted tests
empyre-client --bed-host 127.0.0.1 --bed-port 8765 \
              --script scenarios/new_player.yaml
```

## Legacy items

- [ ] Make sure all trades route through the bank
- [x] Check quests to make sure they route through the bank
- [x] Check all empyre modules for direct manipulation of player.coins or member.coins
- [x] Add integrated tests for bank routing via BED (127.0.0.1:8765)
