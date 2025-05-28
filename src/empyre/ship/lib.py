import copy

from argparse import Namespace

from bbsengine6 import io, database, member, util
from bbsengine6.listbox import Listbox, ListboxItem
from .. import lib as libempyre

MAXSHIPYARDS:int = 10
SHIPSPERSHIPYARD:int = 10

class Ship(object):
    def __init__(self, args, **kwargs):
        self.args = args
        self.player = kwargs.get("player", None)
        self.location = kwargs.get("location", "mainland")
#        io.echo(f"Ship.100: {self.player=}", level="debug")
#        io.echo(f"{self.player=}", level="debug")
#        self.playermoniker = player.moniker
        self.moniker = None
        self.kind = "cargo"
        self.manifest = {}
        self.navigator = False
        self.status = None
        self.datecreated = None
        self.createdbymoniker = None
        self.datedocked = None

#        self.dbh = database.connect(args)

    def load(self, moniker:str) -> bool:
        sql = f"select * from empyre.ship where moniker=%s"
        dat = (moniker,)
        dbh = database.connect(self.args)
        cur = dbh.cursor()
        cur.execute(sql, dat)
        if cur.rowcount == 0:
            return False
        rec = cur.fetchone()
        for f in ("moniker", "kind", "manifest", "navigator", "location", "status", "datedocked", "datedockedlocal", "playermoniker"):
            setattr(self, f, rec[f])
        return True

    def save(self, commit=True, moniker=None):
        io.echo(f"saving ship {self.moniker}", level="debug")
        ship = {}
        for f in ("moniker", "kind", "manifest", "navigator", "location", "status", "datedocked", "playermoniker"):
            ship[f] = getattr(self, f)
        pk = ship["moniker"]
        if moniker is not None:
            if moniker != ship["moniker"]:
                ship["moniker"] = moniker
#        io.echo(f"{moniker=} {pk=} {ship=}", level="debug")
        database.update(self.args, "empyre.__ship", pk, ship, primarykey="moniker", updatepk=True)
        if commit is True:
            database.commit(self.args)

    def getmanifestentry(self, name):
        return self.manifest[name] if name in self.manifest else None

    def adjust(self):
        c = count(self.args, self.player.moniker)

        if self.player.ships != c:
            io.echo("adjusting {self.player.ships=} to {count=}", level="debug")
            self.player.ships = c
            self.player.save()

        return True

def build(args, **kwargs):
    player = kwargs.get("player", None)
    if player is None:
        io.echo("You do not exist! Go Away!", level="error")
        return False

    if player.ships+1 > player.shipyards*SHIPSPERSHIPYARD:
        io.echo("You need to build a shipyard before you can build a ship.")
        shipyardres = player.getresource("shipyards")
        libempyre.trade(args, player, "shipyards", **shipyardres)
        player.adjust()
        player.save()

    ship = Ship(args, **kwargs)
    _ship = _edit(args, "build", ship, **kwargs)
    if _ship == ship:
        io.echo("no changes")
    else:
        io.echo("changes made")

    if io.inputboolean("{promptcolor}build ship? {optioncolor}[Yn]{promptcolor}: {inputcolor}", "Y") is True:
        s = {}
        s["moniker"] = ship.moniker
        s["playermoniker"] = player.moniker
        for k in ("manifest", "location", "status", "kind", "navigator"):
            s[k] = getattr(ship, k)
        s["datecreated"] = "now()" # ship.datecreated
        s["createdbymoniker"] = member.getcurrentmoniker(args)
        s["datedocked"] = "now()"
        res = database.insert(args, "empyre.__ship", s, mogrify=True, primarykey="moniker")
        database.commit(args)
        return s
    return True

def _edit(args, mode, ship, **kwargs):
    player = kwargs.get("player", None)

    _ship = copy.copy(ship)

    done = False
    while not done:
        io.echo(f"{{optioncolor}}[N]{{labelcolor}}ame: {{valuecolor}}{ship.moniker}", end="")
        if _ship.moniker != ship.moniker:
            io.echo(f" {{labelcolor}}(was: {{valuecolor}}{_ship.moniker}{{labelcolor}})")
        else:
            io.echo()

        io.echo(f"{{optioncolor}}[O]{{labelcolor}}wner: {{valuecolor}}{ship.player.moniker}", end="")
        if _ship.player.moniker != ship.player.moniker:
            io.echo(f" {{labelcolor}}(was: {{valuecolor}}{_ship.player.moniker}{{labelcolor}})")
        else:
            io.echo()

        io.echo(f"{{optioncolor}}[A]{{labelcolor}} Navigator: {{valuecolor}}{ship.navigator}", end="")
        if _ship.navigator != ship.navigator:
            io.echo(f" {{labelcolor}}(was: {{valuecolor}}{_ship.navigator}{{labelcolor}})")
        else:
            io.echo()

        ch = io.inputchar(f"{{promptcolor}}{mode} ship: {{inputcolor}}", "MNOAKQ", "")
        if ch == "Q":
            io.echo("Quit")
            done = True
        elif ch == "N":
            completer = completeShipName(args, **kwargs)
            ship.moniker = inputshipname(args, ship.moniker, completer=completer, verify=verifyShipNameNotFound)
        elif ch == "L":
            io.echo("Load")
            ship.load()
        elif ch == "U":
            io.echo("Unload")
            ship.unload()
        elif ch == "A":
            io.echo("Navigator")
            nav = player.getresource("navigators")
            if nav is None:
                io.echo("'navigator' is not a valid resource.", level="error")
                continue
            if player.coins < nav["price"]:
                io.echo("You need {} to purchase a navigator".format(util.pluralize(nav["price"], "coin", "coins", **nav)))
            else:
                player.coins -= nav["price"]
                ship.navigator = True
        elif ch == "K":
            io.echo("Kind")
            k = io.inputchoice("[C]argo [P]assenger [M]ilitary", "CPM", "C")
            if k == "C":
                io.echo("cargo")
                ship.kind = "cargo"
            elif k == "P":
                io.echo("passenger")
                ship.kind = "passenger"
            elif k == "M":
                io.echo("military carrier")
                ship.kind = "carrier"
    return ship

class completeShipName(object):
    def __init__(self, args, **kwargs):
        self.args = args

        self.player = kwargs.get("player", None)

        self.pool = kwargs.get("pool", None)
        if self.pool is None:
            io.echo(f"empyre.ship.lib.completeShipName.100: {self.pool=}")
            return

        with database.connect(args, pool=self.pool) as conn:
            with database.cursor(conn) as cur:
                sql = "select moniker from empyre.ship where playermoniker=%s"
                dat = (self.player.moniker,)
                cur.execute(sql, dat)
                self.names = []
                if cur.rowcount > 0:
                    for rec in cur.fetchall():
                        self.names.append(rec["moniker"])

    # @log_exceptions
    def complete(self:object, text:str, state:int):
        vocab = []
        for a in self.attrs:
            vocab.append(a["name"])
        results = [x for x in vocab if x.startswith(text)] + [None]
        return results[state]

def verifyShipNameFound(moniker:str, **kwargs) -> bool:
    args = kwargs["args"] if "args" in kwargs else Namespace()

    io.echo(f"verifyShipNameFound.120: {args=} {moniker=}", level="debug")
    pool = kwargs.get("pool", None)
    if pool is None:
        io.echo(f"empyre.ship.lib.verifyShipNameFound.100: {pool=}", level="error")
        return None
    with database.connect(args, pool=pool) as conn:
        with database.cursor(conn) as cur:
            sql = "select 1 from empyre.ship where moniker=%s"
            dat = (moniker,)
            cur.execute(sql, dat)
            io.echo(f"verifyShipNameFound.100: mogrify={cur.mogrify(sql, dat)}", level="debug")
            if cur.rowcount == 0:
                return False
            return True

def verifyShipNameNotFound(moniker:str, **kwargs) -> bool:
    args = kwargs["args"] if "args" in kwargs else Namespace()

    io.echo(f"verifyShipNameNotFound.120: {args=} {moniker=}", level="debug")
    pool = kwargs.get("pool", None)
    if pool is None:
        io.echo(f"empyre.ship.lib.verifyShipNameFound.100: {pool=}", level="error")
        return None
    with database.connect(args, pool=pool) as conn:
        with database.cursor(conn) as cur:
            sql = "select 1 from empyre.ship where moniker=%s"
            dat = (moniker,)
            cur.execute(sql, dat)
            io.echo(f"verifyShipNameFound.100: mogrify={cur.mogrify(sql, dat)}", level="debug")
            if cur.rowcount == 0:
                return False
            return True

def inputshipname(args, prompt:str, currentmoniker="", **kwargs) -> str:
    verify = kwargs.pop("verify", verifyShipNameNotFound)
    moniker = io.inputstring(prompt, currentmoniker, verify=verify, args=args, **kwargs)
    if args.debug is True:
        io.echo(f"inputshipname.100: {moniker=}", level="debug")
    return moniker


def selectship(args, **kw):
    class EmpyreShipListbox(Listbox):
        def __init__(self, args, title:str, **kw):
#            io.echo(f"{kw=}", level="debug")
            self.player = kw["player"] if "player" in kw else None
#            io.echo(f"selectship: {self.player=}", level="debug")
            super().__init__(args, title=title, **kw)

        def fetchpage(self):
            self.cur.scroll(self.page*self.pagesize, mode="absolute")
            self.items = []
            for rec in self.cur.fetchmany(self.pagesize):
                self.items.append(self.itemclass(rec, self.terminalwidth, self.player))
            self.numitems = len(self.items)
            return self.items

    class EmpyreShipListboxItem(ListboxItem):
        def __init__(self, rec:dict, width:int=None, player=None, location:str="mainland"):
            super().__init__(rec, width, player, location)
#            io.echo(f"empyreshiplistboxitem: {player=}", level="debug")
            self.ship = Ship(args, **kw)
            self.ship.load(rec["moniker"])

            left = f"{self.ship.moniker}"
            datedocked = util.datestamp(self.ship.datedockedlocal, format="%m/%d @ %I%M%P")
            right = f"{self.ship.location} {datedocked}"
            rightlen = len(right)
            self.label = f"{left.ljust(width-rightlen-10)}{right}" # %s%s {{/all}}{{var:acscolor}}{{acs:vline}}" % (left.ljust(width-rightlen-4), right)
            self.pk = self.ship.moniker
            self.rec = rec
            self.width = width
            self.player = player
            self.height = 1

        def help(self):
            io.echo("use KEY_ENTER to select one of your ships")
            return

        def display(self):
            io.echo(f"{{/all}}{{cha}} {{engine.menu.cursorcolor}}{{engine.menu.color}} {{engine.menu.boxcharcolor}}{{acs:vline}}{{cic}} {self.label.ljust(self.width-9, ' ')} {{/all}}{{engine.menu.boxcharcolor}}{{acs:vline}}{{engine.menu.shadowcolor}} {{engine.menu.color}} {{/all}}{{cha}}", end="", flush=True)
            return

    player = kw.get("player", None)
    io.echo(f"{player=}", level="debug")
    if player is None:
        io.echo("You do not exist! Go Away!", level="error")
        return False

    totalships = count(args, player.moniker)

    pool = kw.get("pool", None)
    if pool is None:
        io.echo(f"empyre.ship.lib.selectship.200: {pool=}", level="error")
        return False

    with database.connect(args, pool=pool) as conn:
        with database.cursor(conn) as cur:
            sql = f"select * from empyre.ship where playermoniker=%s"
            dat = (player.moniker,)
            cur.execute(sql, dat)

    io.echo(f"{kw['player']=}", level="debug")
    lb = EmpyreShipListbox(args, "select ship", keyhandler=None, totalitems=totalships, itemclass=EmpyreShipListboxItem, **kw)
    return lb.run("select ship: ")

def getship(args, moniker, **kw):
    player = kw["player"] if "player" in kw else None
    if player is None:
        io.echo("You do not exist! Go Away!")
        return None
    sql = "select * from empyre.ship where moniker=%s"
    dat = (moniker,)
    dbh = database.connect(args)
    cur = dbh.cursor()
    cur.execute(sql, dat)
    if cur.rowcount == 0:
        return None
    rec = cur.fetchone()
    ship = Ship(args, rec=rec, **kw)
    ship.load(moniker)
    return ship

def empyshipkeyhandler(args, ch, lb):
    io.echo("inside empyreshipkeyhandler", level="debug")
    currentitem = lb.currentitem
    if ch == "KEY_ENTER":
        io.setvar("cic", "{currentitemcolor}")
        currentitem.display()
        io.echo("{restorecursor}", end="", flush=True)
        io.echo(f"{currentitem.player.moniker}")
        return False

def selectmanifestitem(args, **kw):
    class EmpyreShipManifestListbox(Listbox):
        def __init__(self, args, title, **kw):
            ship = kw["ship"] if "ship" in kw else None
            if ship is None:
                io.echo("ship not defined.", level="error")
                return None
            player = kw["player"] if "player" in kw else None
            if player is None:
                io.echo("player not defined", level="error")
                return None
            
            self.itemclass = kw["itemclass"] if "itemclass" in kw else None
            
            self.width = kw["width"] if "width" in kw else io.getterminalwidth()

            self.data = []
            for k, v in ship.manifest.items():
                self.data.append(self.itemclass(k, res=player.getresource(k), value=v, width=self.width, player=player, ship=ship))

            super().__init__(args, title=title, totalitems=len(self.data), **kw)

        def fetchpage(self):
            self.items = []
            n = self.page*self.pagesize
            upper = self.pagesize+n
            if upper > self.totalitems:
                upper = self.totalitems
            for x in range(n, upper):
                self.items.append(self.data[x])
            self.numitems = len(self.items) # number of items on the page in case it doesn't equal pagesize
            io.echo(f"{self.items=}")
            return self.items

    class EmpyreShipManifestListboxItem(object):
        def __init__(self, resourcename:str, width:int=None, **kw):
            self.ship = kw["ship"] if "ship" in kw else None
            self.player = kw["player"] if "player" in kw else None
            self.pk = resourcename
            self.label = "NEEDINFO"
            self.res = self.player.getresource(resourcename)
            self.height = 1
#            self.rec = rec
            self.width = width
            io.echo(f"{self.width=}", level="debug")

            self.manifestitem = self.ship.manifest[self.pk] if self.pk in self.ship.manifest else {}
            value = self.manifestitem["value"]

            left = f"{self.pk}"
            right = f"{value:>6n}" # {util.pluralize(value, **self.res)}"
            rightlen = len(right)
            self.label = f"{left.ljust(self.width-rightlen-10)}{right}" # %s%s {{/all}}{{var:acscolor}}{{acs:vline}}" % (left.ljust(width-rightlen-4), right)
            
        def help(self):
            io.echo("use KEY_ENTER to select a ship resource")
            return

        def display(self):
            io.echo(f"{{/all}}{{cha}} {{engine.menu.cursorcolor}}{{engine.menu.color}} {{engine.menu.boxcharcolor}}{{acs:vline}}{{cic}} {self.label.ljust(self.width-9, ' ')} {{/all}}{{engine.menu.boxcharcolor}}{{acs:vline}}{{engine.menu.shadowcolor}} {{engine.menu.color}} {{/all}}{{cha}}", end="", flush=True)
            return

    ship = kw["ship"] if "ship" in kw else None
    if ship is None:
        io.echo("You do not exist! Go Away!")
        return False

    lb = EmpyreShipManifestListbox(args, "select ship resource", keyhandler=None, itemclass=EmpyreShipManifestListboxItem, **kw)
    op = lb.run("ship resource: ")
    if op.kind == "select":
        io.echo(f"{op.listitem.pk}")
    return op

def runmodule(args, modulename, **kw):
    return libempyre.runmodule(args, f"ship.{modulename}", **kw)

# @since 20240414
def count(args, playermoniker=None, **kwargs):
    def _work(conn):
        with database.cursor(conn) as cur:
            sql:str = "select count(moniker) from empyre.ship where playermoniker=%s"
            dat:tuple = (playermoniker,)
            cur.execute(sql, dat)
            return cur.rowcount

    conn = kwargs.get("conn", None)
    if conn is None:
        pool = kwargs.get("pool", None)
        if pool is None:
            io.echo(f"empyre.lib.countships.100: {pool=}", level="error")
            return False
        with database.connect(args, pool=pool) as conn:
            return _work(conn)
    return _work(conn)
