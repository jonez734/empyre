from unittest.mock import patch, MagicMock

import pytest

from empyre.combat.ambushnoble import main


@pytest.fixture
def player():
    p = MagicMock()
    p.moniker = "attacker"
    p.soldiers = 100
    p.nobles = 2
    p.turncount = 0
    p.getresource.return_value = {"emoji": "", "plural": "soldiers"}
    return p


@pytest.fixture
def otherplayer():
    op = MagicMock()
    op.moniker = "defender"
    op.soldiers = 50
    op.nobles = 3
    return op


class TestAmbushNoble:
    def test_returns_false_when_player_missing(self, test_args):
        with patch("empyre.combat.ambushnoble.io.echo"):
            result = main(test_args)
        assert result is False

    def test_returns_true_when_player_has_no_soldiers(self, test_args, player, otherplayer):
        player.soldiers = 0
        with patch("empyre.combat.ambushnoble.util.heading"):
            with patch("empyre.combat.ambushnoble.io.echo") as mock_echo:
                result = main(test_args, player=player, otherplayer=otherplayer)
        assert result is True
        echo_calls = [str(c) for c in mock_echo.call_args_list]
        assert any("no soldiers" in c.lower() for c in echo_calls)

    def test_returns_true_when_opponent_has_few_nobles(self, test_args, player, otherplayer):
        player.soldiers = 100
        otherplayer.nobles = 1
        with patch("empyre.combat.ambushnoble.util.heading"):
            with patch("empyre.combat.ambushnoble.io.echo") as mock_echo:
                result = main(test_args, player=player, otherplayer=otherplayer)
        assert result is True
        echo_calls = [str(c) for c in mock_echo.call_args_list]
        assert any("no nobles" in c.lower() for c in echo_calls)

    def test_returns_true_when_opponent_few_soldiers(self, test_args, player, otherplayer):
        player.soldiers = 100
        player.nobles = 1
        otherplayer.nobles = 2
        otherplayer.soldiers = 10
        with patch("empyre.combat.ambushnoble.util.heading"):
            with patch("empyre.combat.ambushnoble.io.echo"):
                result = main(test_args, player=player, otherplayer=otherplayer)
        assert result is True

    def test_returns_true_when_player_has_no_nobles(self, test_args, player, otherplayer):
        player.nobles = 0
        otherplayer.nobles = 3
        otherplayer.soldiers = 50
        with patch("empyre.combat.ambushnoble.util.heading"):
            with patch("empyre.combat.ambushnoble.io.echo") as mock_echo:
                result = main(test_args, player=player, otherplayer=otherplayer)
        assert result is True
        echo_calls = [str(c) for c in mock_echo.call_args_list]
        assert any("no nobles" in c.lower() for c in echo_calls)

    def test_guards_foil_attack_on_failure(self, test_args, player, otherplayer):
        player.soldiers = 100
        otherplayer.soldiers = 100
        with patch("empyre.combat.ambushnoble.util.heading"):
            with patch("empyre.combat.ambushnoble.io.echo") as mock_echo:
                with patch(
                    "empyre.combat.ambushnoble.random",
                    side_effect=[0.99, 0.01],
                ):
                    result = main(test_args, player=player, otherplayer=otherplayer)

        assert result is True
        echo_calls = [str(c) for c in mock_echo.call_args_list]
        assert any("guards" in c.lower() for c in echo_calls)

    def test_soldiers_reduced_on_defense_failure(self, test_args, player, otherplayer):
        player.soldiers = 100
        otherplayer.soldiers = 100
        with patch("empyre.combat.ambushnoble.util.heading"):
            with patch("empyre.combat.ambushnoble.io.echo"):
                with patch(
                    "empyre.combat.ambushnoble.random",
                    side_effect=[0.01, 0.99],
                ):
                    result = main(test_args, player=player, otherplayer=otherplayer)

        assert result is True
        assert player.soldiers < 100

    def test_calls_adjust_and_save(self, test_args, player, otherplayer):
        player.soldiers = 100
        player.nobles = 1
        otherplayer.soldiers = 100
        with patch("empyre.combat.ambushnoble.util.heading"):
            with patch("empyre.combat.ambushnoble.io.echo"):
                with patch(
                    "empyre.combat.ambushnoble.random",
                    side_effect=[0.99, 0.01],
                ):
                    main(test_args, player=player, otherplayer=otherplayer)
        player.adjust.assert_called()
        player.save.assert_called()