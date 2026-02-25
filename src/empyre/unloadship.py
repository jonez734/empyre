import ttyio6 as ttyio
import bbsengine6 as bbsengine

from . import lib

def init(args, **kw):
    return

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

def transfercargo(args, name, anount, player, ship):
    res = player.getresource(resourcename)
    if res is None:
        ttyio.echo(f"{name!r} does not exist!", level="error")
        return False

    if name not in ship.manifest:
        ttyio.echo(f"{name!r} is not on the manifest", level="error")
        return False

    if ship.manifest[name] < 1:
        ttyio.echo(f"The ship does not have {name!r}")
        ship.manifest[name] = 0

    x = ttyio.inputinteger(f"{{var:promptcolor}}{name}: {{var:inputcolor}}", ship.manifest[name])
    if x > ship.manifest[name]:
        emoji = res["emoji"] if "emoji" in res else ""
        ttyio.echo("The manifest does not contain {x} {bbsengine.util.pluralize(x, res['singular'], res['plural'], emoji)}", level="error")
        return False
    
    if name not in player:
        setattr(player, name) = x
        ship.manifest[name] -= x
        return True
    
    attr = getattr(player, name)
    attr += x
    ship.manifest[name] -= x

    if attr < 0:
        attr = 0
        
    if ship.manifest[name] < 0:
        ship.manifest[name] = 0

def main(args, **kw):
    bbsengine.util.heading("unload ship")
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
            ship.manifest["grain"] -= grain
        else:
            ship.manifest["grain"] = grain
        player.grain += grain

    serfs = ttyio.inputinteger("serfs: ", ship.manifest["serfs"])
        
    if serfs > player.serfs or serfs < 0:
        ttyio.echo("You only have {bbsengine.util.pluralize(player.serfs, 'serf', 'serf'}!")
    else:
        if "serfs" in ship.manifest:
            ship.manifest["serfs"] -= serfs
        else:
            ship.manifest["serfs"] = serfs
        if ship.manifest["serfs"] < 0:
            ship.manifest["serfs"] = 0
        player.serfs += serfs

    logs = ttyio.inputinteger("logs: ", ship.manifest["logs"])
        
    if logs > player.timber or timber < 0:
        ttyio.echo("You only have {bbsengine.util.pluralize(player.timber, 'board', 'boards'}!")
    else:
        if "timber" in ship.manifest:
            ship.manifest["timber"] -= timber
        else:
            ship.manifest["timber"] = timber
        if ship.manifest["timber"] < 0:
            ship.manifest["timber"] = 0
        player.timber += timber

    return True
