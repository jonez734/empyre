import time

from datetime import datetime
import dateutil.tz

from bbsengine6 import io, member

from . import lib # this means "import lib from the current package" also allows .. and ...

from . import player as libplayer

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args, **kwargs):
    return None

def main(args, **kwargs):
    player = kwargs.get("player", None)
    pool = kwargs.get("pool", None)
    if pool is None:
        io.echo(f"empyre.play.main.300: {pool=}", level="error")
        return False

#    currentmoniker = member.getcurrentmoniker(args, **kwargs)
#    playercount = libplayer.count(args, currentmoniker, **kwargs)
#    io.echo(f"empyre.main.100: {playercount=}", level="debug")
#    if playercount is None:
#        player = libplayer.create(args, pool=pool)
#        if player is None:
#            io.echo("empyre.main.200: unable to create new player!", level="error")
#            return False
#    elif playercount > 0:
#        io.echo(f"empyre.main.220: {pool=}", level="debug")
#        player = libplayer.select(args, currentmoniker, **kwargs)
#        if player is None:
#            return False

#    player = kw["player"] if "player" in kw else None
#    if player is None:
#        io.echo("You do not exist! Go Away!")
#        return False

#    io.echo(f"empyre.play.main.200: {player.resources['grain']=} {player.grain=} {player.attributes=}")
#    player.datelastplayedepoch = time.mktime(time.localtime())
    tzlocal = dateutil.tz.tzlocal()
    player.datelastplayed = datetime.now(tzlocal)
    
    io.echo(f"empyre.play.200: checking for sysop options... {kwargs=}")
    if lib.runmodule(args, "sysopoptions", **kwargs) is False:
        io.echo(f"failed to run module", level="error")
    else:
        io.echo(" ok ", level="ok")

    io.echo("{f6}{cyan}it is a new year...{/all}")
    if player.turncount >= libplayer.TURNSPERDAY:
        io.echo("{red}The other rulers unite against you for hogging the game!{/all}")
        player.turncount = libplayer.TURNSPERDAY
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

#    for x in ("dock",):# "investments"):
    for x in ("weather", "disaster", "colonytrip", "harvest", "town", "combat", "shipyard", "dock", "investments", "yearlyreport"): # quests after combat?
        if args.debug is True:
            io.echo(f"play.100: {x=}", level="debug")
        if lib.runmodule(args, x, **kwargs) is False:
            io.echo("error running submodule %r" % (x), level="error")
        player.adjust()
        player.save()

    io.echo("turn complete!", level="success")
    io.echo("{/all}")

    return True
