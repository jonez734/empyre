# @since 20220729
# @since 20230716 ported to bbsengine6

#import ttyio6 as ttyio
#import bbsengine6 as bbsengine
from bbsengine6 import io, util

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def main(args, **kwargs):
    player = kwargs["player"] if "player" in kwargs else None

    # if you are a KING, you only get average weather and below
    if player.rank == 2:
        weathercondition = util.diceroll(4) # random.randint(1, 4)
    else:
        weathercondition = util.diceroll(6) # random.randint(1, 6)

    io.echo("{cyan}")
    if weathercondition == 1:
        io.echo(":desert: Poor Weather. No Rain. Locusts Migrate")
    elif weathercondition == 2:
        io.echo(":cactus: Early Frosts. Arid Conditions")
    elif weathercondition == 3:
        io.echo(":thunder-cloud-and-rain: Flash Floods. Too Much Rain")
    elif weathercondition == 4:
        io.echo("Average Weather. Good Year")
    elif weathercondition == 5:
        io.echo("Fine Weather. Long Summer")
    elif weathercondition == 6:
        io.echo(":sun: Fantastic Weather! Great Year!")
        
    io.echo("{/all}")
    player.weathercondition = weathercondition

    return True
