from bbsengine6 import io, listbox, database, member

from . import lib
from .. import lib as empyre

class EmpyreShipListboxItem(object):
    def __init__(self, rec:dict, width:int):
        self.ship = lib.Ship(args)
        self.ship.load(rec["id"])
        self.ship.name = f"ship {rec['id']}"

        res = self.player.getresource("land")
        left = f"{self.player.moniker}"
        lastplayed = util.datestamp(self.player.datelastplayed, format="%m/%d@%I%M%P")
        right = f"{util.pluralize(res['value'], **res)} {lastplayed}"
        rightlen = len(right)
        self.label = f"{left.ljust(width-rightlen-10)}{right}" # %s%s {{/all}}{{var:acscolor}}{{acs:vline}}" % (left.ljust(width-rightlen-4), right)

        self.status = ""
        self.pk = self.player.moniker
        self.rec = rec
        self.width = width

    def help(self):
        io.echo("use KEY_ENTER to select one of your ships")
        return

    def display(self):
        io.echo(f"{{/all}}{{cha}} {{var:engine.menu.cursorcolor}}{{var:engine.menu.color}} {{var:engine.menu.boxcharcolor}}{{acs:vline}}{{var:cic}} {self.label.ljust(self.width-9, ' ')} {{/all}}{{var:engine.menu.boxcharcolor}}{{acs:vline}}{{var:engine.menu.shadowcolor}} {{var:engine.menu.color}} {{/all}}{{cha}}", end="", flush=True)
        return

def main(args, **kw):
    io.echo("ships")
    
    player = kw["player"] if "player" in kw else NOne
    if player is None:
        io.echo("You do not exist! Go Away!", level="error")
        return False

    if player.ships == 0:
        io.echo("You have no ships!")
        return False

    currentmemberid = member.getcurrentid()
    sql = "select name from empyre.ship where memberid=%s and location='' or location='mainland'"
    dat = (currentmembid,)
    dbh = database.connect(args)
    cur = dbh.cursor()
    cur.execute(sql, dat)
    if cur.rowcount != player.ships:
        io.echo(f"{cur.rowcount} ships in database. {player.ships=}")
        # insert empty ship records
        ship = {}

    res = cur.fetchone()
    done = False
    while not done:
        io.echo("{var:optioncolor}[M]{var:labelcolor}anifest")
        io.echo("{var:optioncolor}[N]{var:labelcolor}ame")
        io.echo("{var:optioncolor}[S]{var:labelcolor}crap")
        io.echo("{var:optioncolor}[X]{var:labelcolor} exit to dock")
        
        ch = io.inputchar("ship: {var:inputcolor}", "NMSXQ", "X")
        if ch == "Q" or ch == "X":
            done = True
        elif ch == "M":
            manifest(args, player)
        elif ch == "N":
            name = lib.inputshipname(args, "ship name:")
