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
        ship = libship.selectship(args, conn=conn, **kwargs)
        if ship is None:
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
            ch = io.inputchar("ship: {inputcolor}", "ULMSXQ", "X", **kwargs)
            if ch == "Q" or ch == "X":
                io.echo("Exit")
                done = True
            elif ch == "M":
                moniker = libship.inputshipname(
                    args, "ship's moniker:", ship.moniker, **kwargs
                )
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

    conn = kwargs.get("conn", None)
    if conn is None:
        pool = kwargs.get("pool", None)
        with database.connect(args, pool=pool) as conn:
            return _work(conn)
    return _work(conn)
