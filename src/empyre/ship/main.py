from bbsengine6 import io, database

from . import lib as libship
from .. import lib as libempyre

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args=None, **kwargs):
    return None

def main(args, **kwargs):
    io.echo("ships")

#    io.echo(f"empyre.ship.main.200: {kwargs.get('pool')=}", level="debug")

    def _work(conn):
        sql = "select moniker from empyre.ship where location=%s and playermoniker=%s"
        dat = (location, player.moniker,)
        with database.cursor(conn) as cur:
            cur.execute(sql, dat)
#            if cur.rowcount == 0:
#                io.echo("building first ship")
#                libship.build(args, **kwargs)

            ship = libship.selectship(args, cur=cur, **kwargs)
            if ship is None:
                return True

#            io.echo(f"{ship.moniker=}", level="debug")
            if ship is None:
                io.echo("No ship selected")
                return True

            done = False
            while not done:
                player.adjust()
                player.save()
                ship.adjust()
                ship.save()
                io.echo("{optioncolor}[L]{labelcolor} Load")
                io.echo("{optioncolor}[U]{labelcolor} Unload")
                io.echo(f"{{optioncolor}}[M]{{labelcolor}} Moniker: {ship.moniker}")
                io.echo("{optioncolor}[S]{labelcolor} Sail")
                io.echo("{optioncolor}[X]{labelcolor} Exit to dock")

                libempyre.setbottombar(args, f"ship: {ship.moniker}", player=player)
                ch = io.inputchar("ship: {inputcolor}", "ULMSXQ", "X")
                if ch == "Q" or ch == "X":
                    io.echo("Exit")
                    done = True
                elif ch == "M":
                    moniker = libship.inputshipname(args, "ship's moniker:", ship.moniker, **kwargs)
                    if moniker == ship.moniker:
                        io.echo("no change")
                        continue
                    ship.adjust()
                    ship.save(moniker=moniker)
                elif ch == "L":
                    libship.runmodule(args, "load", ship=ship, **kwargs)
                elif ch == "U":
                    libship.runmodule(args, "unload", ship=ship, **kwargs)
                elif ch == "S":
                    libship.runmodule(args, "sail", ship=ship, **kwargs)
            return True

    player = kwargs.get("player", None)
    #    location = kwargs["location"] if "location" in kwargs else "mainland"
    if player is None:
        io.echo("You do not exist! Go Away!", level="error")
        return False
    if player.ships > player.shipyards * libship.SHIPSPERSHIPYARD:
        shipyardres = player.getresource("shipyards")
        libempyre.trade(args, player, "shipyards", **shipyardres)
        if player.ships > player.shipyards * libship.SHIPSPERSHIPYARD:
            io.echo("aborted")
            return False

    player.adjust()
    player.save()

    location = kwargs.get("location", "mainland")

    conn = kwargs.get("conn", None)
    if conn is None:
        pool = kwargs.get("pool", None)
        with database.connect(args, pool=pool) as conn:
            return _work(conn)
    return _work(conn)
