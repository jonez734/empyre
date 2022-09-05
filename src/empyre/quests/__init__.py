import ttyio5 as ttyio
import bbsengine5 as bbsengine

from .. import lib

def init(args, **kw):
    pass

# @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/mdl.emp.delx3.txt#L337
def main(args, **kwargs):
    player = kwargs["player"] if "player" in kwargs else None

    # @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/emp.menu5.txt
    quests = {
        "raidpiratecamp":
        {
            "title": "Raid the Pirate's Camp",
            "intro": "raidpiratecamp-intro.txt",
            "win": "raidpiratecamp-win.txt",
            "fail": "raidpiratecamp-fail.txt",
            "callback": "quests.raidpiratecamp"
        },
        "hauntedcave":
        {
            "title":"Mystery of the Haunted Cave", 
            "intro": "hauntedcave-intro.txt",
            "callback": "empyre.quests.hauntedcave"
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
            "intro": "zircon-intro.txt",
#            "win": "zircon-win.txt",
            "fail":"zircon-fail.txt",
        },
    }

    def isquestcompleted():
        return ttyio.inputboolean("{var:promptcolor}quest completed? {var:optioncolor}[Yn]{var:promptcolor}: {var:inputcolor}", "Y")

        if bbsengine.diceroll(20) > 7:
#            ttyio.echo("You failed to complete the quest.")
            return False
        return True

    def menu():
        bbsengine.title("quests")

#        ttyio.echo("Quests are currently disabled pending repairs.")
#        return

        ttyio.echo("runnablequests=%r" % (runnablequests), level="debug")
        index = 0
        for q in runnablequests:
            ch = chr(ord("1")+index)
            t = q["title"]
            callback = q["callback"] if "callback" in q else None
            ttyio.echo("{bggray}{white}[%s]{green} %s" % (ch, t))
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
        if (callback is not None and lib.checkmodule(args, player, callback, buildargs=False) is True) is True:
            ttyio.echo("true")
            runnablequests.append(q)
            options += chr(ord("1")+index)
            index += 1
            ttyio.echo("empyre.quests.100: added quest to list")

    ttyio.echo("runnablequests=%r" % (runnablequests), level="debug")
    options += "?Q"

    done = False
    while not done:
        lib.setarea(args, player, "quests")

        menu()

        ch = ttyio.inputchar("quest [%s]: " % (options), options, "Q")
        if ch == "Q":
            ttyio.echo("Q -- quit")
            done = True
            break
        elif ch == "?":
            menu()
            continue

        quest = runnablequests[ord(ch)-ord("1")]
        ttyio.echo("%s -- %s" % (ch, quest["title"]))
        if "intro" in quest:
            bbsengine.filedisplay(args, bbsengine.buildfilepath(lib.QUESTDIR, quest["intro"]))

        if lib.runsubmodule(args, player, quest["callback"]) is True:
            if "win" in quest:
                bbsengine.filedisplay(args, bbsengine.buildfilepath(lib.QUESTDIR, quest["win"]))
            else:
                ttyio.echo("Quest Completed.")
    
        else:
            if "fail" in quest:
                bbsengine.filedisplay(args, bbsengine.buildfilepath(lib.QUESTDIR, quest["fail"]))
            else:
                ttyio.echo("Quest Incomplete.")

        player.save()
    
    return
