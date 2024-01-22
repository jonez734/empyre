#import ttyio6 as ttyio
#import bbsengine6 as bbsengine
from bbsengine6 import io, util, member

from .. import lib

# @since 20230106 moved from town.py
# @since 20200816

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args, **kw):
    return None

# @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_town.lbl#L293
def main(args, player, **kwargs):
    util.heading("natural disaster bank") # , titlecolor="{bggray}{white}", hrcolor="{darkgreen}")
    lib.setarea(args, player, "natural disaster bank") # "{bggray}{white}%s{/all}" % ("bank".ljust(terminalwidth)))
    io.echo()
    exchangerate = 3 #:1 -- 3 coins per credit
    credits = member.getcredits(args)
    buf = "You have {var:empyre.highlightcolor}%s{/all} and {var:empyre.highlightcolor}%s{/all}" % (util.pluralize(player.coins, "coin", "coins", emoji=":moneybag:"), util.pluralize(credits, "credit", "credits"))
    io.echo(buf)
    if credits is not None and credits > 0:
        io.echo("The exchange rate is {var:empyre.highlightcolor}%s per credit{/all}.{F6}"  % (util.pluralize(exchangerate, "coin", "coins", emoji=":moneybag:")))
        amount = io.inputinteger("{var:promptcolor}Exchange how many credits?: {var:inputcolor}")
        io.echo("{/all}")
    else:
        io.echo("You have no credits")
        return
    if amount is None or amount < 1:
        return

    if args.debug is True:
        io.echo(f"empyre.town.bank.100: {credits=}", level="debug")

    if amount > credits:
        io.echo("Get REAL! You only have {var:empyre.highlightcolor} %s {/all}!" % (util.pluralize(credits, "credit", "credits")))
        return

    credits -= amount
    player.coins += amount*exchangerate

    member.setcredits(args, player.memberid, credits)

    io.echo("You now have {var:empyre.highlightcolor}%s{/all} and {var:empyre.highlightcolor}%s{/all}" % (util.pluralize(player.coins, "coin", "coins", emoji=":moneybag:"), util.pluralize(credits, "credit", "credits")))
    lib.setarea(args, player, "natural disaster bank")
    return True
