from bbsengine6 import io, util

from .. import data
from .. import lib as libempyre

def init(args, **kw):
    return True
    
def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

# @see empire6/mdl.emp.delx3.txt#L337
def main(args, **kw):
    player = kw["player"] if "player" in kw else None

    # @see empire6/emp.menu5.txt
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
        return io.inputboolean("{var:promptcolor}quest completed? {var:optioncolor}[Yn]{var:promptcolor}: {var:inputcolor}", "Y")

        if util.diceroll(20) > 7:
#            ttyio.echo("You failed to complete the quest.")
            return False
        return True

    def help(**kw):
        util.heading("quests")

#        ttyio.echo("Quests are currently disabled pending repairs.")
#        return

        if args.debug is True:
            io.echo(f"runnablequests={runnablequests!r}", level="debug")

        index = 0
        for q in runnablequests:
            ch = chr(ord("1")+index)
            t = q["title"]
            callback = q["callback"] if "callback" in q else None
            io.echo(f"{{var:optioncolor}}[{ch}]{{var:valuecolor}} {t}")
            index += 1
        io.echo("{/all}")
        return

    runnablequests = []
    options = ""
    index = 0
    for q in quests.values():
        io.echo("q=%r" % (q), level="debug")
        callback = q["callback"] if "callback" in q else None
        io.echo("empyre.quests.100: callback=%r" % (callback), level="debug")
        if (callback is not None and module.checkmodule(args, callback, buildargs=False, **kw) is True) is True:
            io.echo("true")
            runnablequests.append(q)
            options += chr(ord("1")+index)
            index += 1
            io.echo("empyre.quests.100: added quest to list", level="debug")

    if args.debug is True:
        io.echo(f"{runnablequests=}" % (runnablequests), level="debug")

    options += "?Q"

    done = False
    while not done:
        libempyre.setarea(args, player, "quests")

        help()

        ch = io.inputchar(f"{{var:promptcolor}}quest {{var:optioncolor}}[{options}]{{var:promptcolor}}: {{var:inputcolor}}", options, "Q", help=help)
        if ch == "Q":
            io.echo("Q -- quit")
            done = True
            break

        quest = runnablequests[ord(ch)-ord("1")]
        io.echo("%s -- %s" % (ch, quest["title"]))
#        if "intro" in quest:
#            bbsengine.filedisplay(args, bbsengine.buildfilepath(lib.QUESTDIR, quest["intro"]))
        if "intro" in quest:
            util.filedisplay(args, data.get(quest["intro"])) # bbsengine.buildfilepath(lib.QUESTDIR, quest["intro"]))  # data.get(quest["intro"]))

        if module.runsubmodule(args, quest["callback"], **kw) is True:
            if "win" in quest:
                util.filedisplay(args, util.buildfilepath(libempyre.QUESTDIR, quest["win"]))
            else:
                io.echo("Quest Completed.")
    
        else:
            if "fail" in quest:
                util.filedisplay(args, util.buildfilepath(libempyre.QUESTDIR, quest["fail"]))
            else:
                io.echo("Quest Incomplete.")

        player.save()
    
    return
