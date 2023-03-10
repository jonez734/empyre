import random

import ttyio5 as ttyio
import bbsengine5 as bbsengine

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

# @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/plus_emp6_combat.lbl#L74
def main(args, player, **kw):
#    player = kw["player"] if "player" in kw else None
    if player is None:
        ttyio.echo("You do not exist! Go Away!")
        return

    otherplayer = kw["otherplayer"] if "otherplayer" in kw else None
    if otherplayer is None:
        ttyio.echo("Your oponent does not exist!")
        return True

    def update():
        ttyio.echo("%s: %s %s: %s" % (player.name, bbsengine.pluralize(player.soldiers, "soldier", "soldiers"), otherplayer.name, bbsengine.pluralize(otherplayer.soldiers, "soldier", "soldiers")))
        return

    ff = 1

    pv = 0 # player victory

    sr = otherplayer.soldiers # aka 'wa'
    sg = player.soldiers

    a2 = 20
    b2 = 20

    a = 0

    sr = otherplayer.soldiers
    sg = player.soldiers

    loop = True
    while loop:
        if a == 5:
            a = 0
            ttyio.echo("%s: %s   %s: %s" % (player.name, bbsengine.pluralize(player.soldiers, "soldier", "soldiers"), otherplayer.name, bbsengine.pluralize(otherplayer.soldiers, "soldier", "soldiers")))

        a += 1

        if player.soldiers < 1:
            player.soldiers = 0
            ttyio.echo("You have no soldiers!")
            break

        if otherplayer.soldiers < 1:
            otherplayer.soldiers = 0
            ttyio.echo("Your opponent has no soldiers!")
            break

        wz = int(player.soldiers * 0.08) # 8%
        ed = int(otherplayer.soldiers * 0.08)
        # z9 == player.training, og == otherplayer.training, and ez == otherplayer.land
        # if (rnd(1)*wz)+(rnd(1)*(300+z9*5)) > (rnd(1)*ed)+(rnd(1)*(300+og*5)) then {:combat_90} # what are "z9" and "og"?
        if ((random.random()*wz)+(random.random()*(300+player.training*5))) > ((random.random()*ed)+(random.random()*(300+otherplayer.training*5))):
            otherplayer.soldiers -= 1 # ew -= 1
            b2 -= 1
            a2 = 20
            if otherplayer.soldiers > 0 and b2 > 0:
                # another round
                continue

            # at this point, either otherplayer.soldiers == 0 or b2 == 0
            bn = 1 # when > 0, shows player attributes
            if player.soldiers > random.randint(0, otherplayer.land):
                ttyio.echo("You conquered their land!")
                player.land += otherplayer.land
                otherplayer.land = 0
                break
        else:
            player.soldiers -= 1
            a2 -= 1
            b2 = 20
            if player.soldiers > 0 and a2 > 0:
                continue
            player.soldiers = 0
            pv = 1

        otherplayer.adjust()
        otherplayer.save()
        
        player.adjust()
        player.save()
