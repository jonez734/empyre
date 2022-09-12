import ttyio5 as ttyio
import bbsengine5 as bbsengine

from . import lib

# @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_maint.lbl#L6
# @since 20200831 written
# @since 20220730 converted to a submodule

def init(args, **kw):
    pass

def access(args, op, **kw):
    ttyio.echo("empyre.maint.access.100: trace")
#    sysop = False
    sysop = bbsengine.checkflag(args, "SYSOP")
    if sysop is True:
        return True
    ttyio.echo("empyre.sysopoptions.access.100: permission denied")
    return False

def main(args, **kw):
    player = kw["player"] if "player" in kw else None
    sysop = bbsengine.checksysop(args)
    done = False
    while not done:
        bbsengine.title("maint")
        lib.setarea(args, player, "maint")
        buf = """{f6}{var:labelcolor}Options:{/all}{f6}
{var:optioncolor}[D]{var:labelcolor}} Auto-Reset{f6}
{var:optioncolor}[X]{var:labelcolor} bbs credit / empyre coin exchange rate{f6}
{var:optioncolor}[E]{var:labelcolor} Edit Player's profile{f6}
{var:optioncolor}[L]{var:labelcolor} List Players{f6}
{var:optioncolor}[R]{var:labelcolor} Reset Empyre{f6}
{var:optioncolor}[S]{var:labelcolor} Scratch News{f6}
{var:optioncolor}[Y]{var:labelcolor} Your Stats{f6:2}
{var:optioncolor}[Q]{var:labelcolor} Quit{F6}
"""
        ttyio.echo(buf)
        ch = ttyio.inputchar("{cyan}maintenance: {lightgreen}", "DXELRSYQ", "")

        if ch == "Q":
            ttyio.echo("Quit")
            done = True
            continue
        elif ch == "D":
            ttyio.echo("Auto-Reset (not implemented)")
            continue
        elif ch == "E":
            ttyio.echo("Edit Player's Profile")
            playername = lib.inputplayername("player name: ", player.name, args=args)
            playerid = lib.getplayerid(args, playername)
            if playerid is None:
                continue
            p = lib.Player(args)
            p.load(playerid)
            lib.setarea(args, p, "edit player %r" % (playername))
            p.edit()
            p.adjust()
            p.status()
            lib.setarea(args, p, "edit player %r" % (playername))
            if ttyio.inputboolean("save? [Yn]: ", "Y") is True:
                p.save()
        elif ch == "L":
            ttyio.echo("List Players")
            lib.runsubmodule(args, player, "listplayers")
        elif ch == "P":
            ttyio.echo("Play Empyre")
            if lib.runsubmodule(args, player, "play") is not True:
                ttyio.echo("error running 'play' submodule", level="error")
#            play(args, player)
        elif ch == "R":
            ttyio.echo("Reset Empyre")
            lib.runsubmodule(args, player, "resetempyre")
        elif ch == "S":
            ttyio.echo("Scratch News")
            lib.runsubmodule(args, player, "scratchnews")
        elif ch == "X":
            ttyio.echo("bbs credit -> empyre coin exchange rate, not implemented")
        elif ch == "Y":
            if sysop is True:
                ttyio.echo("Player Stats")
                playername = lib.inputplayername("player: ", "", verify=lib.verifyPlayerNameFound, args=args)
            else:
                ttyio.echo("Your stats")
                playername = player.name
            playerid = lib.getplayerid(args, playername)
            if playerid is None:
                ttyio.echo("%s not found." % (playername), level="error")
                continue
            p = lib.Player(args)
            p.load(playerid)
            p.status()

    ttyio.echo()
    return True