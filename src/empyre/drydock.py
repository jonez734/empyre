# @since 20220803 created 'drydock' module @see mdl.emp.delx2.txt#50277

import ttyio5 as ttyio
import bbsengine5 as bbsengine


from . import lib

def init(args, **kw):
    return

def access(args, op, **kw):
    return True

def main(args, **kw):
    player = kw["player"] if "player" in kw else None

    if player is None:
        ttyio.echo("you do not exist! go away!", level="error")
        return False

    loop = True
    while loop:
        bbsengine.title("dry dock")
        lib.setarea(args, player, "dry dock")

        ttyio.echo("You have %s and %s" % (bbsengine.pluralize(player.ships, "ship", "ships"), bbsengine.pluralize(player.navigators, "navigator", "navigators")))
        ttyio.echo(":compass: {var:optioncolor}[R]{var:labelcolor}ecruit navigator{var:normalcolor}") # show how many are needed per ship
        ttyio.echo(":package: {var:optioncolor}[E]{var:labelcolor}xports{var:normalcolor}")
        ttyio.echo(":anchor: {var:optioncolor}[S]{var:labelcolor}hips{var:normalcolor}")
        ttyio.echo("{f6}:door: {var:optioncolor}[Q]{var:labelcolor}uit{var:normalcolor}")
        ch = ttyio.inputchar("{var:promptcolor}dry dock: {var:inputcolor}", "RESQ", "Q")
        if ch == "Q":
            loop = False
            break
        elif ch == "E":
            ttyio.echo("Exports")
        elif ch == "R":
            ttyio.echo("Recuit Navigator")
            if player.navigators <= player.ships:
                need = abs(player.ships - player.navigators)
                if need > 0:
                    ttyio.echo("You need %s to outfit your %s." % (bbsengine.pluralize(player.navigators, "navigator", "navigators"), bbsengine.pluralize(player.ships, "ship", "ships")))
        elif ch == "S":
            ttyio.echo("Ships")

    return True
