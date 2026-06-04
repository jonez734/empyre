import pytest
from unittest.mock import patch

from empyre.ship import load as ship_load
from empyre.ship import sail as ship_sail
from empyre.ship import unload as ship_unload
from empyre.ship.lib import (
    Ship,
    create,
    load,
    count,
    runmodule as ship_runmodule,
    verifyShipNameFound,
    verifyShipNameNotFound,
)
from bbsengine6 import member as member_module
from bbsengine6.listbox import ListboxItem, ListboxResult

from .helpers import create_test_ship


TEST_LOGINID = "empyre_test_user"
TEST_MEMBER_MONIKER = "test_member"


def _listbox_selected(pk: str) -> ListboxResult:
    """Build a ListboxResult('selected', ListboxItem(pk=pk)) for mocking."""
    item = ListboxItem()
    item.pk = pk
    return ListboxResult("selected", item)


def _listbox_cancelled() -> ListboxResult:
    return ListboxResult("cancelled")


@pytest.fixture(autouse=True)
def patch_getcurrentloginid():
    with patch("bbsengine6.util.getcurrentloginid", return_value=TEST_LOGINID):
        yield


@pytest.fixture(autouse=True)
def patch_getcurrentmoniker():
    with patch.object(
        member_module, "getcurrentmoniker", return_value=TEST_MEMBER_MONIKER
    ):
        yield


@pytest.fixture
def player_with_shipyard(test_player):
    test_player.shipyards = 1
    test_player.ships = 0
    return test_player


@pytest.fixture
def player_with_grain(player_with_shipyard):
    player_with_shipyard.grain = 1000
    return player_with_shipyard


class TestShipCreateIntegration:
    def test_create_inserts_ship(
        self, test_args, test_pool, db_conn, clean_tables, player_with_shipyard
    ):
        ship = create(
            test_args,
            player=player_with_shipyard,
            pool=test_pool,
            moniker="my_test_ship",
            kind="cargo",
            location="mainland",
        )

        assert ship is not None
        assert ship.moniker == "my_test_ship"
        assert ship.kind == "cargo"
        assert ship.location == "mainland"
        assert ship.status == "build"
        assert ship.playermoniker == "test_player"

        loaded = load(test_args, "my_test_ship", pool=test_pool)
        assert loaded is not None
        assert loaded.moniker == "my_test_ship"
        assert loaded.kind == "cargo"
        assert loaded.location == "mainland"

    def test_create_returns_none_when_no_pool(self, test_args, test_player):
        ship = create(test_args, player=test_player, pool=None, moniker="orphan")
        assert ship is None

    def test_create_returns_none_when_no_player(self, test_args, test_pool):
        ship = create(test_args, player=None, pool=test_pool, moniker="orphan")
        assert ship is None

    def test_create_returns_none_when_over_capacity(
        self, test_args, test_pool, db_conn, clean_tables, test_player
    ):
        test_player.shipyards = 0
        test_player.ships = 0
        ship = create(
            test_args,
            player=test_player,
            pool=test_pool,
            moniker="overflow_ship",
        )
        assert ship is None

    def test_create_sets_all_attributes(
        self, test_args, test_pool, db_conn, clean_tables, player_with_shipyard
    ):
        manifest = {"grain": {"value": 500}}
        ship = create(
            test_args,
            player=player_with_shipyard,
            pool=test_pool,
            moniker="attr_ship",
            kind="passenger",
            manifest=manifest,
            navigator=True,
            location="island_a",
            status="docked",
        )

        assert ship.moniker == "attr_ship"
        assert ship.kind == "passenger"
        assert ship.manifest == manifest
        assert ship.navigator is True
        assert ship.location == "island_a"
        assert ship.status == "docked"

        loaded = load(test_args, "attr_ship", pool=test_pool)
        assert loaded.kind == "passenger"
        assert loaded.navigator is True
        assert loaded.location == "island_a"

    def test_create_increments_player_ships_count(
        self, test_args, test_pool, db_conn, clean_tables, player_with_shipyard
    ):
        create_test_ship(
            test_args,
            test_pool,
            moniker="counted_ship_1",
            playermoniker="test_player",
            createdbymoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
            player=player_with_shipyard,
        )
        create_test_ship(
            test_args,
            test_pool,
            moniker="counted_ship_2",
            playermoniker="test_player",
            createdbymoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
            player=player_with_shipyard,
        )
        db_conn.commit()

        ship = create_test_ship(
            test_args,
            test_pool,
            moniker="counted_ship_3",
            playermoniker="test_player",
            createdbymoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
            player=player_with_shipyard,
        )

        player_with_shipyard.ships = 0
        ship.adjust()
        assert player_with_shipyard.ships == 3


class TestShipLoadIntegration:
    def test_load_returns_ship(
        self, test_args, test_pool, db_conn, clean_tables, player_with_shipyard
    ):
        create_test_ship(
            test_args,
            test_pool,
            moniker="load_me",
            playermoniker="test_player",
            createdbymoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
            kind="carrier",
            manifest={"soldiers": {"value": 50}},
            navigator=True,
            location="harbor",
            status="docked",
        )
        db_conn.commit()

        loaded = load(test_args, "load_me", pool=test_pool)

        assert loaded is not None
        assert loaded.moniker == "load_me"
        assert loaded.kind == "carrier"
        assert loaded.navigator is True
        assert loaded.location == "harbor"
        assert loaded.status == "docked"
        assert loaded.playermoniker == "test_player"

    def test_load_returns_none_when_not_found(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        result = load(test_args, "nonexistent_ship_xyz", pool=test_pool)
        assert result is None

    def test_load_returns_none_when_no_pool(self, test_args, test_player):
        result = load(test_args, "any_ship", pool=None)
        assert result is None


class TestShipSaveIntegration:
    def test_save_updates_existing_ship(
        self, test_args, test_pool, db_conn, clean_tables, player_with_shipyard
    ):
        ship = create_test_ship(
            test_args,
            test_pool,
            moniker="update_me",
            playermoniker="test_player",
            createdbymoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
            kind="cargo",
            manifest={},
        )
        db_conn.commit()

        ship.kind = "carrier"
        ship.manifest = {"grain": {"value": 1000}}
        ship.navigator = True
        ship.location = "distant_shore"
        ship.save(commit=True)

        loaded = load(test_args, "update_me", pool=test_pool)
        assert loaded.kind == "carrier"
        assert loaded.navigator is True
        assert loaded.location == "distant_shore"
        assert loaded.manifest == {"grain": {"value": 1000}}

    def test_save_with_commit_false_rollback(
        self, test_args, test_pool, db_conn, clean_tables, player_with_shipyard
    ):
        ship = create_test_ship(
            test_args,
            test_pool,
            moniker="rollback_ship",
            playermoniker="test_player",
            createdbymoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
            kind="cargo",
        )
        db_conn.commit()

        ship.kind = "carrier"
        ship.save(commit=False, conn=db_conn)
        db_conn.rollback()

        loaded = load(test_args, "rollback_ship", pool=test_pool)
        assert loaded.kind == "cargo"

    def test_save_preserves_playermoniker(
        self, test_args, test_pool, db_conn, clean_tables, player_with_shipyard
    ):
        ship = create_test_ship(
            test_args,
            test_pool,
            moniker="owned_ship",
            playermoniker="test_player",
            createdbymoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
        )
        db_conn.commit()

        ship.location = "new_port"
        ship.save(commit=True)

        loaded = load(test_args, "owned_ship", pool=test_pool)
        assert loaded.playermoniker == "test_player"


class TestShipCountIntegration:
    def test_count_returns_count(
        self, test_args, test_pool, db_conn, clean_tables, player_with_shipyard
    ):
        create_test_ship(
            test_args,
            test_pool,
            moniker="count_ship_1",
            playermoniker="test_player",
            createdbymoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
        )
        create_test_ship(
            test_args,
            test_pool,
            moniker="count_ship_2",
            playermoniker="test_player",
            createdbymoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
        )
        db_conn.commit()

        result = count(test_args, "test_player", pool=test_pool)
        assert result == 2

    def test_count_returns_zero_for_nonexistent_player(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        result = count(test_args, "nonexistent_player_xyz", pool=test_pool)
        assert result == 0

    def test_count_returns_zero_when_no_pool(self, test_args):
        result = count(test_args, "any_player", pool=None)
        assert result == 0


class TestShipVerifyIntegration:
    def test_verify_ship_name_found(
        self, test_args, test_pool, db_conn, clean_tables, player_with_shipyard
    ):
        create_test_ship(
            test_args,
            test_pool,
            moniker="found_ship",
            playermoniker="test_player",
            createdbymoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
        )
        db_conn.commit()

        result = verifyShipNameFound(test_args, "found_ship", pool=test_pool)
        assert result is False

    def test_verify_ship_name_not_found(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        result = verifyShipNameNotFound(
            test_args, "available_ship_name", pool=test_pool
        )
        assert result is True


class TestShipAdjustIntegration:
    def test_adjust_updates_player_ships_count(
        self, test_args, test_pool, db_conn, clean_tables, player_with_shipyard
    ):
        create_test_ship(
            test_args,
            test_pool,
            moniker="adjust_ship_1",
            playermoniker="test_player",
            createdbymoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
            player=player_with_shipyard,
        )
        create_test_ship(
            test_args,
            test_pool,
            moniker="adjust_ship_2",
            playermoniker="test_player",
            createdbymoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
            player=player_with_shipyard,
        )
        db_conn.commit()

        player_with_shipyard.ships = 0
        ship = create_test_ship(
            test_args,
            test_pool,
            moniker="adjust_ship_3",
            playermoniker="test_player",
            createdbymoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
            player=player_with_shipyard,
        )

        ship.adjust()

        assert player_with_shipyard.ships == 3


class TestShipAttributes:
    def test_ship_init_sets_default_attributes(self, test_args):
        ship = Ship(test_args)

        assert ship.moniker is None
        assert ship.kind == "cargo"
        assert ship.manifest == {}
        assert ship.navigator is False
        assert ship.status is None
        assert ship.datedocked is None
        assert ship.datecreated is None

    def test_ship_allows_arbitrary_attribute_assignment(self, test_args):
        ship = Ship(test_args)
        ship.moniker = "My Ship"
        ship.kind = "carrier"
        ship.navigator = True
        ship.location = "harbor"
        ship.playermoniker = "player1"

        assert ship.moniker == "My Ship"
        assert ship.kind == "carrier"
        assert ship.navigator is True
        assert ship.location == "harbor"
        assert ship.playermoniker == "player1"


class TestShipLoadTUI:
    """Tests empyre.ship.load.main() with real DB and mocked interactive IO."""

    def test_load_tui_moves_resource_from_player_to_ship(
        self, test_args, test_pool, db_conn, clean_tables, player_with_grain
    ):
        create_test_ship(
            test_args,
            test_pool,
            moniker="load_tui_ship",
            playermoniker="test_player",
            createdbymoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
            kind="cargo",
            manifest={},
            status="docked",
        )
        db_conn.commit()

        ship = load(test_args, "load_tui_ship", pool=test_pool)
        with (
            patch(
                "empyre.ship.load.libempyre.selectresource",
                return_value=_listbox_selected("grain"),
            ),
            patch("empyre.ship.load.io.inputinteger", return_value=100),
        ):
            ship_load.main(
                test_args, player=player_with_grain, ship=ship, pool=test_pool
            )

        reloaded = load(test_args, "load_tui_ship", pool=test_pool)
        assert reloaded.manifest == {"grain": {"value": 100}}
        assert player_with_grain.grain == 900

    def test_load_tui_appends_to_existing_manifest_entry(
        self, test_args, test_pool, db_conn, clean_tables, player_with_grain
    ):
        create_test_ship(
            test_args,
            test_pool,
            moniker="load_tui_ship_existing",
            playermoniker="test_player",
            createdbymoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
            kind="cargo",
            manifest={"grain": {"value": 50}},
            status="docked",
        )
        db_conn.commit()

        ship = load(test_args, "load_tui_ship_existing", pool=test_pool)
        with (
            patch(
                "empyre.ship.load.libempyre.selectresource",
                return_value=_listbox_selected("grain"),
            ),
            patch("empyre.ship.load.io.inputinteger", return_value=25),
        ):
            ship_load.main(
                test_args, player=player_with_grain, ship=ship, pool=test_pool
            )

        reloaded = load(test_args, "load_tui_ship_existing", pool=test_pool)
        assert reloaded.manifest == {"grain": {"value": 75}}
        assert player_with_grain.grain == 975

    def test_load_tui_creates_new_manifest_entry(
        self, test_args, test_pool, db_conn, clean_tables, player_with_shipyard
    ):
        create_test_ship(
            test_args,
            test_pool,
            moniker="load_tui_ship_new",
            playermoniker="test_player",
            createdbymoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
            kind="cargo",
            manifest={},
            status="docked",
        )
        db_conn.commit()
        player_with_shipyard.gold = 1000

        ship = load(test_args, "load_tui_ship_new", pool=test_pool)
        with (
            patch(
                "empyre.ship.load.libempyre.selectresource",
                return_value=_listbox_selected("gold"),
            ),
            patch("empyre.ship.load.io.inputinteger", return_value=10),
        ):
            ship_load.main(
                test_args, player=player_with_shipyard, ship=ship, pool=test_pool
            )

        reloaded = load(test_args, "load_tui_ship_new", pool=test_pool)
        assert reloaded.manifest == {"gold": {"value": 10}}
        assert player_with_shipyard.gold == 990

    def test_load_tui_aborts_when_resource_selection_cancelled(
        self, test_args, test_pool, db_conn, clean_tables, player_with_grain
    ):
        create_test_ship(
            test_args,
            test_pool,
            moniker="load_tui_ship_cancel",
            playermoniker="test_player",
            createdbymoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
            kind="cargo",
            manifest={},
            status="docked",
        )
        db_conn.commit()

        ship = load(test_args, "load_tui_ship_cancel", pool=test_pool)
        with patch(
            "empyre.ship.load.libempyre.selectresource",
            return_value=_listbox_cancelled(),
        ):
            ship_load.main(
                test_args, player=player_with_grain, ship=ship, pool=test_pool
            )

        reloaded = load(test_args, "load_tui_ship_cancel", pool=test_pool)
        assert reloaded.manifest == {}
        assert player_with_grain.grain == 1000

    def test_load_tui_aborts_when_amount_is_none(
        self, test_args, test_pool, db_conn, clean_tables, player_with_grain
    ):
        create_test_ship(
            test_args,
            test_pool,
            moniker="load_tui_ship_none",
            playermoniker="test_player",
            createdbymoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
            kind="cargo",
            manifest={},
            status="docked",
        )
        db_conn.commit()

        ship = load(test_args, "load_tui_ship_none", pool=test_pool)
        with (
            patch(
                "empyre.ship.load.libempyre.selectresource",
                return_value=_listbox_selected("grain"),
            ),
            patch("empyre.ship.load.io.inputinteger", return_value=None),
        ):
            ship_load.main(
                test_args, player=player_with_grain, ship=ship, pool=test_pool
            )

        reloaded = load(test_args, "load_tui_ship_none", pool=test_pool)
        assert reloaded.manifest == {}
        assert player_with_grain.grain == 1000

    def test_load_tui_aborts_when_amount_is_negative(
        self, test_args, test_pool, db_conn, clean_tables, player_with_grain
    ):
        create_test_ship(
            test_args,
            test_pool,
            moniker="load_tui_ship_neg",
            playermoniker="test_player",
            createdbymoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
            kind="cargo",
            manifest={},
            status="docked",
        )
        db_conn.commit()

        ship = load(test_args, "load_tui_ship_neg", pool=test_pool)
        with (
            patch(
                "empyre.ship.load.libempyre.selectresource",
                return_value=_listbox_selected("grain"),
            ),
            patch("empyre.ship.load.io.inputinteger", return_value=-5),
        ):
            ship_load.main(
                test_args, player=player_with_grain, ship=ship, pool=test_pool
            )

        reloaded = load(test_args, "load_tui_ship_neg", pool=test_pool)
        assert reloaded.manifest == {}
        assert player_with_grain.grain == 1000

    def test_load_tui_aborts_when_amount_exceeds_player_resources(
        self, test_args, test_pool, db_conn, clean_tables, player_with_grain
    ):
        create_test_ship(
            test_args,
            test_pool,
            moniker="load_tui_ship_short",
            playermoniker="test_player",
            createdbymoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
            kind="cargo",
            manifest={},
            status="docked",
        )
        db_conn.commit()
        player_with_grain.grain = 10

        ship = load(test_args, "load_tui_ship_short", pool=test_pool)
        with (
            patch(
                "empyre.ship.load.libempyre.selectresource",
                return_value=_listbox_selected("grain"),
            ),
            patch("empyre.ship.load.io.inputinteger", return_value=100),
        ):
            ship_load.main(
                test_args, player=player_with_grain, ship=ship, pool=test_pool
            )

        reloaded = load(test_args, "load_tui_ship_short", pool=test_pool)
        assert reloaded.manifest == {}
        assert player_with_grain.grain == 10


class TestShipUnloadTUI:
    """Tests empyre.ship.unload.main() with real DB and mocked interactive IO."""

    def test_unload_tui_moves_resource_from_ship_to_player(
        self, test_args, test_pool, db_conn, clean_tables, player_with_grain
    ):
        create_test_ship(
            test_args,
            test_pool,
            moniker="unload_tui_ship",
            playermoniker="test_player",
            createdbymoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
            kind="cargo",
            manifest={"grain": {"value": 200}},
            status="docked",
        )
        db_conn.commit()
        player_with_grain.grain = 0

        ship = load(test_args, "unload_tui_ship", pool=test_pool)
        with (
            patch(
                "empyre.ship.unload.manifest.select_item",
                return_value=_listbox_selected("grain"),
            ),
            patch("empyre.ship.unload.io.inputinteger", return_value=50),
        ):
            ship_unload.main(
                test_args, player=player_with_grain, ship=ship, pool=test_pool
            )

        reloaded = load(test_args, "unload_tui_ship", pool=test_pool)
        assert reloaded.manifest == {"grain": {"value": 150}}
        assert player_with_grain.grain == 50

    def test_unload_tui_reduces_manifest_to_zero(
        self, test_args, test_pool, db_conn, clean_tables, player_with_grain
    ):
        create_test_ship(
            test_args,
            test_pool,
            moniker="unload_tui_ship_zero",
            playermoniker="test_player",
            createdbymoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
            kind="cargo",
            manifest={"grain": {"value": 10}},
            status="docked",
        )
        db_conn.commit()
        player_with_grain.grain = 0

        ship = load(test_args, "unload_tui_ship_zero", pool=test_pool)
        with (
            patch(
                "empyre.ship.unload.manifest.select_item",
                return_value=_listbox_selected("grain"),
            ),
            patch("empyre.ship.unload.io.inputinteger", return_value=10),
        ):
            ship_unload.main(
                test_args, player=player_with_grain, ship=ship, pool=test_pool
            )

        reloaded = load(test_args, "unload_tui_ship_zero", pool=test_pool)
        assert reloaded.manifest == {"grain": {"value": 0}}
        assert player_with_grain.grain == 10

    def test_unload_tui_aborts_when_manifest_selection_cancelled(
        self, test_args, test_pool, db_conn, clean_tables, player_with_grain
    ):
        create_test_ship(
            test_args,
            test_pool,
            moniker="unload_tui_ship_cancel",
            playermoniker="test_player",
            createdbymoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
            kind="cargo",
            manifest={"grain": {"value": 100}},
            status="docked",
        )
        db_conn.commit()

        ship = load(test_args, "unload_tui_ship_cancel", pool=test_pool)
        with patch(
            "empyre.ship.unload.manifest.select_item", return_value=_listbox_cancelled()
        ):
            ship_unload.main(
                test_args, player=player_with_grain, ship=ship, pool=test_pool
            )

        reloaded = load(test_args, "unload_tui_ship_cancel", pool=test_pool)
        assert reloaded.manifest == {"grain": {"value": 100}}

    def test_unload_tui_aborts_when_amount_is_none(
        self, test_args, test_pool, db_conn, clean_tables, player_with_grain
    ):
        create_test_ship(
            test_args,
            test_pool,
            moniker="unload_tui_ship_none",
            playermoniker="test_player",
            createdbymoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
            kind="cargo",
            manifest={"grain": {"value": 100}},
            status="docked",
        )
        db_conn.commit()

        ship = load(test_args, "unload_tui_ship_none", pool=test_pool)
        with (
            patch(
                "empyre.ship.unload.manifest.select_item",
                return_value=_listbox_selected("grain"),
            ),
            patch("empyre.ship.unload.io.inputinteger", return_value=None),
        ):
            ship_unload.main(
                test_args, player=player_with_grain, ship=ship, pool=test_pool
            )

        reloaded = load(test_args, "unload_tui_ship_none", pool=test_pool)
        assert reloaded.manifest == {"grain": {"value": 100}}

    def test_unload_tui_aborts_when_amount_is_zero(
        self, test_args, test_pool, db_conn, clean_tables, player_with_grain
    ):
        create_test_ship(
            test_args,
            test_pool,
            moniker="unload_tui_ship_zeroamt",
            playermoniker="test_player",
            createdbymoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
            kind="cargo",
            manifest={"grain": {"value": 100}},
            status="docked",
        )
        db_conn.commit()

        ship = load(test_args, "unload_tui_ship_zeroamt", pool=test_pool)
        with (
            patch(
                "empyre.ship.unload.manifest.select_item",
                return_value=_listbox_selected("grain"),
            ),
            patch("empyre.ship.unload.io.inputinteger", return_value=0),
        ):
            ship_unload.main(
                test_args, player=player_with_grain, ship=ship, pool=test_pool
            )

        reloaded = load(test_args, "unload_tui_ship_zeroamt", pool=test_pool)
        assert reloaded.manifest == {"grain": {"value": 100}}

    def test_unload_tui_aborts_when_amount_is_negative(
        self, test_args, test_pool, db_conn, clean_tables, player_with_grain
    ):
        create_test_ship(
            test_args,
            test_pool,
            moniker="unload_tui_ship_neg",
            playermoniker="test_player",
            createdbymoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
            kind="cargo",
            manifest={"grain": {"value": 100}},
            status="docked",
        )
        db_conn.commit()

        ship = load(test_args, "unload_tui_ship_neg", pool=test_pool)
        with (
            patch(
                "empyre.ship.unload.manifest.select_item",
                return_value=_listbox_selected("grain"),
            ),
            patch("empyre.ship.unload.io.inputinteger", return_value=-5),
        ):
            ship_unload.main(
                test_args, player=player_with_grain, ship=ship, pool=test_pool
            )

        reloaded = load(test_args, "unload_tui_ship_neg", pool=test_pool)
        assert reloaded.manifest == {"grain": {"value": 100}}

    def test_unload_tui_aborts_when_amount_exceeds_manifest(
        self, test_args, test_pool, db_conn, clean_tables, player_with_grain
    ):
        create_test_ship(
            test_args,
            test_pool,
            moniker="unload_tui_ship_over",
            playermoniker="test_player",
            createdbymoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
            kind="cargo",
            manifest={"grain": {"value": 10}},
            status="docked",
        )
        db_conn.commit()

        ship = load(test_args, "unload_tui_ship_over", pool=test_pool)
        with (
            patch(
                "empyre.ship.unload.manifest.select_item",
                return_value=_listbox_selected("grain"),
            ),
            patch("empyre.ship.unload.io.inputinteger", return_value=100),
        ):
            ship_unload.main(
                test_args, player=player_with_grain, ship=ship, pool=test_pool
            )

        reloaded = load(test_args, "unload_tui_ship_over", pool=test_pool)
        assert reloaded.manifest == {"grain": {"value": 10}}


class TestShipSailTUI:
    """Tests empyre.ship.sail.main() (dispatch only — sail is currently a stub)."""

    def test_sail_main_returns_true_with_valid_inputs(self, test_args):
        class FakeShip:
            moniker = "any_ship"

        class FakePlayer:
            moniker = "any_player"

        result = ship_sail.main(
            test_args, player=FakePlayer(), ship=FakeShip(), pool=None
        )
        assert result is True

    def test_sail_main_returns_false_without_player(self, test_args):
        class FakeShip:
            moniker = "any_ship"

        result = ship_sail.main(test_args, ship=FakeShip(), pool=None)
        assert result is False

    def test_sail_main_returns_false_without_ship(self, test_args):
        class FakePlayer:
            moniker = "any_player"

        result = ship_sail.main(test_args, player=FakePlayer(), pool=None)
        assert result is False


class TestShipRunmoduleDispatch:
    """Tests empyre.ship.lib.runmodule() dispatches to the correct submodule."""

    def test_runmodule_dispatches_to_ship_load(self, test_args, test_pool):
        with patch(
            "empyre.ship.lib.libempyre.runmodule", return_value=True
        ) as mock_dispatch:
            ship_runmodule(
                test_args, "load", ship=object(), player=object(), pool=test_pool
            )

        mock_dispatch.assert_called_once()
        args, kwargs = mock_dispatch.call_args[0], mock_dispatch.call_args[1]
        assert args[1] == "ship.load"
        assert kwargs.get("ship") is not None
        assert kwargs.get("player") is not None
        assert kwargs.get("pool") is test_pool

    def test_runmodule_dispatches_to_ship_unload(self, test_args, test_pool):
        with patch(
            "empyre.ship.lib.libempyre.runmodule", return_value=True
        ) as mock_dispatch:
            ship_runmodule(
                test_args, "unload", ship=object(), player=object(), pool=test_pool
            )

        args, _ = mock_dispatch.call_args[0], mock_dispatch.call_args[1]
        assert args[1] == "ship.unload"

    def test_runmodule_dispatches_to_ship_sail(self, test_args, test_pool):
        with patch(
            "empyre.ship.lib.libempyre.runmodule", return_value=True
        ) as mock_dispatch:
            ship_runmodule(
                test_args, "sail", ship=object(), player=object(), pool=test_pool
            )

        args, _ = mock_dispatch.call_args[0], mock_dispatch.call_args[1]
        assert args[1] == "ship.sail"

    def test_runmodule_passes_kwargs_through(self, test_args, test_pool):
        with patch(
            "empyre.ship.lib.libempyre.runmodule", return_value=True
        ) as mock_dispatch:
            marker_ship = object()
            marker_player = object()
            ship_runmodule(
                test_args,
                "sail",
                ship=marker_ship,
                player=marker_player,
                pool=test_pool,
            )

        kwargs = mock_dispatch.call_args[1]
        assert kwargs.get("ship") is marker_ship
        assert kwargs.get("player") is marker_player
        assert kwargs.get("pool") is test_pool


class TestShipFullLifecycleTUI:
    """End-to-end test: create a ship, load it, unload it, and sail."""

    def test_create_load_unload_sail_full_lifecycle(
        self, test_args, test_pool, db_conn, clean_tables, player_with_grain
    ):
        ship = create(
            test_args,
            player=player_with_grain,
            pool=test_pool,
            moniker="lifecycle_ship",
            kind="cargo",
            status="docked",
        )
        assert ship is not None
        assert ship.moniker == "lifecycle_ship"

        loaded = load(test_args, "lifecycle_ship", pool=test_pool)
        assert loaded is not None
        assert loaded.manifest == {}
        assert loaded.kind == "cargo"

        with (
            patch(
                "empyre.ship.load.libempyre.selectresource",
                return_value=_listbox_selected("grain"),
            ),
            patch("empyre.ship.load.io.inputinteger", return_value=100),
        ):
            ship_load.main(
                test_args, player=player_with_grain, ship=loaded, pool=test_pool
            )

        after_load = load(test_args, "lifecycle_ship", pool=test_pool)
        assert after_load.manifest == {"grain": {"value": 100}}

        with (
            patch(
                "empyre.ship.unload.manifest.select_item",
                return_value=_listbox_selected("grain"),
            ),
            patch("empyre.ship.unload.io.inputinteger", return_value=30),
        ):
            ship_unload.main(
                test_args, player=player_with_grain, ship=after_load, pool=test_pool
            )

        after_unload = load(test_args, "lifecycle_ship", pool=test_pool)
        assert after_unload.manifest == {"grain": {"value": 70}}

        result = ship_sail.main(
            test_args, player=player_with_grain, ship=after_unload, pool=test_pool
        )
        assert result is True
