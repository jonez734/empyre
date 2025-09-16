from bbsengine6 import io, util

from . import lib

from .. import lib as libempyre
from .. import player as libplayer

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args, **kwargs):
    return None

MENU = (
    {"hotkey": "1", "label": "Attack Army",   "callback": "attackarmy"},
    {"hotkey": "2", "label": "Attack Palace", "callback": "attackpalace"},
    {"hotkey": "3", "label": "Attack Nobles", "callback": "attacknobles"},
    {"hotkey": "4", "label": "Send Diplomat", "callback": "senddiplomat"},
    {"hotkey": "5", "label": "Joust",         "callback": "joust"}
)

def main(args, **kwargs):
    player = kwargs["player"] if "player" in kwargs else None
    otherplayer = None

    def sneakattack():
        pass

    def combathelp(**kwargs):
        util.heading("Combat Menu")
        for m in MENU:
            io.echo(f"{{var:optioncolor}}[{m['hotkey']}]{{var:labelcolor}} {m['label']}")
        return

    libempyre.setarea(args, "combat: select opponent", player=player)

    otherplayer = libplayer.select(args, title="select opponent", prompt="opponent: ", **kwargs)
    if otherplayer is False:
        io.echo("failed to select opponent", level="error")
        return False
    elif otherplayer is None:
        io.echo("no attack.", level="info")
        return None

    if player.moniker == otherplayer.moniker:
        if io.inputboolean(f"{{var:promptcolor}}it is unwise to attack yourself. are you sure?: {{var:inputcolor}}", "N") is False:
            io.echo("{f6}aborted{f6}")
            return True

    combathelp()

    done = False
    while not done:
        player.adjust()
        player.save()

        otherplayer.adjust()
        otherplayer.save()

        libempyre.setarea(args, "combat", help=True, player=player)

        # @see empire6/mdl.emp.delx3.txt#L91
        ch = io.inputchar("{var:promptcolor}Combat Command {var:optioncolor}[1-6,?,Q]{var:promptcolor}: {var:inputcolor}", "123456Q?", "Q", help=combathelp)
        i = ord(ch)-ord("1")
        if ch in ("1", "2", "3", "4", "5"):
            io.echo(f"{{var:inputcolor}}{MENU[i]['label']}")
            if lib.runmodule(args, MENU[i]["callback"], otherplayer=otherplayer, **kwargs) is False:
                io.echo("attack failed (module error)", level="error")
                continue
        elif ch == "?" or ch == "KEY_HELP":
            io.echo("{var:inputcolor}Help")
            combathelp()
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
