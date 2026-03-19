from unittest.mock import patch, MagicMock

from empyre.town import juicebar


class TestJuiceBarCheckAvailable:
    def test_returns_false_when_no_mercs_available(self, test_args, test_pool):
        mock_cur = MagicMock()
        mock_cur.rowcount = 0
        with patch("empyre.town.juicebar.database.cursor") as mock_cursor:
            mock_cursor.return_value.__enter__.return_value = mock_cur
            with patch("empyre.town.juicebar.database.connect") as mock_connect:
                mock_connect.return_value.__enter__.return_value = MagicMock()
                mock_connect.return_value.__exit__ = MagicMock(return_value=False)
                result = juicebar.checkavailable(test_args, pool=test_pool)
        assert result is False

    def test_returns_true_when_mercs_available(self, test_args, test_pool):
        mock_cur = MagicMock()
        mock_cur.rowcount = 1
        mock_cur.fetchone.return_value = {"moniker": "team1"}
        with patch("empyre.town.juicebar.database.cursor") as mock_cursor:
            mock_cursor.return_value.__enter__.return_value = mock_cur
            with patch("empyre.town.juicebar.database.connect") as mock_connect:
                mock_connect.return_value.__enter__.return_value = MagicMock()
                mock_connect.return_value.__exit__ = MagicMock(return_value=False)
                result = juicebar.checkavailable(test_args, pool=test_pool)
        assert result is True

    def test_returns_false_with_conn_when_no_mercs(self, test_args, db_conn):
        mock_cur = MagicMock()
        mock_cur.rowcount = 0
        with patch("empyre.town.juicebar.database.cursor") as mock_cursor:
            mock_cursor.return_value.__enter__.return_value = mock_cur
            result = juicebar.checkavailable(test_args, conn=db_conn)
        assert result is False

    def test_returns_true_with_conn_when_mercs_available(self, test_args, db_conn):
        mock_cur = MagicMock()
        mock_cur.rowcount = 1
        mock_cur.fetchone.return_value = {"moniker": "team1"}
        with patch("empyre.town.juicebar.database.cursor") as mock_cursor:
            mock_cursor.return_value.__enter__.return_value = mock_cur
            result = juicebar.checkavailable(test_args, conn=db_conn)
        assert result is True

    def test_returns_false_when_pool_is_none(self, test_args):
        result = juicebar.checkavailable(test_args, pool=None)
        assert result is False

    def test_init_returns_true(self, test_args):
        assert juicebar.init(test_args) is True

    def test_access_returns_true(self, test_args):
        assert juicebar.access(test_args, "op") is True

    def test_buildargs_returns_none(self, test_args):
        assert juicebar.buildargs(test_args) is None
