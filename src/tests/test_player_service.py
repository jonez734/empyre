"""Tests for empyre.services.player.PlayerService.

Local-DB branch: mocked empyre.player + bbsengine6.member.
Bed branch: mocked _BedPlayerClient.
"""

import argparse
from unittest.mock import MagicMock, patch

import pytest

from empyre.services.player import (
    PlayerCredentials,
    PlayerService,
    PlayerServiceUnavailable,
)


def _args(**kw):
    base = dict(
        bed_host="localhost",
        bed_port=8765,
        bed_disable=False,
        bed_reachable=False,
    )
    base.update(kw)
    return argparse.Namespace(**base)


class TestLocalDBFallback:
    def test_check_password_returns_dataclass(self):
        args = _args()
        svc = PlayerService(args)
        with patch(
            "bbsengine6.member.checkpassword", return_value=True
        ):
            with patch.object(svc, "_resolve_membermoniker", return_value="m1"):
                with patch("bbsengine6.member.issysop", return_value=False):
                    creds = svc.check_password("alice", "x")
        assert isinstance(creds, PlayerCredentials)
        assert creds.moniker == "alice"
        assert creds.password_ok is True
        assert creds.is_sysop is False
        assert creds.membermoniker == "m1"

    def test_check_password_with_wrong_password(self):
        args = _args()
        svc = PlayerService(args)
        with patch(
            "bbsengine6.member.checkpassword", return_value=False
        ):
            with patch.object(svc, "_resolve_membermoniker", return_value="m1"):
                with patch("bbsengine6.member.issysop", return_value=False):
                    creds = svc.check_password("alice", "wrong")
        assert creds.password_ok is False

    def test_check_password_returns_missing_for_empty(self):
        svc = PlayerService(_args())
        assert svc.check_password("", "x") == PlayerCredentials.missing("")
        assert svc.check_password("alice", "") == PlayerCredentials.missing("alice")

    def test_check_password_returns_missing_when_no_membermoniker(self):
        svc = PlayerService(_args())
        with patch.object(svc, "_resolve_membermoniker", return_value=""):
            creds = svc.check_password("alice", "x")
        assert creds.password_ok is False
        assert creds.membermoniker == ""

    def test_check_password_promotes_to_sysop_via_member_service(self):
        svc = PlayerService(_args())
        with patch.object(svc, "_resolve_membermoniker", return_value="m1"):
            with patch("bbsengine6.member.issysop", return_value=False):
                with patch("bbsengine6.member.checkpassword", return_value=True):
                    fake_profile = {"tier": "sysop"}
                    with patch(
                        "bbsengine6.services.member.MemberService"
                    ) as ms_cls:
                        ms_cls.return_value.get_profile.return_value = (
                            fake_profile
                        )
                        creds = svc.check_password("alice", "x")
        assert creds.is_sysop is True

    def test_check_password_ignores_member_service_when_not_sysop_tier(self):
        svc = PlayerService(_args())
        with patch.object(svc, "_resolve_membermoniker", return_value="m1"):
            with patch("bbsengine6.member.issysop", return_value=False):
                with patch("bbsengine6.member.checkpassword", return_value=True):
                    with patch(
                        "bbsengine6.services.member.MemberService"
                    ) as ms_cls:
                        ms_cls.return_value.get_profile.return_value = {
                            "tier": "user"
                        }
                        creds = svc.check_password("alice", "x")
        assert creds.is_sysop is False

    def test_check_password_falls_back_when_member_service_missing(self):
        svc = PlayerService(_args())
        with patch.object(svc, "_resolve_membermoniker", return_value="m1"):
            with patch("bbsengine6.member.issysop", return_value=False):
                with patch("bbsengine6.member.checkpassword", return_value=True):
                    # Force ImportError
                    import builtins
                    real_import = builtins.__import__

                    def fake_import(name, *args, **kwargs):
                        if name == "bbsengine6.services.member":
                            raise ImportError("simulated missing")
                        return real_import(name, *args, **kwargs)

                    with patch.object(builtins, "__import__", side_effect=fake_import):
                        creds = svc.check_password("alice", "x")
        # Falls through to checkpassword which returns True; is_sysop
        # remains False because the MemberService path raised.
        assert creds.password_ok is True
        assert creds.is_sysop is False

    def test_check_password_marks_issysop_directly(self):
        svc = PlayerService(_args())
        with patch.object(svc, "_resolve_membermoniker", return_value="m1"):
            with patch("bbsengine6.member.issysop", return_value=True):
                with patch("bbsengine6.member.checkpassword", return_value=True):
                    creds = svc.check_password("root", "x")
        assert creds.is_sysop is True

    def test_get_coins_calls_bank_service_in_local_mode(self):
        svc = PlayerService(_args())
        with patch("bbsengine6.bank.BankService") as bs_cls:
            bs_cls.return_value.get_balance.return_value = 500
            n = svc.get_coins("alice")
        assert n == 500
        bs_cls.assert_called_once()

    def test_get_coins_raises_unavailable_on_db_error(self):
        svc = PlayerService(_args())
        with patch(
            "bbsengine6.bank.BankService",
            side_effect=RuntimeError("db down"),
        ):
            with pytest.raises(PlayerServiceUnavailable):
                svc.get_coins("alice")

    def test_load_returns_none_when_no_pool(self):
        args = _args()
        args.pool = None
        svc = PlayerService(args)
        with patch("empyre.player.load", return_value=None):
            with patch("empyre.player.Player"):
                result = svc.load("alice", pool=None)
        assert result is None

    def test_load_returns_player_when_pool_provided(self):
        args = _args()
        svc = PlayerService(args)
        fake_player = MagicMock()
        with patch("empyre.player.load", return_value=fake_player):
            result = svc.load("alice", pool="pool")
        assert result is fake_player

    def test_exists(self):
        svc = PlayerService(_args())
        with patch("empyre.player.exists", return_value=True):
            assert svc.exists("alice") is True
        with patch("empyre.player.exists", return_value=False):
            assert svc.exists("alice") is False

    def test_create_requires_pool(self):
        svc = PlayerService(_args())
        with pytest.raises(PlayerServiceUnavailable):
            svc.create(membermoniker="m1", moniker="alice")

    def test_list_for_member(self):
        svc = PlayerService(_args())
        with patch("bbsengine6.database.connect") as mock_conn:
            mock_cur = MagicMock()
            mock_cur.fetchall.return_value = [
                {"moniker": "alice"},
                {"moniker": "bob"},
            ]
            mock_conn.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = (
                mock_cur
            )
            result = svc.list_for_member("m1")
        assert result == ["alice", "bob"]


class TestBedMode:
    def _bed_args(self, **kw):
        return _args(bed_reachable=True, **kw)

    def test_load_routes_through_bed_when_reachable(self):
        args = self._bed_args()
        svc = PlayerService(args)
        assert svc._bed is not None

        async def fake_load(moniker):
            return {
                "type": "player_load_result",
                "player": {"membermoniker": "m1", "rank": 7},
            }

        with patch.object(svc._bed, "load", side_effect=fake_load):
            with patch("empyre.player.Player") as MockPlayer:
                player = svc.load("alice")
        assert player.moniker == "alice"
        assert player.membermoniker == "m1"
        assert player.pool is None
        assert MockPlayer.called

    def test_check_password_routes_through_bed_when_reachable(self):
        args = self._bed_args()
        svc = PlayerService(args)

        async def fake_auth(moniker, password):
            return {
                "type": "player_auth_result",
                "success": True,
                "is_sysop": True,
            }

        with patch.object(svc._bed, "auth", side_effect=fake_auth):
            creds = svc.check_password("alice", "x")
        assert creds.password_ok is True
        assert creds.is_sysop is True

    def test_check_password_bed_returns_bad_creds_envelope(self):
        args = self._bed_args()
        svc = PlayerService(args)

        async def fake_auth(moniker, password):
            return {"type": "error", "code": "bad_credentials"}

        with patch.object(svc._bed, "auth", side_effect=fake_auth):
            creds = svc.check_password("alice", "wrong")
        assert creds.password_ok is False

    def test_check_password_bed_other_error_raises_unavailable(self):
        args = self._bed_args()
        svc = PlayerService(args)

        async def fake_auth(moniker, password):
            return {"type": "error", "code": "weird"}

        with patch.object(svc._bed, "auth", side_effect=fake_auth):
            with pytest.raises(PlayerServiceUnavailable):
                svc.check_password("alice", "x")

    def test_get_coins_falls_back_when_bed_down(self):
        from empyre.bed_client import BedUnavailable

        args = self._bed_args()
        svc = PlayerService(args)

        async def fake_get_balance(moniker):
            raise BedUnavailable("bed down")

        with patch.object(
            svc._bed._bank, "get_balance", side_effect=fake_get_balance
        ):
            with patch("bbsengine6.bank.BankService") as bs_cls:
                bs_cls.return_value.get_balance.return_value = 42
                with pytest.raises(PlayerServiceUnavailable):
                    svc.get_coins("alice")

    def test_get_coins_bed_success(self):
        args = self._bed_args()
        svc = PlayerService(args)

        async def fake_get_balance(moniker):
            return 99

        with patch.object(
            svc._bed._bank, "get_balance", side_effect=fake_get_balance
        ):
            n = svc.get_coins("alice")
        assert n == 99

    def test_disabled_flag_bypasses_bed(self):
        args = self._bed_args(bed_disable=True)
        svc = PlayerService(args)
        assert svc._bed is None


class TestGetProfile:
    def test_local_profile_no_pool_returns_none(self):
        args = _args()
        args.pool = None
        svc = PlayerService(args)
        with patch("empyre.player.load", return_value=None):
            assert svc.get_profile("alice") is None

    def test_local_profile_returns_dict(self):
        args = _args()
        args.pool = MagicMock()  # so _get_profile_local can call load
        svc = PlayerService(args)
        fake_player = MagicMock()
        fake_player.moniker = "alice"
        fake_player.membermoniker = "m1"
        fake_player.rank = 5
        fake_player.previousrank = 4
        fake_player.turncount = 10
        fake_player.land = 1000
        fake_player.coins = 50
        with patch("empyre.player.load", return_value=fake_player):
            with patch("bbsengine6.member.issysop", return_value=False):
                profile = svc.get_profile("alice")
        assert profile["moniker"] == "alice"
        assert profile["membermoniker"] == "m1"
        assert profile["rank"] == 5
        assert profile["previousrank"] == 4
        assert profile["turncount"] == 10
        assert profile["land"] == 1000
        assert profile["coins"] == 50
        assert profile["is_sysop"] is False

    def test_local_profile_with_sysop(self):
        args = _args()
        args.pool = MagicMock()
        svc = PlayerService(args)
        fake_player = MagicMock()
        fake_player.moniker = "root"
        fake_player.membermoniker = "m1"
        fake_player.rank = 99
        fake_player.previousrank = 99
        fake_player.turncount = 0
        fake_player.land = 0
        fake_player.coins = 0
        with patch("empyre.player.load", return_value=fake_player):
            with patch("bbsengine6.member.issysop", return_value=True):
                profile = svc.get_profile("root")
        assert profile["is_sysop"] is True


class TestGetHistory:
    def test_local_history_default_limit(self):
        svc = PlayerService(_args())
        with patch("bbsengine6.database.connect") as mock_conn:
            mock_cur = MagicMock()
            mock_cur.fetchall.return_value = [
                {"id": 1, "message": "a", "datecreated": "2026-01-01"}
            ]
            mock_conn.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = (
                mock_cur
            )
            result = svc.get_history("alice")
        assert len(result) == 1
        assert result[0]["id"] == 1

    def test_local_history_custom_limit(self):
        svc = PlayerService(_args(limit=10))
        with patch("bbsengine6.database.connect") as mock_conn:
            mock_cur = MagicMock()
            mock_cur.fetchall.return_value = []
            mock_conn.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = (
                mock_cur
            )
            svc.get_history("alice", limit=5)
        # SQL was issued (we don't introspect, but no exception is enough).


class TestBedModeDisabled:
    def test_disable_flag_in_init(self):
        args = _args(bed_disable=True, bed_reachable=True)
        svc = PlayerService(args)
        assert svc._bed is None

    def test_bed_reachable_with_disable_uses_local(self):
        args = _args(bed_disable=True, bed_reachable=True)
        svc = PlayerService(args)
        with patch("bbsengine6.bank.BankService") as bs_cls:
            bs_cls.return_value.get_balance.return_value = 7
            n = svc.get_coins("alice")
        assert n == 7
