from bbsengine6 import io, listbox, database, member

from . import lib as libship
from .. import lib as libempyre
from .. import player as libplayer

def keyhandler(args, ch, listbox):
    currentitem = listbox.currentitem
    ship = currentitem.rec

    keys = {}
    keys["KEY_INS"] = "insertperson"

    if ch in ("KEY_INS"):
        io.setvar("cic", "{currentitemcolor}")
        currentitem.display()
        io.echo("{restorecursor}new ship")
        ship = libship.build(args)
        libship.insert(args, "__ship", ship)
        return True # key has been handled
    return False

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args=None, **kw):
    return None

def main(args, **kwargs):
    io.echo("ships")
    
    def _work(conn):
        sql = f"select moniker from empyre.ship where location=%s and playermoniker=%s"
        dat = (location, player.moniker,)
        with database.cursor(conn) as cur:
            cur.execute(sql, dat)
            if cur.rowcount == 0:
                io.echo("building first ship")
                libship.build(args, **kwargs)

            op = libship.selectship(args, cur=cur, **kwargs)
            if op.kind == "exit":
                return True

            ship = op.listitem.ship
        #    ship.player = player

            io.echo(f"{ship.moniker=}", level="debug")
            if ship is None:
                io.echo("No ship selected")
                return True

            done = False
            while not done:
                player.adjust()
                player.save()
                ship.adjust()
                ship.save()
                io.echo(f"{{optioncolor}}[L]{{labelcolor}} Load")
                io.echo(f"{{optioncolor}}[U]{{labelcolor}} Unload")
                io.echo(f"{{optioncolor}}[M]{{labelcolor}} Moniker: {ship.moniker}")
                io.echo(f"{{optioncolor}}[S]{{labelcolor}} Sail")
                io.echo(f"{{optioncolor}}[X]{{labelcolor}} Exit to dock")
                
                ch = io.inputchar("ship: {inputcolor}", "ULMSXQ", "X")
                if ch == "Q" or ch == "X":
                    io.echo("Exit")
                    done = True
                elif ch == "M":
                    moniker = libship.inputshipname(args, "ship's moniker:", ship.moniker)
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
#    location = kw["location"] if "location" in kw else "mainland"
    if player is None:
        io.echo("You do not exist! Go Away!", level="error")
        return False
    n = libship.count(args, player.moniker, **kwargs)
    player.ships = n
    if n == 0:
        io.echo("You have no ships!")
        libship.build(args, **kwargs)
        return False

    if player.ships > player.shipyards*libship.SHIPSPERSHIPYARD:
        shipyardres = player.getresource("shipyards")
        libempyre.trade(args, player, "shipyards", **shipyardres)
        if player.ships > player.shipyards*libship.SHIPSPERSHIPYARD:
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
