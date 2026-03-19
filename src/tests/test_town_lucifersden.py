from unittest.mock import patch

from empyre.town import lucifersden


class DummyPlayer:
    def __init__(self, coins=1000, serfs=2000, land=5000):
        self.coins = coins
        self.serfs = serfs
        self.land = land


class TestLucifersDen:
    def test_returns_early_when_player_has_too_many_coins(self, test_args):
        player = DummyPlayer(coins=15000, serfs=2000, land=5000)
        result = lucifersden.main(test_args, player=player)
        assert result is True

    def test_returns_early_when_player_has_too_much_land(self, test_args):
        player = DummyPlayer(coins=1000, serfs=2000, land=20000)
        result = lucifersden.main(test_args, player=player)
        assert result is True

    def test_returns_false_when_player_is_none(self, test_args):
        result = lucifersden.main(test_args)
        assert result is False

    def test_player_declines_to_gamble(self, test_args):
        player = DummyPlayer(coins=5000, serfs=2000, land=5000)
        with patch("empyre.town.lucifersden.lib.setbottombar"):
            with patch("empyre.town.lucifersden.io.inputboolean", return_value=False):
                result = lucifersden.main(test_args, player=player)
        assert result is True

    def test_bet_exceeds_coins_exits(self, test_args):
        player = DummyPlayer(coins=500, serfs=2000, land=5000)
        with patch("empyre.town.lucifersden.lib.setbottombar"):
            with patch("empyre.town.lucifersden.io.inputboolean", return_value=True):
                with patch("empyre.town.lucifersden.io.inputinteger", return_value=1000):
                    result = lucifersden.main(test_args, player=player)
        assert result is None

    def test_bet_of_zero_exits(self, test_args):
        player = DummyPlayer(coins=1000, serfs=2000, land=5000)
        with patch("empyre.town.lucifersden.lib.setbottombar"):
            with patch("empyre.town.lucifersden.io.inputboolean", return_value=True):
                with patch("empyre.town.lucifersden.io.inputinteger", return_value=0):
                    result = lucifersden.main(test_args, player=player)
        assert result is None

    def test_fewer_than_1000_serfs_exits(self, test_args):
        player = DummyPlayer(coins=1000, serfs=500, land=5000)
        with patch("empyre.town.lucifersden.lib.setbottombar"):
            with patch("empyre.town.lucifersden.io.inputboolean", return_value=True):
                with patch("empyre.town.lucifersden.io.inputinteger", return_value=100):
                    result = lucifersden.main(test_args, player=player)
        assert result is None

    def test_init_returns_true(self, test_args):
        assert lucifersden.init(test_args) is True

    def test_access_returns_true(self, test_args):
        assert lucifersden.access(test_args, "op") is True

    def test_buildargs_returns_none(self, test_args):
        assert lucifersden.buildargs(test_args) is None
