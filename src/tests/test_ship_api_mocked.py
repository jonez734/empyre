import argparse
from unittest.mock import MagicMock, patch

import pytest

from empyre.ship import load as ship_load
from empyre.ship import unload as ship_unload
from empyre.ship.lib import (
    Ship,
    count,
    create,
)

from .helpers import listbox_cancelled, listbox_selected


pytestmark = pytest.mark.unit


@pytest.fixture
def mock_args():
    args = MagicMock(spec=argparse.Namespace)
    args.debug = False
    return args


@pytest.fixture
def mock_player():
    p = MagicMock()
    p.moniker = "test_player"
    p.ships = 0
    p.shipyards = 1
    p.grain = 1000
    p.gold = 500
    p.coins = 100
    p.serfs = 10
    p.getresource = MagicMock(
        side_effect=lambda name, **kw: {
            "grain": {
                "singular": "bushel",
                "plural": "bushels",
                "emoji": ":crop:",
            },
            "gold": {
                "singular": "coin",
                "plural": "coins",
                "emoji": ":moneybag:",
            },
            "serfs": {
                "singular": "serf",
                "plural": "serfs",
                "emoji": ":person:",
            },
        }.get(
            name,
            {"singular": name, "plural": name + "s", "emoji": ""},
        )
    )
    return p


@pytest.fixture
def mock_ship():
    s = MagicMock()
    s.moniker = "mock_ship"
    s.manifest = {}
    s.adjust = MagicMock()
    s.save = MagicMock()
    return s


@pytest.fixture
def mock_pool():
    return MagicMock()


class TestCreateMocked:
    def test_create_calls_insert_with_all_attributes(
        self, mock_args, mock_player, mock_pool
    ):
        with (
            patch("empyre.ship.lib.database.insert") as mock_insert,
            patch("empyre.ship.lib.database.connect") as mock_connect,
            patch("empyre.ship.lib.count", return_value=1),
            patch(
                "empyre.ship.lib.member.getcurrentmoniker",
                return_value="test_member",
            ),
            patch(
                "empyre.ship.lib._generateuniqueshipname",
                return_value="auto_name",
            ),
        ):
            mock_conn = MagicMock()
            mock_connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
            mock_connect.return_value.__exit__ = MagicMock(return_value=False)
            ship = create(
                mock_args,
                player=mock_player,
                pool=mock_pool,
                moniker="new_ship",
                kind="cargo",
                location="mainland",
            )

        assert ship is not None
        assert ship.moniker == "new_ship"
        assert ship.kind == "cargo"
        assert ship.location == "mainland"
        assert ship.status == "build"
        assert ship.playermoniker == "test_player"
        mock_insert.assert_called_once()
        call_args = mock_insert.call_args
        assert call_args[0][1] == "empyre.__ship"
        assert call_args[1]["primarykey"] == "moniker"

    def test_create_returns_ship_with_mirrored_attributes(
        self, mock_args, mock_player, mock_pool
    ):
        with (
            patch("empyre.ship.lib.database.insert"),
            patch("empyre.ship.lib.database.connect") as mock_connect,
            patch("empyre.ship.lib.count", return_value=1),
            patch(
                "empyre.ship.lib.member.getcurrentmoniker",
                return_value="test_member",
            ),
            patch(
                "empyre.ship.lib._generateuniqueshipname",
                return_value="auto_name",
            ),
        ):
            mock_conn = MagicMock()
            mock_connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
            mock_connect.return_value.__exit__ = MagicMock(return_value=False)
            ship = create(
                mock_args,
                player=mock_player,
                pool=mock_pool,
                moniker="attr_ship",
                kind="passenger",
                navigator=True,
                location="island",
                status="docked",
            )

        assert ship.kind == "passenger"
        assert ship.navigator is True
        assert ship.location == "island"
        assert ship.status == "docked"

    def test_create_returns_none_when_no_pool(self, mock_args, mock_player):
        with patch("empyre.ship.lib.database.insert") as mock_insert:
            result = create(mock_args, player=mock_player, pool=None, moniker="orphan")

        assert result is None
        mock_insert.assert_not_called()

    def test_create_returns_none_when_no_player(self, mock_args, mock_pool):
        with patch("empyre.ship.lib.database.insert") as mock_insert:
            result = create(mock_args, player=None, pool=mock_pool, moniker="orphan")

        assert result is None
        mock_insert.assert_not_called()

    def test_create_returns_none_when_over_capacity(
        self, mock_args, mock_player, mock_pool
    ):
        mock_player.shipyards = 0
        mock_player.ships = 0
        with patch("empyre.ship.lib.database.insert") as mock_insert:
            result = create(
                mock_args, player=mock_player, pool=mock_pool, moniker="overflow"
            )

        assert result is None
        mock_insert.assert_not_called()

    def test_create_uses_kwargs_overrides(self, mock_args, mock_player, mock_pool):
        with (
            patch("empyre.ship.lib.database.insert"),
            patch("empyre.ship.lib.database.connect") as mock_connect,
            patch("empyre.ship.lib.count", return_value=1),
            patch(
                "empyre.ship.lib.member.getcurrentmoniker",
                return_value="test_member",
            ),
            patch(
                "empyre.ship.lib._generateuniqueshipname",
                return_value="auto_name",
            ),
        ):
            mock_conn = MagicMock()
            mock_connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
            mock_connect.return_value.__exit__ = MagicMock(return_value=False)
            ship = create(
                mock_args,
                player=mock_player,
                pool=mock_pool,
                moniker="override_ship",
                kind="carrier",
                manifest={"grain": {"value": 500}},
                navigator=True,
                location="harbor",
                status="docked",
            )

        assert ship.kind == "carrier"
        assert ship.manifest == {"grain": {"value": 500}}
        assert ship.navigator is True
        assert ship.location == "harbor"
        assert ship.status == "docked"


class TestSaveMocked:
    def test_save_calls_update_with_primary_key(
        self, mock_args, mock_player, mock_pool
    ):
        mock_ship = Ship(mock_args, pool=mock_pool, player=mock_player)
        mock_ship.moniker = "save_me"
        mock_ship.kind = "cargo"
        mock_ship.manifest = {}
        mock_ship.navigator = False
        mock_ship.location = "mainland"
        mock_ship.status = "docked"
        mock_ship.playermoniker = "test_player"

        mock_conn = MagicMock()
        with patch("empyre.ship.lib.database.update") as mock_update:
            result = mock_ship.save(commit=True, conn=mock_conn)

        assert result is True
        mock_update.assert_called_once()
        call_args = mock_update.call_args
        assert call_args[0][1] == "empyre.__ship"
        assert call_args[1]["primarykey"] == "moniker"
        assert call_args[1]["commit"] is True

    def test_save_returns_false_when_no_pool_no_conn(self, mock_args):
        mock_ship = Ship(mock_args, pool=None)
        mock_ship.moniker = "no_pool_ship"

        result = mock_ship.save(commit=True)

        assert result is False

    def test_save_with_commit_false(self, mock_args, mock_player, mock_pool):
        mock_ship = Ship(mock_args, pool=mock_pool, player=mock_player)
        mock_ship.moniker = "no_commit_ship"
        mock_ship.kind = "cargo"
        mock_ship.manifest = {}
        mock_ship.navigator = False
        mock_ship.location = "mainland"
        mock_ship.status = "docked"
        mock_ship.playermoniker = "test_player"

        mock_conn = MagicMock()
        with patch("empyre.ship.lib.database.update") as mock_update:
            result = mock_ship.save(commit=False, conn=mock_conn)

        assert result is True
        assert mock_update.call_args[1]["commit"] is False


class TestLoadMocked:
    def test_load_tui_moves_resource_from_player_to_ship(
        self, mock_args, mock_player, mock_ship
    ):
        mock_ship.manifest = {}
        with (
            patch(
                "empyre.ship.load.libempyre.selectresource",
                return_value=listbox_selected("grain"),
            ),
            patch("empyre.ship.load.io.inputinteger", return_value=100),
            patch("empyre.ship.load.database.commit"),
        ):
            result = ship_load.main(
                mock_args, player=mock_player, ship=mock_ship, pool=None
            )

        assert result is True
        assert mock_player.grain == 900
        assert mock_ship.manifest == {"grain": {"value": 100}}
        mock_ship.save.assert_called_once()

    def test_load_tui_aborts_on_cancelled_selection(
        self, mock_args, mock_player, mock_ship
    ):
        mock_ship.manifest = {}
        with (
            patch(
                "empyre.ship.load.libempyre.selectresource",
                return_value=listbox_cancelled(),
            ),
            patch("empyre.ship.load.database.commit"),
        ):
            result = ship_load.main(
                mock_args, player=mock_player, ship=mock_ship, pool=None
            )

        assert result is True
        assert mock_player.grain == 1000
        assert mock_ship.manifest == {}
        mock_ship.save.assert_not_called()

    def test_load_tui_aborts_on_amount_exceeds_player(
        self, mock_args, mock_player, mock_ship
    ):
        mock_ship.manifest = {}
        mock_player.grain = 10
        with (
            patch(
                "empyre.ship.load.libempyre.selectresource",
                return_value=listbox_selected("grain"),
            ),
            patch("empyre.ship.load.io.inputinteger", return_value=100),
            patch("empyre.ship.load.database.commit"),
        ):
            result = ship_load.main(
                mock_args, player=mock_player, ship=mock_ship, pool=None
            )

        assert result is True
        assert mock_player.grain == 10
        assert mock_ship.manifest == {}
        mock_ship.save.assert_not_called()

    def test_load_tui_aborts_on_negative_amount(
        self, mock_args, mock_player, mock_ship
    ):
        mock_ship.manifest = {}
        with (
            patch(
                "empyre.ship.load.libempyre.selectresource",
                return_value=listbox_selected("grain"),
            ),
            patch("empyre.ship.load.io.inputinteger", return_value=-5),
            patch("empyre.ship.load.database.commit"),
        ):
            result = ship_load.main(
                mock_args, player=mock_player, ship=mock_ship, pool=None
            )

        assert result is True
        assert mock_player.grain == 1000
        assert mock_ship.manifest == {}
        mock_ship.save.assert_not_called()

    def test_load_tui_aborts_on_amount_none(self, mock_args, mock_player, mock_ship):
        mock_ship.manifest = {}
        with (
            patch(
                "empyre.ship.load.libempyre.selectresource",
                return_value=listbox_selected("grain"),
            ),
            patch("empyre.ship.load.io.inputinteger", return_value=None),
            patch("empyre.ship.load.database.commit"),
        ):
            result = ship_load.main(
                mock_args, player=mock_player, ship=mock_ship, pool=None
            )

        assert result is True
        assert mock_player.grain == 1000
        assert mock_ship.manifest == {}
        mock_ship.save.assert_not_called()


class TestUnloadMocked:
    def test_unload_tui_moves_resource_from_ship_to_player(
        self, mock_args, mock_player, mock_ship
    ):
        mock_ship.manifest = {"grain": {"value": 200}}
        mock_player.grain = 0
        with (
            patch(
                "empyre.ship.unload.manifest.select_item",
                return_value=listbox_selected("grain"),
            ),
            patch("empyre.ship.unload.io.inputinteger", return_value=50),
            patch("empyre.ship.unload.database.commit"),
        ):
            result = ship_unload.main(
                mock_args, player=mock_player, ship=mock_ship, pool=None
            )

        assert result is True
        assert mock_ship.manifest == {"grain": {"value": 150}}
        assert mock_player.grain == 50
        mock_ship.save.assert_called_once()

    def test_unload_tui_reduces_manifest_to_zero(
        self, mock_args, mock_player, mock_ship
    ):
        mock_ship.manifest = {"grain": {"value": 10}}
        mock_player.grain = 0
        with (
            patch(
                "empyre.ship.unload.manifest.select_item",
                return_value=listbox_selected("grain"),
            ),
            patch("empyre.ship.unload.io.inputinteger", return_value=10),
            patch("empyre.ship.unload.database.commit"),
        ):
            result = ship_unload.main(
                mock_args, player=mock_player, ship=mock_ship, pool=None
            )

        assert result is True
        assert mock_ship.manifest == {"grain": {"value": 0}}
        assert mock_player.grain == 10
        mock_ship.save.assert_called_once()

    def test_unload_tui_aborts_on_cancelled_selection(
        self, mock_args, mock_player, mock_ship
    ):
        mock_ship.manifest = {"grain": {"value": 100}}
        with (
            patch(
                "empyre.ship.unload.manifest.select_item",
                return_value=listbox_cancelled(),
            ),
            patch("empyre.ship.unload.database.commit"),
        ):
            result = ship_unload.main(
                mock_args, player=mock_player, ship=mock_ship, pool=None
            )

        assert result is True
        assert mock_ship.manifest == {"grain": {"value": 100}}
        mock_ship.save.assert_not_called()

    def test_unload_tui_aborts_on_amount_exceeds_manifest(
        self, mock_args, mock_player, mock_ship
    ):
        mock_ship.manifest = {"grain": {"value": 10}}
        mock_player.grain = 0
        with (
            patch(
                "empyre.ship.unload.manifest.select_item",
                return_value=listbox_selected("grain"),
            ),
            patch("empyre.ship.unload.io.inputinteger", return_value=100),
            patch("empyre.ship.unload.database.commit"),
        ):
            result = ship_unload.main(
                mock_args, player=mock_player, ship=mock_ship, pool=None
            )

        assert result is True
        assert mock_ship.manifest == {"grain": {"value": 10}}
        assert mock_player.grain == 0
        mock_ship.save.assert_not_called()

    def test_unload_tui_aborts_on_negative_amount(
        self, mock_args, mock_player, mock_ship
    ):
        mock_ship.manifest = {"grain": {"value": 100}}
        with (
            patch(
                "empyre.ship.unload.manifest.select_item",
                return_value=listbox_selected("grain"),
            ),
            patch("empyre.ship.unload.io.inputinteger", return_value=-5),
            patch("empyre.ship.unload.database.commit"),
        ):
            result = ship_unload.main(
                mock_args, player=mock_player, ship=mock_ship, pool=None
            )

        assert result is True
        assert mock_ship.manifest == {"grain": {"value": 100}}
        mock_ship.save.assert_not_called()

    def test_unload_tui_aborts_on_amount_zero(self, mock_args, mock_player, mock_ship):
        mock_ship.manifest = {"grain": {"value": 100}}
        with (
            patch(
                "empyre.ship.unload.manifest.select_item",
                return_value=listbox_selected("grain"),
            ),
            patch("empyre.ship.unload.io.inputinteger", return_value=0),
            patch("empyre.ship.unload.database.commit"),
        ):
            result = ship_unload.main(
                mock_args, player=mock_player, ship=mock_ship, pool=None
            )

        assert result is True
        assert mock_ship.manifest == {"grain": {"value": 100}}
        mock_ship.save.assert_not_called()

    def test_unload_tui_aborts_on_amount_none(self, mock_args, mock_player, mock_ship):
        mock_ship.manifest = {"grain": {"value": 100}}
        with (
            patch(
                "empyre.ship.unload.manifest.select_item",
                return_value=listbox_selected("grain"),
            ),
            patch("empyre.ship.unload.io.inputinteger", return_value=None),
            patch("empyre.ship.unload.database.commit"),
        ):
            result = ship_unload.main(
                mock_args, player=mock_player, ship=mock_ship, pool=None
            )

        assert result is True
        assert mock_ship.manifest == {"grain": {"value": 100}}
        mock_ship.save.assert_not_called()


class TestCountMocked:
    def test_count_returns_zero_when_no_pool(self, mock_args):
        result = count(mock_args, "any_player", pool=None)
        assert result == 0

    def test_count_returns_value_from_cursor(self, mock_args, mock_pool):
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = {"cnt": 5}
        mock_cursor_ctx = MagicMock()
        mock_cursor_ctx.__enter__ = MagicMock(return_value=mock_cur)
        mock_cursor_ctx.__exit__ = MagicMock(return_value=False)

        with (
            patch("empyre.ship.lib.database.cursor", return_value=mock_cursor_ctx),
            patch("empyre.ship.lib.database.connect") as mock_connect,
        ):
            mock_conn = MagicMock()
            mock_connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
            mock_connect.return_value.__exit__ = MagicMock(return_value=False)
            result = count(mock_args, "test_player", pool=mock_pool)

        assert result == 5

    def test_count_returns_zero_when_no_row(self, mock_args, mock_pool):
        mock_cur = MagicMock()
        mock_cur.fetchone.return_value = None
        mock_cursor_ctx = MagicMock()
        mock_cursor_ctx.__enter__ = MagicMock(return_value=mock_cur)
        mock_cursor_ctx.__exit__ = MagicMock(return_value=False)

        with (
            patch("empyre.ship.lib.database.cursor", return_value=mock_cursor_ctx),
            patch("empyre.ship.lib.database.connect") as mock_connect,
        ):
            mock_conn = MagicMock()
            mock_connect.return_value.__enter__ = MagicMock(return_value=mock_conn)
            mock_connect.return_value.__exit__ = MagicMock(return_value=False)
            result = count(mock_args, "test_player", pool=mock_pool)

        assert result == 0
