import ttyio6 as ttyio
import bbsengine6 as bbsengine

from .. import lib

# @since 20230106 moved from town.py
# @since 20200816

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

# @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_town.lbl#L293
def main(args, player, **kwargs):
    bbsengine.util.heading("natural disaster bank") # , titlecolor="{bggray}{white}", hrcolor="{darkgreen}")
    lib.setarea(args, player, "natural disaster bank") # "{bggray}{white}%s{/all}" % ("bank".ljust(terminalwidth)))
    ttyio.echo()
    exchangerate = 3 #:1 -- 3 coins per credit
    credits = bbsengine.member.getcredits(args)
    buf = "You have {var:empyre.highlightcolor}%s{/all} and {var:empyre.highlightcolor}%s{/all}" % (bbsengine.util.pluralize(player.coins, "coin", "coins", emoji=":moneybag:"), bbsengine.util.pluralize(credits, "credit", "credits"))
    ttyio.echo(buf)
    if credits is not None and credits > 0:
        ttyio.echo("The exchange rate is {var:empyre.highlightcolor}%s per credit{/all}.{F6}"  % (bbsengine.util.pluralize(exchangerate, "coin", "coins")))
        amount = ttyio.inputinteger("{cyan}Exchange how many credits?: {lightgreen}")
        ttyio.echo("{/all}")
    else:
        ttyio.echo("You have no credits")
        return
    if amount is None or amount < 1:
        return

    if args.debug is True:
        ttyio.echo(f"empyre.town.bank.100: {credits=}", level="debug")

    if amount > credits:
        ttyio.echo("Get REAL! You only have {var:empyre.highlightcolor} %s {/all}!" % (bbsengine.util.pluralize(credits, "credit", "credits")))
        return

    credits -= amount
    player.coins += amount*exchangerate

    bbsengine.member.setcredits(args, player.memberid, credits)

    ttyio.echo("You now have {var:empyre.highlightcolor}%s{/all} and {var:empyre.highlightcolor}%s{/all}" % (bbsengine.util.pluralize(player.coins, "coin", "coins", emoji=":moneybag:"), bbsengine.util.pluralize(credits, "credit", "credits")))
