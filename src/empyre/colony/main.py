# @since 20220729

import ttyio6 as ttyio
import bbsengine6 as bbsengine

def init(args, **kw):
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args, **kw):
    return None

def stats(args, **kw):
    bbsengine.util.heading("Colony Stats")
    ttyio.echo(f"{colony.moniker} (#{currentplayer.id}")
    ttyio.echo(f"Cash: {currentplayer.coins} Grain: {currentplayer.grain} Tax Rate: {currentplayer.taxrate}%") 
    ttyio.echo(f"Serfs    : {player.serfs}"+STR$(ys)+"{f6}{lt. green}Nobles   :{yellow}"+STR$(yw)
        z$="Im":if im=1 then z$="Ex"
        &"{lt. green}{pound}$zports  :{yellow}"+STR$(ye)+"{f6}{lt. green}Ships    :{yellow}"+STR$(yc)
        &"{f6:2}{lt. green}Navigator:{yellow}"+STR$(x8)+"{f6}{lt. green}Colonies :{yellow}"+STR$(i8)+"{f6}":RETURN

def main(args, **kw):
    player = kw["player"] if "player" in kw else None
    if player is None:
        ttyio.echo("you do not exist! go away!", level="error")
        return False

    ttyio.echo("colony trip... %s{f6}" % (bbsengine.util.pluralize(player.colonies, "colony", "colonies")))
    if player.colonies == 0:
#        ttyio.echo("You don't have any colonies!")
        return True

    ttyio.echo("King George wishes you a safe and prosperous trip to your %s{f6}" % (bbsengine.pluralize(player.colonies, "colony", "colonies", quantity=False)))

    return True
