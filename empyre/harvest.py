import random

import ttyio5 as ttyio
import bbsengine5 as bbsengine

from . import lib

def main(args, **kw):
    player = kw["player"] if "player" in kw else None

    lib.setarea(args, player, "harvest")
    x = int((player.land*player.weathercondition+(random.random()*player.serfs)+player.grain*player.weathercondition)/3)
    x = min(x, player.land+player.serfs*4)
    #if x > (player.land+player.serfs)*4:
    #    x = (player.land+player.serfs)*4
    ttyio.echo("{f6}{lightblue}This year's harvest is :crop: {var:empyre.highlightcolor}%s{/all}{f6}" % (bbsengine.pluralize(x, "bushel", "bushels")))

    # https://github.com/Pinacolada64/ImageBBS/blob/cb68d111c2527470218aedb94b93e7f4b432c345/v1.2/web-page/imageprg-chap5.html#L69
    player.grain += x # "pl=1"? <-- has to do with imagebbs input routines accepting upper/lower case vs only upper

    serfsrequire = player.serfs*5+1
    ttyio.echo("{cyan}Your people require :crop: {var:empyre.highlightcolor}%s{/all} of grain this year{/all}" % (bbsengine.pluralize(serfsrequire, "bushel", "bushels")))
    ttyio.echo()
    price = player.weatherconditions*3+12
    price = int(price/(int(player.land/875)+1))
    lib.trade(args, player, "grain", "grain", price, "bushel", "bushels", emoji=":crop:")
    howmany = serfsrequire if player.grain >= serfsrequire else player.grain
    serfsgiven = ttyio.inputinteger("{cyan}Give them how many? {lightgreen}", howmany)
    ttyio.echo("{/all}")
    if serfsgiven < 1:
        ttyio.echo("(Giving :crop: {var:empyre.highlightcolor}%s{/all} of grain)" % (bbsengine.pluralize(howmany, "bushel", "bushels")))
        serfsgiven = 0
    if serfsgiven > player.grain:
        serfsgiven = player.grain
    player.grain -= serfsgiven
    if args.debug is True:
        ttyio.echo("player.grain=%r" % (player.grain), level="debug")
    if player.grain < 1:
        player.grain = 0
        
    armyrequires = player.soldiers*10+1
    done = False
    ttyio.echo("Your army requires :crop: {var:empyre.highlightcolor}%s{/all} this year and you have :crop: {var:empyre.highlightcolor}%s{/all}." % (bbsengine.pluralize(armyrequires, "bushel", "bushels"), bbsengine.pluralize(int(player.grain), "bushel", "bushels")))
    price = int(6//player.weathercondition)
    price = int(price/(player.land/875)+1)
    lib.trade(args, player, "grain", "bushel", price, "bushel", "bushels", emoji=":crop:")

    ttyio.echo("armyrequires=%r player.grain=%r" % (armyrequires, player.grain), level="debug")

    if armyrequires > player.grain:
        armyrequires = player.grain
    armygiven = ttyio.inputinteger("{cyan}Give them how many? {/all}{lightgreen}", armyrequires)
    if armygiven > player.grain:
        ttyio.echo("You do not have enough grain!")
        armygiven = player.grain
    ttyio.echo("{/all}")
    if armygiven < 1:
        armygiven = 0
    player.grain -= armygiven

    if player.horses > 0:
        horsesrequire = random.randint(2, 7)*player.horses
        ttyio.echo("Your :horse: %s :crop: %s" % (bbsengine.pluralize(player.horses, "horse requires", "horses require", quantity=False), bbsengine.pluralize(horsesrequire, "bushel", "bushels")))
        horsesgiven = ttyio.inputinteger("{cyan}Give them how many? {/all}{lightgreen}", horsesrequire)
        if horsesgiven < 0:
            horsesgiven = 0
        elif horsesgiven > player.grain:
            horsesgiven = player.grain
        player.grain -= horsesgiven

    player.save()
    return True
