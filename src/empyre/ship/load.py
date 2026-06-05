import argparse
from typing import Any, Optional

from bbsengine6 import database, io, util
from .. import lib as libempyre
from . import manifest as ship_manifest  # noqa: F401  (kept for symmetry with unload.py)

STATUS_CANCELLED = "cancelled"
STATUS_NOITEMS = "noitems"


def init(args: argparse.Namespace, **kwargs: Any) -> bool:
    return True


def access(args: argparse.Namespace, op: Any, **kwargs: Any) -> bool:
    return True


def buildargs(args: argparse.Namespace, **kwargs: Any) -> None:
    return None


def main(args: argparse.Namespace, **kwargs: Any) -> bool:
    player: Optional[Any] = kwargs["player"] if "player" in kwargs else None
    ship: Optional[Any] = kwargs["ship"] if "ship" in kwargs else None

    player.save()
    # for name in player.resources.keys():
    #    r = player.resources[name]
    #    r["value"] = getattr(player, name)
    #    io.echo("{name=} {r['value']=}", level="debug")

    op = libempyre.selectresource(
        args, "select load resource", player.resources, **kwargs
    )
    io.echo(f"empyre.ship.load.100: {op=}", level="debug")
    if op.status in (STATUS_CANCELLED, STATUS_NOITEMS):
        return True

    resourcename = op.item.pk
    #    io.echo(f"{resourcename=}", level="debug")

    io.echo("load")
    attr = getattr(player, resourcename)
    amount = io.inputinteger(
        f"{{promptcolor}}load amount of {resourcename}: {{inputcolor}}", attr, **kwargs
    )
    if amount is None:
        io.echo("aborted.")
        return True
    elif amount < 0:
        io.echo("Must specify an amount greater than zero.")
        return True
    elif amount > attr:
        res = player.getresource(resourcename)
        io.echo(
            f"You are short by {{valuecolor}}{util.pluralize(amount - attr, **res)} of {resourcename}."
        )
        return True
    else:
        attr -= amount
        setattr(player, resourcename, attr)
        if resourcename in ship.manifest:
            ship.manifest[resourcename]["value"] += amount
        else:
            ship.manifest[resourcename] = {"value": amount}

    player.adjust()
    player.save()
    ship.adjust()
    ship.save()
    database.commit(args)
    return True
