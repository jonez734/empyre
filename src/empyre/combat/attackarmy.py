import random

from bbsengine6 import io, util

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

# @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/plus_emp6_combat.lbl#L74
def main(args, **kw):
    player = kw["player"] if "player" in kw else None
    if player is None:
        io.echo("You do not exist! Go Away!")
        return False

    otherplayer = kw["otherplayer"] if "otherplayer" in kw else None
    if otherplayer is None:
        io.echo("Your oponent does not exist!")
        return False

    def update():
        io.echo("%s: %s %s: %s" % (player.moniker, util.pluralize(player.soldiers, "soldier", "soldiers"), otherplayer.moniker, util.pluralize(otherplayer.soldiers, "soldier", "soldiers")))
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

    done = False
    while not done:
        if a == 5:
            a = 0
            res = player.getresource("soldiers")
            io.echo("%s: %s   %s: %s" % (player.moniker, util.pluralize(player.soldiers, **res), otherplayer.moniker, util.pluralize(otherplayer.soldiers, **res)))
        a += 1

        if player.soldiers < 1:
            player.soldiers = 0
            io.echo("You have no soldiers!")
            break

        if otherplayer.soldiers < 1:
            otherplayer.soldiers = 0
            io.echo("Your opponent has no soldiers!")
            break

        wz = int(player.soldiers * 0.08) # 8% of total
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
                io.echo("You conquered their land!")
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
