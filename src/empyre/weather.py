# @since 20220729
# @since 20230716 ported to bbsengine6

import ttyio6 as ttyio
import bbsengine6 as bbsengine

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def main(args, **kwargs):
    player = kwargs["player"] if "player" in kwargs else None

    # if you are a KING, you only get average weather and below
    if player.rank == 2:
        weathercondition = bbsengine.util.diceroll(4) # random.randint(1, 4)
    else:
        weathercondition = bbsengine.util.diceroll(6) # random.randint(1, 6)

    ttyio.echo("{cyan}")
    if weathercondition == 1:
        ttyio.echo("Poor Weather. No Rain. Locusts Migrate")
    elif weathercondition == 2:
        ttyio.echo(":cactus: Early Frosts. Arid Conditions")
    elif weathercondition == 3:
        ttyio.echo(":thunder-cloud-and-rain: Flash Floods. Too Much Rain")
    elif weathercondition == 4:
        ttyio.echo("Average Weather. Good Year")
    elif weathercondition == 5:
        ttyio.echo("Fine Weather. Long Summer")
    elif weathercondition == 6:
        ttyio.echo(":sun: Fantastic Weather! Great Year!")
        
    ttyio.echo("{/all}")
    player.weathercondition = weathercondition

    return True
