import ttyio5 as ttyio
import bbsengine5 as bbsengine

from empyremodules import lib

def main(args, **kwargs):
    player = kwargs["player"] if "player" in kwargs else None

    ttyio.echo("sysopoptions.100: trace", level="debug")
    sysop = bbsengine.checkflag(args, "SYSOP")
    if sysop is False:
        ttyio.echo("permission denied")
        return False
    # ttyio.echo("sysopoptions.100: sysop=%r" % (sysop), level="debug")
    lib.setarea(args, player, "sysop options")
    bbsengine.title("sysop options")
    player.turncount = ttyio.inputinteger("{cyan}turncount: {lightgreen}", player.turncount)
    x = ttyio.inputinteger("{cyan}:moneybag: coins: {lightgreen}", player.coins)
    if x > 0:
        player.coins = x
    else:
        ttyio.echo("coins cannot be less than zero")
    ttyio.echo("{/all}")
    player.save()
    return True
