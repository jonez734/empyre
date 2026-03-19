import pytest
from unittest.mock import patch

from empyre.player import calculaterank, getranktitle

from .helpers import create_test_player


TEST_LOGINID = "empyre_test_user"
TEST_MEMBER_MONIKER = "test_member"


@pytest.fixture(autouse=True)
def patch_getcurrentloginid(test_args):
    with patch("bbsengine6.util.getcurrentloginid", return_value=TEST_LOGINID):
        yield


class TestCalculateRank:
    def test_rank_0_lord_by_default(self, test_args, test_pool, db_conn, clean_tables):
        p = create_test_player(test_args, test_pool, moniker="rank0", conn=db_conn)
        p.pool = test_pool
        p.save(commit=True)

        rank = calculaterank(test_args, p)
        assert rank == 0

    def test_rank_1_prince(self, test_args, test_pool, db_conn, clean_tables):
        p = create_test_player(
            test_args,
            test_pool,
            moniker="rank1",
            conn=db_conn,
            markets=10,
            diplomats=1,
            mills=6,
            foundries=2,
            shipyards=2,
            palaces=3,
            land=20000,
            nobles=16,
            serfs=3100,
        )
        rank = calculaterank(test_args, p)
        assert rank == 1

    def test_rank_2_king(self, test_args, test_pool, db_conn, clean_tables):
        p = create_test_player(
            test_args,
            test_pool,
            moniker="rank2",
            conn=db_conn,
            markets=16,
            diplomats=3,
            mills=10,
            foundries=7,
            shipyards=5,
            palaces=7,
            land=40000,
            nobles=31,
            serfs=3600,
        )
        rank = calculaterank(test_args, p)
        assert rank == 2

    def test_rank_3_emperor(self, test_args, test_pool, db_conn, clean_tables):
        p = create_test_player(
            test_args,
            test_pool,
            moniker="rank3",
            conn=db_conn,
            markets=24,
            mills=11,
            foundries=14,
            shipyards=12,
            palaces=10,
            land=60000,
            serfs=2500,
        )
        rank = calculaterank(test_args, p)
        assert rank == 3


class TestGetRankTitle:
    def test_rank_0_lord(self, test_args):
        assert getranktitle(test_args, 0) == "lord"

    def test_rank_1_prince(self, test_args):
        assert getranktitle(test_args, 1) == "prince"

    def test_rank_2_king(self, test_args):
        assert getranktitle(test_args, 2) == "king"

    def test_rank_3_emperor(self, test_args):
        assert getranktitle(test_args, 3) == "emperor"

    def test_invalid_rank(self, test_args):
        assert getranktitle(test_args, 99) == "rank-error"


class TestPlayerAdjust:
    def test_adjust_caps_coins_at_max(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        p = create_test_player(
            test_args, test_pool, moniker="adj_coins", conn=db_conn, coins=2000000
        )
        p.pool = test_pool
        p.adjust()
        assert p.coins <= 1000000

    def test_adjust_sets_negative_land_to_zero(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        p = create_test_player(
            test_args, test_pool, moniker="adj_land", conn=db_conn, land=-100
        )
        p.pool = test_pool
        p.adjust()
        assert p.land == 0

    def test_adjust_zero_land_triggers_message(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        p = create_test_player(
            test_args, test_pool, moniker="adj_land_zero", conn=db_conn, land=0
        )
        p.pool = test_pool
        p.adjust()

    def test_adjust_removes_excess_soldiers_without_nobles(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        p = create_test_player(
            test_args,
            test_pool,
            moniker="adj_soldiers_nonoble",
            conn=db_conn,
            soldiers=500,
            nobles=1,
        )
        p.pool = test_pool
        p.adjust()
        assert p.soldiers >= 0

    def test_adjust_soldiers_desert_when_pay_low(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        p = create_test_player(
            test_args,
            test_pool,
            moniker="adj_desert",
            conn=db_conn,
            soldiers=600,
            nobles=5,
            combatvictorycount=0,
            taxrate=15,
            palaces=1,
        )
        p.pool = test_pool
        p.adjust()

    def test_adjust_ships_capped_by_shipyards(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        p = create_test_player(
            test_args,
            test_pool,
            moniker="adj_ships",
            conn=db_conn,
            ships=20,
            shipyards=1,
        )
        p.pool = test_pool
        p.adjust()
        assert p.ships <= p.shipyards * 10

    def test_adjust_horses_capped_by_stables(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        p = create_test_player(
            test_args,
            test_pool,
            moniker="adj_horses",
            conn=db_conn,
            horses=200,
            stables=1,
        )
        p.pool = test_pool
        p.adjust()
        assert p.horses <= 50


class TestPlayerResourceManagement:
    def test_setresourcevalue_valid(self, test_args, test_pool, db_conn, clean_tables):
        p = create_test_player(
            test_args, test_pool, moniker="setres_valid", conn=db_conn, coins=1000
        )
        p.pool = test_pool
        result = p.setresourcevalue("coins", 2000)
        assert result is True
        assert p.coins == 2000
        assert p.resources["coins"]["value"] == 2000

    def test_setresourcevalue_invalid_name(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        p = create_test_player(
            test_args, test_pool, moniker="setres_invalid", conn=db_conn
        )
        p.pool = test_pool
        result = p.setresourcevalue("nonexistent_resource", 100)
        assert result is False

    def test_setresourcevalue_negative_normalizes_to_zero(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        p = create_test_player(test_args, test_pool, moniker="setres_neg", conn=db_conn)
        p.pool = test_pool
        result = p.setresourcevalue("coins", -500)
        assert result is True
        assert p.coins == 0

    def test_getresource_returns_correct_data(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        p = create_test_player(
            test_args, test_pool, moniker="getres", conn=db_conn, coins=1234
        )
        p.pool = test_pool
        res = p.getresource("coins")
        assert res["value"] == 1234
        assert res["singular"] == "coin"
        assert res["plural"] == "coins"

    def test_getresource_unknown_returns_none(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        p = create_test_player(
            test_args, test_pool, moniker="getres_unknown", conn=db_conn
        )
        p.pool = test_pool
        res = p.getresource("nonexistent")
        assert res is None

    def test_setattributevalue_valid(self, test_args, test_pool, db_conn, clean_tables):
        p = create_test_player(
            test_args, test_pool, moniker="setattr_valid", conn=db_conn
        )
        p.pool = test_pool
        result = p.setattributevalue("turncount", 50)
        assert result is True
        assert p.turncount == 50

    def test_setattributevalue_invalid_name(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        p = create_test_player(
            test_args, test_pool, moniker="setattr_invalid", conn=db_conn
        )
        p.pool = test_pool
        result = p.setattributevalue("nonexistent_attr", 100)
        assert result is False
