from bbsengine6 import io, listbox, database, member

from . import lib
from .. import lib as empyre

def keyhandler(args, ch, listbox):
    currentitem = listbox.currentitem
    ship = currentitem.rec

    keys = {}
    keys["KEY_INS"] = "insertperson"

    if ch in ("KEY_INS"):
        io.setvar("cic", "{currentitemcolor}")
        currentitem.display()
        io.echo("{restorecursor}new ship")
        ship = lib.build(args)
        lib.insert(args, "__ship", ship)
        return True # key has been handled
    return False

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args=None, **kw):
    return None

def main(args, **kw):
    io.echo("ships")
    
    player = kw["player"] if "player" in kw else None
    location = kw["location"] if "location" in kw else "mainland"
    if player is None:
        io.echo("You do not exist! Go Away!", level="error")
        return False
    if player.ships == 0:
        io.echo("You have no ships!")
        lib.newship()
        return False

    location = kw["location"] if "location" in kw else "mainland"

    sql = f"select moniker from empyre.ship where location=%s and playermoniker=%s"
    dat = (location, player.moniker,)
    dbh = database.connect(args)
    cur = dbh.cursor()
    cur.execute(sql, dat)
    if cur.rowcount == 0:
        io.echo("building first ship")
        lib.build(args, **kw)

    op = lib.selectship(args, cur=cur, **kw)
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
        io.echo(f"{{optioncolor}}[L]{{labelcolor}} Load")
        io.echo(f"{{optioncolor}}[U]{{labelcolor}} Unload")
        io.echo(f"{{optioncolor}}[M]{{labelcolor}} Moniker: {ship.moniker}")
        io.echo(f"{{optioncolor}}[S]{{labelcolor}} Scrap")
        io.echo(f"{{optioncolor}}[X]{{labelcolor}} Exit to dock")
        
        ch = io.inputchar("ship: {inputcolor}", "ULMSXQ", "X")
        if ch == "Q" or ch == "X":
            io.echo("Exit")
            done = True
        elif ch == "M":
            moniker = lib.inputshipname(args, "ship's moniker:", ship.moniker)
            if moniker == ship.moniker:
                io.echo("no change")
                continue
            ship.adjust()
            ship.save(moniker=moniker)
        elif ch == "L":
            lib.runmodule(args, "load", ship=ship, **kw)
        elif ch == "U":
            lib.runmodule(args, "unload", ship=ship, **kw)
        elif ch == "S":
            lib.runmodule(args, "scrap", ship=ship, **kw)
    return True

