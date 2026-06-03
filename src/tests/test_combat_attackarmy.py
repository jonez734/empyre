from unittest.mock import patch, MagicMock

import pytest

from empyre.combat.attackarmy import main


@pytest.fixture
def player():
    p = MagicMock()
    p.moniker = "attacker"
    p.soldiers = 100
    p.land = 500
    p.training = 5
    p.getresource.return_value = {"emoji": "", "plural": "soldiers"}
    return p


@pytest.fixture
def otherplayer():
    op = MagicMock()
    op.moniker = "defender"
    op.soldiers = 80
    op.land = 300
    op.training = 3
    op.getresource.return_value = {"emoji": "", "plural": "soldiers"}
    return op


class TestAttackArmy:
    def test_returns_false_when_player_missing(self, test_args):
        with patch("empyre.combat.attackarmy.io.echo"):
            result = main(test_args)
        assert result is False

    def test_returns_false_when_otherplayer_missing(self, test_args):
        p = MagicMock()
        with patch("empyre.combat.attackarmy.io.echo"):
            result = main(test_args, player=p)
        assert result is False

    def test_breaks_when_player_soldiers_exhausted(self, test_args, player, otherplayer):
        player.soldiers = 0
        with patch("empyre.combat.attackarmy.io.echo") as mock_echo:
            with patch("empyre.combat.attackarmy.random.random", return_value=0.5):
                main(test_args, player=player, otherplayer=otherplayer)
        echo_calls = [str(c) for c in mock_echo.call_args_list]
        assert any("no soldiers" in c.lower() for c in echo_calls)

    def test_breaks_when_otherplayer_soldiers_exhausted(self, test_args, player, otherplayer):
        otherplayer.soldiers = 0
        with patch("empyre.combat.attackarmy.io.echo") as mock_echo:
            with patch("empyre.combat.attackarmy.random.random", return_value=0.5):
                main(test_args, player=player, otherplayer=otherplayer)
        echo_calls = [str(c) for c in mock_echo.call_args_list]
        assert any("opponent" in c.lower() and "soldiers" in c.lower() for c in echo_calls)

    def test_player_wins_captures_land(self, test_args, player, otherplayer):
        player.soldiers = 100
        player.training = 100
        otherplayer.soldiers = 1
        otherplayer.land = 300
        initial_land = otherplayer.land

        with patch("empyre.combat.attackarmy.io.echo"):
            with patch("empyre.combat.attackarmy.random.random", return_value=0.99):
                with patch("empyre.combat.attackarmy.random.randint", return_value=1000):
                    main(test_args, player=player, otherplayer=otherplayer)

        assert otherplayer.land == 0
        assert player.land == 500 + initial_land

    def test_player_loses_soldiers_set_to_zero(self, test_args, player, otherplayer):
        player.soldiers = 1
        player.training = 0
        otherplayer.soldiers = 100
        otherplayer.training = 100
        otherplayer.land = 1000

        with patch("empyre.combat.attackarmy.io.echo"):
            with patch("empyre.combat.attackarmy.random.random", return_value=0.01):
                with patch("empyre.combat.attackarmy.random.randint", return_value=0):
                    main(test_args, player=player, otherplayer=otherplayer)

        assert player.soldiers == 0

    def test_calls_adjust_and_save(self, test_args, player, otherplayer):
        player.soldiers = 1
        otherplayer.soldiers = 1
        with patch("empyre.combat.attackarmy.io.echo"):
            with patch("empyre.combat.attackarmy.random.random", return_value=0.99):
                with patch("empyre.combat.attackarmy.random.randint", return_value=1000):
                    main(test_args, player=player, otherplayer=otherplayer)

        player.adjust.assert_called()
        player.save.assert_called()
        otherplayer.adjust.assert_called()
        otherplayer.save.assert_called()