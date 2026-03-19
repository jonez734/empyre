import argparse
import copy
from datetime import datetime
from typing import Any, Optional

import dateutil.tz
from psycopg import sql

from bbsengine6 import database, io, member, util
from bbsengine6.database import _table_identifier
from bbsengine6.listbox import ListboxItem, ListboxResult
from bbsengine6.listboxcursor import ListboxCursor
from .. import lib as libempyre

MAXSHIPYARDS: int = 10
SHIPSPERSHIPYARD: int = 10

ATTRIBUTES: dict = {
    "moniker": {"default": None},
    "navigator": {"default": False},
    "membermoniker": {"default": None},
    "datedocked": {"default": None, "type": datetime},
    "datecreated": {"default": None, "type": datetime},
    "status": {"default": None},
    "manifest": {"default": {}},
    "kind": {"default": "cargo"},
}


class Ship:
    datedocked: Optional[datetime] = None
    datecreated: Optional[datetime] = None

    def __init__(self, args: argparse.Namespace, **kwargs: Any) -> None:
        self.args: argparse.Namespace = args
        self.player: Any = kwargs.get("player", None)
        self.pool: Any = kwargs.get("pool", None)

        self.attributes = copy.copy(ATTRIBUTES)
        for name, data in self.attributes.items():
            setattr(self, name, data["default"])
            self.attributes[name]["value"] = data["default"]

    def save(self, commit: bool = True, moniker: Optional[str] = None) -> bool:
        io.echo(f"saving ship {self.moniker}", level="debug")
        ship = {}
        for f in (
            "moniker",
            "kind",
            "manifest",
            "navigator",
            "location",
            "status",
            "datedocked",
            "playermoniker",
        ):
            ship[f] = getattr(self, f)
        pk = ship["moniker"]
        if moniker is not None:
            if moniker != ship["moniker"]:
                ship["moniker"] = moniker
        database.update(
            self.args,
            "empyre.__ship",
            pk,
            ship,
            primarykey="moniker",
            updatepk=True,
            pool=self.pool,
        )
        return True

    def adjust(self) -> bool:
        c = count(self.args, self.playermoniker, pool=self.pool)

        if self.player is not None and self.player.ships != c:
            io.echo(f"adjusting {self.player.ships=} to {c=}", level="debug")
            self.player.ships = c
            self.player.save()
        return True


def load(args: argparse.Namespace, moniker: str, **kwargs) -> Optional[Any]:

    def _work(conn: Any) -> Optional[Any]:
        with database.cursor(conn) as cur:
            query = sql.SQL("select * from {} where moniker=%s").format(
                _table_identifier("empyre.ship")
            )
            dat = (moniker,)
            cur.execute(query, dat)
            if cur.rowcount == 0:
                io.echo(f"empyre.ship.load.200: {moniker=} not found", level="info")
                return None
            rec = cur.fetchone()
            ship = Ship(args, **kwargs)
            for f in (
                "moniker",
                "kind",
                "manifest",
                "navigator",
                "location",
                "status",
                "datedocked",
                "datedockedlocal",
                "playermoniker",
            ):
                setattr(ship, f, rec.get(f))
            return ship

    conn = kwargs.get("conn")
    if conn is None:
        pool = kwargs.get("pool", None)
        if pool is None:
            io.echo(f"empyre.ship.load.100: {pool=}", level="error")
            return None
        with database.connect(args, pool=pool) as conn:
            return _work(conn)
    return _work(conn)


def build(args: argparse.Namespace, **kwargs: Any) -> Any:
    io.echo(f"empyre.ship.lib.build.100: {kwargs=}", level="debug")
    player = kwargs.get("player", None)
    if player is None:
        io.echo("You do not exist! Go Away!", level="error")
        return False

    pool = kwargs.get("pool", None)

    if player.ships + 1 > player.shipyards * SHIPSPERSHIPYARD:
        io.echo("You need to build a shipyard before you can build a ship.")
        shipyardres = player.getresource("shipyards")
        libempyre.trade(args, player, "shipyards", **shipyardres)
        player.adjust()
        player.save()

    ship = Ship(args, player=player, pool=pool)
    _ship = _edit(args, "build", ship, **kwargs)
    if _ship == ship:
        io.echo("no changes")
    else:
        io.echo("changes made")

    if (
        io.inputboolean(
            "{promptcolor}build ship? {optioncolor}[Yn]{promptcolor}: {inputcolor}", "Y"
        )
        is True
    ):
        s = {}
        s["moniker"] = ship.moniker
        s["playermoniker"] = player.moniker
        for k in ("manifest", "location", "status", "kind", "navigator"):
            s[k] = getattr(ship, k)
        s["datecreated"] = datetime.now(dateutil.tz.tzlocal())
        s["createdbymoniker"] = member.getcurrentmoniker(args, **kwargs)
        s["datedocked"] = datetime.now(dateutil.tz.tzlocal())
        res = database.insert(
            args,
            "empyre.__ship",
            s,
            mogrify=True,
            primarykey="moniker",
            pool=pool,
            **kwargs,
        )
        if res is False:
            io.echo("failed to insert ship", level="error")
            return None
        return s
    return True


def _edit(args: argparse.Namespace, mode: str, ship: Ship, **kwargs: Any) -> Ship:
    player = kwargs.get("player", None)
    io.echo(f"empyre.ship.lib._edit.100: {kwargs=}", level="debug")
    _ship = Ship(args, player=player)
    _ship.moniker = ship.moniker
    _ship.kind = ship.kind
    _ship.manifest = ship.manifest.copy()
    _ship.navigator = ship.navigator
    _ship.location = ship.location
    _ship.status = ship.status
    _ship.playermoniker = ship.playermoniker

    done = False
    while not done:
        io.echo(
            f"{{optioncolor}}[N]{{labelcolor}}ame: {{valuecolor}}{ship.moniker}", end=""
        )
        if _ship.moniker != ship.moniker:
            io.echo(
                f" {{labelcolor}}(was: {{valuecolor}}{_ship.moniker}{{labelcolor}})"
            )
        else:
            io.echo()

        owner = ship.playermoniker if ship.playermoniker else "(none)"
        io.echo(
            f"{{optioncolor}}[O]{{labelcolor}}wner: {{valuecolor}}{owner}",
            end="",
        )
        if _ship.playermoniker != ship.playermoniker:
            was_owner = _ship.playermoniker if _ship.playermoniker else "(none)"
            io.echo(f" {{labelcolor}}(was: {{valuecolor}}{was_owner}{{labelcolor}})")
        else:
            io.echo()

        io.echo(
            f"{{optioncolor}}[A]{{labelcolor}} Navigator: {{valuecolor}}{ship.navigator}",
            end="",
        )
        if _ship.navigator != ship.navigator:
            io.echo(
                f" {{labelcolor}}(was: {{valuecolor}}{_ship.navigator}{{labelcolor}})"
            )
        else:
            io.echo()

        ch = io.inputchar(f"{{promptcolor}}{mode} ship: {{inputcolor}}", "MNOAKQ", "")
        if ch == "Q":
            io.echo("Quit")
            done = True
        elif ch == "N":
            completer = completeShipName(args, **kwargs)
            moniker = inputshipname(
                args,
                ship.moniker,
                completer=completer,
                verify=verifyShipNameNotFound,
                **kwargs,
            )
            if moniker is None or ship.moniker == "":
                io.echo("You must enter a ship name")
                continue
            ship.moniker = moniker
            if ship.status == "build":
                ship.status = "docked"
        elif ch == "L":
            io.echo("Load")
            runmodule(args, "load", ship=ship, player=player, pool=kwargs.get("pool"))
        elif ch == "U":
            io.echo("Unload")
            runmodule(args, "unload", ship=ship, player=player, pool=kwargs.get("pool"))
        elif ch == "A":
            io.echo("Navigator")
            nav = player.getresource("navigators")
            if nav is None:
                io.echo("'navigator' is not a valid resource.", level="error")
                continue
            if player.coins < nav["price"]:
                io.echo(
                    "You need {} to purchase a navigator".format(
                        util.pluralize(nav["price"], "coin", "coins", **nav)
                    )
                )
            else:
                player.coins -= nav["price"]
                ship.navigator = True
        elif ch == "K":
            io.echo("Kind")
            k = io.inputchoice("[C]argo [P]assenger [M]ilitary", "CPM", "C")
            if k == "C":
                io.echo("cargo")
                ship.kind = "cargo"
            elif k == "P":
                io.echo("passenger")
                ship.kind = "passenger"
            elif k == "M":
                io.echo("military carrier")
                ship.kind = "carrier"
    return ship


class completeShipName:
    def __init__(self, args: argparse.Namespace, **kwargs: Any) -> None:
        self.args = args
        self.player = kwargs.get("player", None)
        self.pool = kwargs.get("pool", None)
        self.names: list = []

        if self.pool is None:
            io.echo(f"empyre.ship.lib.completeShipName.100: {self.pool=}")
            return

        with database.connect(args, pool=self.pool) as conn:
            with database.cursor(conn) as cur:
                query = sql.SQL("select moniker from {} where playermoniker=%s").format(
                    _table_identifier("empyre.ship")
                )
                dat = (self.player.moniker,)
                cur.execute(query, dat)
                if cur.rowcount > 0:
                    for rec in cur.fetchall():
                        self.names.append(rec["moniker"])

    def complete(self, text: str, state: int) -> Optional[str]:
        results = [x for x in self.names if x.startswith(text)] + [None]
        return results[state]


def _verifyshipname(args: argparse.Namespace, moniker: str, **kwargs: Any) -> bool:
    io.echo(f"_verifyshipname.100: {kwargs=}", level="debug")

    def _work(conn: Any) -> bool:
        with database.cursor(conn) as cur:
            query = sql.SQL("select 1 from {} where moniker=%s").format(
                _table_identifier("empyre.ship")
            )
            dat = (moniker,)
            cur.execute(query, dat)
            io.echo(
                f"verifyShipNameFound.100: {database.mogrifysql(cur, query.as_string(conn), dat)=}",
                level="debug",
            )
            if cur.rowcount == 0:
                return False
            return True

    conn = kwargs.get("conn")
    if conn is None:
        pool = kwargs.get("pool")
        if pool is None:
            io.echo(f"empyre.ship.lib.verify.100: {pool=}", level="error")
            return False
        with database.connect(args, pool=pool) as conn:
            return _work(conn)


def verifyShipNameFound(args: argparse.Namespace, moniker: str, **kwargs: Any) -> bool:
    if _verifyshipname(args, moniker, **kwargs) is True:
        return False
    return True


def verifyShipNameNotFound(
    args: argparse.Namespace, moniker: str, **kwargs: Any
) -> bool:
    if _verifyshipname(args, moniker, **kwargs) is False:
        return True
    return False


def inputshipname(
    args: argparse.Namespace, prompt: str, currentmoniker: str = "", **kwargs: Any
) -> str:
    verify = kwargs.pop("verify", verifyShipNameNotFound)
    moniker = io.inputstring(prompt, currentmoniker, verify=verify, args=args, **kwargs)
    if args.debug is True:
        io.echo(f"inputshipname.100: {moniker=}", level="debug")
    return moniker


def selectship(args: argparse.Namespace, **kwargs: Any) -> Any:
    player = kwargs.get("player", None)
    if player is None:
        io.echo("You do not exist! Go Away!", level="error")
        return False

    pool = kwargs.get("pool", None)
    if pool is None:
        io.echo(f"empyre.ship.lib.selectship.200: {pool=}", level="error")
        return False

    class EmpyreShipListbox(ListboxCursor):
        def __init__(self, args: argparse.Namespace, title: str, **kwargs: Any) -> None:
            self.player = kwargs.get("player", None)
            self.pool = kwargs.get("pool", None)
            custom_keys = {
                "KEY_INSERT": self._add_ship,
                "e": self._edit_ship,
                "KEY_DELETE": self._decomm_ship,
                "s": self._sail_ship,
                "l": self._load_ship,
            }
            super().__init__(args, title=title, custom_keys=custom_keys, **kwargs)

        def _add_ship(self) -> Optional[ListboxResult]:
            if self.player is None:
                io.echo("You do not exist! Go Away!", level="error")
                return ListboxResult("cancelled")

            totalships = count(self.args, self.player.moniker, pool=self.pool)
            maxships = self.player.shipyards * SHIPSPERSHIPYARD

            if totalships < maxships:
                create(self.args, player=self.player, pool=self.pool)
                return ListboxResult("added")
            else:
                io.echo(
                    f"You need more shipyards to build another ship. You have {maxships} capacity ({totalships} ships)."
                )
                return ListboxResult("cancelled")

        def _edit_ship(self) -> Optional[ListboxResult]:
            if self.currentitem is None:
                return ListboxResult("cancelled")
            ship = self.currentitem.data["ship"]
            _edit(self.args, "edit", ship, player=self.player, pool=self.pool)
            ship.save()
            return ListboxResult("refresh")

        def _sail_ship(self) -> Optional[ListboxResult]:
            if self.currentitem is None:
                return ListboxResult("cancelled")
            ship = self.currentitem.data["ship"]
            if ship.status == "decommissioned":
                io.echo("That ship is decommissioned.")
                return ListboxResult("cancelled")
            runmodule(self.args, "sail", ship=ship, player=self.player, pool=self.pool)
            return ListboxResult("selected", self.currentitem)

        def _load_ship(self) -> Optional[ListboxResult]:
            if self.currentitem is None:
                return ListboxResult("cancelled")
            ship = self.currentitem.data["ship"]
            if ship.status == "decommissioned":
                io.echo("That ship is decommissioned.")
                return ListboxResult("cancelled")
            runmodule(self.args, "load", ship=ship, player=self.player, pool=self.pool)
            return ListboxResult("selected", self.currentitem)

        def _unload_ship(self) -> Optional[ListboxResult]:
            if self.currentitem is None:
                return ListboxResult("cancelled")
            ship = self.currentitem.data["ship"]
            if ship.status == "decommissioned":
                io.echo("That ship is decommissioned.")
                return ListboxResult("cancelled")
            if not ship.manifest:
                io.echo("That ship has nothing to unload.")
                return ListboxResult("cancelled")
            runmodule(
                self.args, "unload", ship=ship, player=self.player, pool=self.pool
            )
            return ListboxResult("selected", self.currentitem)

        def _decomm_ship(self) -> Optional[ListboxResult]:
            if self.currentitem is None:
                io.echo(f"{{bell}}")
                return ListboxResult("cancelled")
            ship = self.currentitem.data["ship"]
            if ship.status == "decommissioned":
                io.echo("That ship is already decommissioned.")
                return ListboxResult("cancelled")
            ship.status = "decommissioned"
            ship.save()
            self.currentitem.disabled = True
            io.echo(f"Ship {ship.moniker} has been decommissioned.")
            return ListboxResult("refresh")

    class EmpyreShipListboxItem(ListboxItem):
        pool: Any = None

        def __init__(self, rec: dict, width: int) -> None:
            super().__init__()
            pool = EmpyreShipListboxItem.pool
            self.ship = load(args, rec["moniker"], pool=pool)

            left = f"{self.ship.moniker}"
            datedocked = util.datestamp(
                self.ship.datedockedlocal, format="%m/%d @ %I%M%P"
            )
            right = f"{self.ship.location} {datedocked}"
            rightlen = len(right)
            self.content = f"{left.ljust(width - rightlen - 10)}{right}"
            self.pk = self.ship.moniker
            self.data = {"ship": self.ship, "rec": rec}
            self.width = width
            self.disabled = self.ship.status == "decommissioned"

        def help(self) -> None:
            io.echo(
                "ENT: Select | INS: Add | E: Edit | DEL: Decommission | S: Sail | L: Load | U: Unload"
            )
            return

    totalships = count(args, player.moniker, pool=pool)

    with database.connect(args, pool=pool) as conn:
        with database.cursor(conn) as cur:
            query = sql.SQL("select * from {} where playermoniker=%s").format(
                _table_identifier("empyre.ship")
            )
            dat = (player.moniker,)
            cur.execute(query, dat)

    EmpyreShipListboxItem.pool = pool
    lb = EmpyreShipListbox(
        args,
        "select ship",
        totalitems=totalships,
        itemclass=EmpyreShipListboxItem,
        **kwargs,
    )
    maxships = player.shipyards * SHIPSPERSHIPYARD
    if totalships < maxships:
        libempyre.setbottombar(
            args,
            f"select ship | ENT: Select | INS: Add | E: Edit | DEL: Decom | S: Sail | L: Load | capacity: {totalships}/{maxships}",
            player=player,
        )
    else:
        libempyre.setbottombar(
            args,
            f"select ship | ENT: Select | INS: Add | E: Edit | DEL: Decom | S: Sail | L: Load | capacity: {totalships}/{maxships} (need shipyard)",
            player=player,
        )
    op = lb.run("select ship: ")
    libempyre.setbottombar(args, "dock", player=player)
    if op.status == "selected" and op.item:
        return op.item.data["ship"]
    return None


def getship(args: argparse.Namespace, moniker: str, **kwargs: Any) -> Optional[Ship]:
    player = kwargs.get("player", None)
    if player is None:
        io.echo("You do not exist! Go Away!")
        return None

    pool = kwargs.get("pool", None)
    if pool is None:
        io.echo(f"getship.100: {pool=}", level="error")
        return None

    with database.connect(args, pool=pool) as conn:
        with database.cursor(conn) as cur:
            query = sql.SQL("select * from {} where moniker=%s").format(
                _table_identifier("empyre.ship")
            )
            dat = (moniker,)
            cur.execute(query, dat)
            if cur.rowcount == 0:
                return None
            ship = load(args, moniker, pool=pool)
            return ship


def empyshipkeyhandler(args: argparse.Namespace, ch: str, lb: Any) -> bool:
    io.echo("inside empyreshipkeyhandler", level="debug")
    currentitem = lb.currentitem
    if ch == "KEY_ENTER":
        io.echo(f"{currentitem.ship.moniker}")
        return False
    return True


def runmodule(args: argparse.Namespace, modulename: str, **kwargs: Any) -> Any:
    return libempyre.runmodule(args, f"ship.{modulename}", **kwargs)


def count(
    args: argparse.Namespace, playermoniker: Optional[str] = None, **kwargs: Any
) -> int:
    def _work(conn: Any) -> int:
        with database.cursor(conn) as cur:
            query = sql.SQL(
                "select count(moniker) from {} where playermoniker=%s"
            ).format(_table_identifier("empyre.ship"))
            dat = (playermoniker,)
            cur.execute(query, dat)
            return cur.rowcount

    conn = kwargs.get("conn")
    if conn is None:
        pool = kwargs.get("pool")
        if pool is None:
            io.echo(f"empyre.ship.count.100: {pool=}", level="error")
            return 0
        with database.connect(args, pool=pool) as conn:
            return _work(conn)
    return _work(conn)


def create(args: argparse.Namespace, **kwargs: Any) -> Optional[Ship]:
    pool = kwargs.get("pool", None)
    if pool is None:
        io.echo("empyre.ship.create.100: {pool=}", level="error")
        return None

    player = kwargs.get("player", None)
    if player is None:
        io.echo("You do not exist! Go Away!", level="error")
        return None

    if player.ships + 1 > player.shipyards * SHIPSPERSHIPYARD:
        io.echo("You need to build a shipyard before you can build a ship.")
        return None

    ship = Ship(args, player=player, pool=pool)
    ship.moniker = kwargs.get("moniker", "Unnamed Ship")
    ship.kind = kwargs.get("kind", "cargo")
    ship.manifest = kwargs.get("manifest", {})
    ship.navigator = kwargs.get("navigator", False)
    ship.location = kwargs.get("location", "mainland")
    ship.status = kwargs.get("status", "build")
    ship.datedocked = datetime.now(dateutil.tz.tzlocal())
    ship.datecreated = datetime.now(dateutil.tz.tzlocal())

    s = {}
    s["moniker"] = ship.moniker
    s["playermoniker"] = player.moniker
    s["manifest"] = ship.manifest
    s["location"] = ship.location
    s["status"] = ship.status
    s["kind"] = ship.kind
    s["navigator"] = ship.navigator
    s["datecreated"] = datetime.now(dateutil.tz.tzlocal())
    s["createdbymoniker"] = member.getcurrentmoniker(args, **kwargs)
    s["datedocked"] = datetime.now(dateutil.tz.tzlocal())

    try:
        conn = kwargs.get("conn", None)
        if conn is None:
            with database.connect(args, pool=pool) as conn:
                database.insert(
                    args,
                    "empyre.__ship",
                    s,
                    mogrify=True,
                    primarykey="moniker",
                    conn=conn,
                )
        else:
            database.insert(
                args,
                "empyre.__ship",
                s,
                mogrify=True,
                primarykey="moniker",
                conn=conn,
                commit=False,
            )
    except Exception as e:
        io.echo(f"empyre.ship.create.200: exception {e}", level="error")
        raise

    return ship
