from unittest.mock import patch, MagicMock

import pytest

from empyre.combat.dragon import main


@pytest.fixture
def player():
    p = MagicMock()
    p.moniker = "dragonlord"
    p.soldiers = 100
    p.dragons = 3
    p.turncount = 0
    p.isdirty = False
    p.getresource.return_value = {"emoji": "", "plural": "dragons"}
    return p


@pytest.fixture
def otherplayer():
    op = MagicMock()
    op.moniker = "victim"
    op.soldiers = 80
    op.grain = 1000
    op.serfs = 500
    op.horses = 50
    op.land = 500
    op.turncount = 0
    op.isdirty = False
    op.getresource.return_value = {"emoji": "", "plural": "land"}
    return op


class TestDragon:
    def test_returns_false_when_player_missing(self, test_args):
        with patch("empyre.combat.dragon.io.echo"):
            result = main(test_args)
        assert result is False

    def test_self_attack_aborts_on_no(self, test_args, player):
        player.moniker = "self"
        with patch("empyre.combat.dragon.io.inputboolean", return_value=False):
            with patch("empyre.combat.dragon.io.echo"):
                result = main(test_args, player=player, otherplayer=player)
        assert result is True
        player.save.assert_not_called()

    def test_negative_dragons_clamped_to_zero(self, test_args, player):
        player.dragons = -1
        with patch("empyre.combat.dragon.io.echo") as mock_echo:
            result = main(test_args, player=player, otherplayer=MagicMock())
        assert result is True
        assert player.dragons == 0

    def test_returns_true_when_no_dragons(self, test_args, player, otherplayer):
        player.dragons = 0
        with patch("empyre.combat.dragon.io.echo") as mock_echo:
            result = main(test_args, player=player, otherplayer=otherplayer)
        assert result is True
        echo_calls = [str(c) for c in mock_echo.call_args_list]
        assert any("dragons" in c.lower() for c in echo_calls)

    def test_declined_unleash_returns_true(self, test_args, player, otherplayer):
        with patch("empyre.combat.dragon.io.echo"):
            with patch("empyre.combat.dragon.io.inputboolean", return_value=False):
                with patch.object(player, "getresource", return_value={"emoji": "", "plural": "dragons"}):
                    result = main(test_args, player=player, otherplayer=otherplayer)
        assert result is True
        otherplayer.save.assert_not_called()

    def test_damages_grain(self, test_args, player, otherplayer):
        otherplayer.grain = 1000
        otherplayer.serfs = 0
        otherplayer.horses = 0
        otherplayer.land = 0

        with patch("empyre.combat.dragon.io.echo"):
            with patch("empyre.combat.dragon.io.inputboolean", return_value=True):
                with patch.object(player, "getresource", return_value={"emoji": "", "plural": "grain"}):
                    with patch("empyre.combat.dragon.util.diceroll", side_effect=[100, 0, 0, 0]):
                        with patch.object(player, "adjust"):
                            with patch.object(player, "save"):
                                with patch.object(otherplayer, "adjust"):
                                    with patch.object(otherplayer, "save"):
                                        result = main(test_args, player=player, otherplayer=otherplayer)

        assert result is True
        assert otherplayer.grain == 900

    def test_damages_serfs(self, test_args, player, otherplayer):
        otherplayer.grain = 0
        otherplayer.serfs = 500
        otherplayer.horses = 0
        otherplayer.land = 0

        with patch("empyre.combat.dragon.io.echo"):
            with patch("empyre.combat.dragon.io.inputboolean", return_value=True):
                with patch.object(player, "getresource", return_value={"emoji": "", "plural": "serfs"}):
                    with patch("empyre.combat.dragon.util.diceroll", side_effect=[0, 50, 0, 0]):
                        with patch.object(player, "adjust"):
                            with patch.object(player, "save"):
                                with patch.object(otherplayer, "adjust"):
                                    with patch.object(otherplayer, "save"):
                                        result = main(test_args, player=player, otherplayer=otherplayer)

        assert result is True
        assert otherplayer.serfs == 450

    def test_damages_horses(self, test_args, player, otherplayer):
        otherplayer.grain = 0
        otherplayer.serfs = 0
        otherplayer.horses = 50
        otherplayer.land = 0

        with patch("empyre.combat.dragon.io.echo"):
            with patch("empyre.combat.dragon.io.inputboolean", return_value=True):
                with patch.object(player, "getresource", return_value={"emoji": "", "plural": "horses"}):
                    with patch("empyre.combat.dragon.util.diceroll", side_effect=[0, 0, 5, 0]):
                        with patch.object(player, "adjust"):
                            with patch.object(player, "save"):
                                with patch.object(otherplayer, "adjust"):
                                    with patch.object(otherplayer, "save"):
                                        result = main(test_args, player=player, otherplayer=otherplayer)

        assert result is True
        assert otherplayer.horses == 45

    def test_damages_land(self, test_args, player, otherplayer):
        otherplayer.grain = 0
        otherplayer.serfs = 0
        otherplayer.horses = 0
        otherplayer.land = 500

        with patch("empyre.combat.dragon.io.echo"):
            with patch("empyre.combat.dragon.io.inputboolean", return_value=True):
                with patch.object(player, "getresource", return_value={"emoji": "", "plural": "acres"}):
                    with patch("empyre.combat.dragon.util.diceroll", side_effect=[0, 0, 0, 50]):
                        with patch.object(player, "adjust"):
                            with patch.object(player, "save"):
                                with patch.object(otherplayer, "adjust"):
                                    with patch.object(otherplayer, "save"):
                                        result = main(test_args, player=player, otherplayer=otherplayer)

        assert result is True
        assert otherplayer.land == 450

    def test_no_damage_message_when_all_zero(self, test_args, player, otherplayer):
        otherplayer.grain = 0
        otherplayer.serfs = 0
        otherplayer.horses = 0
        otherplayer.land = 0

        with patch("empyre.combat.dragon.io.echo") as mock_echo:
            with patch("empyre.combat.dragon.io.inputboolean", return_value=True):
                with patch.object(player, "getresource", return_value={"emoji": "", "plural": "dragons"}):
                    with patch("empyre.combat.dragon.util.diceroll", return_value=0):
                        with patch.object(player, "adjust"):
                            with patch.object(player, "save"):
                                with patch.object(otherplayer, "adjust"):
                                    with patch.object(otherplayer, "save"):
                                        result = main(test_args, player=player, otherplayer=otherplayer)

        assert result is True
        echo_calls = [str(c) for c in mock_echo.call_args_list]
        assert any("did not" in c.lower() or "no damage" in c.lower() for c in echo_calls)

    def test_calls_adjust_and_save(self, test_args, player, otherplayer):
        otherplayer.grain = 0
        otherplayer.serfs = 0
        otherplayer.horses = 0
        otherplayer.land = 0

        with patch("empyre.combat.dragon.io.echo"):
            with patch("empyre.combat.dragon.io.inputboolean", return_value=True):
                with patch.object(player, "getresource", return_value={"emoji": "", "plural": "dragons"}):
                    with patch("empyre.combat.dragon.util.diceroll", return_value=0):
                        with patch.object(player, "adjust"):
                            with patch.object(player, "save"):
                                with patch.object(otherplayer, "adjust"):
                                    with patch.object(otherplayer, "save"):
                                        main(test_args, player=player, otherplayer=otherplayer)
        player.adjust.assert_called()
        player.save.assert_called()
        otherplayer.adjust.assert_called()
        otherplayer.save.assert_called()