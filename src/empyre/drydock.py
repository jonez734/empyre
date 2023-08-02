# @since 20220803 created 'drydock' module @see mdl.emp.delx2.txt#50277

import ttyio5 as ttyio
import bbsengine5 as bbsengine

from . import lib

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def main(args, **kw):
    player = kw["player"] if "player" in kw else None

    if player is None:
        ttyio.echo("you do not exist! go away!", level="error")
        return False
    def help(**kw):
        ttyio.echo(":compass: {var:optioncolor}[R]{var:labelcolor}ecruit navigator{var:normalcolor}") # show how many are needed per ship
        ttyio.echo(":package: {var:optioncolor}[E]{var:labelcolor}xports{var:normalcolor}")
        ttyio.echo(":anchor: {var:optioncolor}[S]{var:labelcolor}hips{var:normalcolor}")
        ttyio.echo("{f6}:door: {var:optioncolor}[Q]{var:labelcolor}uit{var:normalcolor}")

    done = False
    while not done:
        bbsengine.title("dry dock")
        lib.setarea(args, player, "dry dock")
        help()
        ttyio.echo("You have %s and %s" % (bbsengine.pluralize(player.ships, "ship", "ships"), bbsengine.pluralize(player.navigators, "navigator", "navigators")))
        ch = ttyio.inputchar("{var:promptcolor}dry dock: {var:inputcolor}", "RESQ", "Q", help=help)
        if ch == "Q":
            done = True
            break
        elif ch == "E":
            ttyio.echo("Exports{/all}")
        elif ch == "R":
            ttyio.echo("Recuit Navigator{/all}")
            if player.ships == 0:
                ttyio.echo("You do not have any ships.")
            elif player.navigators <= player.ships:
                need = abs(player.ships - player.navigators)
                if need > 0:
                    ttyio.echo("You need %s to outfit your %s." % (bbsengine.util.pluralize(player.navigators, "navigator", "navigators"), bbsengine.util.pluralize(player.ships, "ship", "ships")))
                    lib.trade(args, player, "navigators", "navigators", price=500, singular="navigator", plural="navigators", emoji=":compass:")
        elif ch == "S":
            ttyio.echo("Ships{/all}")
            if player.shipyards > 0:
                lib.trade(args, player, "ships", "ships", price=5000, singular="ship", plural="ships", emoji=":anchor:")
            else:
                ttyio.echo("You do not have any shipyards.")

    return True
