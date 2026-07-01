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
- [ ] Adopt the corrected `menu` envelope: 1:1 projection of `bbsengine6.io.inputchoice()`'s positional and unconditional kwargs (`prompt`, `options`, `default`, `noneok`, `rewriteprompt`, `timeout`). The `help` kwarg is stashed server-side and served via the `help` / `help_result` / `help_error` round-trip (F1, per-menu, on demand). The `f2_handler` kwarg is dropped (not used in this monorepo; F2 is session-level via `key_f2`).

### Phase 0a — `bed` bearer token (cross-project prerequisite)

- [ ] Wait on `bed/TODO.md` "Bearer token" implementation: `bed.api.auth.AuthService`, `bed.api.token_store.TokenStore`, `bed.api.credential_provider` protocol, the `reconnect` / `auth_refresh` / `auth_revoke` message types, and the `--bed-secret` / `--token-ttl` / `--token-persistence` flags.
- [ ] When `bed`'s `AuthService` lands, empyre adopts it instead of rolling its own `AuthService`. The empyre `AuthService` in `empyre/api/handler.py` is reduced to a thin `credential_provider` that calls `empyre.player.loadplayer` + `checkpassword` (legacy empyre accounts) or delegates to `bbsengine6.services.member.MemberService` (SSO).
- [ ] Empyre's `empyre/BED_PROTOCOL.md` documents token lifetimes, refresh, revocation, and the `reconnect` message type, but does not redefine the wire format — `bed`'s protocol doc is the source of truth.

### Phase 0b — `bbsengine6.io` sink + `MessageRouterMixin` adoption (cross-project prerequisite)

- [ ] Wait on `bbsengine6/TODO.md` "`bbsengine6.io` sink
  infrastructure for thin-client BED conversion" Phases 0–5:
  `bbsengine6.io.sink.Sink` protocol, `set_io_sink` / `reset_io_sink`
  contextvar API, `bbsengine6.io.echo_render` public function,
  `bbsengine6.io.mci.parse` / `mci.render`, `echo()` returns
  `str`, and the `MessageRouter` / `MessageRouterMixin` in
  `bbsengine6/net/router.py`.
- [ ] When the sink infrastructure lands, empyre's
  `empyre.api.handler.MessageRouter` adopts `MessageRouterMixin` (a
  one-line change to its class declaration:
  `class MessageRouter(MessageRouterMixin):`). This gives the
  empyre per-game router the `get_session` / `get_pending_request` /
  `resolve_pending_request` / `cleanup_session` / `next_request_id`
  API without changing the existing class hierarchy.
- [ ] The empyre `MessageRouter` is then ready to be the
  incoming-dispatch side of the BED wire format. The
  `BEDSink` (defined in `bed/TODO.md` "BED `Sink` integration with
  `bbsengine6.io`") is the outgoing-send side; it references the
  empyre `MessageRouter` for session access.
- [ ] **Backward compat**: door mode (no `BEDSink` installed) uses
  the default `DefaultSink` behavior, which is the current
  `bbsengine6.io` behavior byte-for-byte. The
  `bbsengine6/tests/test_io_backward_compat.py` suite passes for the
  empyre door-mode pytest corpus.

### Phase 0 — Spec & wire format

- [ ] Write `empyre/BED_PROTOCOL.md` defining every message `type`, request/reply pair, error envelope `{type:"error", code, message}`, listbox frame protocol, cancellation/timeout rules, and the connection section (clients connect to `--bed-host:--bed-port` per `--bed-path`). Reference `bed/TODO.md` for the auth/bearer-token messages and the `menu` / `help` / `key_f2` message types.
- [ ] Add `MessageKind` registry in `empyre.api.handler` mirroring the constants pattern used in `bbsengine6.services`. Include the `help` / `help_result` / `help_error` (F1, per-menu) and `key_f2` / `key_f2_result` / `key_f2_empty` / `key_f2_error` (F2, session-level) types as cross-project primitives owned by `bed`.
- [ ] Extend `databasebuildargs` and `empyre.lib.buildargs` with `--thick/--thin`, `--bed-router`, `--bed-port`. (Client flags `--bed-host`, `--bed-port`, `--bed-path`, `--uri` go in `empyre/client/__main__.py`.)
- [ ] When `empyre/client/__main__.py` lands (Phase 5), register `--bed-host` (default `localhost`), `--bed-port` (default `8765`), `--bed-path` (default `/`), `--uri`, `--moniker`, `--password` (plus `--password-file` / `--password-env`), `--script`, `--tls` / `--insecure`, `--reconnect`. Defaults match bed's own `bedping` defaults so a local `bed` daemon is reachable with no extra args.

### Phase 1 — IO shim (`empyre/io_bridge.py`)

- [ ] Re-export every name empyre uses: `echo`, `inputchoice`, `inputstring`, `inputboolean`, `inputinteger`, `inputchar`, `inputdate`, `inputfilename`, `inputpassword`, `screen.setbottombar`, `screen.register_bottombar_fragment`, `screen.unregister_bottombar_fragment`, `listbox.*`, `readfile.display`.
- [ ] Implement **thick mode** as passthrough to `bbsengine6.io.*` (zero regression).
- [ ] Implement **thin mode** that returns a request envelope to the active `MessageRouter` and `await`s the matching `*_reply`.
- [ ] Select shim at `empyre.lib.init(args, thin=...)` time via `sys.modules` swap of `bbsengine6.io`.
- [ ] Cover `echo` end-to-end as the first vertical slice: server emits `echo`, client renders, client sends `echo_ack`. Detail below in "Phase 1a — echo / echo_ack vertical slice".

### Phase 1a — `echo` / `echo_ack` vertical slice

This is the **first** piece of the thin-client BED conversion to land, ahead
of `inputstring`, `inputboolean`, `inputchoice`, etc. Reason: `echo` is
fire-and-forget at the game level (no reply needed to advance the menu) and
covers the entire transport + shim + client pipeline without requiring
keyboard handling on the client side.

The full protocol envelope is defined in `bed/TODO.md` under "`echo` and
`echo_ack` — generic push-based text channel". Empyre consumes that
envelope; the items below are the empyre-specific pieces.

#### Shim behaviour (`empyre/io_bridge.py`)
- [ ] `echo(text, **style_kwargs)` in **thin mode** MUST:
  1. Build an `EchoFragment` (`request_id`, `stream="main"`, `seq=<next>`,
     `payload={text, style, mci}`, `flush=False`, `ts=<iso8601>`).
  2. Push it onto the active `ThinSession.render_buffer` and assign the
     session's monotonic `seq` counter.
  3. Append to a per-session listbox-friendly ring of fragments (so the
     last N fragments can be re-sent on reconnect-resume).
  4. Return synchronously — `echo` does **not** block on `echo_ack` in v1
     (the IO requests that follow it will block; see "backpressure" below).
- [ ] `echo(..., flush=True)` MUST set `flush=True` on the final fragment
  of the current menu/prompt group; this is the signal to the client that
  an IO request is imminent. The shim records a "pending flush" cursor.
- [ ] `echo(text, mci=...)` in **thick mode** MUST pass through to
  `bbsengine6.io.echo` unchanged — including all `{f6}` / `{labelcolor}` /
  `{var:valuecolor}` tokens. Verified by the existing door-mode pytest
  suite.
- [ ] The shim MUST cache the active `ThinSession` (or `None` for thick
  mode) at `empyre.lib.init` time, so module code that calls
  `bbsengine6.io.echo(...)` indirectly (via the swapped `sys.modules`
  module) reaches the shim without a context-var lookup on every call.

#### Bottom-bar echo (out of scope for v1, noted for follow-up)
- [ ] `screen.setbottombar` / `screen.register_bottombar_fragment` /
  `screen.unregister_bottombar_fragment` will eventually push `echo` frames
  on `stream="bottombar"`. v1 of Phase 1a only handles `stream="main"`.
  Tracked as a follow-up to Phase 7. The bottombar-architecture work
  (`bbsengine6.bottombar.registry_for(name)`, per-connection
  `ContextVar`, back-compat shim deprecation) is in
  `../bbsengine6/TODO-BOTTOMBAR.md` Phase 4a.

#### Backpressure — `flush` semantics
- [ ] The shim MUST NOT send the next IO request (`inputstring`,
  `inputchoice`, etc.) until the in-flight `flush=True` echo's
  `echo_ack` arrives, **or** a configurable server-side timeout
  (`--echo-ack-timeout`, default 30s, inherited from `bed`) elapses.
- [ ] On `ack_timeout`, the shim logs a `logentry` warning with
  `moniker`, `request_id`, `last_seq`, and proceeds with the IO request
  anyway (the client is presumed stuck or disconnected; a future
  disconnect handler will tear down the session).
- [ ] On `echo_nack` (client cannot render — e.g. unknown MCI code), the
  shim logs a `logentry` warning with `reason` + `detail`, increments a
  per-session `nack_count`, and proceeds. If `nack_count > 5` in a single
  session, the shim raises `EchoBudgetExceeded` and the router closes the
  session with `error{code:"echo_budget_exceeded"}`.

#### Style / MCI transcoding (v1 default)
- [ ] In **thick mode** the shim passes through `bbsengine6.io.echo`'s
  exact behaviour (verified by the existing door tests).
- [ ] In **thin mode** the shim accepts both `echo("text", fg="white")`
  keyword arguments (mapped to `payload.style`) and
  `echo("text {f6}rest")` inline MCI tokens (mapped to `payload.mci`).
- [ ] v1 default: the thin client renders `payload.text` only; the
  structured `style` and `mci` fields are kept on the wire for the future
  TUI client to consume, but the headless test client asserts the raw
  `text` field. No transcoding happens server-side in v1.

#### Tests
- [ ] `tests/test_echo_thick_passthrough.py` — in `--thick` mode,
  `io_bridge.echo("hello {f6}world")` produces exactly the same ANSI
  output as the current door-mode `bbsengine6.io.echo`. Asserts byte-for-
  byte equality against a snapshot of the legacy output for a fixed set
  of inputs.
- [ ] `tests/test_echo_thin_envelope.py` — in `--thin` mode, the shim
  builds the correct `EchoFragment` (matches the wire shape in
  `bed/TODO.md`), increments `seq` monotonically, attaches the active
  `ThinSession`'s monotonic `request_id`, and does **not** call any
  blocking I/O.
- [ ] `tests/test_echo_thin_flush.py` — when `flush=True` is passed, the
  shim records a "pending flush" cursor; the next IO call blocks until
  `echo_ack{request_id, last_seq=…}` arrives; an `echo_nack` is logged
  and the IO call still proceeds; an `ack_timeout` logs a warning and
  still proceeds.
- [ ] `tests/test_echo_thin_concurrent_streams.py` — `stream="main"` and
  `stream="bottombar"` (when added later) advance independently.
- [ ] `tests/test_echo_thin_nack_budget.py` — after 5 `echo_nack`s in
  one session, the shim raises `EchoBudgetExceeded` and the router
  sends `error{code:"echo_budget_exceeded"}`.
- [ ] `tests/test_echo_thin_reconnect_resume.py` — start a BED instance,
  connect, send 10 `echo`s, close socket before any `echo_ack`. Reconnect
  with the bearer token. Server replays the unacked fragments in order;
  client sends one `echo_ack{last_seq=10}`; server resumes from seq 11.
- [ ] `tests/test_echo_thin_cancel.py` — server sends `echo_cancel{
  request_id, reason="superseded"}`; client must drop the fragments and
  may send `echo_ack{last_seq=<prior visible seq>}`.

#### Definition of done for Phase 1a
- [ ] All seven test files above pass.
- [ ] The legacy door-mode pytest suite (`tests/`) still passes with the
  shim installed in thick mode (no regressions).
- [ ] A scripted `headless` client can connect, `auth`, receive a
  welcome-banner `echo`, send `echo_ack`, and disconnect cleanly.
- [ ] A `tui` client can connect, `auth`, render a welcome banner to
  stdout, send `echo_ack`, and disconnect cleanly.
- [ ] `empyre/BED_PROTOCOL.md` documents the `echo` / `echo_ack` /
  `echo_batch` / `echo_nack` / `echo_cancel` wire shapes by reference
  to `bed/TODO.md`, with the empyre-specific style/MCI field conventions
  spelled out.

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
- [ ] **screen.setbottombar / register_bottombar_fragment** — push-based; mirror the three fragments empyre registers in `lib.init` to the client at `auth` time, re-push on every `register_*` call. (Bottombar architecture: see `../bbsengine6/TODO-BOTTOMBAR.md`.)
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

> **Cross-reference:** empyre's `coins` column is a separate
> ledger from the casino's `engine.__member.credits` and is
> unaffected by the casino's "Rework: route per-hand money
> through the bank" plan (see `casino/TODO.md`). The
> nullable nature of `coins` noted in this section is
> intentional and not related to the casino's NULL-credits
> work (the casino's `engine.__member.credits` is the
> per-member wallet; empyre's `coins` is a separate,
> empyre-internal currency concept).

## Bed integration (empyre 0.0.x)

Empyre adopts `bed` as a hard dependency and ships its own thin-client
WebSocket integration. This work unblocks the Phase 0/1/2 thin-client
work in the plan above by establishing the bed side of the integration
without the full client/server rewrite.

- [x] Register `--bed-host` (default `localhost`), `--bed-port` (default
  `8765`), `--bed-path` (default `/`), `--bed-probe-timeout`,
  `--bed-call-timeout`, `--bed-disable` in `empyre.lib.buildargs`.
- [x] `--database*` flags are hidden from `--help` (`suppress=True`)
  but still accepted. They remain functional so the local-DB fallback
  in `BankService` / `PlayerService` works when bed is down.
- [x] `empyre.bed_client` module: `BedConnection` (module-level
  singleton, lazy connect, reconnect on failure, `force_close` for
  tests), `BedUnavailable`, `get_bed_connection`, `probe_bed`,
  `reset_bed_connection`. All websocket transport lives here; no
  other empyre module imports `websockets` directly. The message-
  family wrapper `BedBankClient` was removed from this module and now
  lives in `bed.client.bank` (commit `f758b01`); the shim here
  re-exports only the transport symbols.
- [x] `empyre.lib.init` does a one-shot TCP probe and sets
  `args.bed_reachable`; `empyre.lib.get_player_coins` and
  `sync_player_coins` consult the probe via `PlayerService`.
  When `--bed-disable` is set, the probe is skipped and
  `args.bed_reachable = False` so the direct-DB bank path runs.
- [x] `BankServiceHandler` is auth-gated, owner-or-sysop, every
  error path uses `bed.api.errors.error_envelope` so the client
  sees `recoverable` and can choose between `auth` and `reconnect`.
  Wire envelopes (`bank_balance`, `bank_added`, `bank_removed`,
  `bank_history`) match the cross-project family used by
  bbsengine6-bank, casino, and mistermcfeely.
- [x] `empyre.services.player.PlayerService` is the single owner of
  player auth, load, profile, history. Routes through bed when
  reachable, falls back to local `empyre.player` + `bbsengine6.member`
  otherwise. SSO via `bbsengine6.services.member.MemberService` is
  consulted in the local-DB branch. `PlayerServiceUnavailable` is
  the single exception type callers translate to a recoverable
  `bed_unavailable` envelope.
- [x] `MessageRouter` in `empyre.api.handler` wires every service
  to its message types: `auth`, `ping`, `list_islands`,
  `join_island`, `leave_island`, `island_info`, `list_colonies`,
  `list_ships`, `ship_info`, `buy_ship`, `sail_ship`,
  `list_towns`, `town_info`, `town_tax`, `recruit_soldiers`,
  `market_prices`, `buy_resource`, `sell_resource`,
  `chat_island`, `chat_global`, `emote`, `bank_balance`,
  `bank_add`, `bank_remove`, `bank_history`, `player_load`,
  `player_auth`, `player_info`, `player_history`,
  `subscribe_channel`, `unsubscribe_channel`, `get_subscriptions`.
- [x] `PlayerServiceHandler` replaces the legacy
  `MemberServiceHandler` stub. Always delegates to
  `empyre.services.player.PlayerService`; wire messages
  `player_load` -> `player_load_result`, `player_auth` ->
  `player_auth_result`, `player_info` -> `player_info_result`,
  `player_history` -> `player_history_result`. Tests updated
  (`src/tests/test_api_handler.py`).
- [x] `pyproject.toml` declares `bed` as a runtime dependency.

### Tests added

- [x] `src/tests/test_bed_flags.py` — covers every `--bed-*`
  default value, every CLI override, and the `args.bed_reachable`
  lifecycle in three states (`--bed-disable`, bed unreachable,
  bed reachable).
- [x] `src/tests/test_bed_client.py` — unit tests for the
  `empyre.bed_client` shim. All network is mocked; no real
  bed daemon, no real websockets.
- [x] `src/tests/test_bed_end_to_end.py` — module-level
  pytest skip unless `127.0.0.1:8765` is reachable; exercises
  the real wire protocol through `BedConnection`,
  `BedBankClient`, and `PlayerService` (bed-mode branch).
- [x] `src/tests/test_auth_uses_player_service.py` — regression
  guard that `AuthService._handle_auth` goes through
  `empyre.services.player.PlayerService` and not through
  the (non-existent) `empyre.player.loadplayer` /
  `empyre.player.checkpassword` paths.
- [x] `src/tests/test_bank_session.py` — behavioural tests
  for the refactored `BankServiceHandler` using
  `unittest.mock`; every success and every error matches
  the cross-project `bank_*` family.

Future tests to add when the bank schema is verified: full
add/remove round-trip, `list_services` sanity, `PlayerService`
end-to-end against a known member.
