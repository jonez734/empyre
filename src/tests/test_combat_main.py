from unittest.mock import patch, MagicMock

import pytest

from empyre.combat.main import main


@pytest.fixture
def mock_player():
    p = MagicMock()
    p.moniker = "attacker"
    p.soldiers = 100
    p.land = 500
    p.nobles = 3
    p.training = 5
    p.resources = {}
    p.attributes = {}
    p.turncount = 0
    p.isdirty = False
    p.getresource.return_value = {"emoji": "", "plural": "soldiers"}
    return p


@pytest.fixture
def mock_otherplayer():
    op = MagicMock()
    op.moniker = "defender"
    op.soldiers = 80
    op.land = 300
    op.nobles = 2
    op.training = 3
    op.resources = {}
    op.attributes = {}
    op.turncount = 0
    op.isdirty = False
    op.getresource.return_value = {"emoji": "", "plural": "soldiers"}
    return op


class TestCombatMain:
    def test_selects_opponent_then_exits_on_q(self, test_args, mock_player, mock_otherplayer):
        with patch("empyre.combat.main.libplayer.select", return_value=mock_otherplayer):
            with patch("empyre.combat.main.io.inputchar", return_value="Q"):
                with patch("empyre.combat.main.io.echo"):
                    with patch("empyre.combat.main.util.heading"):
                        with patch("empyre.combat.main.lib.runmodule"):
                            with patch.object(mock_player, "adjust"):
                                with patch.object(mock_player, "save"):
                                    with patch.object(mock_otherplayer, "adjust"):
                                        with patch.object(mock_otherplayer, "save"):
                                            with patch("empyre.combat.main.libempyre.setbottombar"):
                                                result = main(test_args, player=mock_player)

        assert result is None

    def test_routes_to_attackarmy_on_key_1(self, test_args, mock_player, mock_otherplayer):
        with patch("empyre.combat.main.libplayer.select", return_value=mock_otherplayer):
            with patch("empyre.combat.main.io.inputchar", return_value="1"):
                with patch("empyre.combat.main.io.echo"):
                    with patch("empyre.combat.main.util.heading"):
                        with patch("empyre.combat.main.lib.runmodule") as mock_rm:
                            mock_rm.return_value = True
                            with patch.object(mock_player, "adjust"):
                                with patch.object(mock_player, "save"):
                                    with patch.object(mock_otherplayer, "adjust"):
                                        with patch.object(mock_otherplayer, "save"):
                                            with patch("empyre.combat.main.libempyre.setbottombar"):
                                                main(test_args, player=mock_player)
                            mock_rm.assert_called_once_with(
                                test_args,
                                "attackarmy",
                                otherplayer=mock_otherplayer,
                                player=mock_player,
                            )

    def test_routes_to_attackpalace_on_key_2(self, test_args, mock_player, mock_otherplayer):
        with patch("empyre.combat.main.libplayer.select", return_value=mock_otherplayer):
            with patch("empyre.combat.main.io.inputchar", return_value="2"):
                with patch("empyre.combat.main.io.echo"):
                    with patch("empyre.combat.main.util.heading"):
                        with patch("empyre.combat.main.lib.runmodule") as mock_rm:
                            mock_rm.return_value = True
                            with patch.object(mock_player, "adjust"):
                                with patch.object(mock_player, "save"):
                                    with patch.object(mock_otherplayer, "adjust"):
                                        with patch.object(mock_otherplayer, "save"):
                                            with patch("empyre.combat.main.libempyre.setbottombar"):
                                                main(test_args, player=mock_player)
                            mock_rm.assert_called_once_with(
                                test_args,
                                "attackpalace",
                                otherplayer=mock_otherplayer,
                                player=mock_player,
                            )

    def test_routes_to_senddiplomat_on_key_4(self, test_args, mock_player, mock_otherplayer):
        with patch("empyre.combat.main.libplayer.select", return_value=mock_otherplayer):
            with patch("empyre.combat.main.io.inputchar", return_value="4"):
                with patch("empyre.combat.main.io.echo"):
                    with patch("empyre.combat.main.util.heading"):
                        with patch("empyre.combat.main.lib.runmodule") as mock_rm:
                            mock_rm.return_value = True
                            with patch.object(mock_player, "adjust"):
                                with patch.object(mock_player, "save"):
                                    with patch.object(mock_otherplayer, "adjust"):
                                        with patch.object(mock_otherplayer, "save"):
                                            with patch("empyre.combat.main.libempyre.setbottombar"):
                                                main(test_args, player=mock_player)
                            mock_rm.assert_called_once_with(
                                test_args,
                                "senddiplomat",
                                otherplayer=mock_otherplayer,
                                player=mock_player,
                            )

    def test_routes_to_joust_on_key_5(self, test_args, mock_player, mock_otherplayer):
        with patch("empyre.combat.main.libplayer.select", return_value=mock_otherplayer):
            with patch("empyre.combat.main.io.inputchar", return_value="5"):
                with patch("empyre.combat.main.io.echo"):
                    with patch("empyre.combat.main.util.heading"):
                        with patch("empyre.combat.main.lib.runmodule") as mock_rm:
                            mock_rm.return_value = True
                            with patch.object(mock_player, "adjust"):
                                with patch.object(mock_player, "save"):
                                    with patch.object(mock_otherplayer, "adjust"):
                                        with patch.object(mock_otherplayer, "save"):
                                            with patch("empyre.combat.main.libempyre.setbottombar"):
                                                main(test_args, player=mock_player)
                            mock_rm.assert_called_once_with(
                                test_args,
                                "joust",
                                otherplayer=mock_otherplayer,
                                player=mock_player,
                            )

    def test_key_3_attacknobles_calls_missing_module(self, test_args, mock_player, mock_otherplayer):
        with patch("empyre.combat.main.libplayer.select", return_value=mock_otherplayer):
            with patch("empyre.combat.main.io.inputchar", return_value="3"):
                with patch("empyre.combat.main.io.echo") as mock_echo:
                    with patch("empyre.combat.main.util.heading"):
                        with patch("empyre.combat.main.lib.runmodule") as mock_rm:
                            mock_rm.return_value = False
                            with patch.object(mock_player, "adjust"):
                                with patch.object(mock_player, "save"):
                                    with patch.object(mock_otherplayer, "adjust"):
                                        with patch.object(mock_otherplayer, "save"):
                                            with patch("empyre.combat.main.libempyre.setbottombar"):
                                                main(test_args, player=mock_player)
                            mock_rm.assert_called_once_with(
                                test_args,
                                "attacknobles",
                                otherplayer=mock_otherplayer,
                                player=mock_player,
                            )
                            echo_calls = [str(c) for c in mock_echo.call_args_list]
                            assert any("Attack Nobles" in c for c in echo_calls)

    def test_self_attack_aborts_when_confirmed_no(self, test_args, mock_player):
        mock_player.moniker = "self"

        with patch("empyre.combat.main.libplayer.select", return_value=mock_player):
            with patch("empyre.combat.main.io.inputboolean", return_value=False):
                with patch("empyre.combat.main.io.echo") as mock_echo:
                    with patch("empyre.combat.main.util.heading"):
                        with patch("empyre.combat.main.lib.runmodule") as mock_rm:
                            with patch.object(mock_player, "adjust"):
                                with patch.object(mock_player, "save"):
                                    with patch("empyre.combat.main.libempyre.setbottombar"):
                                        result = main(test_args, player=mock_player)

                            mock_rm.assert_not_called()
                            echo_calls = [str(c) for c in mock_echo.call_args_list]
                            assert any("aborted" in c.lower() for c in echo_calls)

    def test_returns_none_when_no_opponent_selected(self, test_args, mock_player):
        with patch("empyre.combat.main.libplayer.select", return_value=None):
            with patch("empyre.combat.main.io.echo") as mock_echo:
                with patch("empyre.combat.main.libempyre.setbottombar"):
                    result = main(test_args, player=mock_player)

        assert result is None
        echo_calls = [str(c) for c in mock_echo.call_args_list]
        assert any("no attack" in c.lower() for c in echo_calls)

    def test_returns_false_when_select_fails(self, test_args, mock_player):
        with patch("empyre.combat.main.libplayer.select", return_value=False):
            with patch("empyre.combat.main.io.echo") as mock_echo:
                with patch("empyre.combat.main.libempyre.setbottombar"):
                    result = main(test_args, player=mock_player)

        assert result is False
        echo_calls = [str(c) for c in mock_echo.call_args_list]
        assert any("failed" in c.lower() for c in echo_calls)

    def test_quits_on_key_6(self, test_args, mock_player, mock_otherplayer):
        with patch("empyre.combat.main.libplayer.select", return_value=mock_otherplayer):
            with patch("empyre.combat.main.io.inputchar", return_value="6"):
                with patch("empyre.combat.main.io.echo"):
                    with patch("empyre.combat.main.util.heading"):
                        with patch("empyre.combat.main.lib.runmodule"):
                            with patch.object(mock_player, "adjust"):
                                with patch.object(mock_player, "save"):
                                    with patch.object(mock_otherplayer, "adjust"):
                                        with patch.object(mock_otherplayer, "save"):
                                            with patch("empyre.combat.main.libempyre.setbottombar"):
                                                result = main(test_args, player=mock_player)
        assert result is None

    def test_shows_help_on_question_mark(self, test_args, mock_player, mock_otherplayer):
        call_sequence = ["?", "Q"]

        with patch("empyre.combat.main.libplayer.select", return_value=mock_otherplayer):
            with patch("empyre.combat.main.io.inputchar", side_effect=call_sequence):
                with patch("empyre.combat.main.io.echo"):
                    with patch("empyre.combat.main.util.heading"):
                        with patch("empyre.combat.main.lib.runmodule"):
                            with patch.object(mock_player, "adjust"):
                                with patch.object(mock_player, "save"):
                                    with patch.object(mock_otherplayer, "adjust"):
                                        with patch.object(mock_otherplayer, "save"):
                                            with patch("empyre.combat.main.libempyre.setbottombar"):
                                                main(test_args, player=mock_player)