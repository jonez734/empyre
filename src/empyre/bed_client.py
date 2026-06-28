"""Bed WebSocket client for empyre.

Re-export shim. The actual transport lives in :mod:`bed.client` so
empyre and casino can share a single implementation. The
``BedBankClient`` message-family wrapper now lives in
:mod:`bed.client.bank`; import it directly from there.
"""

from __future__ import annotations

from bed.client import (
    BedConnection,
    BedUnavailable,
    get_bed_connection,
    probe_bed,
    reset_bed_connection,
)


class _RequestId:
    """Backwards-compatible alias. New code should import from bed.client."""

    def __init__(self) -> None:
        from bed.client.connection import _RequestId as _BedRequestId

        self._inner = _BedRequestId()

    def next(self) -> str:
        return self._inner.next()
