import argparse
from typing import Any, Optional

from psycopg import sql

from bbsengine6 import database, io, member, util
from bbsengine6.database import _table_identifier
from bbsengine6.listbox import Listbox, ListboxItem, ListboxResult
from bbsengine6.listboxcursor import ListboxCursor
from .. import lib as libempyre

MAXSHIPYARDS: int = 10
SHIPSPERSHIPYARD: int = 10


class Ship:
    def __init__(self, args: argparse.Namespace, **kwargs: Any) -> None:
        self.args: argparse.Namespace = args
        self.player: Any = kwargs.get("player", None)
        self.location: str = kwargs.get("location", "mainland")
        self.moniker: Optional[str] = None
        self.kind: str = "cargo"
        self.manifest: dict = {}
        self.navigator: bool = False
        self.status: Optional[str] = None
        self.datecreated: Optional[str] = None
        self.createdbymoniker: Optional[str] = None
        self.datedocked: Optional[str] = None
        self.datedockedlocal: Optional[str] = None
        self.playermoniker: Optional[str] = None
        self.pool: Any = kwargs.get("pool", None)

    def load(self, moniker: str) -> bool:
        def _work(conn: Any) -> bool:
            with database.cursor(conn) as cur:
                query = sql.SQL("select * from {} where moniker=%s").format(
                    _table_identifier("empyre.ship")
                )
                dat = (moniker,)
                cur.execute(query, dat)
                if cur.rowcount == 0:
                    return False
                rec = cur.fetchone()
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
                    setattr(self, f, rec[f])
                return True

        pool = self.pool
        if pool is None:
            io.echo(f"Ship.load.100: {pool=}", level="error")
            return False
        with database.connect(self.args, pool=pool) as conn:
            return _work(conn)

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
        if commit is True:
            database.commit(self.args, pool=self.pool)
        return True

    def unload(self) -> bool:
        io.echo("Ship unload not yet implemented", level="debug")
        return True

    def getmanifestentry(self, name: str) -> Optional[Any]:
        return self.manifest[name] if name in self.manifest else None

    def adjust(self) -> bool:
        c = count(self.args, self.player.moniker, pool=self.pool)

        if self.player.ships != c:
            io.echo(f"adjusting {self.player.ships=} to {c=}", level="debug")
            self.player.ships = c
            self.player.save()
        return True


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
        s["datecreated"] = "now()"
        s["createdbymoniker"] = member.getcurrentmoniker(args, **kwargs)
        s["datedocked"] = "now()"
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
        database.commit(args, pool=pool)
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

        io.echo(
            f"{{optioncolor}}[O]{{labelcolor}}wner: {{valuecolor}}{ship.player.moniker}",
            end="",
        )
        if _ship.player.moniker != ship.player.moniker:
            io.echo(
                f" {{labelcolor}}(was: {{valuecolor}}{_ship.player.moniker}{{labelcolor}})"
            )
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
        elif ch == "L":
            io.echo("Load")
            ship.load()
        elif ch == "U":
            io.echo("Unload")
            ship.unload()
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
            custom_keys = {"KEY_INSERT": self._add_ship}
            super().__init__(args, title=title, custom_keys=custom_keys, **kwargs)

        def _add_ship(self) -> Optional[ListboxResult]:
            if self.player is None:
                io.echo("You do not exist! Go Away!", level="error")
                return ListboxResult("cancelled")

            totalships = count(self.args, self.player.moniker, pool=self.pool)
            maxships = self.player.shipyards * SHIPSPERSHIPYARD

            if totalships < maxships:
                build(self.args, player=self.player, pool=self.pool)
                return ListboxResult("added")
            else:
                io.echo(
                    f"You need more shipyards to build another ship. You have {maxships} capacity ({totalships} ships)."
                )
                return ListboxResult("cancelled")

    class EmpyreShipListboxItem(ListboxItem):
        pool: Any = None

        def __init__(self, rec: dict, width: int) -> None:
            super().__init__()
            pool = EmpyreShipListboxItem.pool
            self.ship = Ship(args, player=player, pool=pool)
            self.ship.load(rec["moniker"])

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
            self.disabled = False

        def help(self) -> None:
            io.echo("use KEY_ENTER to select one of your ships")
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
            f"select ship | INS: Add Ship | capacity: {totalships}/{maxships}",
            player=player,
        )
    else:
        libempyre.setbottombar(
            args,
            f"select ship | capacity: {totalships}/{maxships} (need shipyard)",
            player=player,
        )
    op = lb.run("select ship: ")
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
            ship = Ship(args, player=player, pool=pool)
            ship.load(moniker)
            return ship


def empyshipkeyhandler(args: argparse.Namespace, ch: str, lb: Any) -> bool:
    io.echo("inside empyreshipkeyhandler", level="debug")
    currentitem = lb.currentitem
    if ch == "KEY_ENTER":
        io.setvar("cic", "{currentitemcolor}")
        currentitem.display()
        io.echo("{restorecursor}", end="", flush=True)
        io.echo(f"{currentitem.player.moniker}")
        return False
    return True


def selectmanifestitem(args: argparse.Namespace, **kwargs: Any) -> Any:
    class EmpyreShipManifestListboxItem(ListboxItem):
        def __init__(self, resourcename: str, width: int, **kwargs):
            super().__init__()
            self.ship = kwargs.get("ship")
            self.player = kwargs.get("player")
            self.pk = resourcename
            self.res = self.player.getresource(resourcename) if self.player else {}
            self.width = width

            manifestitem = (
                self.ship.manifest[self.pk]
                if self.ship and self.pk in self.ship.manifest
                else {}
            )
            value = manifestitem.get("value", 0)

            left = f"{self.pk}"
            right = f"{value:>6n}"
            rightlen = len(right)
            self.content = f"{left.ljust(width - rightlen - 10)}{right}"
            self.data = {"resource": resourcename, "value": value}
            self.disabled = False

        def help(self):
            io.echo("use KEY_ENTER to select a ship resource")
            return

    ship = kwargs.get("ship")
    if ship is None:
        io.echo("ship not defined!")
        return False

    player = kwargs.get("player")
    if player is None:
        io.echo("player not defined")
        return False

    width = kwargs.get("width", io.terminal.width())

    items = []
    for k, v in ship.manifest.items():
        items.append(
            EmpyreShipManifestListboxItem(k, width=width, ship=ship, player=player)
        )

    lb = Listbox(
        args, "select ship resource", itemsperpage=10, itemheight=1, items=items
    )
    op = lb.run("ship resource: ")
    if op.status == "selected" and op.item:
        io.echo(f"{op.item.pk}")
    return op


def runmodule(args: argparse.Namespace, modulename: str, **kwargs: Any) -> Any:
    return libempyre.runmodule(args, f"ship.{modulename}", **kwargs)


def count(args: argparse.Namespace, playermoniker: Optional[str] = None, **kwargs: Any) -> int:
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
