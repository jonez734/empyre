#import ttyio6 as ttyio
#import bbsengine6 as bbsengine

from bbsengine6 import io

from .. import lib

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args, **kw):
    return None

# @since 20200803
# @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_town.lbl#L90
def main(args, player, **kwargs):
    io.echo("current tax rate: %s" % (player.taxrate))
    x = io.inputinteger("{var:promptcolor}tax rate: {var:inputcolor}", player.taxrate)
    io.echo("{/all}")
    if x is None or x < 1:
        io.echo("no change")
        return True
    if x > 50:
        io.echo("King George looks at you sternly for trying to set such an exhorbitant tax rate, and vetoes the change.", level="error")
        return True
        
    player.taxrate = x
    return True
