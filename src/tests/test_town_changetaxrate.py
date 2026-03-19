from unittest.mock import patch

from empyre.town import changetaxrate


class DummyPlayer:
    def __init__(self, taxrate=15):
        self.taxrate = taxrate


class TestChangeTaxRate:
    def test_sets_valid_taxrate(self, test_args):
        player = DummyPlayer(taxrate=10)
        with patch("empyre.town.changetaxrate.io.inputinteger", return_value=25):
            result = changetaxrate.main(test_args, player=player)
        assert result is True
        assert player.taxrate == 25

    def test_sets_taxrate_to_minimum(self, test_args):
        player = DummyPlayer(taxrate=15)
        with patch("empyre.town.changetaxrate.io.inputinteger", return_value=1):
            result = changetaxrate.main(test_args, player=player)
        assert result is True
        assert player.taxrate == 1

    def test_sets_taxrate_to_maximum(self, test_args):
        player = DummyPlayer(taxrate=15)
        with patch("empyre.town.changetaxrate.io.inputinteger", return_value=50):
            result = changetaxrate.main(test_args, player=player)
        assert result is True
        assert player.taxrate == 50

    def test_rejects_taxrate_above_50(self, test_args):
        player = DummyPlayer(taxrate=15)
        with patch("empyre.town.changetaxrate.io.inputinteger", return_value=75):
            result = changetaxrate.main(test_args, player=player)
        assert result is True
        assert player.taxrate == 15

    def test_no_change_when_input_is_none(self, test_args):
        player = DummyPlayer(taxrate=20)
        with patch("empyre.town.changetaxrate.io.inputinteger", return_value=None):
            result = changetaxrate.main(test_args, player=player)
        assert result is True
        assert player.taxrate == 20

    def test_no_change_when_input_is_zero(self, test_args):
        player = DummyPlayer(taxrate=20)
        with patch("empyre.town.changetaxrate.io.inputinteger", return_value=0):
            result = changetaxrate.main(test_args, player=player)
        assert result is True
        assert player.taxrate == 20

    def test_no_change_when_input_is_negative(self, test_args):
        player = DummyPlayer(taxrate=20)
        with patch("empyre.town.changetaxrate.io.inputinteger", return_value=-5):
            result = changetaxrate.main(test_args, player=player)
        assert result is True
        assert player.taxrate == 20

    def test_init_returns_true(self, test_args):
        assert changetaxrate.init(test_args) is True

    def test_access_returns_true(self, test_args):
        assert changetaxrate.access(test_args, "op") is True

    def test_buildargs_returns_none(self, test_args):
        assert changetaxrate.buildargs(test_args) is None
