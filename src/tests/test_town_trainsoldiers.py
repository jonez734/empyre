from unittest.mock import patch

from empyre.town import trainsoldiers


class DummyPlayer:
    def __init__(self, nobles=5, soldiers=0, serfs=2000, land=5000):
        self.nobles = nobles
        self.soldiers = soldiers
        self.serfs = serfs
        self.land = land
        self._saved = False

    def save(self, force=False, commit=True):
        self._saved = True


class TestTrainSoldiers:
    def test_returns_early_when_serfs_less_than_1500(self, test_args):
        player = DummyPlayer(serfs=1000)
        with patch("empyre.town.trainsoldiers.lib.setbottombar"):
            result = trainsoldiers.main(test_args, player=player)
        assert result is True
        assert player.soldiers == 0
        assert player._saved is False

    def test_trains_serfs_to_soldiers_when_player_accepts(self, test_args):
        player = DummyPlayer(nobles=5, soldiers=0, serfs=2000, land=5000)
        eligible = int(player.nobles * 20 - player.soldiers)
        with patch("empyre.town.trainsoldiers.lib.setbottombar"):
            with patch("empyre.town.trainsoldiers.io.inputboolean", return_value=True):
                result = trainsoldiers.main(test_args, player=player)
        assert result is True
        assert player.serfs == 2000 - eligible
        assert player.soldiers == eligible
        assert player.land == 5000 - eligible

    def test_no_training_when_player_declines(self, test_args):
        player = DummyPlayer(nobles=5, soldiers=0, serfs=2000, land=5000)
        with patch("empyre.town.trainsoldiers.lib.setbottombar"):
            with patch("empyre.town.trainsoldiers.io.inputboolean", return_value=False):
                result = trainsoldiers.main(test_args, player=player)
        assert result is True
        assert player.soldiers == 0
        assert player.serfs == 2000
        assert player.land == 5000

    def test_trains_all_eligible_soldiers(self, test_args):
        player = DummyPlayer(nobles=10, soldiers=0, serfs=3000, land=10000)
        eligible = int(player.nobles * 20 - player.soldiers)
        assert eligible == 200
        with patch("empyre.town.trainsoldiers.lib.setbottombar"):
            with patch("empyre.town.trainsoldiers.io.inputboolean", return_value=True):
                trainsoldiers.main(test_args, player=player)
        assert player.soldiers == 200
        assert player.land == 10000 - 200

    def test_init_returns_true(self, test_args):
        assert trainsoldiers.init(test_args) is True

    def test_access_returns_true(self, test_args):
        assert trainsoldiers.access(test_args, "op") is True

    def test_buildargs_returns_none(self, test_args):
        assert trainsoldiers.buildargs(test_args) is None
