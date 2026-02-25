from bbsengine6 import io, util, member, database, session
from argparse import Namespace

from . import lib
from . import _version
from . import player as libplayer

# @see plus_emp6_startturn.lbl
# @since 20200913
# @since 20220729 - submodule

def init(args, **kwargs):
    # ttyio.echo("empyre.mainmenu.init.100: args=%r" % (args), level="debug")
#    io.setvariable("empyre.highlightcolor", "{bggray}{white}")
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args, **kwargs):
    return None

def main(args, **kwargs):
    if args.debug is True:
        io.echo(f"empyre.main.100: {args=}", level="debug")

    options = (
        ("I", "Instructions",     "instructions"),
        ("M", "Maintenance",      "maint", ":maint:"),
        ("N", "News",             "shownews", ":newspaper:"),
        ("L", "List Players",     "maint.listplayers"),
        ("P", "Play Empyre",      "play"),
        ("T", "Town Activities",  "town", ":building:"),
        ("Y", "Your Status",      "playerstatus"),
#        ("G", "Generate NPC",     "generatenpc"),
    )

    def mainmenuhelp(**kwargs):
###        io.echo(f"empyre.mainmenu.help.100: {kwargs=}",level="debug")
        for o in options: #opt, t, callback, emoji in options:
            opt = o[0]
            t = o[1]
            callback = o[2]
            if len(o) == 3:
                emoji = ""
            elif len(o) == 4:
                emoji = o[3]
            io.echo(f"{{/all}}{{optioncolor}}[{opt}]{{/all}} {{valuecolor}} {t} {emoji}")
#            choices += opt
        io.echo(f"{{F6}}{{optioncolor}}[Q]{{/all}}{{valuecolor}} Quit :door:{{/all}}")

    io.echo(f"empyre.main.400: {args=}")
    util.heading("empyre")

    io.echo(f"database: {args.databasename} host: {args.databasehost}:{args.databaseport}", level="debug")

    if lib.runmodule(args, "startup", **kwargs) is False:
        io.echo(f"empyre failed to start up", level="critical")
        return False

    with database.getpool(args, dbname=args.databasename) as pool:
        if session.start(args, pool=pool) is False:
            io.echo(f"empyre.main.240: session.start() failed", level="error")
            return False

        lib.setarea(args, f"empyre {_version.datestamp} githash {_version.githash}", player=None)

        currentmembermoniker = member.getcurrentmoniker(args, pool=pool)
        io.echo(f"main.300: {currentmembermoniker=}", level="debug")
        if currentmembermoniker is False:
            io.echo("empyre.main.200: you do not exist! go away!", level="error")
            return False

        currentplayer = None

        playercount = libplayer.count(args, currentmembermoniker, pool=pool, **kwargs)
        io.echo(f"empyre.main.100: {playercount=}", level="debug")
        if playercount is None:
            currentplayer = libplayer.create(args, pool=pool)
            if currentplayer is None:
                io.echo("empyre.main.200: unable to create new player!", level="error")
                return False
        elif playercount > 1:
            currentplayer = libplayer.select(args, currentmoniker, pool=pool, **kwargs)
            if currentplayer is None:
                io.echo(f"empyre.main.220: error selecting player", level="error")
                return False
        else:
            io.echo(f"empyre.main.300: calling libplayer.load {currentmembermoniker=}", level="debug")
            currentplayer = libplayer.load(args, currentmembermoniker, pool=pool)

        done = False
        while not done:
            # io.echo(f"empyre.main.320: {currentplayer=}", level="debug")
            if currentplayer is not None:
                currentplayer.adjust()
                currentplayer.save()

            lib.setarea(args, f"{_version.datestamp} git {_version.githash}", player=currentplayer)

            util.heading("main menu")

            io.echo()

            choices = "QX"
            for o in options:
                choices += o[0]
            mainmenuhelp()
#            io.echo(f"mainmenu.100: {currentplayer.moniker=}", level="debug")
            try:
    #            io.echo(f"{player.rank=} {player.moniker=}", level="debug")
                if currentplayer is not None:
                    ranktitle = libplayer.getranktitle(args, currentplayer.rank).title()
                    ch = io.inputchoice(f"{{promptcolor}}Your command, {ranktitle.title()} {currentplayer.moniker}? {{inputcolor}}", choices, "", help=mainmenuhelp)
                else:
                    ch = io.inputchoice(f"{{promptcolor}}Your command? {{inputcolor}}", choices, "", help=mainmenuhelp)

                if ch == "Q" or ch == "X":
                    io.echo(":door: {optioncolor}Q{labelcolor} -- quit game{/all}")
                    done = True
                    break
#                elif ch == "Y":
#                    io.echo("Current Player Status")
#                    currentplayer.status()
#                    continue
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
                        io.echo(f"{emoji}{{optioncolor}}{option}{{normalcolor}} -- {title}{{/all}}") #  % (emoji, option, title))
                        res = lib.runmodule(args, submodule, player=currentplayer, pool=pool, **kwargs)
                        if res is not True:
                            io.echo(f"error running submodule {submodule}, returned {res=}", level="error")
                        io.echo()
                        break
            except EOFError:
                io.echo("{/all}*EOF*")
                return True
            except KeyboardInterrupt:
                io.echo("{/all}*INTR*")
                return True

        currentplayer.save()
    return True
