"""End-to-end smoke test against a live bed daemon.

Skipped unless bed is reachable at 127.0.0.1:8765. Exercises the
real wire protocol through:

  - empyre.bed_client.BedConnection (singleton)
  - empyre.bed_client.BedBankClient
  - empyre.services.player.PlayerService (bed-mode branch)

Pattern: a module-level probe runs once; if bed is down the entire
module is skipped. No long-lived state is kept between tests.
"""

import argparse
import asyncio
import socket
import uuid

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


BED_HOST = "127.0.0.1"
BED_PORT = 8765
PROBE_TIMEOUT = 0.5


def _args(**kw):
    base = dict(
        bed_host=BED_HOST,
        bed_port=BED_PORT,
        bed_path="/",
        bed_probe_timeout=PROBE_TIMEOUT,
        bed_call_timeout=5.0,
    )
    base.update(kw)
    return argparse.Namespace(**base)


def _is_bed_reachable():
    try:
        with socket.create_connection(
            (BED_HOST, BED_PORT), timeout=PROBE_TIMEOUT
        ):
            return True
    except (OSError, socket.timeout):
        return False


pytestmark = pytest.mark.skipif(
    not _is_bed_reachable(),
    reason=f"bed not reachable at {BED_HOST}:{BED_PORT}",
)


@pytest.fixture
def args():
    return _args()


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@pytest.fixture
def fresh_connection(args):
    """Yield a freshly-reset BedConnection for the test, then close."""
    reset_bed_connection(args)
    conn = get_bed_connection(args)
    yield conn
    conn.force_close()
    reset_bed_connection(args)


class TestPingPong:
    def test_ping_pong(self, fresh_connection, args):
        reply = _run(fresh_connection.send({"type": "ping"}))
        assert reply["type"] == "pong"


class TestBankRoundTrip:
    def test_get_balance_returns_int(self, fresh_connection, args):
        # We don't have a known player pre-set up; this is just a
        # wire-shape check. The test asserts the reply is well-formed
        # JSON with a "balance" field that can be coerced to int.
        client = BedBankClient(args)
        try:
            balance = _run(client.get_balance("empyre_e2e_smoke"))
        except BedUnavailable as exc:
            pytest.skip(f"bed rejected query: {exc}")
        # The exact value doesn't matter for a smoke test; we just
        # want the round-trip to succeed and return an int.
        assert isinstance(balance, int)
        assert balance >= 0
