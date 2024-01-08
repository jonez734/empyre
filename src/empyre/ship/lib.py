class Ship(object):
    def __init__(self, args, player):
        self.args = args
        self.player = None
        self.name = None
        self.kind = "cargo"
        self.manifest = {}
        self.navigator = False
        self.player = player

def build(self):
    if self.player is None:
        io.echo("You do not exist! Go Away!", level="error")
        return False
    
    ship = Ship(self.args, self.player)
    _ship = self._edit("build", ship)
    if _ship == ship:
        io.echo("no changes")
    else:
        io.echo("changes made")

    if io.inputboolean("{var:promptcolor}build ship?: {var:inputcolor}", "Y") is True:
        s = {}
        s["name"] = ship.name
        s["playerid"] = ship.player.playerid
        s["manifest"] = ship.manifest
        s["location"] = "mainland"
        s["status"] = "operational"
        s["kind"] = "cargo"
        s["datecreated"] = "now()" # ship.datecreated
        s["createdbyid"] = member.getcurrentid(self.args)
        res = database.insert(self.args, "empyre.__ship", s, mogrify=True, primarykey="name")
        database.commit(self.args)

def _edit(self, mode, ship):
    _ship = copy.deepcopy(ship)

    done = False
    while not done:
        io.echo(f"{{var:optioncolor}}[N]{{var:labelcolor}}ame: {{var:valuecolor}}{ship.name}", end="")
        if _ship.name != ship.name:
            io.echo(f" {{var:labelcolor}}(was: {{var:valuecolor}}{_ship.name}{{var:labelcolor}})")
        else:
            io.echo()

        io.echo(f"{{var:optioncolor}}[O]{{var:labelcolor}}wner: {{var:valuecolor}}{ship.player.moniker}", end="")
        if _ship.player.moniker != ship.player.moniker:
            io.echo(f" {{var:labelcolor}}(was: {{var:valuecolor}}{_ship.player.moniker}{{var:labelcolor}})")
        else:
            io.echo()
        
        io.echo(f"n{{var:optioncolor}}[A]{{var:labelcolor}}vigator: {{var:valuecolor}}{ship.navigator}", end="")
        if _ship.navigator != ship.navigator:
            io.echo(f" {{var:labelcolor}}(was: {{var:valuecolor}}{_ship.navigator}{{var:labelcolor}})")
        else:
            io.echo()

        ch = io.inputchar(f"{{var:promptcolor}}{mode} ship: {{var:inputcolor}}", "MNOAKQ", "")
        if ch == "Q":
            io.echo("Quit")
            done = True
        elif ch == "N":
            completer = completeShipName(self.args, self.player)
            ship.name = inputshipname(self.args, ship.name, completer=completer, verify=verifyShipNameNotFound)
        elif ch == "L":
            io.echo("Load")
            ship.load()
        elif ch == "U":
            io.echo("Unload")
            ship.unload()
        elif ch == "A":
            io.echo("Navigator")
            nav = player.getresource("navigator")
            if nav is None:
                io.echo("'navigator' is not a valid resource.", level="error")
                continue
            if player.coins < nav["price"]:
                io.echo("You need {} to purchase a navigator".format(util.pluralize(nav["price"], "coin", "coins", **nav)))
            else:
                player.coins -= nav["price"]
                ship["navigator"] = True
        elif ch == "K":
            io.echo("Kind")
            k = io.inputchoice("[C]argo [P]assenger [M]illitary", "CPM", "C")
            if k == "C":
                io.echo("cargo")
                ship.kind = "cargo"
            elif k == "P":
                io.echo("passenger")
                ship.kind = "passenger"
            elif k == "M":
                io.echo("carrier")
                ship.kind = "carrier"

def editmanifest(self):
    # grain, serf, noble, cannon
    # navigator is not a 'resource', it's part of the ship
    # @see plus_emp6_colony.lbl
#    res = player.getresource("grain")
    amount = io.inputinteger(f"{{var:promptcolor}}amount of grain: {{var:inputcolor}}", self.player.grain)
    if amount < 0:
        io.echo("Must specify an amount greater than zero.")
    elif amount > self.player.grain:
        io.echo("You are short by {} of grain.".format(util.pluralize(amount - self.player.grain, "bushel", "bushels", emoji=":crop:")))
    else:
        self.player.grain -= amount
        if self.player.grain < 0:
            self.player.grain = 0
        if "grain" in self.manifest:
            self.manifest["grain"] += amount
        else:
            self.manifest["grain"] = amount
        self.player.adjust()
        self.player.save()

class completeShipName(object):
    def __init__(self, args, playerid):
        self.args = args
        self.dbh = database.connect(self.args)
        self.cur = dbh.cursor()
        sql = "select name from empyre.ship where playerid=%s"
        dat = (playerid,)
        self.cur.execute()
        self.names = []
        if self.cur.rowcount > 0:
            for rec in self.cur.fetchall():
                self.names.append(rec["name"])

    # @log_exceptions
    def complete(self:object, text:str, state:int):
        vocab = []
        for a in self.attrs:
            vocab.append(a["name"])
        results = [x for x in vocab if x.startswith(text)] + [None]
        return results[state]

def verifyShipNameFound(name:str, **kwargs) -> bool:
    args = kwargs["args"] if "args" in kwargs else Namespace()

    io.echo(f"verifyShipNameFound.120: {args=} {moniker=}", level="debug")
    dbh = database.connect(args)
    cur = dbh.cursor()
    sql = "select 1 from empyre.ship where name=%s"
    dat = (name,)
    cur.execute(sql, dat)
    io.echo(f"verifyShipNameFound.100: mogrify={cur.mogrify(sql, dat)}", level="debug")
    if cur.rowcount == 0:
        return False
    return True

def verifyShipNameNotFound(name:str, **kwargs) -> bool:
    args = kwargs["args"] if "args" in kwargs else Namespace()

    io.echo(f"verifyShipNameNotFound.120: {args=} {name=}", level="debug")
    dbh = database.connect(args)
    cur = dbh.cursor()
    sql = "select 1 from empyre.ship where name=%s"
    dat = (name,)
    cur.execute(sql, dat)
    io.echo(f"verifyShipNameNotFound.100: mogrify={cur.mogrify(sql, dat)}", level="debug")
    if cur.rowcount == 0:
        return True
    return False

def inputshipname(args, ship:Ship, **kw):
    if "verify" in kw:
        verify = kw["verify"]
        del kw["verify"]
    else:
        verify = verifyShipNameNotFound
        
    if ship is not None:
        currentvalue = ship.name
    else:
        currentvalue = ""
    name = io.inputstring("ship name: ", currentvalue, verify=verify, args=args, **kw)
    if args.debug is True:
        io.echo(f"inputshipname.100: {name=}", level="debug")
    return name

def getship(args, name, **kw):
    sql = "select * from empyre.ship where name=%s"
    dat = (name,)
    dbh = database.connect(args)
    cur = dbh.cursor()
    cur.execute(sql, dat)
    if cur.rowcount == 0:
        return False
    res = cur.fetchone()
    ship = Ship()
    ship.name = res["name"]
    ship.player = res["player"]
    ship.location = res["location"]
    ship.status = res["status"]    
    ship.manifest = res["manifest"]
    ship.navigator = res["navigator"]
    
    return ship
