import ttyio5 as ttyio
import bbsengine5 as bbsengine

from .. import lib

def init(args, **kw):
    pass

def access(args, op, **kw):
    return True

def main(args, **kwargs):
    player = kwargs["player"] if "player" in kwargs else None

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

    # @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_town.lbl#L130
    # @since 20200830
    def menu():
        bbsengine.title("town menu")

        for hotkey, description, func in optiontable:
            if callable(func) or lib.checkmodule(args, player, func):
                ttyio.echo("{var:empyre.highlightcolor}[%s]{/all} {green}%s" % (hotkey, description))
                
        ttyio.echo("{/all}")
        ttyio.echo("{var:empyre.highlightcolor}[Q]{/all} :door: {green}Return to the Empyre{/all}{f6}")
    
    terminalwidth = bbsengine.getterminalwidth()

    hotkeys = "Q"
    for hotkey, desc, func in optiontable:
        if callable(func) or lib.checkmodule(args, player, func):
            # ttyio.echo("empyre.town.menu.100: adding hotkey %r" % (hotkey), level="debug")
            hotkeys += hotkey

    loop = True
    while loop:
        lib.setarea(args, player, "town menu")
        player.adjust()
#        player.save()
        menu()
        ch = ttyio.inputchar(f"town [{hotkeys}]: ", hotkeys, "Q")
        if ch == "Q":
            ttyio.echo(":door: {green}Return to the Empyre{/all}")
            loop = False
            continue
        else:
            for key, desc, func in optiontable:
                if ch == key:
                    ttyio.echo(desc)
                    if callable(func):
                        func(args, player)
                    elif lib.checkmodule(args, player, func):
                        lib.runsubmodule(args, player, func)
                    else:
                        ttyio.echo("this option is not operable", level="error")
                    break
    return True
