# barbarians are buying
# @since 20201207
# @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/plus_emp6_combat.lbl#L178

import random

import ttyio5 as ttyio
import bbsengine5 as bbsengine

from . import lib

def init(args, **kw):
    pass

def main(args, **kw):
    player = kw["player"] if "player" in kw else None
    otherplayer = None

    # @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_tourney.lbl#L2
    def joust():
        if player.playerid == otherplayerid:
            ttyio.echo("You cannot joust against yourself! Big mistake!")
            loss = bbsengine.diceroll(player.land//2)
            player.land -= loss
            ttyio.echo("You lost %s." % (bbsengine.pluralize(loss, "acre", "acres")))
            return True

        lib.setarea(args, player, "joust")

        ttyio.echo("joust.100: otherplayer=%r" % (otherplayer), level="debug")

        if player.horses == 0:
            ttyio.echo("You do not have a :horse: horse for your noble to use!")
            return True

        if player.serfs < 900:
            ttyio.echo("Not enough serfs attend. The joust is cancelled.")
            return True

        if otherplayer is None or otherplayer.nobles < 2:
            ttyio.echo("Your opponent does not have enough nobles.")
            return True

        ttyio.echo("{f6:2}Your Noble mounts his mighty steed and aims his lance... ", end="")
        # @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/plus_emp6_tourney.lbl#L12
        if player.nobles > otherplayer.nobles*2:
            # player.joustwin = True # nj=1
            player.nobles += 1
            otherplayer.nobles -= 1
            ttyio.echo("Your noble's lance knocks their opponent to the ground. They get up and swear loyalty to you!")
            # if nj=1 then tt$="{gray1}"+d2$+"{lt. blue}"+na$+"{white} wins joust - {lt. blue}"+en$+"{white} is shamed."
            lib.newsentry(args, player, "{lightblue}%s{white} wins joust - {lightblue}%s{white} is shamed" % (player.name, otherplayer.name))
            return True

        lost = []
        gained = []
        x = bbsengine.diceroll(10)
        ttyio.echo("x=%r" % (x), level="debug")
        if x == 1:
            player.land += 100
            gained.append("100 acres")
        elif x == 2:
            player.land -= 100
            if player.land < 1:
                lost.append("last acre")
            else:
                lost.append("100 acres")
        elif x == 3:
            player.coins += 1000
            gained.append(bbsengine.pluralize(1000, "coin", "coins"))
        elif x == 4:
            if player.coins >= 1000:
                player.coins -= 1000
                lost.append(bbsengine.pluralize(1000, "coin", "coins"))
        elif x == 5:
            player.nobles += 1
            gained.append("1 noble")
        elif x == 6:
            if player.nobles > 0:
                player.nobles -= 1
                if player.nobles < 1:
                    lost.append("your last noble")
                    player.nobles = 0
                else:
                    lost.append("1 noble")
        elif x == 7:
            player.grain += 7000
            gained.append(bbsengine.pluralize(7000, "bushel", "bushels"))
        elif x == 8:
            if player.grain >= 7000:
                player.grain -= 7000
                lost.append(bbsengine.pluralize(7000, "bushel", "bushels"))
        elif x == 9:
            player.shipyards += 1
            gained.append("1 shipyard")
            player.land += 100
            gained.append("100 acres")
        elif x == 10:
            if player.shipyards > 0:
                player.shipyards -= 1
                lost.append("1 shipyard")
            if player.land >= 100:
                player.land -= 100
                lost.append("100 acres")
        
        res = []
        if len(lost) > 0:
            res.append("lost " + bbsengine.oxfordcomma(lost))
        if len(gained) > 0:
            res.append("gained " + bbsengine.oxfordcomma(gained))
        
        if len(res) > 0:
            ttyio.echo("You have %s" % (bbsengine.oxfordcomma(res)))

        player.save()

        otherplayer.save()
        
        return True

    def dragon():
        if player.dragons < 0:
            player.dragons = 0
            return True
        ttyio.echo("You have %s" % (bbsengine.pluralize(player.dragons, "dragon", "dragons")))
        if player.dragons > 0:
            if ttyio.inputboolean("Unleash a dragon? [yN]: ", "N") is False:
                return True

        foo = []
        n = otherplayer.grain//10
        x = bbsengine.diceroll(n)
        if x > 0:
            otherplayer.grain -= x
            foo.append(":crop: %s of grain baked" % (bbsengine.pluralize(x, "bushel", "bushels")))
        n = otherplayer.serfs//10
        x = bbsengine.diceroll(n)
        if x > 0:
            otherplayer.serfs -= x
            foo.append("%s BBQ'd" % (bbsengine.pluralize(x, "serf", "serfs")))
        n = otherplayer.horses//10
        x = bbsengine.diceroll(n)
        if x > 0:
            otherplayer.horses -= x
            foo.append(":horse: %s roasted" % (bbsengine.pluralize(x, "horse", "horses")))
        n = otherplayer.acres//10
        x = bbsengine.diceroll(n)
        if x > 0:
            otherplayer.acres -= x
            foo.append("%s incinerated" % (bbsengine.pluralize(x, "acre", "acres")))
        if bbsengine.diceroll(40) < 21 and player.dragons > 0:
            player.dragons -= 1
            if player.dragons == 0:
                foo.append("your last dragon was killed!")
            else:
                foo.append("a dragon was killed!")
        ttyio.echo(bbsengine.oxfordcomma(foo))

    def sneakattack():
        pass

    def menu():
        bbsengine.title("Combat Menu")
        buf = """
{bggray}{white}[1]{/bgcolor} {green}Attack Army{f6}
{bggray}{white}[2]{/bgcolor} {green}Attack Palace{f6}
{bggray}{white}[3]{/bgcolor} {green}Attack Nobles{f6}
{bggray}{white}[4]{/bgcolor} {green}Cease Fighting{f6}
{bggray}{white}[5]{/bgcolor} {green}Send Diplomat{f6}
{bggray}{white}[6]{/bgcolor} {green}Joust{f6}
{f6}{bggray}{white}[Q]{/bgcolor} {green}Quit{/all}
"""
        ttyio.echo(buf)
        return

    # @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/plus_emp6_combat.lbl#L53
    def senddiplomat():
        if player.diplomats < 1:
            ttyio.echo("{F6:2}{yellow}You have no diplomats!{F6:2}{/all}")
            return
        ttyio.echo("{F6}{purple}Your diplomat rides to the enemy camp...")
        if otherplayer.soldiers < player.soldiers*2:
            land = otherplayer.land // 15
            otherplayer.land -= land
            player.land += land
            ttyio.echo("{F6}{green}Your noble returns with good news! To avoid attack, you have been given %s of land!" % (bbsengine.pluralize(land, "acre", "acres")))
        else:
            player.nobles -= 1
            ttyio.echo("{orange}%s {red}BEHEADS{orange} your noble and tosses their corpse into the moat!" % (otherplayer.name))
        player.save()
        otherplayer.save()

    # @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/plus_emp6_combat.lbl#L74
    def attackarmy():
        def update():
            ttyio.echo("%s: %s %s: %s" % (player.name, bbsengine.pluralize(player.soldiers, "soldier", "soldiers"), otherplayer.name, bbsengine.pluralize(otherplayer.soldiers, "soldier", "soldiers")))
            return

        if player.soldiers < 1:
            player.soldiers = 0
            ttyio.echo("You have no soldiers!")
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

        while not done:
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

    # @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/plus_emp6_combat.lbl#L105
    def attackpalace():
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

    # @todo: len(otherplayers) > 0: roll 1d<len+1>; generate NPC if x = len+1
    #otherplayerrank = random.randint(0, min(3, player.rank + 1))
    #otherplayer = Player(args, npc=True)
    #otherplayer.generate(otherplayerrank)
    #otherplayer.playerid = otherplayer.insert()
    #otherplayer.status()
    #otherplayer.dbh.commit()

    lib.setarea(args, player, "combat - attack whom?")

    otherplayername = lib.inputplayername("Attack Whom? >> ", multiple=False, noneok=True, args=args) # , verify=verifyOpponent)
    if otherplayername is None:
        ttyio.echo("no attack. aborted.", level="error")
        return

    otherplayerid = lib.getplayerid(args, otherplayername)

    otherplayer = lib.Player(args)
    otherplayer.load(otherplayerid)
    if otherplayer is None:
        ttyio.echo("invalid player id. aborted.", level="error")
        return

    menu()

    done = False
    while not done:
        player.save()
        lib.setarea(args, player, "combat")

        # @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/mdl.emp.delx3.txt#L91
        ch = ttyio.inputchar("Battle Command [1-6,?,Q]: ", "123456Q?", "Q")
        if ch == "1":
            ttyio.echo("{lightgreen}Attack Army")
            attackarmy()
        elif ch == "2":
            ttyio.echo("{lightgreen}Attack Palace")
            attackpalace()
        elif ch == "Q" or ch == "4":
            ttyio.echo("{lightgreen}Cease Fighting")
            done = True
        elif ch == "5":
            ttyio.echo("{lightgreen}Send Diplomat")
            senddiplomat()
        elif ch == "6":
            ttyio.echo("{lightgreen}Joust")
            joust()
        elif ch == "?":
            ttyio.echo("{lightgreen}Help")
            menu()
        else:
            ttyio.echo("{lightgreen}%s{cyan} -- Not Yet Implemented" % (ch))
        ttyio.echo("{/all}")
        otherplayer.save()
        player.save()
    return
