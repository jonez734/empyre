import pytest
from unittest.mock import patch

from empyre.ship.lib import (
    Ship,
    create,
    load,
    count,
    verifyShipNameFound,
    verifyShipNameNotFound,
)
from bbsengine6 import member as member_module

from .helpers import create_test_ship


TEST_LOGINID = "empyre_test_user"
TEST_MEMBER_MONIKER = "test_member"


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


class TestShipCreateIntegration:
    def test_create_inserts_ship(self, test_args, test_pool, db_conn, clean_tables, player_with_shipyard):
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
        ship.save(commit=False)
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

        result = verifyShipNameFound(
            test_args, "found_ship", pool=test_pool
        )
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
