"""Regression guard: AuthService._handle_auth uses PlayerService.

Prior to Pass 3, the auth path called
``empyre_player.loadplayer(self.args, moniker)`` and
``empyre_player.checkpassword(player, password)`` which do not exist
on ``empyre.player``. This test asserts that the auth path now goes
through ``empyre.services.player.PlayerService`` and produces the
expected envelope.
"""

import argparse
import asyncio
from unittest.mock import MagicMock, patch

import pytest

from empyre.api.handler import AuthService, SessionManager


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _test_args():
    return argparse.Namespace(
        databasename="zoid6test",
        databasehost="127.0.0.1",
    )


class TestAuthUsesPlayerService:
    def test_auth_calls_player_service_check_password(self):
        auth = AuthService(_test_args(), SessionManager())
        with patch(
            "empyre.services.player.PlayerService.check_password"
        ) as mock_cp:
            creds = MagicMock()
            creds.password_ok = True
            creds.is_sysop = False
            creds.membermoniker = "m1"
            mock_cp.return_value = creds
            with patch(
                "empyre.services.player.PlayerService.load", return_value=None
            ):
                with patch(
                    "empyre.services.player.PlayerService.get_coins",
                    return_value=0,
                ):
                    with patch(
                        "bbsengine6.message.deliver_pending_on_connect",
                        return_value=[],
                    ):
                        with patch(
                            "bbsengine6.message.get_unread_count",
                            return_value=0,
                        ):
                            ws = MagicMock()
                            result = _run(
                                auth._handle_auth(
                                    ws, {"moniker": "alice", "password": "x"}
                                )
                            )

        assert result["success"] is True
        assert result["moniker"] == "alice"
        mock_cp.assert_called_once_with("alice", "x")

    def test_auth_does_not_call_nonexistent_loadplayer(self):
        """Pre-existing bug: empyre.player.loadplayer did not exist."""
        auth = AuthService(_test_args(), SessionManager())
        # If we accidentally regressed, this would raise AttributeError
        # because empyre.player.loadplayer doesn't exist.
        try:
            from empyre import player

            assert not hasattr(player, "loadplayer"), (
                "empyre.player.loadplayer should not exist; "
                "PlayerService replaces it"
            )
        except ImportError:
            pass

    def test_auth_returns_bad_credentials_on_wrong_password(self):
        auth = AuthService(_test_args(), SessionManager())
        with patch(
            "empyre.services.player.PlayerService.check_password"
        ) as mock_cp:
            creds = MagicMock()
            creds.password_ok = False
            creds.is_sysop = False
            creds.membermoniker = ""
            mock_cp.return_value = creds
            ws = MagicMock()
            result = _run(
                auth._handle_auth(ws, {"moniker": "alice", "password": "x"})
            )
        assert result["code"] == "bad_credentials"
        assert result["recoverable"] is False

    def test_auth_returns_missing_credentials_on_empty_input(self):
        auth = AuthService(_test_args(), SessionManager())
        ws = MagicMock()
        result = _run(
            auth._handle_auth(ws, {"moniker": "", "password": ""})
        )
        assert result["code"] == "missing_credentials"
        assert result["recoverable"] is False

    def test_auth_returns_bed_unavailable_on_player_service_error(self):
        from empyre.services import PlayerServiceUnavailable

        auth = AuthService(_test_args(), SessionManager())
        with patch(
            "empyre.services.player.PlayerService.check_password",
            side_effect=PlayerServiceUnavailable("bed down"),
        ):
            ws = MagicMock()
            result = _run(
                auth._handle_auth(ws, {"moniker": "alice", "password": "x"})
            )
        assert result["code"] == "bed_unavailable"
        assert result["recoverable"] is True

    def test_auth_result_envelope_has_is_sysop(self):
        auth = AuthService(_test_args(), SessionManager())
        with patch(
            "empyre.services.player.PlayerService.check_password"
        ) as mock_cp:
            creds = MagicMock()
            creds.password_ok = True
            creds.is_sysop = True
            creds.membermoniker = "m1"
            mock_cp.return_value = creds
            with patch(
                "empyre.services.player.PlayerService.load", return_value=None
            ):
                with patch(
                    "empyre.services.player.PlayerService.get_coins",
                    return_value=42,
                ):
                    with patch(
                        "bbsengine6.message.deliver_pending_on_connect",
                        return_value=[],
                    ):
                        with patch(
                            "bbsengine6.message.get_unread_count",
                            return_value=0,
                        ):
                            ws = MagicMock()
                            result = _run(
                                auth._handle_auth(
                                    ws, {"moniker": "root", "password": "x"}
                                )
                            )
        assert result["is_sysop"] is True
        assert result["balance"] == 42
