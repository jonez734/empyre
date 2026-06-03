from unittest.mock import patch, MagicMock

import pytest

from empyre.combat.joust import main


@pytest.fixture
def player():
    p = MagicMock()
    p.moniker = "challenger"
    p.soldiers = 100
    p.land = 1000
    p.nobles = 3
    p.horses = 5
    p.serfs = 1000
    p.coins = 500
    p.grain = 5000
    p.shipyards = 1
    p.turncount = 0
    p.isdirty = False
    p.getresource.return_value = {"emoji": "", "plural": "land"}
    return p


@pytest.fixture
def otherplayer():
    op = MagicMock()
    op.moniker = "opponent"
    op.soldiers = 80
    op.land = 500
    op.nobles = 2
    op.turncount = 0
    op.isdirty = False
    op.getresource.return_value = {"emoji": "", "plural": "land"}
    return op


class TestJoust:
    def test_returns_false_when_player_missing(self, test_args):
        with patch("empyre.combat.joust.io.echo"):
            result = main(test_args)
        assert result is False

    def test_self_joust_decline_aborts(self, test_args, player):
        with patch("empyre.combat.joust.io.inputboolean", return_value=False):
            with patch("empyre.combat.joust.io.echo"):
                result = main(test_args, player=player, otherplayer=player)
        assert result is True
        player.save.assert_not_called()

    def test_self_joust_confirm_costs_land(self, test_args, player):
        player.land = 1000
        with patch("empyre.combat.joust.io.inputboolean", return_value=True):
            with patch("empyre.combat.joust.io.echo"):
                with patch("empyre.combat.joust.util.diceroll", return_value=50):
                    with patch.object(player, "adjust"):
                        with patch.object(player, "save"):
                            result = main(test_args, player=player, otherplayer=player)
        assert result is True
        assert player.land == 950

    def test_returns_true_when_no_horses(self, test_args, player, otherplayer):
        player.horses = 0
        with patch("empyre.combat.joust.io.echo") as mock_echo:
            with patch("empyre.combat.joust.libempyre.setbottombar"):
                result = main(test_args, player=player, otherplayer=otherplayer)
        assert result is True
        echo_calls = [str(c) for c in mock_echo.call_args_list]
        assert any("horse" in c.lower() for c in echo_calls)

    def test_returns_true_when_insufficient_serfs(self, test_args, player, otherplayer):
        player.serfs = 500
        with patch("empyre.combat.joust.io.echo") as mock_echo:
            with patch("empyre.combat.joust.libempyre.setbottombar"):
                result = main(test_args, player=player, otherplayer=otherplayer)
        assert result is True
        echo_calls = [str(c) for c in mock_echo.call_args_list]
        assert any("serfs" in c.lower() for c in echo_calls)

    def test_returns_true_when_opponent_insufficient_nobles(self, test_args, player, otherplayer):
        otherplayer.nobles = 1
        with patch("empyre.combat.joust.io.echo") as mock_echo:
            with patch("empyre.combat.joust.libempyre.setbottombar"):
                result = main(test_args, player=player, otherplayer=otherplayer)
        assert result is True
        echo_calls = [str(c) for c in mock_echo.call_args_list]
        assert any("nobles" in c.lower() for c in echo_calls)

    def test_overwhelming_advantage_gains_noble(self, test_args, player, otherplayer):
        player.nobles = 5
        otherplayer.nobles = 2
        with patch("empyre.combat.joust.io.echo"):
            with patch("empyre.combat.joust.libempyre.setbottombar"):
                with patch("empyre.combat.joust.libempyre.newsentry"):
                    with patch.object(player, "adjust"):
                        with patch.object(player, "save"):
                            with patch.object(otherplayer, "adjust"):
                                with patch.object(otherplayer, "save"):
                                    result = main(test_args, player=player, otherplayer=otherplayer)
        assert result is True
        assert player.nobles == 6
        assert otherplayer.nobles == 1

    def test_overwhelming_advantage_calls_newsentry(self, test_args, player, otherplayer):
        player.nobles = 5
        otherplayer.nobles = 2
        with patch("empyre.combat.joust.io.echo"):
            with patch("empyre.combat.joust.libempyre.setbottombar"):
                with patch("empyre.combat.joust.libempyre.newsentry") as mock_news:
                    with patch.object(player, "adjust"):
                        with patch.object(player, "save"):
                            with patch.object(otherplayer, "adjust"):
                                with patch.object(otherplayer, "save"):
                                    main(test_args, player=player, otherplayer=otherplayer)
        mock_news.assert_called_once()

    def test_dice_1_gains_100_acres(self, test_args, player, otherplayer):
        player.land = 500
        with patch("empyre.combat.joust.io.echo"):
            with patch("empyre.combat.joust.libempyre.setbottombar"):
                with patch("empyre.combat.joust.util.diceroll", return_value=1):
                    with patch.object(player, "adjust"):
                        with patch.object(player, "save"):
                            with patch.object(otherplayer, "adjust"):
                                with patch.object(otherplayer, "save"):
                                    main(test_args, player=player, otherplayer=otherplayer)
        assert player.land == 600

    def test_dice_2_loses_100_acres(self, test_args, player, otherplayer):
        player.land = 500
        with patch("empyre.combat.joust.io.echo"):
            with patch("empyre.combat.joust.libempyre.setbottombar"):
                with patch("empyre.combat.joust.util.diceroll", return_value=2):
                    with patch.object(player, "adjust"):
                        with patch.object(player, "save"):
                            with patch.object(otherplayer, "adjust"):
                                with patch.object(otherplayer, "save"):
                                    main(test_args, player=player, otherplayer=otherplayer)
        assert player.land == 400

    def test_dice_3_gains_1000_coins(self, test_args, player, otherplayer):
        player.coins = 0
        with patch("empyre.combat.joust.io.echo"):
            with patch("empyre.combat.joust.libempyre.setbottombar"):
                with patch("empyre.combat.joust.util.diceroll", return_value=3):
                    with patch.object(player, "adjust"):
                        with patch.object(player, "save"):
                            with patch.object(otherplayer, "adjust"):
                                with patch.object(otherplayer, "save"):
                                    main(test_args, player=player, otherplayer=otherplayer)
        assert player.coins == 1000

    def test_dice_4_loses_1000_coins(self, test_args, player, otherplayer):
        player.coins = 5000
        with patch("empyre.combat.joust.io.echo"):
            with patch("empyre.combat.joust.libempyre.setbottombar"):
                with patch("empyre.combat.joust.util.diceroll", return_value=4):
                    with patch.object(player, "adjust"):
                        with patch.object(player, "save"):
                            with patch.object(otherplayer, "adjust"):
                                with patch.object(otherplayer, "save"):
                                    main(test_args, player=player, otherplayer=otherplayer)
        assert player.coins == 4000

    def test_dice_5_gains_1_noble(self, test_args, player, otherplayer):
        player.nobles = 2
        with patch("empyre.combat.joust.io.echo"):
            with patch("empyre.combat.joust.libempyre.setbottombar"):
                with patch("empyre.combat.joust.util.diceroll", return_value=5):
                    with patch.object(player, "adjust"):
                        with patch.object(player, "save"):
                            with patch.object(otherplayer, "adjust"):
                                with patch.object(otherplayer, "save"):
                                    main(test_args, player=player, otherplayer=otherplayer)
        assert player.nobles == 3

    def test_dice_6_loses_1_noble(self, test_args, player, otherplayer):
        player.nobles = 3
        with patch("empyre.combat.joust.io.echo"):
            with patch("empyre.combat.joust.libempyre.setbottombar"):
                with patch("empyre.combat.joust.util.diceroll", return_value=6):
                    with patch.object(player, "adjust"):
                        with patch.object(player, "save"):
                            with patch.object(otherplayer, "adjust"):
                                with patch.object(otherplayer, "save"):
                                    main(test_args, player=player, otherplayer=otherplayer)
        assert player.nobles == 2

    def test_dice_7_gains_7000_bushels(self, test_args, player, otherplayer):
        player.grain = 0
        with patch("empyre.combat.joust.io.echo"):
            with patch("empyre.combat.joust.libempyre.setbottombar"):
                with patch("empyre.combat.joust.util.diceroll", return_value=7):
                    with patch.object(player, "adjust"):
                        with patch.object(player, "save"):
                            with patch.object(otherplayer, "adjust"):
                                with patch.object(otherplayer, "save"):
                                    main(test_args, player=player, otherplayer=otherplayer)
        assert player.grain == 7000

    def test_dice_8_loses_7000_bushels(self, test_args, player, otherplayer):
        player.grain = 10000
        with patch("empyre.combat.joust.io.echo"):
            with patch("empyre.combat.joust.libempyre.setbottombar"):
                with patch("empyre.combat.joust.util.diceroll", return_value=8):
                    with patch.object(player, "adjust"):
                        with patch.object(player, "save"):
                            with patch.object(otherplayer, "adjust"):
                                with patch.object(otherplayer, "save"):
                                    main(test_args, player=player, otherplayer=otherplayer)
        assert player.grain == 3000

    def test_dice_9_gains_shipyard_and_100_acres(self, test_args, player, otherplayer):
        player.shipyards = 0
        player.land = 500
        with patch("empyre.combat.joust.io.echo"):
            with patch("empyre.combat.joust.libempyre.setbottombar"):
                with patch("empyre.combat.joust.util.diceroll", return_value=9):
                    with patch.object(player, "adjust"):
                        with patch.object(player, "save"):
                            with patch.object(otherplayer, "adjust"):
                                with patch.object(otherplayer, "save"):
                                    main(test_args, player=player, otherplayer=otherplayer)
        assert player.shipyards == 1
        assert player.land == 600

    def test_dice_10_loses_shipyard_and_100_acres(self, test_args, player, otherplayer):
        player.shipyards = 2
        player.land = 500
        with patch("empyre.combat.joust.io.echo"):
            with patch("empyre.combat.joust.libempyre.setbottombar"):
                with patch("empyre.combat.joust.util.diceroll", return_value=10):
                    with patch.object(player, "adjust"):
                        with patch.object(player, "save"):
                            with patch.object(otherplayer, "adjust"):
                                with patch.object(otherplayer, "save"):
                                    main(test_args, player=player, otherplayer=otherplayer)
        assert player.shipyards == 1
        assert player.land == 400

    def test_calls_adjust_and_save(self, test_args, player, otherplayer):
        player.nobles = 5
        otherplayer.nobles = 2
        with patch("empyre.combat.joust.io.echo"):
            with patch("empyre.combat.joust.libempyre.setbottombar"):
                with patch("empyre.combat.joust.libempyre.newsentry"):
                    with patch.object(player, "adjust"):
                        with patch.object(player, "save"):
                            with patch.object(otherplayer, "adjust"):
                                with patch.object(otherplayer, "save"):
                                    main(test_args, player=player, otherplayer=otherplayer)
        player.adjust.assert_called()
        player.save.assert_called()
        otherplayer.adjust.assert_called()
        otherplayer.save.assert_called()