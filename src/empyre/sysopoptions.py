import ttyio6 as ttyio
import bbsengine6 as bbsengine

from . import lib

def init(args, **kw):
    pass

def access(args, op, **kw):
    sysop = bbsengine.member.checkflag(args, "SYSOP")
    if sysop is True:
        return True
    ttyio.echo("empyre.sysopoptions.access.100: permission denied")
    return False

def main(args, **kwargs):
    player = kwargs["player"] if "player" in kwargs else None
    if player is None:
        ttyio.echo("You do not exist! Go away!", level="error")
        return False

#    ttyio.echo("sysopoptions.100: trace", level="debug")
#    sysop = bbsengine.checkflag(args, "SYSOP")
#    if sysop is False:
#        ttyio.echo("permission denied")
#        return False
    # ttyio.echo("sysopoptions.100: sysop=%r" % (sysop), level="debug")
    lib.setarea(args, player, "sysop options")
    bbsengine.util.heading("sysop options")
    player.turncount = ttyio.inputinteger("{var:promptcolor}turncount: {var:inputcolor}", player.turncount)
    x = ttyio.inputinteger("{var:promptcolor}:moneybag: coins: {var:inputcolor}", player.coins)
    if x > 0:
        player.coins = x
    else:
        ttyio.echo("coins cannot be less than zero")
    ttyio.echo("{/all}")
    player.save()
    ttyio.echo(bbsengine.util.hr())
    return True
