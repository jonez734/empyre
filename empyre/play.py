import time

import ttyio5 as ttyio
import bbsengine5 as bbsengine

from . import lib

def init(args, **kwargs):
    pass

def main(args, player):
    player.datelastplayedepoch = time.mktime(time.localtime())
    
    if lib.runsubmodule(args, player, "sysopoptions") is not True:
        ttyio.echo("error running module 'sysopoptions'", level="error")

    ttyio.echo("{f6}{cyan}it is a new year...{/all}")

    player.turncount += 1

    if player.turncount > 4:
        ttyio.echo("{red}The other rulers unite against you for hogging the game!{/all}")
        return False
    
    player.adjust()
    player.save()

#    adjust(args, player)
    for x in ("weather", "disaster", "harvest", "colonytrip", "town", "combat", "quests", "investments"):
        if lib.runsubmodule(args, player, x) is False:
            ttyio.echo("error running submodule %r" % (x), level="error")
        player.save()

    ttyio.echo("end turn...{F6}")
    
    if player.serfs < 100:
        ttyio.echo("{green}You haven't enough serfs to maintain the empyre! It's turned over to King George and you are {yellow}beheaded{/fgcolor}{green}.{/all}")
        player.memberid = None
        player.save()
        return
        
    player.adjust()
    player.save()

    if lib.runsubmodule(args, player, "yearlyreport") is not True:
        ttyio.echo("error running 'yearlyreport' submodule.", level="debug")
    
    ttyio.echo("turn complete!", level="success")
    ttyio.echo("{/all}")

    return True
