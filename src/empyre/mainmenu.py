import ttyio6 as ttyio
import bbsengine6 as bbsengine

from . import lib
from . import _version

# @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_startturn.lbl#L6
# @since 20200913
# @since 20220729 - submodule

def init(args, **kw):
    # ttyio.echo("empyre.mainmenu.init.100: args=%r" % (args), level="debug")
    ttyio.setvariable("empyre.highlightcolor", "{bggray}{white}")

    return True

def main(args, **kw):
    player = kw["player"] if "player" in kw else None
    if args.debug is True:
        ttyio.echo("empyre.mainmenu.main.100: player=%r" % (player), level="debug")

    options = (
        ("I", "Instructions",    "instructions"),
        ("M", "Maintenance",     "maint"),
        ("N", "News",            "shownews", ":newspaper:"),
        ("L", "List Players",    "maint.listplayers"),
        ("P", "Play Empyre",     "play"),
        ("T", "Town Activities", "town"), #, ":building:"),
        ("Y", "Your Status",     "playerstatus"),
        ("G", "Generate NPC",    "generatenpc"),
    )

    def help(**kw):
        ttyio.echo(f"empyre.mainmenu.help.100: kw={kw!r}",level="debug")
        for o in options: #opt, t, callback, emoji in options:
            opt = o[0]
            t = o[1]
            callback = o[2]
            if len(o) == 3:
                emoji = "  "
            elif len(o) == 4:
                emoji = o[3]
            ttyio.echo(f"{{/all}}{emoji} {{var:optioncolor}}[{opt}]{{/all}}{{var:valuecolor}} {t}")
#            choices += opt
        ttyio.echo("{F6}:door: {var:optioncolor}[Q]{/all}{var:valuecolor} Quit{/all}")

    init(args)
    done = False
    while not done:
        player.save()
        terminalwidth = ttyio.getterminalwidth()
        lib.setarea(args, player, "main menu %s rev %s" % (_version.__datestamp__, _version.__version__))
        bbsengine.util.heading("main menu")
        ttyio.echo()
        choices = "Q"
        for o in options:
            choices += o[0]
        help()
        if args.debug is True:
            ttyio.echo("mainmenu.100: player.name=%r" % (player.name), level="debug")
        try:
            ch = ttyio.inputchar("{var:promptcolor}Your command, %s %s? {var:inputcolor}" % (lib.getranktitle(args, player.rank).title(), player.name.title()), choices, "", help=help)

            if ch == "Q":
                ttyio.echo(":door: {var:optioncolor}Q{cyan} -- quit game{/all}")
                loop = False
                break
            else:
                for o in options:# opt, t, callback in options:
                    if o[0] != ch:
                        continue
                    option = o[0]
                    title = o[1]
                    submodule = o[2]
                    if len(o) == 4:
                        emoji = o[3]
                    else:
                        emoji = ""
                    ttyio.echo(f"{emoji}{{var:optioncolor}}{option}{{var:normalcolor}} -- {title}{{/all}}") #  % (emoji, option, title))
                    res = lib.runsubmodule(args, player, submodule)
                    if res is not True:
                        ttyio.echo(f"error running submodule {submodule}, returned {res!r}", level="error")
                    ttyio.echo()
                    break
        except EOFError:
            ttyio.echo("{lightgreen}EOF{/all}")
            return True
        except KeyboardInterrupt:
            ttyio.echo("{lightgreen}INTR{/all}")
            return True

    player.save()
    return True
