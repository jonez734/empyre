# barbarians are buying
# @since 20201207
# @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/plus_emp6_combat.lbl#L178

import random

import ttyio6 as ttyio
import bbsengine6 as bbsengine

from .. import lib

def init(args, **kw):
    return True

def main(args, **kw):
    menu = (
        {"hotkey": "1", "label": "Attack Army",   "callback": "combat.attackarmy"},
        {"hotkey": "2", "label": "Attack Palace", "callback": "combat.attackpalace"},
        {"hotkey": "3", "label": "Attack Nobles", "callback": "combat.attacknobles"},
        {"hotkey": "4", "label": "Send Diplomat", "callback": "combat.senddiplomat"},
        {"hotkey": "5", "label": "Joust",         "callback": "combat.joust"}
    )
    player = kw["player"] if "player" in kw else None
    otherplayer = None

    def sneakattack():
        pass

    def help():
        bbsengine.util.heading("Combat Menu")
        for m in menu:
            ttyio.echo(f"{{var:optioncolor}}[{m['hotkey']}]{{var:labelcolor}} {m['label']}")
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
        ttyio.echo("no attack.", level="info")
        return

    otherplayerid = lib.getplayerid(args, otherplayername)

    otherplayer = lib.Player(args)
    otherplayer.load(otherplayerid)
    if otherplayer is None:
        ttyio.echo("invalid player id. aborted.", level="error")
        return

    help()

    done = False
    while not done:
        player.adjust()
        player.save()
        otherplayer.adjust()
        otherplayer.save()

        lib.setarea(args, player, "combat", help=True)

        # @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/mdl.emp.delx3.txt#L91
        ch = ttyio.inputchar("{var:promptcolor}Battle Command {var:optioncolor}[1-6,?,Q]{var:promptcolor}: {var:inputcolor}", "123456Q?", "Q", help=help)
        i = ord(ch)-ord("1")
        if ch in ("1", "2", "3", "4", "5"):
            ttyio.echo(f"{{var:inputcolor}}{menu[i]['label']}")
            if lib.runsubmodule(args, player, menu[i]["callback"], otherplayer=otherplayer) is False:
                ttyio.echo("attack failed (module error)", level="error")
                continue
        elif ch == "?" or ch == "KEY_HELP":
            ttyio.echo("{lightgreen}Help")
            help()
        elif ch == "Q" or ch == "6":
            ttyio.echo("{lightgreen}Cease Fighting")
            done = True
        else:
            ttyio.echo("{lightgreen}%s{cyan} -- Not Yet Implemented" % (ch))
        ttyio.echo("{/all}")
        otherplayer.save()
        player.save()
    return
