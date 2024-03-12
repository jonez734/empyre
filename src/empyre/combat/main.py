from bbsengine6 import io, util

from . import lib

from .. import lib as libempyre

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

def main(args, **kw):
    menu = (
        {"hotkey": "1", "label": "Attack Army",   "callback": "attackarmy"},
        {"hotkey": "2", "label": "Attack Palace", "callback": "attackpalace"},
        {"hotkey": "3", "label": "Attack Nobles", "callback": "attacknobles"},
        {"hotkey": "4", "label": "Send Diplomat", "callback": "senddiplomat"},
        {"hotkey": "5", "label": "Joust",         "callback": "joust"}
    )
    player = kw["player"] if "player" in kw else None
    otherplayer = None

    def sneakattack():
        pass

    def help():
        util.heading("Combat Menu")
        for m in menu:
            io.echo(f"{{var:optioncolor}}[{m['hotkey']}]{{var:labelcolor}} {m['label']}")
        return

    # @todo: len(otherplayers) > 0: roll 1d<len+1>; generate NPC if x = len+1
    #otherplayerrank = random.randint(0, min(3, player.rank + 1))
    #otherplayer = Player(args, npc=True)
    #otherplayer.generate(otherplayerrank)
    #otherplayer.playerid = otherplayer.insert()
    #otherplayer.status()
    #otherplayer.dbh.commit()

    libempyre.setarea(args, player, "combat: select opponent")

    otherplayer = libempyre.selectplayer(args, title="select opponent", prompt="opponent: ")
    #libempyre.inputplayername("Attack Whom? >> ", multiple=False, noneok=True, args=args) # , verify=verifyOpponent)
    if otherplayer is None:
        io.echo("no attack.", level="info")
        return

#    otherplayerid = libempyre.getplayerid(args, otherplayername)

#    otherplayer = libempyre.Player(args)
#    otherplayer.load(otherplayerid)
#    if otherplayer is None:
#        io.echo("invalid player id. aborted.", level="error")
#        return False

    help()

    done = False
    while not done:
        player.adjust()
        player.save()

        otherplayer.adjust()
        otherplayer.save()

        libempyre.setarea(args, "combat", help=True, player=player)

        # @see empire6/mdl.emp.delx3.txt#L91
        ch = io.inputchar("{var:promptcolor}Combat Command {var:optioncolor}[1-6,?,Q]{var:promptcolor}: {var:inputcolor}", "123456Q?", "Q", help=help)
        i = ord(ch)-ord("1")
        if ch in ("1", "2", "3", "4", "5"):
            io.echo(f"{{var:inputcolor}}{menu[i]['label']}")
            if lib.runmodule(args, menu[i]["callback"], otherplayer=otherplayer, **kw) is False:
                io.echo("attack failed (module error)", level="error")
                continue
        elif ch == "?" or ch == "KEY_HELP":
            io.echo("{var:inputcolor}Help")
            help()
        elif ch == "Q" or ch == "6":
            io.echo("{var:inputcolor}Cease Fighting")
            done = True
        else:
            io.echo(f"{{var:inputcolor}}{ch}{{cyan}} -- Not Yet Implemented")
        io.echo("{/all}")
        otherplayer.adjust()
        otherplayer.save()

        player.adjust()
        player.save()
    return
