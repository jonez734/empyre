#import ttyio6 as ttyio
#import bbsengine6 as bbsengine
from bbsengine6 import io, util

from .. import lib
#from .. import module

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

def main(args, **kw):
    if not "player" in kw:
        io.echo("You do not exist! Go Away!", level="error")
        return False

    player = kw["player"]
    if player is None:
        io.echo("You do not exist! Go Away!", level="error")
        return False

    optiontable = (
        ("C", ":bank: Cyclone's Natural Disaster Bank", "town.naturaldisasterbank"),
        ("L", ":fire: Lucifer's Den", "town.lucifersden"), # lucifersden),
        ("P", ":prince: Soldier Promotion to Noble", "town.soldierpromotion"),
        ("R", ":house: Realtor's Advice", "town.realtorsadvice"),
#        ("S", "   Slave Market", None),
        ("T", ":receipt: Change Tax Rate", "town.changetaxrate"),
#        ("U", "   Utopia's Auction", None),
#        ("W", "   Buy Soldiers", None),
        ("X", ":military-helmet: Train Serfs to Soldiers", "town.trainsoldiers"),
        ("Y", "   Your Status", lib.playerstatus)
    )

    def help():
        for hotkey, description, func in optiontable:
            if callable(func) is True or lib.checkmodule(args, func) is True:
                io.echo(f"{{var:optioncolor}}[{hotkey}]{{var:labelcolor}} {description}")
    
    # @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_town.lbl#L130
    # @since 20200830
    def menu():
        util.heading("town menu")

        help()
        
        io.echo("{/all}{var:empyre.highlightcolor}[Q]{/all} :door: {green}Return to the Empyre{/all}{f6}")
    
    terminalwidth = io.getterminalwidth()

    hotkeys = "Q"
    for hotkey, desc, func in optiontable:
        if callable(func) or lib.checkmodule(args, func, **kw):
            # ttyio.echo("empyre.town.menu.100: adding hotkey %r" % (hotkey), level="debug")
            hotkeys += hotkey

    done = False
    while not done:
        lib.setarea(args, "town menu", player=player)
        player.adjust()
        player.save()
        menu()
        ch = io.inputchar(f"{{var:promptcolor}}town {{var:optioncolor}}[{hotkeys}]{{var:promptcolor}}: {{var:inputcolor}}", hotkeys, "Q")
        if ch == "Q":
            io.echo(":door: {green}Return to the Empyre{/all}")
            done = True
            continue
        else:
            for key, desc, func in optiontable:
                if func is None:
                    continue

                if ch == key:
                    io.echo(desc)
                    if callable(func):
                        func(args, player, **kw)
                        break
                    lib.runmodule(args, func, **kw)
                    break
    return True
