import argparse
from datetime import datetime
from typing import Any, Optional

from empyre.player import Player
from bbsengine6 import database


def make_test_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", default=False)
    defaults = {
        "databasename": "zoid6test",
        "databasehost": "/var/run/postgresql",
        "databaseport": 5432,
        "databaseuser": "opencode",
        "databasepassword": None,
    }
    from bbsengine6 import database

    database.buildargdatabasegroup(parser, defaults)
    return parser.parse_args([])


def create_test_player(
    args: argparse.Namespace,
    pool: Any,
    moniker: str,
    membermoniker: Optional[str] = None,
    conn: Optional[Any] = None,
    insert: bool = True,
    **resource_overrides: Any,
) -> Player:
    if membermoniker is None:
        membermoniker = moniker + "_member"

    p = Player(args, pool=pool, conn=conn)
    p.pool = pool

    for name, value in [("moniker", moniker), ("membermoniker", membermoniker)]:
        setattr(p, name, value)
        if name in p.attributes:
            p.attributes[name]["value"] = value

    for name, value in resource_overrides.items():
        setattr(p, name, value)
        if name in p.resources:
            p.resources[name]["value"] = value

    p.sync()

    if insert and conn is not None:
        rec = p.buildrec()
        rec["datecreated"] = datetime.now()
        database.insert(
            args, "empyre.__player", rec, primarykey="moniker", conn=conn, commit=True
        )

    return p
