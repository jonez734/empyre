from bbsengine6 import io, util
from .. import lib as libempyre
from . import lib

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

def main(args, **kw):
    player = kw["player"] if "player" in kw else None
    if player is None:
        io.echo("You do not exist! Go Away!", level="error")
        return False

    optiontable = (
        ("C", "Cyclone's Natural Disaster Bank :bank:", "naturaldisasterbank"),
        ("L", "Lucifer's Den :fire:", "lucifersden"), # lucifersden),
        ("P", "Soldier Promotion to Noble :prince:", "soldierpromotion"),
        ("R", "Realtor's Advice :house:", "realtorsadvice"),
        ("J", "Juicebar", "juicebar"),
#        ("S", "   Slave Market", None),
        ("T", "Change Tax Rate :receipt:", "changetaxrate"),
#        ("U", "   Utopia's Auction", None),
#        ("W", "   Buy Soldiers", None),
        ("X", "Train Serfs to Soldiers :military-helmet:", "trainsoldiers"),
        ("Y", "Your Status", libempyre.playerstatus)
    )

    def help(**kw):
        for hotkey, description, func in optiontable:
            if callable(func) is True or lib.checkmodule(args, func) is True:
                io.echo(f"{{optioncolor}}[{hotkey}]{{labelcolor}} {description}")
    
    # @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_town.lbl#L130
    # @since 20200830
    def menu():
        util.heading("town menu")

        help()
        
        io.echo("{/all}{optioncolor}[Q]{/all} {labelcolor}Return to the Empyre :door:{/all}{f6}")
    
    terminalwidth = io.getterminalwidth()

    hotkeys = "QX"
    for hotkey, desc, func in optiontable:
        if callable(func) or lib.checkmodule(args, func, **kw):
            # ttyio.echo("empyre.town.menu.100: adding hotkey %r" % (hotkey), level="debug")
            hotkeys += hotkey

    done = False
    while not done:
        libempyre.setarea(args, "town menu", player=player)
        player.adjust()
        player.save()
        menu()
        ch = io.inputchar(f"{{promptcolor}}town {{optioncolor}}[{hotkeys}]{{promptcolor}}: {{inputcolor}}", hotkeys, "Q", help=help)
        if ch == "Q" or ch == "X":
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
                        func(args, **kw)
                    else:
                        lib.runmodule(args, func, **kw)
                    break
    return True
