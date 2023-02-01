import ttyio5 as ttyio
import bbsengine5 as bbsengine

from .. import lib

# @since 20230106 moved from town.py
# @since 20200816

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

# @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_town.lbl#L293
def main(args, player, **kwargs):
    bbsengine.title("natural disaster bank") # , titlecolor="{bggray}{white}", hrcolor="{darkgreen}")
    lib.setarea(args, player, "natural disaster bank") # "{bggray}{white}%s{/all}" % ("bank".ljust(terminalwidth)))
    ttyio.echo()
    exchangerate = 3 #:1 -- 3 coins per credit
    credits = bbsengine.getmembercredits(args)
    buf = "You have :moneybag: {var:empyre.highlightcolor}%s{/all} and {var:empyre.highlightcolor}%s{/all}" % (bbsengine.pluralize(player.coins, "coin", "coins"), bbsengine.pluralize(credits, "credit", "credits"))
    ttyio.echo(buf)
    if credits is not None and credits > 0:
        ttyio.echo("The exchange rate is {var:empyre.highlightcolor}%s per credit{/all}.{F6}"  % (bbsengine.pluralize(exchangerate, "coin", "coins")))
        amount = ttyio.inputinteger("{cyan}Exchange how many credits?: {lightgreen}")
        ttyio.echo("{/all}")
    else:
        ttyio.echo("You have no credits")
        return
    if amount is None or amount < 1:
        return

    credits = bbsengine.getmembercredits(args, player.memberid)

    if amount > credits:
        ttyio.echo("Get REAL! You only have {var:empyre.highlightcolor} %s {/all}!" % (bbsengine.pluralize(amount, "credit", "credits")))
        return

    credits -= amount
    player.coins += amount*exchangerate

    bbsengine.setmembercredits(args, player.memberid, credits)

    ttyio.echo("You now have {var:empyre.highlightcolor}%s{/all} and {var:empyre.highlightcolor}%s{/all}" % (bbsengine.pluralize(player.coins, "coin", "coins"), bbsengine.pluralize(credits, "credit", "credits")))