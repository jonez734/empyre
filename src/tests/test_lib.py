from unittest.mock import patch, MagicMock, PropertyMock

from empyre.lib import (
    generatename,
    buildargs,
    checkmodule,
    runmodule,
    init,
    newsentry,
    Island,
    Colony,
    ShipKind,
    Weather,
    completeResourceName,
    setbottombar,
)


class TestGeneratename:
    def test_returns_name_from_list(self, test_args):
        with patch("empyre.lib.random.randint", return_value=0):
            name = generatename(test_args)
            assert name == "Richye"

    def test_returns_last_name(self, test_args):
        with patch("empyre.lib.random.randint", return_value=45):
            name = generatename(test_args)
            assert name == "Icell"

    def test_returns_middle_name(self, test_args):
        with patch("empyre.lib.random.randint", return_value=25):
            name = generatename(test_args)
            assert name == "Joycie"

    def test_random_randint_called_within_bounds(self, test_args):
        with patch("empyre.lib.random.randint", return_value=5) as mock_rand:
            generatename(test_args)
            mock_rand.assert_called_once()
            args = mock_rand.call_args[0]
            assert args[0] == 0
            assert args[1] == 45


class TestBuildargs:
    def test_returns_parser(self, test_args):
        result = buildargs()
        assert result is not None

    def test_parser_has_debug_flag(self, test_args):
        parser = buildargs()
        ns = parser.parse_args(["--debug"])
        assert ns.debug is True

    def test_parser_has_verbose_flag(self, test_args):
        parser = buildargs()
        ns = parser.parse_args(["--verbose"])
        assert ns.verbose is True

    def test_parser_has_modules_option(self, test_args):
        parser = buildargs()
        ns = parser.parse_args([])
        assert isinstance(ns.modules, tuple)
        assert "town" in ns.modules
        assert "shipyard" in ns.modules

    def test_parser_default_modules_includes_weather(self, test_args):
        parser = buildargs()
        ns = parser.parse_args([])
        assert "weather" in ns.modules


class TestCheckmodule:
    def test_returns_false_for_nonexistent_module(self, test_args):
        result = checkmodule(test_args, "nonexistent_module_xyz")
        assert result is False

    def test_returns_true_for_valid_module(self, test_args):
        result = checkmodule(test_args, "town")
        assert result is True

    def test_calls_module_check_with_correct_name(self, test_args):
        with patch("empyre.lib.module.check", return_value=True) as mock_check:
            result = checkmodule(test_args, "town")
            mock_check.assert_called_once_with(test_args, "empyre.town")
            assert result is True


class TestRunmodule:
    def test_calls_module_run_with_correct_name(self, test_args):
        with patch("empyre.lib.module.run", return_value=True) as mock_run:
            result = runmodule(test_args, "town")
            mock_run.assert_called_once()
            call_args = mock_run.call_args[0]
            assert call_args[0] == test_args
            assert call_args[1] == "empyre.town"
            assert result is True

    def test_returns_false_when_checkmodule_fails(self, test_args):
        with patch("empyre.lib.checkmodule", return_value=False):
            result = runmodule(test_args, "nonexistent")
            assert result is False


class TestInit:
    def test_returns_true(self, test_args):
        result = init(test_args)
        assert result is True


class TestNewsentry:
    def test_inserts_newsentry_record(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        p = MagicMock()
        p.moniker = "newsentry_test"
        p.membermoniker = "test_member"

        with patch("bbsengine6.database.insert", return_value=1) as mock_insert:
            newsentry(test_args, "test message", player=p)
            mock_insert.assert_called_once()
            pos_args = mock_insert.call_args[0]
            assert pos_args[0] is test_args
            assert pos_args[1] == "empyre.__newsentry"
            assert "message" in pos_args[2]
            kw = mock_insert.call_args[1]
            assert kw["commit"] is True
            assert kw["returnid"] is True

    def test_returns_none(self, test_args, test_pool, db_conn, clean_tables):
        p = MagicMock()
        p.moniker = "newsentry_test2"
        p.membermoniker = "test_member"

        with patch("bbsengine6.database.insert", return_value=1):
            result = newsentry(test_args, "another message", player=p)
            assert result is None

    def test_debug_mode_prints_debug_info(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        p = MagicMock()
        p.moniker = "newsentry_debug"
        p.membermoniker = "test_member"
        args = test_args
        args.debug = True

        with patch("bbsengine6.database.insert", return_value=1):
            with patch("bbsengine6.io.echo") as mock_echo:
                newsentry(args, "debug message", player=p)
                debug_calls = [str(c) for c in mock_echo.call_args_list]
                assert any("ne=" in c for c in debug_calls)
                assert any("neid=" in c for c in debug_calls)


class TestIsland:
    def test_init_sets_default_trees(self):
        args = MagicMock()
        island = Island(args)
        assert island.trees == 500
        assert island.args is args
        assert island.playermoniker is None
        assert island.membermoniker is None


class TestColony:
    def test_init_sets_args(self):
        args = MagicMock()
        colony = Colony(args)
        assert colony.args is args


class TestShipKind:
    def test_passenger_value(self):
        assert ShipKind.PASSENGER.value == "passenger"

    def test_cargo_value(self):
        assert ShipKind.CARGO.value == "cargo"

    def test_is_str_subclass(self):
        assert issubclass(ShipKind, str)


class TestWeather:
    def test_poor_value(self):
        assert Weather.POOR.value == 1

    def test_fantastic_value(self):
        assert Weather.FANTASTIC.value == 6

    def test_all_weather_values(self):
        assert Weather.ARID.value == 2
        assert Weather.RAIN.value == 3
        assert Weather.AVERAGE.value == 4
        assert Weather.LONGSUMMER.value == 5

    def test_display_calls_io_echo(self):
        with patch("bbsengine6.io.echo") as mock_echo:
            Weather.display(Weather.POOR)
            mock_echo.assert_called_once()
            assert ":desert:" in str(mock_echo.call_args)

    def test_display_fantastic(self):
        with patch("bbsengine6.io.echo") as mock_echo:
            Weather.display(Weather.FANTASTIC)
            mock_echo.assert_called_once()
            assert ":sun:" in str(mock_echo.call_args)

    def test_display_average(self):
        with patch("bbsengine6.io.echo") as mock_echo:
            Weather.display(Weather.AVERAGE)
            mock_echo.assert_called_once()


class TestCompleteResourceName:
    def test_complete_returns_matching_names(self):
        args = MagicMock()
        attrs = [
            {"name": "coins"},
            {"name": "land"},
            {"name": "grain"},
        ]
        completer = completeResourceName(args, attrs)
        results = completer.complete("g", 0)
        assert "grain" in results
        assert "coins" not in results

    def test_complete_returns_none_when_no_match(self):
        args = MagicMock()
        attrs = [{"name": "coins"}, {"name": "land"}]
        completer = completeResourceName(args, attrs)
        result = completer.complete("xyz", 0)
        assert result is None

    def test_complete_state_parameter(self):
        args = MagicMock()
        attrs = [{"name": "alpha"}, {"name": "beta"}]
        completer = completeResourceName(args, attrs)
        r0 = completer.complete("a", 0)
        r1 = completer.complete("a", 1)
        assert r0 == "alpha"
        assert r1 is None


class TestSetbottombar:
    def test_returns_none(self):
        args = MagicMock()
        args.debug = False
        with patch("bbsengine6.io.screen.setbottombar"):
            result = setbottombar(args, "test message")
            assert result is None

    def test_calls_screen_setbottombar(self):
        args = MagicMock()
        args.debug = False
        with patch("bbsengine6.io.screen.setbottombar") as mock_sb:
            setbottombar(args, "test buffer")
            mock_sb.assert_called_once()
            call_args = mock_sb.call_args[0]
            assert call_args[0] == "test buffer"
            assert callable(call_args[1])

    def test_rightside_callable_passed(self):
        args = MagicMock()
        args.debug = False
        with patch("bbsengine6.io.screen.setbottombar") as mock_sb:
            setbottombar(args, "msg", player=None)
            rightside_fn = mock_sb.call_args[0][1]
            result = rightside_fn()
            assert isinstance(result, str)

    def test_rightside_with_debug_no_player(self):
        args = MagicMock()
        args.debug = True
        with patch("bbsengine6.io.screen.setbottombar") as mock_sb:
            setbottombar(args, "", player=None)
            rightside_fn = mock_sb.call_args[0][1]
            result = rightside_fn()
            assert result == "debug"

    def test_player_dirty_marker(self):
        args = MagicMock()
        args.debug = False
        mock_player = MagicMock()
        mock_player.isdirty = PropertyMock(return_value=True)
        mock_player.turncount = 0
        mock_player.moniker = "test"
        mock_player.coins = 100
        mock_player.getresource.return_value = {"emoji": ""}

        with patch("bbsengine6.io.screen.setbottombar") as mock_sb:
            with patch("empyre.lib.libplayer.TURNSPERDAY", 10):
                setbottombar(args, "msg", player=mock_player)
                rightside_fn = mock_sb.call_args[0][1]
                result = rightside_fn(player=mock_player)
                assert "*" in result
                assert mock_player.moniker in result

    def test_player_clean_no_marker(self):
        args = MagicMock()
        args.debug = False
        mock_player = MagicMock()
        mock_player.isdirty.return_value = False
        mock_player.turncount = 0
        mock_player.moniker = "test"
        mock_player.coins = 100
        mock_player.getresource.return_value = {"emoji": ""}

        with patch("bbsengine6.io.screen.setbottombar") as mock_sb:
            setbottombar(args, "msg", player=mock_player)
            rightside_fn = mock_sb.call_args[0][1]
            result = rightside_fn()
            assert "*" not in result
