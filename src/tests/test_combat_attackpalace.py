from unittest.mock import patch, MagicMock

import pytest

from empyre.combat.attackpalace import main


@pytest.fixture
def player():
    p = MagicMock()
    p.moniker = "attacker"
    p.soldiers = 100
    p.palaces = 1
    p.getresource.return_value = {"emoji": "", "plural": "soldiers"}
    return p


@pytest.fixture
def otherplayer():
    op = MagicMock()
    op.moniker = "defender"
    op.soldiers = 80
    op.palaces = 2
    op.nobles = 3
    op.getresource.return_value = {"emoji": "", "plural": "soldiers"}
    return op


class TestAttackPalace:
    def test_returns_true_when_opponent_has_no_palaces(self, test_args, player, otherplayer):
        otherplayer.palaces = 0
        with patch("empyre.combat.attackpalace.io.echo") as mock_echo:
            result = main(test_args, player=player, otherplayer=otherplayer)
        assert result is True
        echo_calls = [str(c) for c in mock_echo.call_args_list]
        assert any("no palaces" in c.lower() for c in echo_calls)

    def test_returns_true_when_player_has_no_soldiers(self, test_args, player, otherplayer):
        player.soldiers = 0
        with patch("empyre.combat.attackpalace.io.echo") as mock_echo:
            result = main(test_args, player=player, otherplayer=otherplayer)
        assert result is True
        echo_calls = [str(c) for c in mock_echo.call_args_list]
        assert any("no soldiers" in c.lower() for c in echo_calls)

    def test_guards_thwart_attack_on_failure(self, test_args, player, otherplayer):
        player.soldiers = 30
        otherplayer.soldiers = 10

        with patch("empyre.combat.attackpalace.io.echo") as mock_echo:
            with patch(
                "empyre.combat.attackpalace.random.random",
                side_effect=[1.0, 1.0],
            ):
                with patch("empyre.combat.attackpalace.random.randint", return_value=2):
                    result = main(test_args, player=player, otherplayer=otherplayer)

        assert result is True
        echo_calls = [str(c) for c in mock_echo.call_args_list]
        assert any("guards" in c.lower() for c in echo_calls)
        assert player.soldiers == 28

    def test_success_destroys_palace_and_resets_soldiers(self, test_args, player, otherplayer):
        player.soldiers = 100
        otherplayer.soldiers = 50
        otherplayer.palaces = 2
        otherplayer.nobles = 3
        initial_nobles = otherplayer.nobles

        with patch("empyre.combat.attackpalace.io.echo"):
            with patch(
                "empyre.combat.attackpalace.random.random",
                side_effect=[0.01, 0.01],
            ):
                with patch("empyre.combat.attackpalace.random.randint", return_value=5):
                    result = main(test_args, player=player, otherplayer=otherplayer)

        assert result is True
        assert otherplayer.palaces == 1
        assert otherplayer.nobles == initial_nobles + 1

    def test_success_resets_soldiers_to_nobles_times_20(self, test_args, player, otherplayer):
        player.soldiers = 100
        otherplayer.soldiers = 500
        otherplayer.palaces = 1
        otherplayer.nobles = 5

        with patch("empyre.combat.attackpalace.io.echo"):
            with patch(
                "empyre.combat.attackpalace.random.random",
                side_effect=[0.01, 0.01],
            ):
                with patch("empyre.combat.attackpalace.random.randint", return_value=5):
                    result = main(test_args, player=player, otherplayer=otherplayer)

        assert result is True
        assert otherplayer.soldiers == 5 * 20

    def test_success_reduces_player_soldiers_by_half(self, test_args, player, otherplayer):
        player.soldiers = 100
        otherplayer.soldiers = 50
        otherplayer.palaces = 1
        otherplayer.nobles = 1

        with patch("empyre.combat.attackpalace.io.echo"):
            with patch(
                "empyre.combat.attackpalace.random.random",
                side_effect=[0.01, 0.01],
            ):
                with patch("empyre.combat.attackpalace.random.randint", return_value=50):
                    result = main(test_args, player=player, otherplayer=otherplayer)

        assert result is True
        assert player.soldiers == 50