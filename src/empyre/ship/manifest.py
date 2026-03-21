import argparse
from typing import Any, Optional

from psycopg import sql

from bbsengine6 import database, io
from bbsengine6.database import _table_identifier
from bbsengine6.listbox import Listbox, ListboxItem, ListboxResult


def init(args, **kwargs):
    return True


def access(args, op, **kwargs):
    return True


def buildargs(args, **kwargs):
    return None


def load(ship) -> dict:
    def _work(conn: Any) -> dict:
        with database.cursor(conn) as cur:
            query = sql.SQL("select manifest from {} where moniker=%s").format(
                _table_identifier("empyre.ship")
            )
            dat = (ship.moniker,)
            cur.execute(query, dat)
            if cur.rowcount == 0:
                return {}
            rec = cur.fetchone()
            manifest = rec.get("manifest", {})
            ship.manifest = manifest if manifest else {}
            return ship.manifest

    pool = getattr(ship, "pool", None)
    if pool is None:
        io.echo(f"manifest.load.100: {pool=}", level="error")
        return {}
    with database.connect(ship.args, pool=pool) as conn:
        return _work(conn)


def save(ship) -> bool:
    def _work(conn: Any) -> bool:
        with database.cursor(conn) as cur:
            query = sql.SQL("update {} set manifest=%s where moniker=%s").format(
                _table_identifier("empyre.ship")
            )
            database.execute(cur, query, ship.manifest, ship.moniker)
            return cur.rowcount > 0

    pool = getattr(ship, "pool", None)
    if pool is None:
        io.echo(f"manifest.save.100: {pool=}", level="error")
        return False
    with database.connect(ship.args, pool=pool) as conn:
        return _work(conn)


def get_entry(ship, name: str) -> Optional[Any]:
    return ship.manifest[name] if name in ship.manifest else None


def select_item(args: argparse.Namespace, ship, player, **kwargs: Any) -> Any:
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

    if ship is None:
        io.echo("ship not defined!")
        return ListboxResult("cancelled")

    if player is None:
        io.echo("player not defined")
        return ListboxResult("cancelled")

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


def main(args, **kwargs):
    s = kwargs.get("ship")
    if s is None:
        io.echo("Ship does not exist", level="error")
        return False
    io.echo(f"ship {s.moniker} manifest{{f6:2}}")
    # TODO: Implement ship manifest viewer
    return True
