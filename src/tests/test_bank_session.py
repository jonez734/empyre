"""Behavioural tests for the refactored BankServiceHandler.

These tests use unittest.mock to fake the bank_service; no real DB.
The envelope-shape tests assert that every success and every error
matches the cross-project bank_* family used by bbsengine6-bank,
casino, mistermcfeely, and now empyre.
"""

import argparse
import asyncio
from unittest.mock import MagicMock, patch

import pytest

from empyre.api.handler import BankServiceHandler, SessionManager


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _make_handler(bank_service=None, sessions=None):
    args = argparse.Namespace()
    sessions = sessions or SessionManager()
    handler = BankServiceHandler(args, sessions)
    if bank_service is not None:
        handler.bank_service = bank_service
    return handler, sessions, args


def _register(sessions, moniker="alice", is_sysop=False):
    sessions.register_session(1, moniker, is_sysop=is_sysop)


class TestBankBalance:
    def test_balance_without_session_returns_not_authenticated(self):
        handler, sessions, _ = _make_handler()
        result = _run(handler._handle_balance(999, {}))
        assert result["type"] == "error"
        assert result["code"] == "not_authenticated"
        assert result["recoverable"] is True

    def test_balance_with_session_uses_session_moniker(self):
        bank_service = MagicMock()
        bank_service.get_balance.return_value = 100
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="alice")

        result = _run(handler._handle_balance(1, {}))

        bank_service.get_balance.assert_called_once_with("alice")
        assert result["type"] == "bank_balance"
        assert result["moniker"] == "alice"
        assert result["balance"] == 100
        assert result["is_sysop"] is False

    def test_balance_ignores_requested_moniker_for_non_sysop(self):
        bank_service = MagicMock()
        bank_service.get_balance.return_value = 42
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="alice")

        result = _run(handler._handle_balance(1, {"moniker": "bob"}))

        # Non-sysop session must not be able to read another account's balance.
        assert result["code"] == "forbidden"
        assert result["recoverable"] is False
        bank_service.get_balance.assert_not_called()

    def test_balance_allows_requested_moniker_for_sysop(self):
        bank_service = MagicMock()
        bank_service.get_balance.return_value = 999
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="root", is_sysop=True)

        result = _run(handler._handle_balance(1, {"moniker": "bob"}))

        bank_service.get_balance.assert_called_once_with("bob")
        assert result["moniker"] == "bob"
        assert result["is_sysop"] is True

    def test_balance_includes_is_sysop(self):
        bank_service = MagicMock()
        bank_service.get_balance.return_value = 0
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="root", is_sysop=True)

        result = _run(handler._handle_balance(1, {}))

        assert result["is_sysop"] is True

    def test_balance_handles_bank_service_exception(self):
        bank_service = MagicMock()
        bank_service.get_balance.side_effect = RuntimeError("db down")
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="alice")

        result = _run(handler._handle_balance(1, {}))

        assert result["type"] == "error"
        assert result["code"] == "database_error"
        assert result["recoverable"] is True
        assert "db down" in result["message"]


class TestBankAdd:
    def test_add_without_session_returns_not_authenticated(self):
        handler, sessions, _ = _make_handler()
        result = _run(handler._handle_add(999, {"moniker": "alice", "amount": 100}))
        assert result["code"] == "not_authenticated"
        assert result["recoverable"] is True

    def test_add_as_non_sysop_returns_forbidden(self):
        bank_service = MagicMock()
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="alice", is_sysop=False)

        result = _run(handler._handle_add(1, {"moniker": "bob", "amount": 100}))

        assert result["code"] == "forbidden"
        assert result["recoverable"] is False
        bank_service.add_funds.assert_not_called()

    def test_add_as_sysop_succeeds(self):
        bank_service = MagicMock()
        bank_service.add_funds.return_value = {
            "success": True,
            "new_balance": 250,
        }
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="root", is_sysop=True)

        result = _run(handler._handle_add(1, {"moniker": "alice", "amount": 100}))

        bank_service.add_funds.assert_called_once_with(
            "alice", 100, transaction_type="deposit", description="deposit"
        )
        assert result["type"] == "bank_added"
        assert result["moniker"] == "alice"
        assert result["amount"] == 100
        assert result["new_balance"] == 250
        assert result["is_sysop"] is True

    def test_add_requires_moniker(self):
        bank_service = MagicMock()
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="root", is_sysop=True)

        result = _run(handler._handle_add(1, {"amount": 100}))

        assert result["code"] == "invalid_request"
        assert result["recoverable"] is False
        bank_service.add_funds.assert_not_called()

    def test_add_rejects_zero_amount(self):
        bank_service = MagicMock()
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="root", is_sysop=True)

        result = _run(handler._handle_add(1, {"moniker": "alice", "amount": 0}))

        assert result["code"] == "invalid_request"
        bank_service.add_funds.assert_not_called()

    def test_add_rejects_negative_amount(self):
        bank_service = MagicMock()
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="root", is_sysop=True)

        result = _run(handler._handle_add(1, {"moniker": "alice", "amount": -5}))

        assert result["code"] == "invalid_request"
        bank_service.add_funds.assert_not_called()

    def test_add_propagates_failure_envelope(self):
        bank_service = MagicMock()
        bank_service.add_funds.return_value = {
            "success": False,
            "message": "some other failure",
        }
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="root", is_sysop=True)

        result = _run(handler._handle_add(1, {"moniker": "alice", "amount": 100}))

        assert result["code"] == "add_failed"
        assert result["recoverable"] is True
        assert "some other failure" in result["message"]

    def test_add_handles_bank_service_exception(self):
        bank_service = MagicMock()
        bank_service.add_funds.side_effect = RuntimeError("db boom")
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="root", is_sysop=True)

        result = _run(handler._handle_add(1, {"moniker": "alice", "amount": 100}))

        assert result["code"] == "database_error"
        assert result["recoverable"] is True


class TestBankRemove:
    def test_remove_without_session_returns_not_authenticated(self):
        handler, sessions, _ = _make_handler()
        result = handler._handle_remove(999, {"amount": 100})
        assert result["code"] == "not_authenticated"

    def test_remove_for_own_moniker_succeeds(self):
        bank_service = MagicMock()
        bank_service.remove_funds.return_value = {
            "success": True,
            "new_balance": 50,
        }
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="alice")

        result = handler._handle_remove(
            1, {"moniker": "alice", "amount": 50}
        )

        bank_service.remove_funds.assert_called_once_with(
            "alice", 50, transaction_type="withdrawal", description="withdrawal"
        )
        assert result["type"] == "bank_removed"
        assert result["moniker"] == "alice"
        assert result["amount"] == 50
        assert result["new_balance"] == 50

    def test_remove_for_other_moniker_as_non_sysop_returns_forbidden(self):
        bank_service = MagicMock()
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="alice")

        result = handler._handle_remove(
            1, {"moniker": "bob", "amount": 100}
        )

        assert result["code"] == "forbidden"
        assert result["recoverable"] is False
        bank_service.remove_funds.assert_not_called()

    def test_remove_for_other_moniker_as_sysop_succeeds(self):
        bank_service = MagicMock()
        bank_service.remove_funds.return_value = {
            "success": True,
            "new_balance": 0,
        }
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="root", is_sysop=True)

        result = handler._handle_remove(
            1, {"moniker": "bob", "amount": 100}
        )

        bank_service.remove_funds.assert_called_once_with(
            "bob", 100, transaction_type="withdrawal", description="withdrawal"
        )
        assert result["type"] == "bank_removed"
        assert result["moniker"] == "bob"

    def test_remove_defaults_to_session_moniker_when_not_supplied(self):
        bank_service = MagicMock()
        bank_service.remove_funds.return_value = {
            "success": True,
            "new_balance": 0,
        }
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="alice")

        result = handler._handle_remove(1, {"amount": 50})

        bank_service.remove_funds.assert_called_once_with(
            "alice", 50, transaction_type="withdrawal", description="withdrawal"
        )
        assert result["moniker"] == "alice"

    def test_remove_rejects_zero_amount(self):
        bank_service = MagicMock()
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="alice")

        result = handler._handle_remove(1, {"moniker": "alice", "amount": 0})

        assert result["code"] == "invalid_request"
        bank_service.remove_funds.assert_not_called()

    def test_remove_insufficient_funds_returns_recoverable_error(self):
        bank_service = MagicMock()
        bank_service.remove_funds.return_value = {
            "success": False,
            "message": "Insufficient funds. Balance: 0",
        }
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="alice")

        result = handler._handle_remove(1, {"moniker": "alice", "amount": 50})

        assert result["code"] == "insufficient_funds"
        assert result["recoverable"] is True
        assert "Insufficient" in result["message"]

    def test_remove_other_failure_returns_remove_failed(self):
        bank_service = MagicMock()
        bank_service.remove_funds.return_value = {
            "success": False,
            "message": "some other failure",
        }
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="alice")

        result = handler._handle_remove(1, {"moniker": "alice", "amount": 50})

        assert result["code"] == "remove_failed"
        assert result["recoverable"] is True

    def test_remove_handles_bank_service_exception(self):
        bank_service = MagicMock()
        bank_service.remove_funds.side_effect = RuntimeError("db boom")
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="alice")

        result = handler._handle_remove(1, {"moniker": "alice", "amount": 50})

        assert result["code"] == "database_error"
        assert result["recoverable"] is True


class TestBankHistory:
    def test_history_without_session_returns_not_authenticated(self):
        handler, sessions, _ = _make_handler()
        result = handler._handle_history(999, {})
        assert result["code"] == "not_authenticated"

    def test_history_own_moniker_succeeds(self):
        bank_service = MagicMock()
        bank_service.get_history.return_value = [{"id": 1, "amount": 10}]
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="alice")

        result = handler._handle_history(1, {"moniker": "alice"})

        bank_service.get_history.assert_called_once_with("alice", 50)
        assert result["type"] == "bank_history"
        assert result["moniker"] == "alice"
        assert result["transactions"] == [{"id": 1, "amount": 10}]
        assert result["is_sysop"] is False

    def test_history_other_moniker_as_non_sysop_returns_forbidden(self):
        bank_service = MagicMock()
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="alice")

        result = handler._handle_history(1, {"moniker": "bob"})

        assert result["code"] == "forbidden"
        assert result["recoverable"] is False
        bank_service.get_history.assert_not_called()

    def test_history_other_moniker_as_sysop_succeeds(self):
        bank_service = MagicMock()
        bank_service.get_history.return_value = []
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="root", is_sysop=True)

        result = handler._handle_history(1, {"moniker": "bob"})

        bank_service.get_history.assert_called_once_with("bob", 50)
        assert result["type"] == "bank_history"
        assert result["moniker"] == "bob"
        assert result["is_sysop"] is True

    def test_history_default_limit_is_50(self):
        bank_service = MagicMock()
        bank_service.get_history.return_value = []
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="alice")

        handler._handle_history(1, {"moniker": "alice"})

        bank_service.get_history.assert_called_once_with("alice", 50)

    def test_history_respects_limit(self):
        bank_service = MagicMock()
        bank_service.get_history.return_value = []
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="alice")

        handler._handle_history(1, {"moniker": "alice", "limit": 10})

        bank_service.get_history.assert_called_once_with("alice", 10)

    def test_history_envelope_is_shaped(self):
        bank_service = MagicMock()
        bank_service.get_history.return_value = []
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="alice", is_sysop=True)

        result = handler._handle_history(1, {"moniker": "alice"})

        assert "moniker" in result
        assert "transactions" in result
        assert "is_sysop" in result

    def test_history_handles_bank_service_exception(self):
        bank_service = MagicMock()
        bank_service.get_history.side_effect = RuntimeError("db boom")
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="alice")

        result = handler._handle_history(1, {"moniker": "alice"})

        assert result["code"] == "database_error"
        assert result["recoverable"] is True


class TestBankErrorEnvelope:
    """Every error path must produce a {type, code, message, recoverable} dict."""

    @pytest.mark.parametrize(
        "call",
        [
            lambda h: _run(h._handle_balance(999, {})),
            lambda h: _run(h._handle_add(999, {"moniker": "x", "amount": 1})),
            lambda h: h._handle_remove(999, {"amount": 1}),
            lambda h: h._handle_history(999, {}),
        ],
    )
    def test_error_envelope_shape(self, call):
        handler, sessions, _ = _make_handler()
        result = call(handler)
        assert set(result.keys()) == {"type", "code", "message", "recoverable"}
        assert result["type"] == "error"
        assert result["code"] == "not_authenticated"

    def test_database_error_is_recoverable(self):
        bank_service = MagicMock()
        bank_service.get_balance.side_effect = RuntimeError("db down")
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="alice")

        result = _run(handler._handle_balance(1, {}))

        assert result["code"] == "database_error"
        assert result["recoverable"] is True

    def test_insufficient_funds_is_recoverable(self):
        bank_service = MagicMock()
        bank_service.remove_funds.return_value = {
            "success": False,
            "message": "Insufficient funds. Balance: 0",
        }
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="alice")

        result = handler._handle_remove(1, {"moniker": "alice", "amount": 50})

        assert result["code"] == "insufficient_funds"
        assert result["recoverable"] is True

    def test_forbidden_is_not_recoverable(self):
        bank_service = MagicMock()
        handler, sessions, _ = _make_handler(bank_service=bank_service)
        _register(sessions, moniker="alice")

        result = handler._handle_remove(1, {"moniker": "bob", "amount": 50})

        assert result["code"] == "forbidden"
        assert result["recoverable"] is False


class TestBankAuthAlignment:
    """The auth_result envelope must include is_sysop.

    Now that AuthService._handle_auth uses PlayerService (Pass 3),
    this test exercises the live code path with mocked PlayerService
    methods. The deeper regression guards for PlayerService live in
    test_auth_uses_player_service.py.
    """

    def test_auth_result_envelope_includes_is_sysop(self, test_args):
        from empyre.api.handler import AuthService, SessionManager
        from empyre.services import PlayerCredentials

        sm = SessionManager()
        auth = AuthService(test_args, sm)
        creds = PlayerCredentials(
            moniker="alice", membermoniker="m1", is_sysop=True, password_ok=True
        )
        player = MagicMock()
        player.turncount = 5
        player.land = 100

        with patch(
            "empyre.services.player.PlayerService.check_password",
            return_value=creds,
        ):
            with patch(
                "empyre.services.player.PlayerService.load",
                return_value=player,
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
                                    ws, {"moniker": "alice", "password": "x"}
                                )
                            )
        assert result["success"] is True
        assert result["is_sysop"] is True
        assert result["moniker"] == "alice"
