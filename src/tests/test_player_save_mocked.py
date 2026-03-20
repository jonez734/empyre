import argparse
import unittest
from unittest.mock import MagicMock, patch

from empyre.player import Player
import empyre.player


def get_test_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", default=False)
    defaults = {
        "databasename": "zoid6",
        "databasehost": "localhost",
        "databaseport": 5432,
        "databaseuser": "opencode",
        "databasepassword": None,
    }
    from bbsengine6 import database

    database.buildargdatabasegroup(parser, defaults)
    args = parser.parse_args([])
    return args


def make_player(args, mock_pool, mock_conn):
    player = Player.__new__(Player)
    player.args = args
    player.pool = mock_pool
    player.conn = None
    player.debug = False
    player.moniker = "testplayer"
    player.membermoniker = "member1"
    player.resources = {}
    player.attributes = {}
    player.buildrec = MagicMock(return_value={})
    return player


class TestPlayerUpdate(unittest.TestCase):
    def setUp(self):
        self.args = get_test_args()
        self.mock_pool = MagicMock()
        self.mock_conn = MagicMock()
        self.mock_pool.getconn.return_value = self.mock_conn
        self.mock_conn.autocommit = False

    def test_update_forwards_commit_true_by_default(self):
        with patch("empyre.player.database") as mock_db:
            mock_db.update.side_effect = lambda *a, **kw: (
                self.mock_conn.commit() if kw.get("commit") else None,
                True,
            )[-1]
            player = make_player(self.args, self.mock_pool, self.mock_conn)
            result = player.update(self.mock_conn)
            mock_db.update.assert_called_once()
            _, kwargs = mock_db.update.call_args
            self.assertEqual(kwargs.get("commit"), True)
            self.assertTrue(result)

    def test_update_forwards_commit_false_when_set(self):
        with patch("empyre.player.database") as mock_db:
            mock_db.update.side_effect = lambda *a, **kw: (
                self.mock_conn.commit() if kw.get("commit") else None,
                True,
            )[-1]
            player = make_player(self.args, self.mock_pool, self.mock_conn)
            result = player.update(self.mock_conn, commit=False)
            _, kwargs = mock_db.update.call_args
            self.assertEqual(kwargs.get("commit"), False)
            self.assertTrue(result)

    def test_update_returns_false_when_conn_is_none(self):
        with patch("empyre.player.database") as mock_db:
            player = make_player(self.args, self.mock_pool, self.mock_conn)
            result = player.update(None)
            mock_db.update.assert_not_called()
            self.assertFalse(result)


class TestPlayerSave(unittest.TestCase):
    def setUp(self):
        self.args = get_test_args()
        self.mock_pool = MagicMock()
        self.mock_conn = MagicMock()
        self.mock_pool.getconn.return_value = self.mock_conn
        self.mock_conn.autocommit = False

    def test_save_commits_transaction(self):
        with (
            patch("empyre.player.database") as mock_db,
            patch("empyre.player.database.cursor") as mock_cursor,
        ):
            mock_cursor.return_value.__enter__ = MagicMock(return_value=MagicMock())
            mock_cursor.return_value.__exit__ = MagicMock(return_value=False)
            mock_db.connect.return_value.__enter__ = MagicMock(
                return_value=self.mock_conn
            )
            mock_db.connect.return_value.__exit__ = MagicMock(return_value=False)
            mock_db.update.side_effect = lambda *a, **kw: (
                self.mock_conn.commit() if kw.get("commit") else None,
                True,
            )[-1]

            player = make_player(self.args, self.mock_pool, self.mock_conn)
            player.isdirty = MagicMock(return_value=True)
            player.sync = MagicMock()

            result = player.save(commit=True)

            mock_db.update.assert_called_once()
            _, kwargs = mock_db.update.call_args
            self.assertEqual(kwargs.get("commit"), True)
            self.mock_conn.commit.assert_called_once()
            player.sync.assert_called_once()
            self.assertTrue(result)

    def test_save_does_not_commit_when_commit_false(self):
        with (
            patch("empyre.player.database") as mock_db,
            patch("empyre.player.database.cursor") as mock_cursor,
        ):
            mock_cursor.return_value.__enter__ = MagicMock(return_value=MagicMock())
            mock_cursor.return_value.__exit__ = MagicMock(return_value=False)
            mock_db.connect.return_value.__enter__ = MagicMock(
                return_value=self.mock_conn
            )
            mock_db.connect.return_value.__exit__ = MagicMock(return_value=False)
            mock_db.update.side_effect = lambda *a, **kw: (
                self.mock_conn.commit() if kw.get("commit") else None,
                True,
            )[-1]

            player = make_player(self.args, self.mock_pool, self.mock_conn)
            player.isdirty = MagicMock(return_value=True)
            player.sync = MagicMock()

            result = player.save(commit=False)

            mock_db.update.assert_called_once()
            _, kwargs = mock_db.update.call_args
            self.assertEqual(kwargs.get("commit"), False)
            self.mock_conn.commit.assert_not_called()
            self.assertTrue(result)

    def test_save_skips_update_when_not_dirty(self):
        with patch("empyre.player.database") as mock_db:
            mock_db.connect.return_value.__enter__ = MagicMock(
                return_value=self.mock_conn
            )
            mock_db.connect.return_value.__exit__ = MagicMock(return_value=False)

            player = make_player(self.args, self.mock_pool, self.mock_conn)
            player.isdirty = MagicMock(return_value=False)
            player.sync = MagicMock()

            result = player.save()

            player.sync.assert_not_called()
            mock_db.update.assert_not_called()
            self.assertIsNone(result)

    def test_save_returns_none_when_no_moniker(self):
        with patch("empyre.player.database") as mock_db:
            player = make_player(self.args, self.mock_pool, self.mock_conn)
            player.moniker = None
            player.isdirty = MagicMock(return_value=True)

            result = player.save()

            mock_db.connect.assert_not_called()
            self.assertIsNone(result)

    def test_save_returns_none_when_no_membermoniker(self):
        with patch("empyre.player.database") as mock_db:
            player = make_player(self.args, self.mock_pool, self.mock_conn)
            player.membermoniker = None
            player.isdirty = MagicMock(return_value=True)

            result = player.save()

            mock_db.connect.assert_not_called()
            self.assertIsNone(result)


class TestPlayerLoad(unittest.TestCase):
    def setUp(self):
        self.args = get_test_args()
        self.mock_pool = MagicMock()
        self.mock_conn = MagicMock()
        self.mock_pool.getconn.return_value = self.mock_conn
        self.mock_conn.autocommit = False

    def test_load_returns_player_and_commits(self):
        with (
            patch("empyre.player.database") as mock_db,
            patch("empyre.player.database.cursor") as mock_cursor,
            patch("empyre.player.build") as mock_build,
        ):
            mock_cursor.return_value.__enter__ = MagicMock(return_value=MagicMock())
            mock_cursor.return_value.__exit__ = MagicMock(return_value=False)
            mock_db.connect.return_value.__enter__ = MagicMock(
                return_value=self.mock_conn
            )
            mock_db.connect.return_value.__exit__ = MagicMock(
                side_effect=lambda *args: self.mock_conn.commit() or False
            )

            mock_cur = mock_cursor.return_value.__enter__.return_value
            mock_cur.rowcount = 1
            mock_cur.fetchone.return_value = {
                "moniker": "testplayer",
                "resources": {},
            }

            mock_player = MagicMock()
            mock_build.return_value = mock_player

            result = empyre.player.load(self.args, "testplayer", pool=self.mock_pool)

            self.assertEqual(result, mock_player)
            self.mock_conn.commit.assert_called_once()
            mock_build.assert_called_once()

    def test_load_returns_none_when_not_found(self):
        with (
            patch("empyre.player.database") as mock_db,
            patch("empyre.player.database.cursor") as mock_cursor,
        ):
            mock_cursor.return_value.__enter__ = MagicMock(return_value=MagicMock())
            mock_cursor.return_value.__exit__ = MagicMock(return_value=False)
            mock_db.connect.return_value.__enter__ = MagicMock(
                return_value=self.mock_conn
            )
            mock_db.connect.return_value.__exit__ = MagicMock(
                side_effect=lambda *args: self.mock_conn.commit() or False
            )

            mock_cur = mock_cursor.return_value.__enter__.return_value
            mock_cur.rowcount = 0

            result = empyre.player.load(self.args, "nonexistent", pool=self.mock_pool)

            self.assertIsNone(result)
            self.mock_conn.commit.assert_called_once()

    def test_load_returns_false_when_pool_is_none(self):
        with patch("empyre.player.database") as mock_db:
            result = empyre.player.load(self.args, "testplayer", pool=None)
            self.assertFalse(result)
            mock_db.connect.assert_not_called()


class TestPlayerCount(unittest.TestCase):
    def setUp(self):
        self.args = get_test_args()
        self.mock_pool = MagicMock()
        self.mock_conn = MagicMock()
        self.mock_pool.getconn.return_value = self.mock_conn
        self.mock_conn.autocommit = False

    def test_count_returns_count_and_commits(self):
        with (
            patch("empyre.player.database") as mock_db,
            patch("empyre.player.database.cursor") as mock_cursor,
        ):
            mock_cursor.return_value.__enter__ = MagicMock(return_value=MagicMock())
            mock_cursor.return_value.__exit__ = MagicMock(return_value=False)
            mock_db.connect.return_value.__enter__ = MagicMock(
                return_value=self.mock_conn
            )
            mock_db.connect.return_value.__exit__ = MagicMock(
                side_effect=lambda *args: self.mock_conn.commit() or False
            )

            mock_cur = mock_cursor.return_value.__enter__.return_value
            mock_cur.rowcount = 1
            mock_cur.fetchone.return_value = {"count": 3}

            result = empyre.player.count(self.args, "member1", pool=self.mock_pool)

            self.assertEqual(result, 3)
            self.mock_conn.commit.assert_called_once()

    def test_count_returns_none_when_rowcount_zero(self):
        with (
            patch("empyre.player.database") as mock_db,
            patch("empyre.player.database.cursor") as mock_cursor,
        ):
            mock_cursor.return_value.__enter__ = MagicMock(return_value=MagicMock())
            mock_cursor.return_value.__exit__ = MagicMock(return_value=False)
            mock_db.connect.return_value.__enter__ = MagicMock(
                return_value=self.mock_conn
            )
            mock_db.connect.return_value.__exit__ = MagicMock(
                side_effect=lambda *args: self.mock_conn.commit() or False
            )

            mock_cur = mock_cursor.return_value.__enter__.return_value
            mock_cur.fetchone.return_value = None

            result = empyre.player.count(self.args, "member1", pool=self.mock_pool)

            self.assertIsNone(result)
            self.mock_conn.commit.assert_called_once()

    def test_count_returns_none_when_pool_is_none(self):
        with patch("empyre.player.database") as mock_db:
            result = empyre.player.count(self.args, "member1", pool=None)
            self.assertIsNone(result)
            mock_db.connect.assert_not_called()


class TestPlayerCreate(unittest.TestCase):
    def setUp(self):
        self.args = get_test_args()
        self.mock_pool = MagicMock()
        self.mock_conn = MagicMock()
        self.mock_pool.getconn.return_value = self.mock_conn
        self.mock_conn.autocommit = False

    def test_create_calls_insert_with_commit_true(self):
        mock_player = MagicMock()
        mock_player.attributes = {}
        with (
            patch("empyre.player.database") as mock_db,
            patch("empyre.player.database.cursor") as mock_cursor,
            patch.object(empyre.player, "inputplayername") as mock_input,
            patch.object(empyre.player, "member") as mock_member,
            patch.object(empyre.player.Player, "__new__", return_value=mock_player),
        ):
            mock_cursor.return_value.__enter__ = MagicMock(return_value=MagicMock())
            mock_cursor.return_value.__exit__ = MagicMock(return_value=False)
            mock_db.connect.return_value.__enter__ = MagicMock(
                return_value=self.mock_conn
            )
            mock_db.connect.return_value.__exit__ = MagicMock(return_value=False)
            mock_db.insert.return_value = "newplayer"
            mock_input.return_value = "newplayer"
            mock_member.getcurrentmoniker.return_value = "member1"

            mock_player.buildrec = MagicMock(return_value={"moniker": "newplayer"})
            result = empyre.player.create(self.args, pool=self.mock_pool)

            mock_db.insert.assert_called_once()
            _, kwargs = mock_db.insert.call_args
            self.assertEqual(kwargs.get("commit"), True)
            self.assertIsNotNone(result)

    def test_create_returns_false_when_pool_is_none(self):
        with patch("empyre.player.database") as mock_db:
            result = empyre.player.create(self.args, pool=None)
            self.assertFalse(result)
            mock_db.insert.assert_not_called()


class TestPlayerExists(unittest.TestCase):
    def setUp(self):
        self.args = get_test_args()
        self.mock_pool = MagicMock()
        self.mock_conn = MagicMock()
        self.mock_pool.getconn.return_value = self.mock_conn
        self.mock_conn.autocommit = False

    def test_exists_returns_true_when_player_found(self):
        self.args.pool = self.mock_pool
        with (
            patch("empyre.player.database") as mock_db,
            patch("empyre.player.database.cursor") as mock_cursor,
        ):
            mock_cursor.return_value.__enter__ = MagicMock(return_value=MagicMock())
            mock_cursor.return_value.__exit__ = MagicMock(return_value=False)
            mock_db.connect.return_value.__enter__ = MagicMock(
                return_value=self.mock_conn
            )
            mock_db.connect.return_value.__exit__ = MagicMock(
                side_effect=lambda *args: self.mock_conn.commit() or False
            )

            mock_cur = mock_cursor.return_value.__enter__.return_value
            mock_cur.rowcount = 1

            result = empyre.player.exists("testplayer", args=self.args)

            self.assertTrue(result)
            self.mock_conn.commit.assert_called_once()

    def test_exists_returns_false_when_player_not_found(self):
        with (
            patch("empyre.player.database") as mock_db,
            patch("empyre.player.database.cursor") as mock_cursor,
        ):
            mock_cursor.return_value.__enter__ = MagicMock(return_value=MagicMock())
            mock_cursor.return_value.__exit__ = MagicMock(return_value=False)
            mock_db.connect.return_value.__enter__ = MagicMock(
                return_value=self.mock_conn
            )
            mock_db.connect.return_value.__exit__ = MagicMock(
                side_effect=lambda *args: self.mock_conn.commit() or False
            )

            mock_cur = mock_cursor.return_value.__enter__.return_value
            mock_cur.rowcount = 0

            result = empyre.player.exists("nonexistent", args=self.args)

            self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
