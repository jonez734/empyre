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
    lib.setarea(args, "natural disaster bank", player=player) # "{bggray}{white}%s{/all}" % ("bank".ljust(terminalwidth)))
    coinres = player.getresource("coins")
    io.echo()
    exchangerate = 3 #:1 -- 3 coins per credit
    cr = member.getcredits(args, **kwargs)
    io.echo(f"{{var:labelcolor}}You have {{var:valuecolor}}{util.pluralize(player.coins, **coinres)}{{var:labelcolor}} and {{var:valuecolor}}{util.pluralize(cr, 'credit', 'credits', emoji=':moneybag:')}{{/all}}")
    if cr is not None and cr > 0:
        io.echo(f"{{var:labelcolor}}The exchange rate is {{var:valuecolor}}{util.pluralize(exchangerate, **coinres)} per credit{{/all}}.{{F6}}")
        amount = io.inputinteger(f"{{var:promptcolor}}Exchange how many credits?: {{var:inputcolor}}")
        io.echo("{/all}")
    else:
        io.echo("You have no credits")
        return

    if amount is None or amount < 1:
        return

    if args.debug is True:
        io.echo(f"empyre.town.bank.100: {credits=}", level="debug")

    if amount > cr:
        io.echo(f"{{var:labelcolor}}Get REAL! You only have {{var:valuecolor}}{util.pluralize(cr, **coinres)}{{var:labelcolor}}!")
        return

    player.coins += amount*exchangerate
    cr -= amount
    member.setcredits(args, player.moniker, cr, **kwargs)

    player.save()

    io.echo(f"{{var:normalcolor}}You now have {{var:valuecolor}}{util.pluralize(player.coins, **coinres)}{{var:normalcolor}} and {{var:valuecolor}}{util.pluralize(cr, 'credit', 'credits', emoji=':moneybag:')}{{var:normalcolor}}")
    lib.setarea(args, "natural disaster bank", player=player)
    return True
