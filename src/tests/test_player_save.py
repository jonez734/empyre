import pytest
from unittest.mock import patch

from empyre.player import load, exists, count

from .helpers import create_test_player


TEST_LOGINID = "empyre_test_user"
TEST_MEMBER_MONIKER = "test_member"


@pytest.fixture(autouse=True)
def patch_getcurrentloginid(test_args):
    with patch("bbsengine6.util.getcurrentloginid", return_value=TEST_LOGINID):
        yield


class TestPlayerSaveIntegration:
    def test_save_inserts_new_player(self, test_args, test_pool, db_conn, clean_tables):
        p = create_test_player(
            test_args,
            test_pool,
            moniker="save_test_player",
            membermoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
        )
        p.pool = test_pool

        result = p.save(force=True, commit=True)

        assert result is True
        loaded = load(test_args, "save_test_player", pool=test_pool)
        assert loaded is not None
        assert loaded.moniker == "save_test_player"

    def test_save_updates_existing_player(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        p = create_test_player(
            test_args,
            test_pool,
            moniker="update_test_player",
            membermoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
            coins=1000,
        )
        p.pool = test_pool
        p.save(force=True, commit=True)

        p.coins = 2000
        result = p.save(commit=True)

        assert result is True
        loaded = load(test_args, "update_test_player", pool=test_pool)
        assert loaded.coins == 2000

    def test_save_skips_update_when_clean(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        p = create_test_player(
            test_args,
            test_pool,
            moniker="clean_player",
            membermoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
            insert=True,
        )
        p.pool = test_pool
        p.save(force=True, commit=True)
        assert p.isdirty() is False

        with patch("empyre.player.database") as mock_db:
            result = p.save(commit=True)
            mock_db.update.assert_not_called()
        assert result is None

    def test_save_returns_none_when_no_moniker(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        p = create_test_player(
            test_args,
            test_pool,
            moniker="nomark",
            membermoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
        )
        p.pool = test_pool
        p.moniker = None
        with patch("empyre.player.database") as mock_db:
            result = p.save(commit=True)
            mock_db.connect.assert_not_called()
        assert result is None

    def test_save_returns_none_when_no_membermoniker(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        p = create_test_player(
            test_args,
            test_pool,
            moniker="nomem",
            membermoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
        )
        p.pool = test_pool
        p.membermoniker = None
        with patch("empyre.player.database") as mock_db:
            result = p.save(commit=True)
            mock_db.connect.assert_not_called()
        assert result is None

    def test_save_with_commit_false_does_not_commit(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        p = create_test_player(
            test_args,
            test_pool,
            moniker="nocommit_player",
            membermoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
            insert=False,
        )
        p.pool = test_pool
        p.coins = 999
        result = p.save(force=True, commit=False)

        assert result is True
        db_conn.rollback()

        loaded = load(test_args, "nocommit_player", pool=test_pool)
        assert loaded is None

    def test_update_commits_by_default(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        p = create_test_player(
            test_args,
            test_pool,
            moniker="update_default",
            membermoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
        )
        p.pool = test_pool
        p.save(force=True, commit=True)

        p.coins = 5000
        p.sync()
        result = p.update(db_conn)

        assert result is True
        db_conn.commit()

        loaded = load(test_args, "update_default", pool=test_pool)
        assert loaded.coins == 5000

    def test_update_with_commit_false(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        p = create_test_player(
            test_args,
            test_pool,
            moniker="update_nocommit",
            membermoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
        )
        p.pool = test_pool
        p.save(force=True, commit=True)

        p.coins = 6000
        p.sync()
        p.update(db_conn, commit=False)
        db_conn.rollback()

        loaded = load(test_args, "update_nocommit", pool=test_pool)
        assert loaded.coins == 250000

    def test_update_returns_false_when_conn_is_none(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        p = create_test_player(
            test_args,
            test_pool,
            moniker="update_noconn",
            membermoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
        )
        p.pool = test_pool
        result = p.update(None)
        assert result is False


class TestPlayerLoadIntegration:
    def test_load_returns_player(self, test_args, test_pool, db_conn, clean_tables):
        p = create_test_player(
            test_args,
            test_pool,
            moniker="load_test_player",
            membermoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
            coins=5000,
            land=10000,
        )
        p.pool = test_pool
        p.save(force=True, commit=True)

        loaded = load(test_args, "load_test_player", pool=test_pool)

        assert loaded is not None
        assert loaded.moniker == "load_test_player"
        assert loaded.coins == 5000
        assert loaded.land == 10000

    def test_load_returns_none_when_not_found(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        result = load(test_args, "nonexistent_player_xyz", pool=test_pool)
        assert result is None

    def test_load_returns_false_when_pool_is_none(self, test_args):
        result = load(test_args, "any_player", pool=None)
        assert result is False

    def test_load_restores_resources_correctly(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        p = create_test_player(
            test_args,
            test_pool,
            moniker="resource_restore",
            membermoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
            soldiers=200,
            nobles=10,
        )
        p.pool = test_pool
        p.save(force=True, commit=True)

        loaded = load(test_args, "resource_restore", pool=test_pool)
        assert loaded.soldiers == 200
        assert loaded.nobles == 10


class TestPlayerExistsIntegration:
    def test_exists_returns_true(self, test_args, test_pool, db_conn, clean_tables):
        p = create_test_player(
            test_args,
            test_pool,
            moniker="exists_player",
            membermoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
        )
        p.pool = test_pool
        p.save(force=True, commit=True)

        result = exists("exists_player", args=test_args)
        assert result is True

    def test_exists_returns_false(self, test_args, test_pool, db_conn, clean_tables):
        result = exists("nonexistent_exists_player", args=test_args)
        assert result is False


class TestPlayerCountIntegration:
    def test_count_returns_count(self, test_args, test_pool, db_conn, clean_tables):
        p1 = create_test_player(
            test_args,
            test_pool,
            moniker="count_player1",
            membermoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
        )
        p1.pool = test_pool
        p1.save(commit=True)

        p2 = create_test_player(
            test_args,
            test_pool,
            moniker="count_player2",
            membermoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
        )
        p2.pool = test_pool
        p2.save(commit=True)

        result = count(test_args, TEST_MEMBER_MONIKER, pool=test_pool)
        assert result == 2

    def test_count_returns_none_when_no_players(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        result = count(test_args, TEST_MEMBER_MONIKER, pool=test_pool)
        assert result is None

    def test_count_returns_none_when_pool_is_none(self, test_args):
        result = count(test_args, TEST_MEMBER_MONIKER, pool=None)
        assert result is None


class TestPlayerConsistency:
    def test_verify_consistency_returns_true_for_clean_player(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        p = create_test_player(
            test_args,
            test_pool,
            moniker="consistent_player",
            membermoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
        )
        p.pool = test_pool
        assert p.verify_consistency(verbose=False) is True

    def test_verify_consistency_returns_false_after_modification(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        p = create_test_player(
            test_args,
            test_pool,
            moniker="inconsistent_player",
            membermoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
        )
        p.pool = test_pool
        p.coins = 99999
        assert p.verify_consistency(verbose=False) is False

    def test_sync_updates_resource_values(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        p = create_test_player(
            test_args,
            test_pool,
            moniker="sync_player",
            membermoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
            coins=100,
        )
        p.pool = test_pool
        p.coins = 200
        p.sync()
        assert p.resources["coins"]["value"] == 200

    def test_isdirty_returns_true_after_change(
        self, test_args, test_pool, db_conn, clean_tables
    ):
        p = create_test_player(
            test_args,
            test_pool,
            moniker="dirty_player",
            membermoniker=TEST_MEMBER_MONIKER,
            conn=db_conn,
        )
        p.pool = test_pool
        assert p.isdirty() is False
        p.coins = 999999
        assert p.isdirty() is True
