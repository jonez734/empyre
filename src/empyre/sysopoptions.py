#import ttyio6 as ttyio
#import bbsengine6 as bbsengine
from bbsengine6 import io, member, util

from . import lib

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    conn = kwargs.get("conn", None)
    if conn is None:
        pool = kwargs.get("pool")
        if pool is None:
            return False
        conn = database.connect(args, pool=pool)

    sysop = member.checkflag(args, "SYSOP", mogrify=True, conn=conn)
    io.echo(f"empyre.sysopoptions.120: {sysop=}", level="debug")
    if sysop is True:
        io.echo("empyre.sysopoptions.140: access check pass", level="debug")
        return True
    io.echo("empyre.sysopoptions.access.100: permission denied")
    return False

def buildargs(args, **kwargs):
    return None

def main(args, **kwargs):
    player = kwargs.get("player", None)
    if player is None:
        io.echo("You do not exist! Go away!", level="error")
        return False

#    ttyio.echo("sysopoptions.100: trace", level="debug")
#    sysop = bbsengine.checkflag(args, "SYSOP")
#    if sysop is False:
#        ttyio.echo("permission denied")
#        return False
    # ttyio.echo("sysopoptions.100: sysop=%r" % (sysop), level="debug")
    lib.setarea(args, "sysop options", player=player)
    util.heading("sysop options")
    player.turncount = io.inputinteger("{var:promptcolor}turncount: {var:inputcolor}", player.turncount, args=args, **kw)
    x = io.inputinteger("{var:promptcolor}:moneybag: coins: {var:inputcolor}", player.coins, **kw)
    if x > 0:
        player.coins = x
    else:
        io.echo("coins cannot be less than zero")
    io.echo("{/all}")
    player.adjust()
    player.save()
    io.echo(util.hr())
    return True
