from unittest.mock import patch

from empyre.town import naturaldisasterbank


class DummyPlayer:
    def __init__(self, coins=0, moniker="test_player"):
        self.coins = coins
        self.moniker = moniker
        self._saved = False

    def save(self, force=False, commit=True):
        self._saved = True

    def getresource(self, name, **kwargs):
        if name == "coins":
            return {
                "name": "coins",
                "singular": "coin",
                "plural": "coins",
                "value": self.coins,
                "emoji": ":moneybag:",
            }
        return {"name": name}


class TestNaturalDisasterBank:
    def test_init_returns_true(self, test_args):
        assert naturaldisasterbank.init(test_args) is True

    def test_access_returns_true(self, test_args):
        assert naturaldisasterbank.access(test_args, "op") is True

    def test_buildargs_returns_none(self, test_args):
        assert naturaldisasterbank.buildargs(test_args) is None

    def test_returns_early_when_no_credits(self, test_args):
        player = DummyPlayer(coins=1000)
        with patch("empyre.town.naturaldisasterbank.lib.setbottombar"):
            with patch(
                "empyre.town.naturaldisasterbank.member.getcredits", return_value=None
            ):
                with patch(
                    "empyre.town.naturaldisasterbank.io.inputinteger"
                ) as mock_input:
                    result = naturaldisasterbank.main(test_args, player=player)
        assert result is None
        mock_input.assert_not_called()
        assert player._saved is False

    def test_returns_early_when_credits_are_zero(self, test_args):
        player = DummyPlayer(coins=1000)
        with patch("empyre.town.naturaldisasterbank.lib.setbottombar"):
            with patch(
                "empyre.town.naturaldisasterbank.member.getcredits", return_value=0
            ):
                with patch(
                    "empyre.town.naturaldisasterbank.io.inputinteger"
                ) as mock_input:
                    result = naturaldisasterbank.main(test_args, player=player)
        assert result is None
        mock_input.assert_not_called()
        assert player._saved is False

    def test_exchanges_credits_for_coins_at_3_to_1(self, test_args):
        player = DummyPlayer(coins=500)
        with patch("empyre.town.naturaldisasterbank.lib.setbottombar"):
            with patch(
                "empyre.town.naturaldisasterbank.member.getcredits", return_value=10
            ):
                with patch(
                    "empyre.town.naturaldisasterbank.io.inputinteger", return_value=4
                ):
                    with patch(
                        "empyre.town.naturaldisasterbank.member.setcredits"
                    ) as mock_set:
                        result = naturaldisasterbank.main(test_args, player=player)
        assert result is True
        assert player.coins == 500 + (4 * 3)
        mock_set.assert_called_once()
        positional = mock_set.call_args[0]
        assert positional[1] == "test_player"
        assert positional[2] == 6
        assert player._saved is True

    def test_exchange_amount_equal_to_credits_succeeds(self, test_args):
        player = DummyPlayer(coins=0)
        with patch("empyre.town.naturaldisasterbank.lib.setbottombar"):
            with patch(
                "empyre.town.naturaldisasterbank.member.getcredits", return_value=5
            ):
                with patch(
                    "empyre.town.naturaldisasterbank.io.inputinteger", return_value=5
                ):
                    with patch(
                        "empyre.town.naturaldisasterbank.member.setcredits"
                    ) as mock_set:
                        result = naturaldisasterbank.main(test_args, player=player)
        assert result is True
        assert player.coins == 15
        mock_set.assert_called_once()
        positional = mock_set.call_args[0]
        assert positional[1] == "test_player"
        assert positional[2] == 0

    def test_no_exchange_when_input_is_none(self, test_args):
        player = DummyPlayer(coins=500)
        with patch("empyre.town.naturaldisasterbank.lib.setbottombar"):
            with patch(
                "empyre.town.naturaldisasterbank.member.getcredits", return_value=10
            ):
                with patch(
                    "empyre.town.naturaldisasterbank.io.inputinteger", return_value=None
                ):
                    with patch(
                        "empyre.town.naturaldisasterbank.member.setcredits"
                    ) as mock_set:
                        result = naturaldisasterbank.main(test_args, player=player)
        assert result is None
        assert player.coins == 500
        mock_set.assert_not_called()
        assert player._saved is False

    def test_no_exchange_when_input_is_zero(self, test_args):
        player = DummyPlayer(coins=500)
        with patch("empyre.town.naturaldisasterbank.lib.setbottombar"):
            with patch(
                "empyre.town.naturaldisasterbank.member.getcredits", return_value=10
            ):
                with patch(
                    "empyre.town.naturaldisasterbank.io.inputinteger", return_value=0
                ):
                    with patch(
                        "empyre.town.naturaldisasterbank.member.setcredits"
                    ) as mock_set:
                        result = naturaldisasterbank.main(test_args, player=player)
        assert result is None
        assert player.coins == 500
        mock_set.assert_not_called()
        assert player._saved is False

    def test_no_exchange_when_input_is_negative(self, test_args):
        player = DummyPlayer(coins=500)
        with patch("empyre.town.naturaldisasterbank.lib.setbottombar"):
            with patch(
                "empyre.town.naturaldisasterbank.member.getcredits", return_value=10
            ):
                with patch(
                    "empyre.town.naturaldisasterbank.io.inputinteger", return_value=-3
                ):
                    with patch(
                        "empyre.town.naturaldisasterbank.member.setcredits"
                    ) as mock_set:
                        result = naturaldisasterbank.main(test_args, player=player)
        assert result is None
        assert player.coins == 500
        mock_set.assert_not_called()
        assert player._saved is False

    def test_rejects_amount_exceeding_available_credits(self, test_args):
        player = DummyPlayer(coins=500)
        with patch("empyre.town.naturaldisasterbank.lib.setbottombar"):
            with patch(
                "empyre.town.naturaldisasterbank.member.getcredits", return_value=5
            ):
                with patch(
                    "empyre.town.naturaldisasterbank.io.inputinteger", return_value=10
                ):
                    with patch(
                        "empyre.town.naturaldisasterbank.member.setcredits"
                    ) as mock_set:
                        result = naturaldisasterbank.main(test_args, player=player)
        assert result is None
        assert player.coins == 500
        mock_set.assert_not_called()
        assert player._saved is False
