#import ttyio6 as ttyio
#import bbsengine6 as bbsengine
from bbsengine6 import io, util, member

from .. import lib as libempyre

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

def help(args=None):
    buf = """{f6}{labelcolor}Maint Options:{/all}{f6}
{optioncolor}[D]{labelcolor} Auto-Reset{f6}
{optioncolor}[X]{labelcolor} bbs credit / empyre coin exchange rate{f6}
{optioncolor}[E]{labelcolor} Edit Player's profile{f6}
{optioncolor}[L]{labelcolor} List Players{f6}
{optioncolor}[R]{labelcolor} Reset Empyre{f6}
{optioncolor}[S]{labelcolor} Scratch News{f6}
{optioncolor}[Y]{labelcolor} Your Stats{f6:2}
{optioncolor}[Q]{labelcolor} Quit{F6}
"""
    io.echo(buf)

def main(args, **kw):
    player = kw["player"] if "player" in kw else None
    sysop = member.checkflag(args, "SYSOP")
    done = False
    while not done:
        util.heading("maint")
        libempyre.setarea(args, "maint", **kw)
        help()
        ch = io.inputchar("{promptcolor}maintenance: {inputcolor}", "XELRSYQ", "", help=help)

        if ch == "Q":
            io.echo("Quit")
            done = True
            continue
        elif ch == "D":
            io.echo("Auto-Reset (not implemented)")
            continue
        elif ch == "E":
            io.echo("Edit Player")
            p = libempyre.selectplayer(args, title="select player to edit", prompt="select player:")
            if p is None:
                continue
#            playername = libempyre.inputplayername("{promptcolor}player name: {inputcolor}", player.moniker, args=args)
#            playerid = libempyre.getplayerid(args, playername)
#            if playerid is None:
#                continue
#            p = libempyre.Player(args)
#            p.load(playerid)
            libempyre.setarea(args, p, f"edit player {player.moniker}")
            p.edit()
            p.adjust()
            p.status()
            if io.inputboolean("{promptcolor}save? {optioncolor}[{currentoptioncolor}Y{optioncolor}n]{promptcolor}: {inputcolor}", "Y") is True:
                p.save()
        elif ch == "L":
            io.echo("List Players")
            libempyre.runmodule(args, "maint.listplayers", **kw)
        elif ch == "P":
            io.echo("Play Empyre")
            if libempyre.runmodule(args, "play", **kw) is not True:
                io.echo("error running 'play' submodule", level="error")
#            play(args, player)
        elif ch == "R":
            io.echo("Reset Empyre")
            libempyre.runmodule(args, "maint.resetempyre", **kw)
        elif ch == "S":
            io.echo("Scratch News")
            libempyre.runmodule(args, "maint.scratchnews", **kw)
        elif ch == "X":
            io.echo("bbs credit -> empyre coin exchange rate, not implemented")
        elif ch == "Y":
            if sysop is True:
                io.echo("Player Stats")
                playername = libempyre.inputplayername("{promptcolor}player: {inputcolor}", player.moniker, verify=libempyre.verifyPlayerNameFound, args=args)
            else:
                io.echo("Your stats")
                playername = player.name
            playerid = libempyre.getplayerid(args, playername)
            if playerid is None:
                io.echo(f"{playername} not found.", level="error")
                continue
            p = libempyre.Player(args)
            p.load(playerid)
            p.status()

    io.echo()
    return True
