from .. import lib as libempyre
from bbsengine6 import util, database

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args, **kw):
    return None

def main(args, player, **kwargs):
    util.heading(": hood's real deals! :")
    libempyre.setarea(args, "town -> hood's real deals!", **kwargs)

    def _work(conn):

        # you have 10 shipyards, BSC
        # you have 10 acres of land
        # prompt = "You have {reverse}%s{/reverse} and {reverse}%s{/reverse}" % (pluralize(player.shipyards, "shipyard", "shipyards"), pluralize(player.credits, "credit", "credits"))
        # all of these are ints
        #    lib.trade(args, player, "shipyards", "shipyards", 2500+player.shipyards//2, "shipyard", "shipyards", "a")
        #    lib.trade(args, player, "ships", "ships", 5000, "ship", "ships", "a", ":anchor:")

        res = player.getresource("foundries")
        res["price"] = 2000+player.foundries//2
        libempyre.trade(args, player, "foundries", conn=conn, **res) # "foundries", "foundries", 2000+player.foundries//2, "foundry", "foundries", "a")

        res = player.getresource("mills")
        res["price"] = 500+player.mills//2
        libempyre.trade(args, player, "mills", conn=conn, **res) # "mills", 500+player.mills//2, "mill", "mills", "a")

        res = player.getresource("markets")
        res["price"] = 250+player.markets//2
        libempyre.trade(args, player, "markets", conn=conn, **res) # "markets", 250+player.markets//2, "market", "markets", "a")

        player.adjust()
        player.save()

        return True
    conn = kwargs.get("conn", None)
    if conn is None:
        pool = kwargs.get("pool", None)
        if pool is None:
            io.echo(f"empyre.town.realtorsadvice.100: {pool=}", level="error")
            return False
        with database.connect(args, pool=pool) as conn:
            return _work(conn)
    return _work(conn)
