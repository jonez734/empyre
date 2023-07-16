import ttyio6 as ttyio
import bbsengine6 as bbsengine

from .. import lib

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

# @since 20200803
# @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_town.lbl#L90
def main(args, player, **kwargs):
    ttyio.echo("current tax rate: %s" % (player.taxrate))
    x = ttyio.inputinteger("{green}tax rate: {lightgreen}", player.taxrate)
    ttyio.echo("{/all}")
    if x is None or x < 1:
        ttyio.echo("no change")
        return True
    if x > 50:
        ttyio.echo("King George looks at you sternly for trying to set such an exhorbitant tax rate, and vetoes the change.", level="error")
        return True
        
    player.taxrate = x
    return True
