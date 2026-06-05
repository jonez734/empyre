from unittest.mock import patch

from empyre import market


class DummyPlayer:
    """Minimal player stand-in for market.main().

    market.main() touches: .coins, .getresource, .adjust, .save, .status().
    """

    def __init__(self):
        self.coins = 1000
        self.resources = {
            "grain": {"name": "grain", "value": 412, "price": 0, "default": 0},
            "land": {"name": "land", "value": 65, "price": 0, "default": 0},
            "horses": {"name": "horses", "value": 80, "price": 0, "default": 0},
            "timber": {"name": "timber", "value": 25, "price": 0, "default": 0},
            "spices": {"name": "spices", "value": 150, "price": 0, "default": 0},
        }
        self.status_called = 0
        self.saved_count = 0
        self.adjust_count = 0

    def getresource(self, name, **kwargs):
        return dict(self.resources.get(name, {"name": name, "value": 0, "default": 0}))

    def adjust(self):
        self.adjust_count += 1
        return True

    def save(self, force=False, commit=True):
        self.saved_count += 1
        return True

    def status(self):
        self.status_called += 1


def _quiet_io():
    """Patch io.echo and io.heading to silence all market output."""
    return [
        patch("empyre.market.io.echo"),
        patch("empyre.lib.io.echo"),
    ]


class TestMarkethelp:
    def test_returns_false_when_no_player(self):
        assert market.markethelp() is False
        assert market.markethelp(player=None) is False

    def test_returns_true_with_player(self, test_args):
        player = DummyPlayer()
        with patch("empyre.market.io.echo"):
            assert market.markethelp(player=player) is True


class TestMainRejectsMissingPlayer:
    def test_returns_false_when_no_player(self, test_args):
        with patch("empyre.market.io.echo") as mock_echo:
            result = market.main(test_args)
        assert result is False
        error_calls = [str(c) for c in mock_echo.call_args_list]
        assert any("You do not exist" in c for c in error_calls)


class TestMainRegressionPlayerKwargs:
    """Regression: market.main must not pass `player` twice to io.inputchar.

    play.py calls runmodule(args, x, player=player, **kwargs), so when
    market.main receives **kwargs it already contains player. Previously
    market.main then explicitly forwarded player=player, causing
    "got multiple values for keyword argument 'player'".
    """

    def test_does_not_raise_with_player_in_kwargs(self, test_args):
        player = DummyPlayer()

        with (
            patch("empyre.market.io.echo"),
            patch("empyre.lib.io.echo"),
            patch("empyre.market.libempyre.setbottombar"),
            patch("empyre.market.io.inputchar", return_value="Q") as mock_inputchar,
        ):
            result = market.main(test_args, player=player)

        assert result is True
        # inputchar must have been called exactly once with player in kwargs
        mock_inputchar.assert_called_once()
        call_kwargs = mock_inputchar.call_args.kwargs
        assert "player" in call_kwargs
        assert call_kwargs["player"] is player

    def test_inputchar_receives_kwargs_without_duplicate_player(self, test_args):
        """When **kwargs already carries player, inputchar must get it once."""
        player = DummyPlayer()

        with (
            patch("empyre.market.io.echo"),
            patch("empyre.lib.io.echo"),
            patch("empyre.market.libempyre.setbottombar"),
            patch("empyre.market.io.inputchar", return_value="Q") as mock_inputchar,
        ):
            market.main(test_args, player=player, pool="ignored-conn-pool")

        call_kwargs = mock_inputchar.call_args.kwargs
        # No duplicate-key TypeError: player appears exactly once in kwargs.
        assert list(call_kwargs.values()).count(player) == 1
        # Other kwargs flow through unchanged.
        assert call_kwargs.get("pool") == "ignored-conn-pool"
        assert call_kwargs.get("args") is test_args


class TestMainQuitFlow:
    def test_quit_returns_true_and_exits_loop(self, test_args):
        player = DummyPlayer()

        with (
            patch("empyre.market.io.echo"),
            patch("empyre.lib.io.echo"),
            patch("empyre.market.libempyre.setbottombar"),
            patch("empyre.market.io.inputchar", return_value="Q") as mock_inputchar,
        ):
            result = market.main(test_args, player=player)

        assert result is True
        mock_inputchar.assert_called_once()
        # No trades, no status, no adjust/save from the quit path itself.
        assert player.status_called == 0


class TestMainYourStatsFlow:
    def test_y_calls_status(self, test_args):
        player = DummyPlayer()

        with (
            patch("empyre.market.io.echo"),
            patch("empyre.lib.io.echo"),
            patch("empyre.market.libempyre.setbottombar"),
            patch("empyre.market.io.inputchar", side_effect=["Y", "Q"]),
        ):
            result = market.main(test_args, player=player)

        assert result is True
        assert player.status_called == 1

    def test_status_continues_loop_until_quit(self, test_args):
        player = DummyPlayer()

        with (
            patch("empyre.market.io.echo"),
            patch("empyre.lib.io.echo"),
            patch("empyre.market.libempyre.setbottombar"),
            patch("empyre.market.io.inputchar", side_effect=["Y", "Y", "Q"]),
        ):
            result = market.main(test_args, player=player)

        assert result is True
        assert player.status_called == 2


class TestMainTradeFlow:
    def test_grain_trade_invokes_trade_and_saves(self, test_args):
        player = DummyPlayer()

        with (
            patch("empyre.market.io.echo"),
            patch("empyre.lib.io.echo"),
            patch("empyre.market.libempyre.setbottombar"),
            patch("empyre.market.libempyre.trade") as mock_trade,
            patch("empyre.market.io.inputchar", side_effect=["G", "Q"]),
        ):
            result = market.main(test_args, player=player)

        assert result is True
        mock_trade.assert_called_once()
        # trade was called with (args, player, name, **res) — check name.
        trade_args = mock_trade.call_args
        assert trade_args.args[0] is test_args
        assert trade_args.args[1] is player
        assert trade_args.args[2] == "grain"
        # Trade path adjusts and saves the player.
        assert player.adjust_count == 1
        assert player.saved_count == 1

    def test_each_resource_letter_triggers_trade(self, test_args):
        for letter, resource in [
            ("G", "grain"),
            ("L", "land"),
            ("H", "horses"),
            ("T", "timber"),
            ("S", "spices"),
        ]:
            player = DummyPlayer()
            with (
                patch("empyre.market.io.echo"),
                patch("empyre.lib.io.echo"),
                patch("empyre.market.libempyre.setbottombar"),
                patch("empyre.market.libempyre.trade") as mock_trade,
                patch("empyre.market.io.inputchar", side_effect=[letter, "Q"]),
            ):
                result = market.main(test_args, player=player)

            assert result is True, f"failed for letter {letter}"
            mock_trade.assert_called_once()
            assert mock_trade.call_args.args[2] == resource, (
                f"wrong resource for letter {letter}"
            )


class TestMainUnknownInput:
    def test_unknown_letter_does_not_break_loop(self, test_args):
        player = DummyPlayer()

        with (
            patch("empyre.market.io.echo"),
            patch("empyre.lib.io.echo"),
            patch("empyre.market.libempyre.setbottombar"),
            patch("empyre.market.io.inputchar", side_effect=["X", "Q"]),
        ):
            result = market.main(test_args, player=player)

        assert result is True
        assert player.status_called == 0


class TestMainHeadingAndBottomBar:
    def test_heading_and_setbottombar_called_once(self, test_args):
        player = DummyPlayer()

        with (
            patch("empyre.market.io.echo"),
            patch("empyre.lib.io.echo"),
            patch("empyre.market.util.heading") as mock_heading,
            patch("empyre.market.libempyre.setbottombar") as mock_sbb,
            patch("empyre.market.io.inputchar", return_value="Q"),
        ):
            market.main(test_args, player=player)

        mock_heading.assert_called_once_with(": corn exchange :")
        mock_sbb.assert_called_once()
        # setbottombar is called with (args, "market", player=player)
        assert mock_sbb.call_args.args[0] is test_args
        assert mock_sbb.call_args.args[1] == "market"
        assert mock_sbb.call_args.kwargs.get("player") is player
