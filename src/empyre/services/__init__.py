"""empyre.services — domain service layer.

The :class:`empyre.services.player.PlayerService` is the only place
empyre touches the empyre.player + engine.member tables for
load, auth, profile, and history. It owns the bed-fallback decision
so the rest of the game (AuthService, BankServiceHandler, the
door-mode TUI, the future thin-client) doesn't have to think about
it.
"""

from .player import (
    PlayerService,
    PlayerCredentials,
    PlayerServiceUnavailable,
)

__all__ = [
    "PlayerService",
    "PlayerCredentials",
    "PlayerServiceUnavailable",
]
