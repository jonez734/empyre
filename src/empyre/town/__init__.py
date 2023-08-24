import ttyio6 as ttyio
import bbsengine6 as bbsengine

from .. import lib
from .. import module

def init(args, **kw):
    pass

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

def main(args, **kwargs):
    if not "player" in kwargs:
        ttyio.echo("You do not exist! Go Away!", level="error")
        return False

    player = kwargs["player"]

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
            if callable(func) is True or module.checkmodule(args, player, func) is True:
                ttyio.echo("{var:empyre.highlightcolor}[%s]{/all} {green}%s" % (hotkey, description))
    
    # @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_town.lbl#L130
    # @since 20200830
    def menu():
        bbsengine.util.heading("town menu")

        help()
        
        ttyio.echo("{/all}{var:empyre.highlightcolor}[Q]{/all} :door: {green}Return to the Empyre{/all}{f6}")
    
    terminalwidth = ttyio.getterminalwidth()

    hotkeys = "Q"
    for hotkey, desc, func in optiontable:
        if callable(func) or module.checkmodule(args, player, func):
            # ttyio.echo("empyre.town.menu.100: adding hotkey %r" % (hotkey), level="debug")
            hotkeys += hotkey

    done = False
    while not done:
        lib.setarea(args, player, "town menu")
        player.adjust()
        player.save()
        menu()
        ch = ttyio.inputchar(f"{{var:promptcolor}}town {{var:optioncolor}}[{hotkeys}]{{var:promptcolor}}: {{var:inputcolor}}", hotkeys, "Q")
        if ch == "Q":
            ttyio.echo(":door: {green}Return to the Empyre{/all}")
            done = True
            continue
        else:
            for key, desc, func in optiontable:
                if ch == key:
                    ttyio.echo(desc)
                    if callable(func):
                        func(args, player)
                    elif module.checkmodule(args, player, func):
                        module.runsubmodule(args, player, func)
                    else:
                        ttyio.echo(f"option {desc!r} is not operable", level="error")
                    break
    return True
