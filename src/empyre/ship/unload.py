import argparse
from typing import Any, Optional

from bbsengine6 import database, io, util

from . import manifest

STATUS_CANCELLED = "cancelled"
STATUS_NOITEMS = "noitems"


def init(args: argparse.Namespace, **kwargs: Any) -> bool:
    return True


def access(args: argparse.Namespace, op: Any, **kwargs: Any) -> bool:
    return True


def buildargs(args: Optional[argparse.Namespace] = None, **kwargs: Any) -> None:
    return None


def main(args: argparse.Namespace, **kwargs: Any) -> bool:
    player = kwargs["player"] if "player" in kwargs else None
    ship = kwargs["ship"] if "ship" in kwargs else None

    io.echo("unload")
    if args.debug is True:
        io.echo(f"{player=} {ship=}", level="debug")
    op = manifest.select_item(args, ship, player, **kwargs)
    if args.debug is True:
        io.echo(f"{op=}", level="debug")
    if op.status in (STATUS_CANCELLED, STATUS_NOITEMS):
        return True

    resourcename = op.item.pk
    manifestentry = manifest.get_entry(ship, resourcename)
    if type(manifestentry) is int:
        manifestentry = {"value": manifestentry}
    manifestentryvalue = manifestentry["value"]

    playerres = player.getresource(resourcename)

    playerattr = getattr(player, resourcename)

    io.echo(f"{resourcename=}", level="debug")
    if resourcename not in ship.manifest:
        io.echo(f"You do not have any {resourcename} on board.")
        ship.manifest[resourcename] = {"value": 0}
        return True

    amount = io.inputinteger(
        f"{{promptcolor}}unload amount of {resourcename}: {{inputcolor}}",
        manifestentry["value"],
        **kwargs,
    )
    if amount is None or amount == 0:
        io.echo("aborted.")
        return True

    if amount < 0:
        io.echo("Must specify an amount greater than zero.")
        return True
    if amount > manifestentryvalue:
        io.echo(
            f"This ship has {{valuecolor}}{util.pluralize(manifestentryvalue, **playerres)}"
        )
        return True

    if manifestentryvalue < 0:
        manifestentryvalue = 0

    manifestentry["value"] = manifestentryvalue - amount
    playerattr += amount
    setattr(player, resourcename, playerattr)

    ship.manifest[resourcename] = manifestentry

    player.adjust()
    player.save()
    ship.adjust()
    ship.save()
    database.commit(args)
    return True
