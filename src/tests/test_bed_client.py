"""Unit tests for empyre.bed_client (BedConnection, BedBankClient, probe_bed).

These tests mock out the network entirely (no real bed, no real
websockets). The end-to-end smoke test against a real bed lives in
tests/test_bed_end_to_end.py.
"""

import argparse
import asyncio
import json
import socket
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from empyre import bed_client
from empyre.bed_client import (
    BedBankClient,
    BedConnection,
    BedUnavailable,
    get_bed_connection,
    probe_bed,
    reset_bed_connection,
)


def _args(**kw):
    base = dict(
        bed_host="localhost",
        bed_port=8765,
        bed_path="/",
        bed_probe_timeout=0.25,
        bed_call_timeout=5.0,
    )
    base.update(kw)
    return argparse.Namespace(**base)


def _run(coro):
    """Run an async coroutine to completion in a fresh event loop."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class TestProbeBed:
    def test_probe_returns_true_when_socket_connects(self):
        args = _args()
        fake_sock = MagicMock()
        fake_sock.__enter__ = MagicMock(return_value=fake_sock)
        fake_sock.__exit__ = MagicMock(return_value=False)
        with patch(
            "empyre.bed_client.socket.create_connection",
            return_value=fake_sock,
        ) as mock_conn:
            assert probe_bed(args) is True
        mock_conn.assert_called_once_with(("localhost", 8765), timeout=0.25)

    def test_probe_returns_false_on_connection_refused(self):
        args = _args()
        with patch(
            "empyre.bed_client.socket.create_connection",
            side_effect=ConnectionRefusedError("nope"),
        ):
            assert probe_bed(args) is False

    def test_probe_returns_false_on_timeout(self):
        args = _args()
        with patch(
            "empyre.bed_client.socket.create_connection",
            side_effect=socket.timeout("slow"),
        ):
            assert probe_bed(args) is False

    def test_probe_returns_false_on_gaierror(self):
        args = _args(bed_host="no-such-host.invalid")
        assert probe_bed(args) is False

    def test_probe_uses_args_bed_host_and_port(self):
        args = _args(bed_host="bed.example.com", bed_port=9999)
        fake_sock = MagicMock()
        fake_sock.__enter__ = MagicMock(return_value=fake_sock)
        fake_sock.__exit__ = MagicMock(return_value=False)
        with patch(
            "empyre.bed_client.socket.create_connection",
            return_value=fake_sock,
        ) as mock_conn:
            assert probe_bed(args) is True
        mock_conn.assert_called_once_with(("bed.example.com", 9999), timeout=0.25)

    def test_probe_uses_args_bed_probe_timeout(self):
        args = _args(bed_probe_timeout=1.5)
        fake_sock = MagicMock()
        fake_sock.__enter__ = MagicMock(return_value=fake_sock)
        fake_sock.__exit__ = MagicMock(return_value=False)
        with patch(
            "empyre.bed_client.socket.create_connection",
            return_value=fake_sock,
        ) as mock_conn:
            probe_bed(args)
        mock_conn.assert_called_once_with(("localhost", 8765), timeout=1.5)

    def test_probe_uses_safe_defaults_when_args_missing(self):
        """A bare Namespace (e.g. test fixture) should still probe."""
        bare = argparse.Namespace()
        fake_sock = MagicMock()
        fake_sock.__enter__ = MagicMock(return_value=fake_sock)
        fake_sock.__exit__ = MagicMock(return_value=False)
        with patch(
            "empyre.bed_client.socket.create_connection",
            return_value=fake_sock,
        ) as mock_conn:
            assert probe_bed(bare) is True
        mock_conn.assert_called_once_with(("localhost", 8765), timeout=0.25)


class TestBedConnectionSingleton:
    def test_get_bed_connection_returns_same_instance(self):
        args = _args()
        reset_bed_connection(args)
        a = get_bed_connection(args)
        b = get_bed_connection(args)
        assert a is b
        reset_bed_connection(args)

    def test_different_args_get_different_instances(self):
        a_args = _args(bed_host="a")
        b_args = _args(bed_host="b")
        reset_bed_connection(a_args)
        reset_bed_connection(b_args)
        a = get_bed_connection(a_args)
        b = get_bed_connection(b_args)
        assert a is not b
        reset_bed_connection(a_args)
        reset_bed_connection(b_args)

    def test_reset_bed_connection_drops_cached(self):
        args = _args()
        reset_bed_connection(args)
        a = get_bed_connection(args)
        reset_bed_connection(args)
        b = get_bed_connection(args)
        assert a is not b
        reset_bed_connection(args)


def _mock_websocket(send_log, replies):
    """Build an async-mock websocket that records sends and returns replies.

    send_log: list to which sent messages (decoded) are appended.
    replies: list of reply dicts to be returned (in order) on recv().
    """
    ws = MagicMock()
    ws.send = AsyncMock(
        side_effect=lambda payload: send_log.append(json.loads(payload))
    )
    ws.recv = AsyncMock(side_effect=replies)
    ws.closed = False
    return ws


class TestBedConnectionSend:
    def test_send_injects_request_id_when_missing(self):
        args = _args()
        reset_bed_connection(args)
        conn = get_bed_connection(args)

        send_log = []
        ws = _mock_websocket(send_log, [json.dumps({"type": "pong", "request_id": "r1"})])
        with patch.object(conn, "_connect", AsyncMock(return_value=ws)):
            reply = _run(conn.send({"type": "ping"}))

        assert reply["type"] == "pong"
        assert len(send_log) == 1
        assert send_log[0]["type"] == "ping"
        assert send_log[0]["request_id"].startswith("r")
        reset_bed_connection(args)

    def test_send_preserves_explicit_request_id(self):
        args = _args()
        reset_bed_connection(args)
        conn = get_bed_connection(args)

        send_log = []
        ws = _mock_websocket(
            send_log,
            [json.dumps({"type": "bank_balance_result", "request_id": "abc"})],
        )
        with patch.object(conn, "_connect", AsyncMock(return_value=ws)):
            reply = _run(
                conn.send({"type": "bank_balance", "moniker": "x", "request_id": "abc"})
            )

        assert reply["type"] == "bank_balance_result"
        assert send_log[0]["request_id"] == "abc"
        reset_bed_connection(args)

    def test_send_raises_bed_unavailable_on_connection_refused(self):
        from websockets.exceptions import WebSocketException

        args = _args()
        reset_bed_connection(args)
        conn = get_bed_connection(args)

        with patch.object(
            conn,
            "_connect",
            AsyncMock(side_effect=WebSocketException("refused")),
        ):
            with pytest.raises(BedUnavailable):
                _run(conn.send({"type": "ping", "request_id": "r1"}))
        reset_bed_connection(args)

    def test_send_raises_bed_unavailable_on_timeout(self):
        args = _args()
        reset_bed_connection(args)
        conn = get_bed_connection(args)

        with patch.object(
            conn,
            "_connect",
            AsyncMock(side_effect=asyncio.TimeoutError()),
        ):
            with pytest.raises(BedUnavailable):
                _run(conn.send({"type": "ping", "request_id": "r1"}))
        reset_bed_connection(args)

    def test_send_drops_connection_on_recv_failure(self):
        from websockets.exceptions import ConnectionClosed

        args = _args()
        reset_bed_connection(args)
        conn = get_bed_connection(args)

        # First ws succeeds the connect but recv raises.
        first_ws = MagicMock()
        first_ws.send = AsyncMock()
        first_ws.recv = AsyncMock(side_effect=ConnectionClosed(None, None))
        first_ws.closed = True

        # Second ws (after redial) succeeds.
        second_ws = MagicMock()
        second_ws.send = AsyncMock()
        second_ws.recv = AsyncMock(
            return_value=json.dumps({"type": "pong", "request_id": "r2"})
        )
        second_ws.closed = False

        # Even though recv fails, the first attempt is consumed; verify
        # that the second send reconnects.
        with patch.object(
            conn, "_connect", AsyncMock(side_effect=[first_ws, second_ws])
        ):
            with pytest.raises(BedUnavailable):
                _run(conn.send({"type": "ping", "request_id": "r1"}))
            # The next call should reconnect.
            reply = _run(conn.send({"type": "ping", "request_id": "r2"}))
            assert reply["type"] == "pong"
        reset_bed_connection(args)

    def test_send_raises_bed_unavailable_on_non_json_reply(self):
        args = _args()
        reset_bed_connection(args)
        conn = get_bed_connection(args)

        ws = MagicMock()
        ws.send = AsyncMock()
        ws.recv = AsyncMock(return_value="not json {{{")
        ws.closed = False

        with patch.object(conn, "_connect", AsyncMock(return_value=ws)):
            with pytest.raises(BedUnavailable):
                _run(conn.send({"type": "ping", "request_id": "r1"}))
        reset_bed_connection(args)

    def test_send_warns_on_mismatched_request_id(self):
        args = _args()
        reset_bed_connection(args)
        conn = get_bed_connection(args)

        send_log = []
        ws = _mock_websocket(
            send_log,
            [json.dumps({"type": "pong", "request_id": "different"})],
        )
        with patch.object(conn, "_connect", AsyncMock(return_value=ws)):
            with patch("empyre.bed_client.io.echo") as mock_echo:
                _run(conn.send({"type": "ping", "request_id": "r1"}))
        warn_calls = [c for c in mock_echo.call_args_list if "mismatched" in str(c)]
        assert warn_calls, "expected a warning about mismatched request_id"
        reset_bed_connection(args)


class TestBedConnectionForceClose:
    def test_force_close_drops_cached_websocket(self):
        args = _args()
        reset_bed_connection(args)
        conn = get_bed_connection(args)
        ws = MagicMock()
        ws.close = MagicMock(return_value=None)
        conn._ws = ws

        conn.force_close()

        assert conn._ws is None

    def test_force_close_is_safe_when_no_websocket(self):
        args = _args()
        reset_bed_connection(args)
        conn = get_bed_connection(args)
        conn._ws = None
        # Should not raise.
        conn.force_close()
        assert conn._ws is None

    def test_force_close_handles_async_close(self):
        args = _args()
        reset_bed_connection(args)
        conn = get_bed_connection(args)

        async def _close():
            return None

        ws = MagicMock()
        ws.close = MagicMock(side_effect=lambda: _close())
        conn._ws = ws

        # Should not raise even though close() is a coroutine.
        conn.force_close()
        assert conn._ws is None


class TestBedConnectionRedial:
    def test_send_redials_after_force_close(self):
        args = _args()
        reset_bed_connection(args)
        conn = get_bed_connection(args)

        # First connection is a working ws.
        first = MagicMock()
        first.send = AsyncMock()
        first.recv = AsyncMock(
            return_value=json.dumps({"type": "pong", "request_id": "r1"})
        )
        first.closed = False

        # Then force_close(); next send must reconnect.
        second = MagicMock()
        second.send = AsyncMock()
        second.recv = AsyncMock(
            return_value=json.dumps({"type": "pong", "request_id": "r2"})
        )
        second.closed = False

        connect = AsyncMock(side_effect=[first, second])
        with patch.object(conn, "_connect", connect):
            reply1 = _run(conn.send({"type": "ping", "request_id": "r1"}))
            assert reply1["type"] == "pong"
            conn.force_close()
            reply2 = _run(conn.send({"type": "ping", "request_id": "r2"}))
            assert reply2["type"] == "pong"

        assert connect.call_count == 2
        reset_bed_connection(args)


class TestBedBankClient:
    def test_get_balance_sends_correct_envelope(self):
        args = _args()
        reset_bed_connection(args)
        conn = get_bed_connection(args)

        send_log = []
        ws = _mock_websocket(
            send_log,
            [json.dumps({"type": "bank_balance_result", "balance": 42})],
        )
        client = BedBankClient(args)
        with patch.object(conn, "_connect", AsyncMock(return_value=ws)):
            balance = _run(client.get_balance("alice"))

        assert balance == 42
        assert send_log[0]["type"] == "bank_balance"
        assert send_log[0]["moniker"] == "alice"
        reset_bed_connection(args)

    def test_add_funds_sends_correct_envelope(self):
        args = _args()
        reset_bed_connection(args)
        conn = get_bed_connection(args)

        send_log = []
        ws = _mock_websocket(
            send_log,
            [
                json.dumps(
                    {
                        "type": "bank_add_result",
                        "moniker": "alice",
                        "amount": 100,
                        "new_balance": 250,
                    }
                )
            ],
        )
        client = BedBankClient(args)
        with patch.object(conn, "_connect", AsyncMock(return_value=ws)):
            reply = _run(client.add_funds("alice", 100, description="wage"))

        assert reply["new_balance"] == 250
        assert send_log[0]["type"] == "bank_add"
        assert send_log[0]["moniker"] == "alice"
        assert send_log[0]["amount"] == 100
        assert send_log[0]["description"] == "wage"
        reset_bed_connection(args)

    def test_remove_funds_sends_correct_envelope(self):
        args = _args()
        reset_bed_connection(args)
        conn = get_bed_connection(args)

        send_log = []
        ws = _mock_websocket(
            send_log,
            [
                json.dumps(
                    {
                        "type": "bank_remove_result",
                        "moniker": "alice",
                        "amount": 30,
                        "new_balance": 220,
                    }
                )
            ],
        )
        client = BedBankClient(args)
        with patch.object(conn, "_connect", AsyncMock(return_value=ws)):
            reply = _run(client.remove_funds("alice", 30))

        assert reply["new_balance"] == 220
        assert send_log[0]["type"] == "bank_remove"
        assert send_log[0]["amount"] == 30
        reset_bed_connection(args)

    def test_get_history_sends_correct_envelope(self):
        args = _args()
        reset_bed_connection(args)
        conn = get_bed_connection(args)

        send_log = []
        ws = _mock_websocket(
            send_log,
            [
                json.dumps(
                    {
                        "type": "bank_history_result",
                        "transactions": [
                            {"id": 1, "amount": 10},
                            {"id": 2, "amount": 20},
                        ],
                    }
                )
            ],
        )
        client = BedBankClient(args)
        with patch.object(conn, "_connect", AsyncMock(return_value=ws)):
            history = _run(client.get_history("alice", limit=5))

        assert history == [{"id": 1, "amount": 10}, {"id": 2, "amount": 20}]
        assert send_log[0]["type"] == "bank_history"
        assert send_log[0]["moniker"] == "alice"
        assert send_log[0]["limit"] == 5
        reset_bed_connection(args)

    def test_get_balance_raises_bed_unavailable_on_error_reply(self):
        args = _args()
        reset_bed_connection(args)
        conn = get_bed_connection(args)

        send_log = []
        ws = _mock_websocket(
            send_log,
            [json.dumps({"type": "error", "code": "not_authenticated", "message": "x"})],
        )
        client = BedBankClient(args)
        with patch.object(conn, "_connect", AsyncMock(return_value=ws)):
            with pytest.raises(BedUnavailable):
                _run(client.get_balance("alice"))
        reset_bed_connection(args)

    def test_raises_bed_unavailable_on_transport_failure(self):
        from websockets.exceptions import WebSocketException

        args = _args()
        reset_bed_connection(args)
        conn = get_bed_connection(args)

        client = BedBankClient(args)
        with patch.object(
            conn,
            "_connect",
            AsyncMock(side_effect=WebSocketException("refused")),
        ):
            with pytest.raises(BedUnavailable):
                _run(client.get_balance("alice"))
        reset_bed_connection(args)
