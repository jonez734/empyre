import random

from bbsengine6 import io, util

from . import lib

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args, **kwargs):
    return None

def main(args, **kwargs):
    player = kwargs.get("player", None)
    conn = kwargs.get("conn", None)

    grainres = player.getresource("grain")

    lib.setarea(args, "harvest", **kwargs)
    x = int((player.land*player.weatherconditions+(random.random()*player.serfs)+player.grain*player.weatherconditions)/3)
    x = min(x, player.land+player.serfs*4)
    #if x > (player.land+player.serfs)*4:
    #    x = (player.land+player.serfs)*4
    io.echo(f"{{f6}}{{normalcolor}}This year's harvest is {{valuecolor}}{util.pluralize(x, **grainres)}{{f6}}")

    # https://github.com/Pinacolada64/ImageBBS/blob/cb68d111c2527470218aedb94b93e7f4b432c345/v1.2/web-page/imageprg-chap5.html#L69
    player.grain += x # "pl=1"? <-- has to do with imagebbs input routines accepting upper/lower case vs only upper

    serfsrequire = player.serfs*5+1

    io.echo(f"{{normalcolor}}Your people require {{valuecolor}}{util.pluralize(serfsrequire, **grainres)}{{normalcolor}} of grain this year{{/all}}{{f6}}")
    price = player.weatherconditions*3+12
    price = int(price/(int(player.land/875)+1))
    lib.trade(args, player, "grain", **grainres)
    howmany = serfsrequire if player.grain >= serfsrequire else player.grain
    serfsgiven = io.inputinteger("{promptcolor}Give them how many?: {inputcolor}", howmany)
    io.echo("{/all}")
    if serfsgiven < 1:
        io.echo(f"{{(normalcolor}}Giving {{valuecolor}}{util.pluralize(howmany, **grainres)}{{normalcolor}} of grain)")
        serfsgiven = 0
    if serfsgiven > player.grain:
        serfsgiven = player.grain
    player.grain -= serfsgiven
    if args.debug is True:
        io.echo(f"{player.grain=}", level="debug")
    if player.grain < 1:
        player.grain = 0
        
    player.armyrequires = player.soldiers*10+1
    done = False
    io.echo(f"{{normalcolor}}Your army requires {util.pluralize(player.armyrequires, **grainres)}{{normalcolor}} this year and you have {{valuecolor}}{util.pluralize(player.grain, **grainres)}")
    price = int(6//player.weathercondition)
    price = int(price/(player.land/875)+1)
    grainres["price"] = price
    lib.trade(args, player, "grain", **grainres) # "bushel", price, "bushel", "bushels", emoji=":crop:")

    io.echo(f"{player.armyrequires=} {player.grain=}", level="debug")

    if player.armyrequires > player.grain:
        player.armyrequires = player.grain
    player.armygiven = io.inputinteger("{promptcolor}Give them how many?: {/all}{inputcolor}", player.armyrequires)
    if player.armygiven > player.grain:
        io.echo(f"You do not have enough grain! Your army has been given {util.pluralize(player.grain, **grainres)}")
        player.armygiven = player.grain
    io.echo("{/all}")
    if player.armygiven < 1:
        player.armygiven = 0
    player.grain -= player.armygiven
    io.echo(f"You gave your army {util.pluralize(player.armygiven, **grainres)}")

    horsesres = player.getresource("horses", singular="horse requires", plural="horses require")
    if player.horses > 0:
        horsesrequire = random.randint(2, 7)*player.horses*10
        io.echo(f"Your {util.pluralize(player.horses, quantity=False, **horsesres)} {util.pluralize(horsesrequire, **grainres)}")
        horsesgiven = io.inputinteger("{promptcolor}Give them how many?: {/all}{inputcolor}", horsesrequire)
        if horsesgiven < 0:
            horsesgiven = 0
        elif horsesgiven > player.grain:
            horsesgiven = player.grain
        player.grain -= horsesgiven
        player.horsesgiven = horsesgiven

    player.adjust()
    player.save()
    return True
