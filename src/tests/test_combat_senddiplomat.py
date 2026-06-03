from unittest.mock import patch, MagicMock

import pytest

from empyre.combat.senddiplomat import main


@pytest.fixture
def player():
    p = MagicMock()
    p.moniker = "attacker"
    p.soldiers = 100
    p.land = 500
    p.diplomats = 1
    p.nobles = 3
    p.getresource.return_value = {"emoji": "", "plural": "land"}
    return p


@pytest.fixture
def otherplayer():
    op = MagicMock()
    op.moniker = "defender"
    op.soldiers = 30
    op.land = 300
    op.nobles = 2
    return op


class TestSendDiplomat:
    def test_returns_false_when_player_missing(self, test_args):
        with patch("empyre.combat.senddiplomat.io.echo"):
            result = main(test_args)
        assert result is False

    def test_returns_true_when_no_diplomats(self, test_args, player, otherplayer):
        player.diplomats = 0
        with patch("empyre.combat.senddiplomat.io.echo") as mock_echo:
            result = main(test_args, player=player, otherplayer=otherplayer)
        assert result is True
        echo_calls = [str(c) for c in mock_echo.call_args_list]
        assert any("no diplomats" in c.lower() for c in echo_calls)

    def test_land_transfer_when_opponent_weak(self, test_args, player, otherplayer):
        player.soldiers = 100
        otherplayer.soldiers = 30
        otherplayer.land = 300
        initial_opponent_land = otherplayer.land

        with patch("empyre.combat.senddiplomat.io.echo") as mock_echo:
            main(test_args, player=player, otherplayer=otherplayer)

        land_transfer = initial_opponent_land // 15
        assert otherplayer.land == initial_opponent_land - land_transfer
        assert player.land == 500 + land_transfer

    def test_noble_beheaded_when_opponent_strong(self, test_args, player, otherplayer):
        player.soldiers = 100
        player.nobles = 3
        otherplayer.soldiers = 200
        otherplayer.land = 300

        with patch("empyre.combat.senddiplomat.io.echo") as mock_echo:
            main(test_args, player=player, otherplayer=otherplayer)

        assert player.nobles == 2
        echo_calls = [str(c) for c in mock_echo.call_args_list]
        assert any("behead" in c.lower() for c in echo_calls)

    def test_calls_adjust_and_save(self, test_args, player, otherplayer):
        otherplayer.soldiers = 30
        otherplayer.land = 300
        with patch("empyre.combat.senddiplomat.io.echo"):
            main(test_args, player=player, otherplayer=otherplayer)
        player.adjust.assert_called()
        player.save.assert_called()
        otherplayer.adjust.assert_called()
        otherplayer.save.assert_called()