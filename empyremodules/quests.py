import ttyio5 as ttyio
import bbsengine5 as bbsengine

from . import lib

QUESTDIR = "~jam/projects/empyre/data/quests/"

# @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/mdl.emp.delx3.txt#L337
def main(args, **kwargs):
    player = kwargs["player"] if "player" in kwargs else None

    # @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/emp.menu5.txt
    quests = (
        {
            "name": "raidpiratecamp", 
            "title": "Raid the Pirate's Camp",
            "intro": "raidpiratecamp-intro.txt",
            "win": "raidpiratecamp-win.txt",
            "fail": "raidpiratecamp-fail.txt",
            "callback": "quests.raidpiratecamp"
        },
        {
            "name": "hauntedcave", 
            "title":"Mystery of the Haunted Cave", 
            "intro": "hauntedcave-intro.txt",
            "callback": "quests.hauntedcave"
        },
        {
            "name": "rescuemaidenssister", 
            "title": "Rescue the Maiden's Sister", 
            "callback": None
        },
        {"name": "questofgods", "title": "The Quest of the Gods", "callback": None},
        {"name": "evilcult", "title": "Eradicate the Evil Cult", "callback": None},
        {"name": "islandofspice", "title": "Search for the Island of Spice", "callback": None},
        {"name": "birdcity", "title": "Quest for the Legendary Bird City", "callback": None},
        {
            "name": "mountainsideship",
            "title": "Look for the Mountain-Side Ship",
            "callback": None,
            "win": "mountainsideship-win.txt",
        },
        {
            "name": "zircon",
            "title": "Seek Arch-Mage Zircon's Help {yellow}{f6}    Warning: Zircon's help is a gamble!{/all}",
            "callback": "quests.zircon",
            "intro": "zircon-intro.txt",
            "win": "zircon-win.txt",
            "fail":"zircon-fail.txt",
        },
    )

    def isquestcompleted():
        return ttyio.inputboolean("quest completed? [Yn]: ", "Y")

        if bbsengine.diceroll(20) > 7:
#            ttyio.echo("You failed to complete the quest.")
            return False
        return True

    def menu():
        bbsengine.title("quests")

#        ttyio.echo("Quests are currently disabled pending repairs.")
#        return

        index = 0
        for q in quests:
            ch = chr(ord("1")+index)
            t = q["title"]
            callback = q["callback"] if "callback" in q else None
            if callable(callback) is True:
                ttyio.echo("{bggray}{white}[%s]{green} %s" % (ch, t))
                index += 1
        ttyio.echo("{/all}")
        return


    runnablequests = []
    options = ""
    index = 0
    for q in quests:
        callback = q["callback"] if "callback" in q else None
        if callback is not None and callable(callback):
            runnablequests.append(q)
            options += chr(ord("1")+index)
            index += 1

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

        qindex = ord(ch)-ord("1")
        quest = runnablequests[qindex]
        ttyio.echo("%s -- %s" % (ch, quest["title"]))
        if "intro" in quest:
            bbsengine.filedisplay(args, bbsengine.buildfilepath(QUESTDIR, quest["intro"]))

        if quest["callback"]() is True:
            if "win" in quest:
                bbsengine.filedisplay(args, bbsengine.buildfilepath(QUESTDIR, quest["win"]))
            
            ttyio.echo("Quest Completed.")
    
        else:
            if "fail" in quest:
                bbsengine.filedisplay(args, bbsengine.buildfilepath(QUESTDIR, quest["fail"]))
            
            ttyio.echo("Quest Incomplete.")

        player.save()
    
    return
