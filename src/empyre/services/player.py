"""PlayerService - domain service for empyre players.

Routes through a bed WebSocket when args.bed_reachable is True and
falls back to the local empyre.player + bbsengine6.member tables
otherwise. Used by AuthService._handle_auth (login), the
BankServiceHandler (coins), the door-mode TUI (lib.get_player_coins
and lib.sync_player_coins), and the future empyre.client thin-client
(Phase 5).

The class owns the bed-fallback decision so callers don't have to
think about it. PlayerServiceUnavailable is the single exception
every method can raise when bed is down mid-call; callers
(AuthService, BankServiceHandler) translate that into a recoverable
error envelope.

NOTE on plaintext passwords: check_password sends the password in
plaintext JSON over the WebSocket in bed mode. This matches the
legacy AuthService behaviour. When TODO Phase 0a lands and bed's
AuthService takes over, check_password gets dropped in favour of
bed's auth + bearer token, and the plaintext leaves the wire.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from bbsengine6 import bank as bbs_bank
from bbsengine6 import io
from bbsengine6 import member as bbs_member

from bed.client import BedBankClient, BedConnection, BedUnavailable


class PlayerServiceUnavailable(Exception):
    """Raised when the service is in bed mode and bed is unreachable."""


@dataclass(frozen=True)
class PlayerCredentials:
    """Result of a credential check. Never includes the password."""

    moniker: str
    membermoniker: str
    is_sysop: bool
    password_ok: bool

    @classmethod
    def missing(cls, moniker: str) -> "PlayerCredentials":
        return cls(
            moniker=moniker, membermoniker="", is_sysop=False, password_ok=False
        )


class _BedPlayerClient:
    """Async client for the player_* message family.

    The PlayerService holds one of these when bed is reachable. The
    actual websockets connection is shared via BedConnection.
    """

    def __init__(self, args: argparse.Namespace) -> None:
        self._conn = BedConnection(args)
        self._bank = BedBankClient(args)

    async def load(self, moniker: str) -> Dict[str, Any]:
        reply = await self._conn.send(
            {"type": "player_load", "moniker": moniker}
        )
        if reply.get("type") == "error":
            raise PlayerServiceUnavailable(
                f"player_load: {reply.get('code')}: {reply.get('message')}"
            )
        return reply

    async def auth(self, moniker: str, password: str) -> Dict[str, Any]:
        reply = await self._conn.send(
            {
                "type": "player_auth",
                "moniker": moniker,
                "password": password,
            }
        )
        return reply

    async def info(self, moniker: str) -> Dict[str, Any]:
        reply = await self._conn.send(
            {"type": "player_info", "moniker": moniker}
        )
        if reply.get("type") == "error":
            raise PlayerServiceUnavailable(
                f"player_info: {reply.get('code')}: {reply.get('message')}"
            )
        return reply

    async def history(self, moniker: str, limit: int) -> List[Dict[str, Any]]:
        reply = await self._conn.send(
            {
                "type": "player_history",
                "moniker": moniker,
                "limit": int(limit),
            }
        )
        if reply.get("type") == "error":
            raise PlayerServiceUnavailable(
                f"player_history: {reply.get('code')}: {reply.get('message')}"
            )
        return list(reply.get("transactions", []))


class PlayerService:
    """Domain service for empyre players.

    check_password returns a PlayerCredentials dataclass. Never
    returns the plaintext password.

    load returns a fully-populated empyre.player.Player or None. In
    bed mode the returned Player has pool = None and save() will
    no-op (bed is the writer).

    get_coins returns the live coin balance. In bed mode it
    round-trips to bed; in local-DB mode it uses
    bbsengine6.bank.BankService.get_balance. Both raise
    PlayerServiceUnavailable when bed is down; callers fall back to
    getattr(player, 'coins', 0).

    get_profile returns a small dict suitable for the player_info
    envelope: moniker, membermoniker, rank, ...

    get_history returns up to limit newsentry rows.

    exists, list_for_member, create are local-DB only; the bed
    client is read-only for now.
    """

    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self._bed: Optional[_BedPlayerClient] = None
        if self._bed_reachable():
            self._bed = _BedPlayerClient(args)

    def _bed_reachable(self) -> bool:
        if getattr(self.args, "bed_disable", False):
            return False
        return bool(getattr(self.args, "bed_reachable", False))

    def _local_pool(self):
        return getattr(self.args, "pool", None)

    # ----- auth -----

    def check_password(
        self, moniker: str, password: str
    ) -> PlayerCredentials:
        """Return a PlayerCredentials.

        Local-DB branch order of operations:
        1. Try bbsengine6.services.member.MemberService.get_profile
           (engine SSO); if it returns a non-None profile, use the
           tier field as a sysop hint if present.
        2. Fall back to bbsengine6.member.checkpassword (the
           existing bcrypt/crypt path).

        Bed mode: a player_auth round-trip. The plaintext password
        is sent on the wire (see module docstring).
        """
        if not moniker or not password:
            return PlayerCredentials.missing(moniker or "")

        if self._bed is not None:
            return self._check_password_bed(moniker, password)

        return self._check_password_local(moniker, password)

    def _check_password_local(
        self, moniker: str, password: str
    ) -> PlayerCredentials:
        membermoniker = self._resolve_membermoniker(moniker)
        if not membermoniker:
            return PlayerCredentials.missing(moniker)

        is_sysop = bool(bbs_member.issysop(self.args, moniker=moniker))
        if not is_sysop:
            try:
                from bbsengine6.services.member import MemberService

                profile = MemberService(self.args).get_profile(moniker)
                if profile is not None and profile.get("tier") in (
                    "sysop",
                    "admin",
                ):
                    is_sysop = True
            except Exception:
                # MemberService is engine-level infrastructure; if it
                # doesn't exist or fails, fall through to the legacy
                # checkpassword path.
                pass

        password_ok = bool(
            bbs_member.checkpassword(
                self.args, password, membermoniker=membermoniker
            )
        )

        return PlayerCredentials(
            moniker=moniker,
            membermoniker=membermoniker,
            is_sysop=is_sysop,
            password_ok=password_ok,
        )

    def _check_password_bed(
        self, moniker: str, password: str
    ) -> PlayerCredentials:
        import asyncio

        try:
            reply = asyncio.run(self._bed.auth(moniker, password))
        except BedUnavailable as exc:
            raise PlayerServiceUnavailable(str(exc)) from exc

        if reply.get("type") == "error":
            code = reply.get("code", "")
            if code in ("not_authenticated", "bad_credentials"):
                return PlayerCredentials(
                    moniker=moniker,
                    membermoniker=reply.get("membermoniker", ""),
                    is_sysop=bool(reply.get("is_sysop", False)),
                    password_ok=False,
                )
            raise PlayerServiceUnavailable(
                f"player_auth: {code}: {reply.get('message')}"
            )

        return PlayerCredentials(
            moniker=moniker,
            membermoniker=reply.get("membermoniker", ""),
            is_sysop=bool(reply.get("is_sysop", False)),
            password_ok=bool(reply.get("success", True)),
        )

    # ----- load -----

    def load(
        self, moniker: str, *, pool: Any = None
    ) -> Optional[Any]:
        """Return an empyre.player.Player for moniker or None.

        In bed mode the returned Player has pool = None so that
        Player.save() (which early-returns when pool is None) is a
        no-op. Bed is the writer in that mode.
        """
        if self._bed is not None:
            return self._load_bed(moniker)
        return self._load_local(moniker, pool=pool)

    def _load_local(self, moniker: str, *, pool: Any) -> Optional[Any]:
        from empyre import player as libplayer

        if pool is None:
            pool = self._local_pool()
        if pool is None:
            io.echo(
                f"empyre.services.player.load: no pool for {moniker=}",
                level="error",
            )
            return None
        return libplayer.load(self.args, moniker, pool=pool)

    def _load_bed(self, moniker: str) -> Any:
        import asyncio

        from empyre import player as libplayer

        try:
            reply = asyncio.run(self._bed.load(moniker))
        except BedUnavailable as exc:
            raise PlayerServiceUnavailable(str(exc)) from exc

        player = libplayer.Player(self.args)
        payload = reply.get("player", {})
        player.moniker = moniker
        player.membermoniker = payload.get("membermoniker", "")
        player.pool = None
        for k, v in payload.items():
            if k in ("moniker", "membermoniker"):
                continue
            if hasattr(player, k):
                setattr(player, k, v)
        return player

    # ----- coins -----

    def get_coins(self, moniker: str) -> int:
        """Return the live coin balance. Raises
        PlayerServiceUnavailable if bed is down mid-call."""
        if self._bed is not None:
            import asyncio

            try:
                return asyncio.run(self._bed._bank.get_balance(moniker))
            except BedUnavailable as exc:
                raise PlayerServiceUnavailable(str(exc)) from exc

        try:
            service = bbs_bank.BankService(self.args)
            return int(service.get_balance(moniker))
        except Exception as exc:
            raise PlayerServiceUnavailable(str(exc)) from exc

    # ----- profile -----

    def get_profile(self, moniker: str) -> Optional[Dict[str, Any]]:
        """Return a small dict for the player_info envelope.

        Reads the local empyre.player + bank tables (no bed round-
        trip) so the profile renders instantly on a reconnect.
        """
        if self._bed is not None:
            try:
                return self._get_profile_bed(moniker)
            except PlayerServiceUnavailable:
                return None
        return self._get_profile_local(moniker)

    def _get_profile_local(self, moniker: str) -> Optional[Dict[str, Any]]:
        from empyre import player as libplayer

        pool = self._local_pool()
        if pool is None:
            return None
        p = libplayer.load(self.args, moniker, pool=pool)
        if p is None:
            return None
        return {
            "moniker": getattr(p, "moniker", moniker),
            "membermoniker": getattr(p, "membermoniker", ""),
            "rank": getattr(p, "rank", 0),
            "previousrank": getattr(p, "previousrank", 0),
            "turncount": getattr(p, "turncount", 0),
            "land": getattr(p, "land", 0),
            "coins": getattr(p, "coins", 0),
            "is_sysop": bool(
                bbs_member.issysop(self.args, moniker=moniker)
            ),
        }

    def _get_profile_bed(self, moniker: str) -> Optional[Dict[str, Any]]:
        import asyncio

        reply = asyncio.run(self._bed.info(moniker))
        if reply.get("type") == "error":
            code = reply.get("code", "")
            if code in ("not_found", "player_not_found"):
                return None
            raise PlayerServiceUnavailable(
                f"player_info: {code}: {reply.get('message')}"
            )
        return reply.get("player")

    # ----- history -----

    def get_history(
        self, moniker: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Player-side history (empyre.__newsentry for now)."""
        if self._bed is not None:
            import asyncio

            try:
                return asyncio.run(self._bed.history(moniker, limit))
            except BedUnavailable as exc:
                raise PlayerServiceUnavailable(str(exc)) from exc

        from bbsengine6 import database

        try:
            with database.connect(self.args) as conn:
                with database.cursor(conn) as cur:
                    cur.execute(
                        database.query(
                            "SELECT id, message, datecreated "
                            "FROM empyre.__newsentry "
                            "WHERE playermoniker = :moniker "
                            "ORDER BY datecreated DESC "
                            "LIMIT :limit",
                            moniker=moniker,
                            limit=int(limit),
                        )
                    )
                    rows = cur.fetchall()
                    return [dict(r) for r in rows]
        except Exception as exc:
            raise PlayerServiceUnavailable(str(exc)) from exc

    # ----- local-DB only helpers -----

    def exists(self, moniker: str) -> bool:
        from empyre import player as libplayer

        return bool(libplayer.exists(moniker, args=self.args))

    def list_for_member(self, membermoniker: str) -> List[str]:
        from bbsengine6 import database

        with database.connect(self.args) as conn:
            with database.cursor(conn) as cur:
                cur.execute(
                    database.query(
                        "SELECT moniker FROM empyre.__player "
                        "WHERE membermoniker = :moniker "
                        "ORDER BY datelastplayed DESC",
                        moniker=membermoniker,
                    )
                )
                return [row["moniker"] for row in cur.fetchall()]

    def create(
        self, *, membermoniker: str, moniker: str, **kwargs: Any
    ) -> Any:
        from empyre import player as libplayer

        pool = self._local_pool()
        if pool is None:
            raise PlayerServiceUnavailable(
                "PlayerService.create requires a DB pool"
            )
        return libplayer.create(
            self.args,
            pool=pool,
            membermoniker=membermoniker,
            moniker=moniker,
        )

    # ----- internal -----

    def _resolve_membermoniker(self, moniker: str) -> str:
        from bbsengine6 import database

        try:
            with database.connect(self.args) as conn:
                with database.cursor(conn) as cur:
                    cur.execute(
                        database.query(
                            "SELECT membermoniker FROM empyre.__player "
                            "WHERE moniker = :moniker",
                            moniker=moniker,
                        )
                    )
                    row = cur.fetchone()
                    if row is None:
                        return ""
                    return row.get("membermoniker", "") or ""
        except Exception:
            return ""
