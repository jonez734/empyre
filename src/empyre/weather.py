# @since 20220729
# @since 20230716 ported to bbsengine6
from bbsengine6 import io, util
from . import lib as libempyre

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args=None, **kw):
    return None

def main(args, **kwargs):
    player = kwargs["player"] if "player" in kwargs else None
    if player is None:
        io.echo("You do not exist, go away!", level="error")
        return False

    # if you are a KING, you only get average weather and below
    if player.rank == 2:
        weathercondition = util.diceroll(4) # random.randint(1, 4)
    else:
        weathercondition = util.diceroll(6) # random.randint(1, 6)

    io.echo("{cyan}", end="")
    if weathercondition == libempyre.Weather.POOR:
        io.echo(":desert: Poor Weather. No Rain. Locusts Migrate")
    elif weathercondition == libempyre.Weather.ARID:
        io.echo(":cactus: Early Frosts. Arid Conditions")
    elif weathercondition == libempyre.Weather.RAIN:
        io.echo(":thunder-cloud-and-rain: Flash Floods. Too Much Rain")
    elif weathercondition == libempyre.Weather.AVERAGE:
        io.echo("Average Weather. Good Year")
    elif weathercondition == libempyre.Weather.LONGSUMMER:
        io.echo("Fine Weather. Long Summer")
    elif weathercondition == libempyre.Weather.FANTASTIC:
        io.echo(":sun: Fantastic Weather! Great Year!")
        
    io.echo("{/all}", end="", flush=True)
    player.weathercondition = weathercondition

    return True
