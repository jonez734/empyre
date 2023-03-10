import random

import ttyio5 as ttyio

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

# @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/plus_emp6_combat.lbl#L105
def main(args, **kwargs):
    player = kwargs["player"] if "player" in kwargs else None
    otherplayer = kwargs["otherplayer"] if "otherplayer" in kwargs else None

    if otherplayer.palaces < 1:
        ttyio.echo("They have no palaces!")
        return

    if player.soldiers < 1:
        ttyio.echo("You have no soldiers!")
        return

    # https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/plus_emp6_combat.lbl#L108
    ttyio.echo("{F6:2}You attack an enemy palace...")
    if random.random()*player.soldiers < random.random()*otherplayer.soldiers*3:
        ttyio.echo("{F6}{lightblue}Guards appear and thwart your attempt!")
        soldierslost = random.randint(2, player.soldiers//3)
        ttyio.echo("{F6:2}{white}--> {lightblue}The guards kill %s{F6}" % (bbsengine.pluralize(soldierslost, "soldier", "soldiers")))
        player.soldiers -= soldierslost # sl
        ttyio.echo("{/all}")
        return
    ttyio.echo("{F6}You destroyed one of their palaces!{f6}")
    soldierslost = random.randint(1, player.soldiers//2)
    if otherplayer.nobles > 0:
        otherplayer.nobles += 1
    otherplayer.soldiers = min(otherplayer.nobles*20, otherplayer.soldiers)
    #if otherplayer.soldiers > otherplayer.nobles*20:
    #    otherplayer.soldiers = otherplayer.nobles*20
    # e1=e1+(e1>.):en=en+(en>.):if ew>en*20 then ew=en*20
    return
