from random import random

import ttyio5 as ttyio
import bbsengine5 as bbsengine

from . import lib

def init(args, **kw):
    return True

def main(args, **kw):
    player = kw["player"] if "player" in kw else None
    if player is None:
        return False
    
    ttyio.echo("ambush noble")

    if player.soldiers < 1: # x(21)
        ttyio.echo("You do not have any soldiers!")
        return True
    
    if random()*player.soldiers<random()*otherplayer.soldiers*1.7:
        ttyio.echo("his guards foil your plans!")
        # @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/mdl.emp.delx3.txt#L160
        x = random()*(player.soldiers*0.3)+1
        player.soldiers -= x

    # if k(6)<2ork(21)<20orx(6)<1then a$=c2$+"{f5}None Found!":sys c(.):goto 50091
    if otherplayer.nobles < 2 or otherplayer.soldiers < 20 or player.nobles < 1:
        ttyio.echo("None found!")
        return True
    # x=int(rnd(1)*(x(21)*.3)+1):x(21)=x(21)-x:if x(21)<.then x(21)=.
    
    return True
