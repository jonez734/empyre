from bbsengine6 import io, database, util
from . import ship as libship

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args, **kwargs):
    return None

def help(**kwargs):
    io.echo(":compass: {optioncolor}[R]{labelcolor}ecruit navigator{normalcolor}") # show how many are needed per ship
    io.echo(":package: {optioncolor}[E]{labelcolor}xports{normalcolor}")
##    io.echo(":anchor: {optioncolor}[S]{labelcolor}hips{normalcolor}")
##    io.echo(" {optioncolor}[T]{labelcolor}rade Shipyards{normalcolor}")
    io.echo("{f6}:door: {optioncolor}[Q]{labelcolor}uit{normalcolor}")
    return True


def main(args, **kwargs):
    currentplayer = kwargs.get("player", None)
    if currentplayer is None:
        io.echo("You do not exist! Go Away!", level="error")
        return False

    if currentplayer.shipyards > 0:
        if io.inputboolean("{promptcolor}visit shipyard?: {inputcolor}") is False:
            io.echo("no shipyard visit")
            return True

    util.heading("shipyard")
    done = False
    while not done:
        help()
        ch = io.inputchar(f"shipyard: {{inputcolor}}", "BQ", "Q")
        if ch == "Q":
            done = True
            break
        elif ch == "B":
            io.echo(f"Build Ship")
            coinres = currentplayer.getresource("coins")

            shipres = currentplayer.getresource("ships")

            if currentplayer.ships+1 > currentplayer.shipyards*libship.SHIPSPERSHIPYARD:
                io.echo(f"you do not have enough shipyard capacity to build another ship")
                break

            io.echo(f"A ship costs {shipres.price} {util.pluralize('coins', **coinres)}. You have {util.pluralize('coin', **coinres)}")
            break
#        elif ch == "T":
#            io.echo("Trade Shipyards")
#            res = player.getresource("shipyards")
#            lib.trade(args, player, **res)
#        elif ch == "S":
#            shipslistbox(args, player)
    return True
