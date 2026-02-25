import ttyio6 as ttyio
import bbsengine6 as bbsengine

from . import lib

def init(args, **kw):
    return

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

def main(args, **kw):
    bbsengine.util.heading("load ship")
    # query ship name to be loaded
    # grain, serf, noble, navigator
    if player.ships == 0:
        ttyio.echo("You do not have any ships!")
        return True
    
    grain = ttyio.inputinteger("grain: ", player.grain)
    if grain > player.grain:
        ttyio.echo("You only have {bbsengine.util.pluralize(player.grain, 'bushel', 'bushels', emoji=':crop:')}!")
    else:
        if "grain" in ship.manifest:
            ship.manifest["grain"] += grain
        else:
            ship.manifest["grain"] = grain
        player.grain -= grain

    serfs = ttyio.inputinteger("serfs: ", player.serfs)
    if serfs > player.serfs:
        ttyio.echo("You only have {bbsengine.util.pluralize(player.serfs, 'serf', 'serf'}!")
    else:
        if "serfs" in ship.manifest:
            ship.manifest["serfs"] += serfs
        else:
            ship.manifest["serfs"] = serfs
        player.serfs -= serfs

    return True
