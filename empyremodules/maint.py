import ttyio5 as ttyio
import bbsengine5 as bbsengine

from . import lib

# @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_maint.lbl#L6
# @since 20200831 written
# @since 20220730 converted to a submodule

def init(args, **kw):
    pass

def main(args, **kw):
    player = kw["player"] if "player" in kw else None

    done = False
    while not done:
        bbsengine.title("maint")
        lib.setarea(args, player, "maint")
        buf = """{f6}{purple}Options:{/all}{f6}
{yellow}[D]{gray} Auto-Reset{f6}
{yellow}[X]{gray} bbs credit / empyre coin exchange rate{f6}
{yellow}[E]{gray} Edit Player's profile{f6}
{yellow}[L]{gray} List Players{f6}
{yellow}[R]{gray} Reset Empyre{f6}
{yellow}[S]{gray} Scratch News{f6}
{yellow}[Y]{gray} Your Stats{f6:2}
{yellow}[Q]{gray} Quit{F6}
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
            playername = inputplayername("player name: ", player.name, args=args)
            playerid = getplayerid(args, playername)
            if playerid is None:
                continue
            p = lib.Player(args)
            p.load(playerid)
            p.edit()
            if p.isdirty() is True:
                if ttyio.inputboolean("save? [Yn]: ", "Y") is True:
                    p.save()
                    if player.memberid == p.memberid:
                        ttyio.echo("player.memberid is p.memberid")
                        player = p
            else:
                if ttyio.inputboolean("save? [yN]: ", "N") is True:
#                    p.save()
                    if player.memberid == p.memberid:
                        ttyio.echo("player.memberid is p.memberid")
                        player = p
        elif ch == "L":
            ttyio.echo("List Players")
            otherplayers(args, player)
        elif ch == "P":
            ttyio.echo("Play Empyre")
            if lib.runsubmodule(args, player, "play") is not True:
                ttyio.echo("error running 'play' submodule", level="error")
#            play(args, player)
        elif ch == "R":
            ttyio.echo("Reset Empyre")
            resetempire(args, player)
        elif ch == "S":
            ttyio.echo("Scratch News")
            scratchnews(args, player)
        elif ch == "X":
            ttyio.echo("bbs credit -> empyre coin exchange rate, not implemented")
        elif ch == "Y":
            ttyio.echo("Player Stats")
            playername = lib.inputplayername("player: ", "", verify=verifyPlayerNameFound, args=args)
            playerid = lib.getplayerid(args, playername)
            if playerid is None:
                ttyio.echo("%s not found." % (playername), level="error")
                continue
            p = lib.Player(args)
            p.load(playerid)
            p.status()

    ttyio.echo()
    return
