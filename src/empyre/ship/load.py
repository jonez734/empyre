from bbsengine6 import io, database, util
from . import lib
from .. import lib as libempyre

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

def main(args, **kw):
    player = kw["player"] if "player" in kw else None
    ship = kw["ship"] if "ship" in kw else None

    player.save()
    #for name in player.resources.keys():
    #    r = player.resources[name]
    #    r["value"] = getattr(player, name)
    #    io.echo("{name=} {r['value']=}", level="debug")

    op = libempyre.selectresource(args, "select load resource", player.resources, **kw)
    if op.kind == "exit":
        return True

    resourcename = op.listitem.pk
#    io.echo(f"{resourcename=}", level="debug")

    io.echo("load")
    attr = getattr(player, resourcename)
    amount = io.inputinteger(f"{{promptcolor}}load amount of {resourcename}: {{inputcolor}}", attr)
    if amount is None:
        io.echo("aborted.")
        return True
    elif amount < 0:
        io.echo("Must specify an amount greater than zero.")
        return True
    elif amount > attr:
        res = player.getresource(resourcename)
        io.echo(f"You are short by {{valuecolor}}{util.pluralize(amount - attr, **res)} of {resourcename}.")
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
