# @since 20220803 created 'drydock' module @see mdl.emp.delx2.txt#50277
# @since 20231222 renamed 'drydock' to 'dock'
#import bbsengine6 as bbsengine
from bbsengine6 import io, util

from . import lib as libempyre
from .ship import lib as libship

def scanshiplocations(args, location):
    sql = "select * from empyre.ship where ownerid=%s and location=%s"
    dat = (currentplayerid, location)

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args, **kwargs):
    return None

def dockhelp(**kwargs):
    io.echo("{var:optioncolor}[T]{var:labelcolor} Trade")
    io.echo("{var:optioncolor}[S]{var:labelcolor} Ship :ship:")
    io.echo("{var:optioncolor}[X]{var:labelcolor} Exit{var:normalcolor} :door:")
    return True

def trade(args, **kwargs):
    player = kwargs.get("player", None)

    yrd = player.getresource("shipyards")
    libempyre.trade(args, player, "shipyards", **yrd)

#    shp = player.getresource("ships")
#    libempyre.trade(args, player, "ships", **shp)

    nav = player.getresource("navigators")
    libempyre.trade(args, player, "navigators", **nav)

    player.adjust()
    player.save()

def main(args, **kwargs):
    player = kwargs.get("player", None)
    if player is None:
        io.echo("you do not exist! go away!", level="error")
        return False

    libempyre.setarea(args, "dock", player=player)

    io.echo("checking ship count..: ", end="")
    s = libship.count(args, playermoniker=player.moniker, **kwargs)
    io.echo(f"{s=}")

    if player.ships != s:
        player.ships = s
        player.adjust()
        player.save()

    done = False
    while not done:
        util.heading("dock")
        dockhelp()
        shp = player.getresource("ships")
        nav = player.getresource("navigators")
        yrd = player.getresource("shipyards")
        io.echo(f"You have {util.pluralize(player.ships, **shp)}, {util.pluralize(player.shipyards, **yrd)}, and {util.pluralize(player.navigators, **nav)}")
        ch = io.inputchar("{var:promptcolor}dock: {var:inputcolor}", "STQX", "X", help=dockhelp)
        if ch == "Q" or ch == "X":
            io.echo("exit")
            done = True
            break
        elif ch == "T":
            trade(args, **kwargs)
        elif ch == "R":
            io.echo("Recuit Navigator{/all}")
            if player.ships == 0:
                io.echo("You do not have any ships.")
            elif player.navigators <= player.ships and player.ships > 0:
                need = abs(player.ships - player.navigators)
                if need > 0:
#                    nav = player.getresource("navigators")
#                    shp = player.getresource("ships")
                    io.echo(f"You need {util.pluralize(need, **nav)} to outfit your {util.pluralize(player.ships, **shp)}.")
                    libempyre.trade(args, player, "navigators", "navigators", **nav)
        elif ch == "S":
            io.echo("Ships{/all}")
            libempyre.runmodule(args, "ship", location="mainland", **kwargs)
        else:
            io.echo("{bell}")

    return True
