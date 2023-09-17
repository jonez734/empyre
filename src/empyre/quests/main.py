import ttyio6 as ttyio
import bbsengine6 as bbsengine

from .. import data
from .. import lib
from . import module

def init(args, **kw):
    return True
    
def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

# @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/mdl.emp.delx3.txt#L337
def main(args, **kw):
    player = kw["player"] if "player" in kw else None

    # @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/emp.menu5.txt
    quests = {
        "raidpiratecamp":
        {
            "title": "Raid the Pirate's Camp",
            "intro": "raidpiratecamp-intro.txt",
            "win": "raidpiratecamp-win.txt",
            "fail": "raidpiratecamp-fail.txt",
            "callback": "raidpiratecamp"
        },
        "hauntedcave":
        {
            "title":"Mystery of the Haunted Cave",
            "intro": "hauntedcave-intro.txt",
            "callback": "hauntedcave"
        },
        "rescuemaindenssister":
        {
            "title": "Rescue the Maiden's Sister",
            "callback": None
        },
        "questofgods":
        {
            "title": "The Quest of the Gods", 
            "callback": None
        },
        "evilcult":
        {
            "title": "Eradicate the Evil Cult", 
            "callback": None
        },
        "islandofspice":
        {
            "title": "Search for the Island of Spice", 
            "callback": None
        },
        "birdcity":
        {
            "title": "Quest for the Legendary Bird City", 
            "callback": None
        },
        "mountainsideship":
        {
            "title": "Look for the Mountain-Side Ship",
            "callback": None,
            "win": "mountainsideship-win.txt",
        },
        "zircon":
        {
            "title": "Seek Arch-Mage Zircon's Help {yellow}{f6}    Warning: Zircon's help is a gamble!{/all}",
            "callback": "quests.zircon",
            "intro": "quest-zircon-intro.txt",
#            "win": "zircon-win.txt",
            "fail":"zircon-fail.txt",
        },
    }

    def isquestcompleted():
        return ttyio.inputboolean("{var:promptcolor}quest completed? {var:optioncolor}[Yn]{var:promptcolor}: {var:inputcolor}", "Y")

        if bbsengine.util.diceroll(20) > 7:
#            ttyio.echo("You failed to complete the quest.")
            return False
        return True

    def help(**kw):
        bbsengine.util.heading("quests")

#        ttyio.echo("Quests are currently disabled pending repairs.")
#        return

        if args.debug is True:
            ttyio.echo(f"runnablequests={runnablequests!r}", level="debug")

        index = 0
        for q in runnablequests:
            ch = chr(ord("1")+index)
            t = q["title"]
            callback = q["callback"] if "callback" in q else None
            ttyio.echo(f"{{var:optioncolor}}[{ch}]{{var:valuecolor}} {t}")
            index += 1
        ttyio.echo("{/all}")
        return

    runnablequests = []
    options = ""
    index = 0
    for q in quests.values():
        ttyio.echo("q=%r" % (q), level="debug")
        callback = q["callback"] if "callback" in q else None
        ttyio.echo("empyre.quests.100: callback=%r" % (callback), level="debug")
        if (callback is not None and module.checkmodule(args, callback, buildargs=False, **kw) is True) is True:
            ttyio.echo("true")
            runnablequests.append(q)
            options += chr(ord("1")+index)
            index += 1
            ttyio.echo("empyre.quests.100: added quest to list", level="debug")

    if args.debug is True:
        ttyio.echo(f"{runnablequests=}" % (runnablequests), level="debug")

    options += "?Q"

    done = False
    while not done:
        lib.setarea(args, player, "quests")

        help()

        ch = ttyio.inputchar(f"{{var:promptcolor}}quest {{var:optioncolor}}[{options}]{{var:promptcolor}}: {{var:inputcolor}}", options, "Q", help=help)
        if ch == "Q":
            ttyio.echo("Q -- quit")
            done = True
            break

        quest = runnablequests[ord(ch)-ord("1")]
        ttyio.echo("%s -- %s" % (ch, quest["title"]))
#        if "intro" in quest:
#            bbsengine.filedisplay(args, bbsengine.buildfilepath(lib.QUESTDIR, quest["intro"]))
        if "intro" in quest:
            bbsengine.util.filedisplay(args, data.get(quest["intro"])) # bbsengine.buildfilepath(lib.QUESTDIR, quest["intro"]))  # data.get(quest["intro"]))

        if module.runsubmodule(args, quest["callback"], **kw) is True:
            if "win" in quest:
                bbsengine.util.filedisplay(args, bbsengine.util.buildfilepath(lib.QUESTDIR, quest["win"]))
            else:
                ttyio.echo("Quest Completed.")
    
        else:
            if "fail" in quest:
                bbsengine.util.filedisplay(args, bbsengine.buildfilepath(lib.QUESTDIR, quest["fail"]))
            else:
                ttyio.echo("Quest Incomplete.")

        player.save()
    
    return
