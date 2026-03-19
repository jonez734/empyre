from unittest.mock import patch

from empyre.town import soldierpromotion


class DummyPlayer:
    def __init__(self, soldiers=0, turncount=0, soldierpromotioncount=0):
        self.soldiers = soldiers
        self.turncount = turncount
        self.soldierpromotioncount = soldierpromotioncount
        self.nobles = 0
        self.serfs = 1000
        self.land = 10000
        self._saved = False

    def save(self, force=False, commit=True):
        self._saved = True


class TestSoldierPromotion:
    def test_returns_early_when_fewer_than_10_soldiers(self, test_args):
        player = DummyPlayer(soldiers=5)
        result = soldierpromotion.main(test_args, player=player)
        assert result is None
        assert player.nobles == 0
        assert player._saved is False

    def test_declines_promotion_when_player_says_no(self, test_args):
        player = DummyPlayer(soldiers=20, turncount=1, soldierpromotioncount=0)
        with patch("empyre.town.soldierpromotion.io.inputboolean", return_value=False):
            with patch("empyre.town.soldierpromotion.random.randint", return_value=3):
                result = soldierpromotion.main(test_args, player=player)
        assert result is None
        assert player.soldiers == 20
        assert player.nobles == 0

    def test_returns_early_when_promotable_is_zero(self, test_args):
        player = DummyPlayer(soldiers=20, turncount=1, soldierpromotioncount=0)
        with patch("empyre.town.soldierpromotion.io.inputboolean", return_value=True):
            with patch("empyre.town.soldierpromotion.random.randint", return_value=0):
                result = soldierpromotion.main(test_args, player=player)
        assert result is None
        assert player.soldiers == 20
        assert player.nobles == 0

    def test_init_returns_true(self, test_args):
        assert soldierpromotion.init(test_args) is True

    def test_access_returns_true(self, test_args):
        assert soldierpromotion.access(test_args, "op") is True

    def test_buildargs_returns_none(self, test_args):
        assert soldierpromotion.buildargs(test_args) is None
