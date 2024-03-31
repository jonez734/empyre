import time

from datetime import datetime
import dateutil.tz

from bbsengine6 import io

from . import lib # this means "import lib from the current package" also allows .. and ...

def init(args, **kwargs):
    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

def main(args, **kw):
    player = kw["player"] if "player" in kw else None
    if player is None:
        io.echo("You do not exist! Go Away!")
        return False

#    player.datelastplayedepoch = time.mktime(time.localtime())
    tzlocal = dateutil.tz.tzlocal()
    player.datelastplayed = datetime.now(tzlocal)
    
    if lib.runmodule(args, "sysopoptions", **kw) is False:
        io.echo("error running module 'sysopoptions'", level="warn")

    io.echo("{f6}{cyan}it is a new year...{/all}")

    if player.turncount >= lib.TURNSPERDAY:
        io.echo("{red}The other rulers unite against you for hogging the game!{/all}")
        player.turncount = lib.TURNSPERDAY
        player.save()
        return True
    
#    if player.coins is not None:
#        coins = player.getresource("coins")
#        coins["value"] = player.coins
#        player.coins = None
    player.turncount += 1
    player.adjust()
    player.save()
    io.echo(f"{player.datelastplayed=}", level="debug")

    for x in ("dock",): # town.naturaldisasterbank",): # "yearlyreport",):
#    for x in ("weather", "disaster", "harvest", "colonytrip", "town", "combat", "dock", "quests", "investments"):
        if args.debug is True:
            io.echo(f"play.100: {x=}", level="debug")
        if lib.runmodule(args, x, **kw) is False:
            io.echo("error running submodule %r" % (x), level="error")
        player.adjust()
        player.save()

    io.echo("end turn...{F6}")
    
    if player.serfs < 100:
        player.beheaded = True
        player.memberid = None
        player.adjust()
        player.save(force=True)
        io.echo("{normalcolor}You haven't enough serfs to maintain the empyre! It's turned over to King George and you are {highlightcolor}beheaded{normalcolor}.{/all}")
        return

    player.adjust()
    player.save()

    if lib.runmodule(args, "yearlyreport", **kw) is not True:
        io.echo("error running 'yearlyreport' submodule.", level="debug")
    
    io.echo("turn complete!", level="success")
    io.echo("{/all}")

    return True
