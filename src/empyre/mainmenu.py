import ttyio5 as ttyio
import bbsengine5 as bbsengine

from . import lib
from . import _version

# @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_startturn.lbl#L6
# @since 20200913
# @since 20220729 - submodule

def init(args, **kw):
    ttyio.echo("empyre.mainmenu.init.100: args=%r" % (args))
    return True

def main(args, **kw):
    player = kw["player"] if "player" in kw else None
    ttyio.echo("empyre.mainmenu.main.100: player=%r" % (player), level="debug")

    options = (
        ("I", "Instructions",    "instructions"),
        ("M", "Maintenance",     "maint"),
        ("N", "News",            "shownews", ":newspaper:"),
        ("L", "List Players",    "listplayers"),
        ("P", "Play Empyre",     "play"),
        ("T", "Town Activities", "town"), #, ":building:"),
        ("Y", "Your Status",     "playerstatus"),
        ("G", "Generate NPC",    "generatenpc"),
    )

    ttyio.echo("empyre.mainmenu.main.100: trace")
#    ttyio.echo("title=%r" % (title))
    done = False
    while not done:
        player.save()
        terminalwidth = bbsengine.getterminalwidth()
        lib.setarea(args, player, "main menu %s rev %s" % (_version.__datestamp__, _version.__version__))
        bbsengine.title("main menu")
        ttyio.echo()
        choices = "Q"
        for o in options: #opt, t, callback, emoji in options:
            opt = o[0]
            t = o[1]
            callback = o[2]
            if len(o) == 3:
                emoji = "  "
            elif len(o) == 4:
                emoji = o[3]
            ttyio.echo("{/all}%s {var:empyre.highlightcolor}[%s]{/all}{green} %s" % (emoji, opt, t))
            choices += opt
        ttyio.echo("{F6}:door: {var:empyre.highlightcolor}[Q]{/bgcolor}{green} Quit{/all}")

        if args.debug is True:
            ttyio.echo("mainmenu.100: player.name=%r" % (player.name), level="debug")
        try:
            ch = ttyio.inputchar("{green}Your command, %s %s? {lightgreen}" % (lib.getranktitle(args, player.rank).title(), player.name.title()), choices, "")

            if ch == "Q":
                ttyio.echo(":door: {lightgreen}Q{cyan} -- quit game{/all}")
                return True
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
                    ttyio.echo("%s{lightgreen}%s{cyan} -- %s{/all}" % (emoji, option, title))
                    if lib.runsubmodule(args, player, submodule) is not True:
                        ttyio.echo("error running submodule %r" % (submodule), level="error")
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
