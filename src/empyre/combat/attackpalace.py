import random

from bbsengine6 import io, util

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args, **kwargs):
    return None

# @see empire6/plus_emp6_combat.lbl#L105
def main(args, **kwargs):
    player = kwargs.get("player", None)
    otherplayer = kwargs.get("otherplayer", None)

    if otherplayer.palaces < 1:
        io.echo("They have no palaces!")
        return True

    if player.soldiers < 1:
        io.echo("You have no soldiers!")
        return True

    # empire6/plus_emp6_combat.lbl#L108
    io.echo("{F6:2}You attack an enemy palace...")
    if random.random()*player.soldiers < random.random()*otherplayer.soldiers*3:
        io.echo("{F6}{lightblue}Guards appear and thwart your attempt!")
        soldierslost = random.randint(2, player.soldiers//3)
        res = player.getresource("soldiers")
        io.echo("{F6:2}{white}--> {lightblue}The guards kill %s{F6}" % (util.pluralize(soldierslost, **res)))
        player.soldiers -= soldierslost # sl
        io.echo("{/all}")
        return True
    io.echo("{F6}You destroyed one of their palaces!{f6}")
    soldierslost = random.randint(1, player.soldiers//2)
    if otherplayer.nobles > 0:
        otherplayer.nobles += 1
    otherplayer.soldiers = min(otherplayer.nobles*20, otherplayer.soldiers)
    #if otherplayer.soldiers > otherplayer.nobles*20:
    #    otherplayer.soldiers = otherplayer.nobles*20
    # e1=e1+(e1>.):en=en+(en>.):if ew>en*20 then ew=en*20
    return True
