import argparse
from datetime import datetime
from typing import Any, Optional

import dateutil.tz

from empyre.player import Player
from empyre.ship.lib import Ship
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


def create_test_ship(
    args: argparse.Namespace,
    pool: Any,
    moniker: str,
    playermoniker: str,
    conn: Optional[Any] = None,
    insert: bool = True,
    createdbymoniker: Optional[str] = None,
    player: Optional[Any] = None,
    **attrs: Any,
) -> Ship:
    if createdbymoniker is None:
        createdbymoniker = playermoniker

    ship = Ship(args, pool=pool, player=player)
    ship.pool = pool
    ship.moniker = moniker
    ship.playermoniker = playermoniker
    ship.kind = attrs.get("kind", "cargo")
    ship.manifest = attrs.get("manifest", {})
    ship.navigator = attrs.get("navigator", False)
    ship.location = attrs.get("location", "mainland")
    ship.status = attrs.get("status", "build")
    ship.datedocked = attrs.get("datedocked", datetime.now(dateutil.tz.tzlocal()))
    ship.datecreated = attrs.get("datecreated", datetime.now(dateutil.tz.tzlocal()))

    if insert and conn is not None:
        s = {
            "moniker": ship.moniker,
            "playermoniker": ship.playermoniker,
            "manifest": ship.manifest,
            "location": ship.location,
            "status": ship.status,
            "kind": ship.kind,
            "navigator": ship.navigator,
            "datecreated": ship.datecreated,
            "createdbymoniker": createdbymoniker,
            "datedocked": ship.datedocked,
        }
        database.insert(
            args, "empyre.__ship", s, primarykey="moniker", conn=conn, commit=True
        )

    return ship
