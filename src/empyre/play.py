import time

from datetime import datetime

import ttyio5 as ttyio
import bbsengine5 as bbsengine

from . import lib # this means "import lib from the current package" also allows .. and ...

def init(args, **kwargs):
    return True

def main(args, **kw):
    player = kw["player"] if "player" in kw else None
#    player.datelastplayedepoch = time.mktime(time.localtime())
    player.datelastplayed = datetime.now().isoformat()
    
    if lib.runsubmodule(args, player, "sysopoptions") is not True:
        ttyio.echo("error running module 'sysopoptions'", level="error")

    ttyio.echo("{f6}{cyan}it is a new year...{/all}")

    if player.turncount >= lib.TURNSPERDAY:
        ttyio.echo("{red}The other rulers unite against you for hogging the game!{/all}")
        player.turncount = lib.TURNSPERDAY
        player.save()
        return True
    
    player.turncount += 1
    player.adjust()
    player.save()

    for x in ("drydock",):
#    for x in ("quests",):
#    for x in ("combat", ):
        if args.debug is True:
            ttyio.echo(f"play.100: x={x!r}", level="debug")
#    for x in ("weather", "disaster", "harvest", "colonytrip", "town", "combat", "drydock", "quests", "investments"):
        if lib.runsubmodule(args, player, x) is False:
            ttyio.echo("error running submodule %r" % (x), level="error")
        player.adjust()
        player.save()

    ttyio.echo("end turn...{F6}")
    
    if player.serfs < 100:
        ttyio.echo("{var:normalcolor}You haven't enough serfs to maintain the empyre! It's turned over to King George and you are {var:highlightcolor}beheaded{var:normalcolor}.{/all}")
        player.memberid = None
        player.beheaded = True
        player.save()
        return
        
    player.adjust()
    player.save()

    if lib.runsubmodule(args, player, "yearlyreport") is not True:
        ttyio.echo("error running 'yearlyreport' submodule.", level="debug")
    
    ttyio.echo("turn complete!", level="success")
    ttyio.echo("{/all}")

    return True
