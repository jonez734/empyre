import argparse
import unittest
from unittest.mock import MagicMock, patch

from empyre.player import Player


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


if __name__ == "__main__":
    unittest.main()
