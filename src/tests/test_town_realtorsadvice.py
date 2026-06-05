from unittest.mock import patch, MagicMock

from empyre.town import realtorsadvice


class DummyPlayer:
    def __init__(
        self,
        foundries=0,
        mills=0,
        markets=0,
        coins=0,
    ):
        self.foundries = foundries
        self.mills = mills
        self.markets = markets
        self.coins = coins
        self._adjusted = False
        self._saved = False

    def getresource(self, name, **kwargs):
        return {
            "name": name,
            "singular": name[:-1] if name.endswith("s") else name,
            "plural": name,
            "value": getattr(self, name, 0),
            "emoji": "",
        }

    def adjust(self):
        self._adjusted = True

    def save(self, force=False, commit=True):
        self._saved = True


class TestRealtorsAdvice:
    def test_init_returns_true(self, test_args):
        assert realtorsadvice.init(test_args) is True

    def test_access_returns_true(self, test_args):
        assert realtorsadvice.access(test_args, "op") is True

    def test_buildargs_returns_none(self, test_args):
        assert realtorsadvice.buildargs(test_args) is None

    def test_returns_false_when_pool_is_none(self, test_args):
        player = DummyPlayer()
        with patch("empyre.town.realtorsadvice.libempyre.setbottombar"):
            with patch("empyre.town.realtorsadvice.io.echo"):
                result = realtorsadvice.main(test_args, player=player)
        assert result is False

    def test_invokes_trade_for_foundries_mills_markets(self, test_args):
        player = DummyPlayer(foundries=2, mills=4, markets=6, coins=100000)
        with patch("empyre.town.realtorsadvice.libempyre.setbottombar"):
            with patch("empyre.town.realtorsadvice.libempyre.trade") as mock_trade:
                with patch(
                    "empyre.town.realtorsadvice.database.connect"
                ) as mock_connect:
                    mock_connect.return_value.__enter__.return_value = MagicMock()
                    mock_connect.return_value.__exit__ = MagicMock(return_value=False)
                    result = realtorsadvice.main(
                        test_args, player=player, pool=MagicMock()
                    )
        assert result is True
        assert mock_trade.call_count == 3
        traded_names = [call.args[2] for call in mock_trade.call_args_list]
        assert traded_names == ["foundries", "mills", "markets"]

    def test_foundries_price_is_2000_plus_half_count(self, test_args):
        player = DummyPlayer(foundries=10, mills=0, markets=0, coins=100000)
        with patch("empyre.town.realtorsadvice.libempyre.setbottombar"):
            with patch("empyre.town.realtorsadvice.libempyre.trade") as mock_trade:
                with patch(
                    "empyre.town.realtorsadvice.database.connect"
                ) as mock_connect:
                    mock_connect.return_value.__enter__.return_value = MagicMock()
                    mock_connect.return_value.__exit__ = MagicMock(return_value=False)
                    realtorsadvice.main(test_args, player=player, pool=MagicMock())
        foundries_call = mock_trade.call_args_list[0]
        assert foundries_call.args[2] == "foundries"
        assert foundries_call.kwargs["price"] == 2005

    def test_mills_price_is_500_plus_half_count(self, test_args):
        player = DummyPlayer(foundries=0, mills=10, markets=0, coins=100000)
        with patch("empyre.town.realtorsadvice.libempyre.setbottombar"):
            with patch("empyre.town.realtorsadvice.libempyre.trade") as mock_trade:
                with patch(
                    "empyre.town.realtorsadvice.database.connect"
                ) as mock_connect:
                    mock_connect.return_value.__enter__.return_value = MagicMock()
                    mock_connect.return_value.__exit__ = MagicMock(return_value=False)
                    realtorsadvice.main(test_args, player=player, pool=MagicMock())
        mills_call = mock_trade.call_args_list[1]
        assert mills_call.args[2] == "mills"
        assert mills_call.kwargs["price"] == 505

    def test_markets_price_is_250_plus_half_count(self, test_args):
        player = DummyPlayer(foundries=0, mills=0, markets=10, coins=100000)
        with patch("empyre.town.realtorsadvice.libempyre.setbottombar"):
            with patch("empyre.town.realtorsadvice.libempyre.trade") as mock_trade:
                with patch(
                    "empyre.town.realtorsadvice.database.connect"
                ) as mock_connect:
                    mock_connect.return_value.__enter__.return_value = MagicMock()
                    mock_connect.return_value.__exit__ = MagicMock(return_value=False)
                    realtorsadvice.main(test_args, player=player, pool=MagicMock())
        markets_call = mock_trade.call_args_list[2]
        assert markets_call.args[2] == "markets"
        assert markets_call.kwargs["price"] == 255

    def test_pricing_with_zero_resources(self, test_args):
        player = DummyPlayer(foundries=0, mills=0, markets=0, coins=100000)
        with patch("empyre.town.realtorsadvice.libempyre.setbottombar"):
            with patch("empyre.town.realtorsadvice.libempyre.trade") as mock_trade:
                with patch(
                    "empyre.town.realtorsadvice.database.connect"
                ) as mock_connect:
                    mock_connect.return_value.__enter__.return_value = MagicMock()
                    mock_connect.return_value.__exit__ = MagicMock(return_value=False)
                    realtorsadvice.main(test_args, player=player, pool=MagicMock())
        prices = [call.kwargs["price"] for call in mock_trade.call_args_list]
        assert prices == [2000, 500, 250]

    def test_player_is_adjusted_and_saved(self, test_args):
        player = DummyPlayer(foundries=1, mills=1, markets=1, coins=100000)
        with patch("empyre.town.realtorsadvice.libempyre.setbottombar"):
            with patch("empyre.town.realtorsadvice.libempyre.trade"):
                with patch(
                    "empyre.town.realtorsadvice.database.connect"
                ) as mock_connect:
                    mock_connect.return_value.__enter__.return_value = MagicMock()
                    mock_connect.return_value.__exit__ = MagicMock(return_value=False)
                    realtorsadvice.main(test_args, player=player, pool=MagicMock())
        assert player._adjusted is True
        assert player._saved is True

    def test_uses_supplied_conn_when_provided(self, test_args, db_conn):
        player = DummyPlayer(foundries=0, mills=0, markets=0, coins=100000)
        with patch("empyre.town.realtorsadvice.libempyre.setbottombar"):
            with patch("empyre.town.realtorsadvice.libempyre.trade") as mock_trade:
                with patch(
                    "empyre.town.realtorsadvice.database.connect"
                ) as mock_connect:
                    realtorsadvice.main(test_args, player=player, conn=db_conn)
        assert mock_trade.call_count == 3
        mock_connect.assert_not_called()
        for call in mock_trade.call_args_list:
            assert call.kwargs["conn"] is db_conn
