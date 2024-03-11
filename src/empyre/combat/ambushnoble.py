from random import random

from bbsengine6 import io, util

from . import lib

def init(args, **kw):
    return True

def main(args, **kw):
    player = kw["player"] if "player" in kw else None
    if player is None:
        return False

    otherplayer = kw["otherplayer"] if "otherplayer" in kw else None

    util.heading("ambush noble")

    if player.soldiers < 1: # x(21)
        io.echo("You do not have any soldiers!")
        return True

    # if k(6)<2ork(21)<20orx(6)<1then a$=c2$+"{f5}None Found!":sys c(.):goto 50091
    if otherplayer.nobles < 2 or otherplayer.soldiers < 20 or player.nobles < 1:
        io.echo("No Nobles found!")
        return True

    if random()*player.soldiers < random()*otherplayer.soldiers*1.7:
        io.echo("Their guards foil your plans!")
        # @see mdl.emp.delx3.txt
        x = int(random()*(player.soldiers*0.3))+1
        player.soldiers -= x

    player.adjust()
    player.save()
    # x=int(rnd(1)*(x(21)*.3)+1):x(21)=x(21)-x:if x(21)<.then x(21)=.

    return True
