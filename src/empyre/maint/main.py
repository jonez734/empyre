#import ttyio6 as ttyio
#import bbsengine6 as bbsengine
from bbsengine6 import io, util, member

from .. import lib as libempyre
from .. import player as libplayer

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args, **kwargs):
    return None

def mainthelp(args=None, **kwargs):
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

def main(args, **kwargs):
    player = kwargs.get("player", None)
    sysop = member.checkflag(args, "SYSOP", **kwargs)
    done = False
    while not done:
        util.heading("maint")
        libempyre.setarea(args, "maint", **kwargs)
        mainthelp()
        ch = io.inputchar("{promptcolor}maintenance: {inputcolor}", "XELRSYQ", "", help=mainthelp)

        if ch == "Q":
            io.echo("Quit")
            done = True
            continue
        elif ch == "D":
            io.echo("Auto-Reset (not implemented)")
            continue
        elif ch == "E":
            io.echo("Edit Player")
            p = libplayer.select(args, title="select player to edit", prompt="select player:", **kwargs)
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
            libempyre.runmodule(args, "maint.listplayers", **kwargs)
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
                playermoniker = libempyre.inputplayername("{promptcolor}player: {inputcolor}", player.moniker, verify=libplayer.verifyPlayerNameFound, args=args, **kwargs)
            else:
                io.echo("Your stats")
                playermoniker = player.moniker
            if playermoniker is None:
                io.echo(f"play{playername} not found.", level="error")
                continue
            p = libplayer.load(args, playermoniker, **kwargs)
            p.status()

    io.echo()
    return True
