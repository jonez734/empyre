from unittest.mock import patch, MagicMock

from empyre.combat import lib


class TestCombatLib:
    def test_runmodule_delegates_to_libempyre_with_combat_prefix(self, test_args):
        with patch("empyre.combat.lib.libempyre.runmodule") as mock_run:
            mock_run.return_value = True
            result = lib.runmodule(test_args, "attackarmy")
            mock_run.assert_called_once_with(test_args, "combat.attackarmy")
            assert result is True

    def test_runmodule_passes_kwargs_through(self, test_args):
        mock_player = MagicMock()
        mock_otherplayer = MagicMock()
        with patch("empyre.combat.lib.libempyre.runmodule") as mock_run:
            mock_run.return_value = True
            lib.runmodule(
                test_args,
                "joust",
                player=mock_player,
                otherplayer=mock_otherplayer,
            )
            _, kwargs = mock_run.call_args
            assert kwargs["player"] is mock_player
            assert kwargs["otherplayer"] is mock_otherplayer