import os
import argparse

import pytest
import psycopg

from bbsengine6 import database


TEST_LOGINID = "empyre_test_user"
TEST_MEMBER_MONIKER = "test_member"


@pytest.fixture(scope="session")
def test_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", default=False)
    defaults = {
        "databasename": os.environ.get("EMPORE_TEST_DBNAME", "zoid6test"),
        "databasehost": os.environ.get("EMPORE_TEST_DBHOST", "/var/run/postgresql"),
        "databaseport": int(os.environ.get("EMPORE_TEST_DBPORT", "5432")),
        "databaseuser": os.environ.get("EMPORE_TEST_DBUSER", "opencode"),
        "databasepassword": os.environ.get("EMPORE_TEST_DBPASS"),
    }
    database.buildargdatabasegroup(parser, defaults)
    args = parser.parse_args([])
    return args


@pytest.fixture(scope="session")
def test_pool(test_args):
    pool = database.getpool(test_args, dbname=test_args.databasename)
    test_args.pool = pool
    yield pool
    pool.close()


@pytest.fixture(scope="session")
def test_engine_member(test_args, test_pool):
    with database.connect(test_args, pool=test_pool) as conn:
        with database.cursor(conn) as cur:
            cur.execute(
                """
                insert into engine.__member (moniker, email, loginid, tz, datecreated, credits)
                values (%s, %s, %s, %s, now(), 100)
                on conflict (moniker) do update set
                    loginid = excluded.loginid,
                    tz = excluded.tz
                """,
                (TEST_MEMBER_MONIKER, "test@empyre.local", TEST_LOGINID, "UTC"),
            )
        conn.commit()

    yield TEST_MEMBER_MONIKER

    with database.connect(test_args, pool=test_pool) as conn:
        with database.cursor(conn) as cur:
            cur.execute(
                "delete from engine.__member where moniker = %s",
                (TEST_MEMBER_MONIKER,),
            )
        conn.commit()


@pytest.fixture(scope="function")
def db_conn(test_args, test_pool, test_engine_member):
    conn = test_pool.getconn()
    conn.autocommit = False
    yield conn
    conn.rollback()
    test_pool.putconn(conn)


@pytest.fixture(scope="function")
def clean_tables(db_conn):
    for table in [
        "empyre.__newsentry",
        "empyre.__colony",
        "empyre.__ship",
        "empyre.__island",
        "empyre.__player",
    ]:
        try:
            with database.cursor(db_conn) as cur:
                cur.execute(f"delete from {table};")
            db_conn.commit()
        except psycopg.errors.UndefinedTable:
            db_conn.rollback()
    yield
