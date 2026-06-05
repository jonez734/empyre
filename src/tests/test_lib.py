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
    trade,
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

    def test_subcommand_disaster_sets_subparser(self, test_args):
        parser = buildargs()
        ns = parser.parse_args(["disaster"])
        assert ns._subparser == "disaster"

    def test_subcommand_town_sets_subparser(self, test_args):
        parser = buildargs()
        ns = parser.parse_args(["town"])
        assert ns._subparser == "town"

    def test_no_subcommand_leaves_subparser_none(self, test_args):
        parser = buildargs()
        ns = parser.parse_args([])
        assert ns._subparser is None

    def test_disaster_subparser_accepts_roll_arg(self, test_args):
        parser = buildargs()
        ns = parser.parse_args(["disaster", "--roll", "5"])
        assert ns.roll == 5

    def test_town_subparser_accepts_choice_arg(self, test_args):
        parser = buildargs()
        ns = parser.parse_args(["town", "--choice", "C"])
        assert ns.choice == "C"


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
        from empyre import lib as empyre_lib

        empyre_lib._current_player = None
        empyre_lib._current_args = None
        args = MagicMock()
        args.debug = False
        with patch("bbsengine6.io.screen.setbottombar"):
            result = setbottombar(args, "test message")
            assert result is None

    def test_calls_screen_setbottombar_with_buf_only(self):
        from empyre import lib as empyre_lib

        empyre_lib._current_player = None
        empyre_lib._current_args = None
        args = MagicMock()
        args.debug = False
        with patch("bbsengine6.io.screen.setbottombar") as mock_sb:
            setbottombar(args, "test buffer")
            mock_sb.assert_called_once_with("test buffer")

    def test_player_kwarg_updates_cached_state(self):
        from empyre import lib as empyre_lib

        empyre_lib._current_player = None
        empyre_lib._current_args = None
        args = MagicMock()
        args.debug = False
        mock_player = MagicMock()
        with patch("bbsengine6.io.screen.setbottombar"):
            setbottombar(args, "msg", player=mock_player)
        assert empyre_lib._current_player is mock_player
        assert empyre_lib._current_args is args

    def test_turns_fragment_renders_count(self):
        from empyre import lib as empyre_lib

        empyre_lib._current_player = None
        empyre_lib._current_args = None
        args = MagicMock()
        args.debug = False
        mock_player = MagicMock()
        mock_player.turncount = 3
        with patch("empyre.lib.libplayer.TURNSPERDAY", 10):
            empyre_lib._current_player = mock_player
            empyre_lib._current_args = args
            result = empyre_lib._empyre_turns_fragment()
        assert "7" in result

    def test_turns_fragment_empty_when_no_player(self):
        from empyre import lib as empyre_lib

        empyre_lib._current_player = None
        empyre_lib._current_args = None
        assert empyre_lib._empyre_turns_fragment() == ""

    def test_player_fragment_marks_dirty(self):
        from empyre import lib as empyre_lib

        empyre_lib._current_player = None
        empyre_lib._current_args = None
        args = MagicMock()
        args.debug = False
        mock_player = MagicMock()
        mock_player.isdirty.return_value = True
        mock_player.moniker = "alice"
        empyre_lib._current_player = mock_player
        empyre_lib._current_args = args
        result = empyre_lib._empyre_player_fragment()
        assert result == "*alice"

    def test_player_fragment_clean_no_marker(self):
        from empyre import lib as empyre_lib

        empyre_lib._current_player = None
        empyre_lib._current_args = None
        args = MagicMock()
        args.debug = False
        mock_player = MagicMock()
        mock_player.isdirty.return_value = False
        mock_player.moniker = "alice"
        empyre_lib._current_player = mock_player
        empyre_lib._current_args = args
        result = empyre_lib._empyre_player_fragment()
        assert result == "alice"
        assert "*" not in result

    def test_coins_fragment_includes_debug_suffix(self):
        from empyre import lib as empyre_lib

        empyre_lib._current_player = None
        empyre_lib._current_args = None
        args = MagicMock()
        args.debug = True
        mock_player = MagicMock()
        mock_player.coins = 100
        mock_player.getresource.return_value = {"emoji": ""}
        empyre_lib._current_player = mock_player
        empyre_lib._current_args = args
        result = empyre_lib._empyre_coins_fragment()
        assert "debug" in result

    def test_coins_fragment_omits_debug_when_off(self):
        from empyre import lib as empyre_lib

        empyre_lib._current_player = None
        empyre_lib._current_args = None
        args = MagicMock()
        args.debug = False
        mock_player = MagicMock()
        mock_player.coins = 100
        mock_player.getresource.return_value = {"emoji": ""}
        empyre_lib._current_player = mock_player
        empyre_lib._current_args = args
        result = empyre_lib._empyre_coins_fragment()
        assert "debug" not in result

    def test_register_and_unregister_fragments(self):
        from empyre import lib as empyre_lib

        empyre_lib._empyre_fragments.clear()
        with patch("bbsengine6.io.screen.register_bottombar_fragment") as mock_reg:
            with patch("bbsengine6.io.screen.unregister_bottombar_fragment") as mock_unreg:
                empyre_lib._register_empyre_fragments()
                assert mock_reg.call_count == 3
                assert len(empyre_lib._empyre_fragments) == 3
                empyre_lib._unregister_empyre_fragments()
                assert mock_unreg.call_count == 3
                assert empyre_lib._empyre_fragments == []
        empyre_lib._empyre_fragments.clear()


class TestTrade:
    def _make_player(self, foundries=5):
        player = MagicMock()
        player.coins = 100000
        player.foundries = foundries
        player.resources = {"foundries": {"value": foundries}}
        player.getresource.side_effect = lambda name, **kw: (
            {
                "value": player.foundries,
                "singular": "foundry",
                "plural": "foundries",
                "name": "foundries",
            }
            if name == "foundries"
            else {
                "singular": "coin",
                "plural": "coins",
                "name": "coins",
                "emoji": ":moneybag:",
            }
        )
        return player

    def test_edit_option_sets_player_attribute(self, test_args):
        player = self._make_player(foundries=5)
        with patch("empyre.lib.setbottombar"):
            with patch("empyre.lib.member.checkflag", return_value=True):
                with patch("empyre.lib.io.inputchar", side_effect=["E", "C"]):
                    with patch("empyre.lib.io.inputinteger", return_value=42):
                        trade(test_args, player, "foundries", price=2000)
        assert player.foundries == 42

    def test_edit_option_zero_replaces_negative_input(self, test_args):
        player = self._make_player(foundries=5)
        with patch("empyre.lib.setbottombar"):
            with patch("empyre.lib.member.checkflag", return_value=True):
                with patch("empyre.lib.io.inputchar", side_effect=["E", "C"]):
                    with patch("empyre.lib.io.inputinteger", return_value=-10):
                        trade(test_args, player, "foundries", price=2000)
        assert player.foundries == 0

    def test_edit_option_preserves_existing_value_when_cancelled(self, test_args):
        player = self._make_player(foundries=5)
        with patch("empyre.lib.setbottombar"):
            with patch("empyre.lib.member.checkflag", return_value=False):
                with patch("empyre.lib.io.inputchar", side_effect=["C"]):
                    with patch("empyre.lib.io.inputinteger") as mock_int:
                        trade(test_args, player, "foundries", price=2000)
        assert player.foundries == 5
        mock_int.assert_not_called()

    def test_edit_option_continues_loop_for_invalid_resource(self, test_args):
        player = self._make_player(foundries=5)
        player.resources = {}
        with patch("empyre.lib.setbottombar"):
            with patch("empyre.lib.member.checkflag", return_value=True):
                with patch("empyre.lib.io.inputchar", side_effect=["E", "C"]):
                    with patch("empyre.lib.io.inputinteger", return_value=99):
                        trade(test_args, player, "foundries", price=2000)
        assert player.foundries == 5

    def test_edit_option_prompts_for_inputinteger_with_current_value(self, test_args):
        player = self._make_player(foundries=7)
        with patch("empyre.lib.setbottombar"):
            with patch("empyre.lib.member.checkflag", return_value=True):
                with patch("empyre.lib.io.inputchar", side_effect=["E", "C"]):
                    with patch(
                        "empyre.lib.io.inputinteger", return_value=1
                    ) as mock_int:
                        trade(test_args, player, "foundries", price=2000)
        mock_int.assert_called_once()
        assert mock_int.call_args.args[1] == 7

    def test_edit_option_continues_after_edit(self, test_args):
        player = self._make_player(foundries=5)
        with patch("empyre.lib.setbottombar"):
            with patch("empyre.lib.member.checkflag", return_value=True):
                with patch(
                    "empyre.lib.io.inputchar", side_effect=["E", "C"]
                ) as mock_ch:
                    with patch("empyre.lib.io.inputinteger", return_value=20):
                        trade(test_args, player, "foundries", price=2000)
        assert mock_ch.call_count == 2
        assert player.foundries == 20
