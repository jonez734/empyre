from bbsengine6 import io, database

from . import lib

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args=None, **kw):
    return None

def main(args, **kw):
    player = kw["player"] if "player" in kw else None
    ship = kw["ship"] if "ship" in kw else None

    io.echo("unload")
    if args.debug is True:
        io.echo(f"{player=} {ship=}", level="debug")
    op = lib.selectmanifestitem(args, **kw)
    if args.debug is True:
        io.echo(f"{op=}", level="debug")
    if op.kind == "exit":
        return True

    resourcename = op.listitem.pk
    playerres = player.getresource(resourcename)
    manifestentry = ship.getmanifestentry(resourcename)
    if type(manifestentry) is int:
        manifestentry = {"value":manifestentry}
    manifestentryvalue = manifestentry["value"]

    playerattr = getattr(player, resourcename)

    io.echo(f"{resourcename=}", level="debug")
    if resourcename not in ship.manifest:
        io.echo(f"You do not have any {resourcename} on board.")
        ship.manifest[resourcename] = {"value":0}
        return True

    amount = io.inputinteger(f"{{promptcolor}}unload amount of {resourcename}: {{inputcolor}}", manifestentry["value"])
    if amount is None or amount == 0:
        io.echo("aborted.")
        return True

    if amount < 0:
        io.echo("Must specify an amount greater than zero.")
        return True
    elif amount > manifestentryvalue:
        io.echo("This ship has {util.pluralize(manifestentryvalue, **playerres)}")
        return True

    else:
        if manifestentryvalue < 0:
            manifestentryvalue = 0

        if amount > manifestentryvalue:
            io.echo("You only have {util.pluralize(amount, **playerres)} on board.")
            return True

        if resourcename in ship.manifest:
            manifestentry["value"] -= amount
        else:
            manifestentry["value"] = 0

        playerattr += amount
        setattr(player, resourcename, playerattr)

        ship.manifest[resourcename] = manifestentry

    player.adjust()
    player.save()
    ship.adjust()
    ship.save()
    return True
