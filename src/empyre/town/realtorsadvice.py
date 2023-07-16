import ttyio6 as ttyio
import bbsengine6 as bbsengine

from .. import lib

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

def main(args, player, **kwargs):
    bbsengine.util.heading(": hood's real deals! :")
    lib.setarea(args, player, "town -> hood's real deals!")
    
    # you have 10 shipyards, BSC
    # you have 10 acres of land
    # prompt = "You have {reverse}%s{/reverse} and {reverse}%s{/reverse}" % (pluralize(player.shipyards, "shipyard", "shipyards"), pluralize(player.credits, "credit", "credits"))
    # all of these are ints
    lib.trade(args, player, "shipyards", "shipyards", 2500+player.shipyards//2, "shipyard", "shipyards", "a")
    lib.trade(args, player, "ships", "ships", 5000, "ship", "ships", "a", ":anchor:")
    lib.trade(args, player, "foundries", "foundries", 2000+player.foundries//2, "foundry", "foundries", "a")
    lib.trade(args, player, "mills", "mills", 500+player.mills//2, "mill", "mills", "a")
    lib.trade(args, player, "markets", "markets", 250+player.markets//2, "market", "markets", "a")
    
    player.save()

    return
