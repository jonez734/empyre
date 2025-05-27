# @since 20250226
import copy
import random
from datetime import datetime

from bbsengine6 import database, io, listbox, member, util

from .ship import lib as libship
from . import lib as libempyre

TURNSPERDAY:int = 99
HORSESPERSTABLE:int = 50
SOLDIERSPERNOBLE:int = 20
SOLDIERS:int = 40
TAXRATE:int = 15
COINS:int = 250000
LAND:int = 5000
MAXLAND:int = 2500000
SERFS:int = 2000
GRAIN:int = 20000
MAXFOUNDRIES:int = 400
MAXMARKETS:int = 500
MAXMILLS:int = 500
MAXCOINS:int = 1000000
# MAXSHIPYARDS:int = 10
# SHIPSPERSHIPYARD:int = 10

RESOURCES = {
    "coins":      { "default":COINS, "price":1, "singular": "coin", "plural":"coins", "emoji":":moneybag:", "ship":None},
    "serfs":      { "default":SERFS+random.randint(0, 200), "singular": "serf", "plural": "serfs", "ship":"passenger", "emoji":":person:"}, # sf x(19)
    "land":       { "default":LAND, "singular":"acre", "plural":"acres", "determiner":"an", "ship":None, "emoji":":farmer:"}, # la x(2)
    "grain":      { "default":GRAIN, "singular": "bushel", "plural": "bushels", "emoji":":crop:", "ship":"cargo"}, # gr
    "soldiers":   { "default":SOLDIERS, "price":20, "singular":"soldier", "plural":"soldiers", "ship":"millitary passenger"},
    "nobles":     { "default":3, "price":25000, "singular":"noble", "plural":"nobles", "ship":"passenger"}, # x(6)
    "palaces":    { "default":1, "price":20, "singular":"palace", "plural":"palaces", "ship":None}, # f%(1)
    "markets":    { "default":1, "price":1000, "singular":"market", "plural":"markets", "ship":None}, # f%(2) x(7)
    "mills":      { "default":1, "price":2000, "singular":"mill", "plural":"mills", "ship":None}, # f%(3) x(8)
    "foundries":  { "default":2, "price":7000, "singular":"foundry", "plural":"foundries", "ship":None}, # f%(4) x(9)
    "shipyards":  { "default":0, "price":8000, "singular":"shipyard", "plural":"shipyards", "ship":None}, # yc or f%(5)? x(10)
    "diplomats":  { "default":0, "price":50000, "singular":"diplomat", "plural":"diplomats", "ship":"passenger millitary"}, # f%(6) 0
    "ships":      { "default":0, "price":5000, "singular":"ship", "plural":"ships", "emoji":":anchor:", "ship":None}, # 5000 each, yc? x(12)
    "navigators": { "default":0, "price":500, "singular": "navigator", "plural": "navigators", "emoji":":compass:"}, # @since 20220907
    "stables":    { "default":1, "price":10000, "singular": "stable", "plural":"stables", "ship":None}, # x(11)
    "colonies":   { "default":0, "ship":None, "singular": "colony", "plural":"colonies"}, # i8
    "spices":     { "default":0, "singular":"ton", "plural":"tons", "ship":"cargo"}, # x(25)
    "cannons":    { "default":0, "singular":"cannon", "plural":"cannons","ship":"any"}, # x(14)
    "forts":      { "default":0, "singular":"fort", "plural":"forts", "ship":None}, # x(13)
    "dragons":    { "default":0, "singular":"dragon", "plural":"dragons", "emoji":":dragon:"},
    "horses":     { "default":50,"emoji":":horse:", "ship":"cargo", "singular":"horse", "plural":"horses"}, # x(23)
    "timber":     { "default":0, "singular":"log", "plural":"logs", "emoji":":wood:", "ship":"cargo"}, # x(16)
    "rebels":     { "default":0, "singular":"rebel", "plural":"rebels", "ship":None},
    "exports":    { "default":0, "singular":"ton", "plural":"tons","emoji": ":package:"},
    "islands":    { "default":0, "singular":"island", "plural":"islands", "emoji":":palmtree:"},
}

ATTRIBUTES = {
    "moniker":               {"default": None },
    "membermoniker":         {"default": None},
    "rank":                  {"default": 0 },
    "previousrank":          {"default": 0 },
    "turncount":             {"default": 0},
    "soldierpromotioncount": {"default": 0 },
    "datepromoted":          {"default": None},
    "combatvictorycount":    {"default": 0},
    "weatherconditions":     {"default": 0},
    "beheaded":              {"default": False},
    "datelastplayed":        {"default": None},
    "datelastplayedlocal":   {"default": None},
    #"coins":                {"default":COINS},
    "taxrate":               {"default": TAXRATE},
    "training":              {"default": 1},
}

class Player(object):
    def __init__(self, args, **kwargs):
        self.args = args

        self.pool = kwargs.get("pool", None)
        if self.pool is None:
            io.echo(f"empyre.Player._init.100: {self.pool=}", level="error")
            return None

#        self.conn = kwargs.get("conn", None)
#        if self.conn is None:
#            self.conn = database.connect(args, pool=self.pool)

        with database.connect(args, pool=self.pool) as conn:
            currentmoniker = member.getcurrentmoniker(args, conn=conn)

        # @see empire6/mdl.emp.delx2.txt#L25
        self.resources = copy.copy(RESOURCES)
        for name, data in self.resources.items():
            val = data["default"]
            # io.echo(f"empyre.Player.100: resource {name=} {val=}", level="debug")
            setattr(self, name, data["default"])
            self.resources[name]["value"] = data["default"]
            # io.echo(f"Player.__init__.100: {name=} {res=} {getattr(self, name)=}", level="debug")

        self.attributes = copy.copy(ATTRIBUTES)
        for name, data in self.attributes.items():
            # io.echo(f"attribute {name} {data['default']=}", level="debug")
            setattr(self, name, data["default"])
            self.attributes[name]["value"] = data["default"]

        self.debug = args.debug

#        tz=0:i1=self.palaces:i2=self.markets:i3=self.mills:i4=self.foundries:i5=self.shipyards:i6=self.diplomats
    def sync(self):
        # io.echo(f"Player.sync()", level="debug")
        for name, data in self.resources.items():
            newval = getattr(self, name)
            res = self.resources[name] # getresource(name)
            curval = res.get("value") #, res.get("default"))
            if newval != curval:
                io.echo(f"empyre.player.sync.100: {name=} {curval=} != {newval=}", level="debug")
            res["value"] = newval

        for name in self.attributes.keys():
            self.setattributevalue(name, getattr(self, name))
        return True

    def verify_consistency(self, verbose=False) -> bool:
        consistent = True

        for name in self.resources.keys():
            attr_val = getattr(self, name, None)
            res_val = self.resources[name].get("value", None)
            if attr_val != res_val:
                consistent = False
                if verbose:
                    io.echo(f"inconsistent resource: {name}: attr={attr_val} != res['value']={res_val}", level="warn")

        for name in self.attributes.keys():
            attr_val = getattr(self, name, None)
            attr_dict_val = self.attributes[name].get("value", None)
            if attr_val != attr_dict_val:
                consistent = False
                if verbose:
                    io.echo(f"inconsistent attribute: {name}: attr={attr_val} != attributes['value']={attr_dict_val}", level="warn")

        if verbose:
            if consistent:
                io.echo("verify_consistency: all values consistent", level="info")
            else:
                io.echo("verify_consistency: inconsistencies found", level="warn")

        return consistent

    def getresource(self, name, **kwargs):
        if self.debug:
            io.echo(f"getresource.100: {name=}")
        if name in self.resources:
            _r = self.resources.get(name)
            r = copy.copy(_r)
            v = getattr(self, name)
            if isinstance(v, int):
                if v is None:
                    v = 0
                else:
                    v = int(v)
            r["value"] = v
            if "emoji" not in r or r["emoji"] is None:
                r["emoji"] = ""
            elif "emoji" in kwargs:
                r["emoji"] = kwargs["emoji"]
            if "singular" in kwargs:
                r["singular"] = kwargs["singular"]
            if "plural" in kwargs:
                r["plural"] = kwargs["plural"]
            if self.debug:
                io.echo(f"{r=}", level="debug")
            return r
        return None

    # @since 20240706 new
    def setresourcevalue(self, name:str, value) -> bool:
        if name in self.resources:
            self.resources[name]["value"] = value
            return True
        return False

    def setattributevalue(self, name:str, value) -> bool:
        if name in self.attributes:
            self.attributes[name]["value"] = value
            return True
        return False

    # @since 20200901
    # @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_maint.lbl#L22
    def edit(self):
        done = False
        while not done:
            libempyre.setarea(self.args, f"edit player resources for {self.moniker}", player=self)
            op = libempyre.selectresource(self.args, "select player resource", self.resources)
            io.echo(f"empyre.Player.edit.100: {op=}", level="debug")
            if op.kind == "exit" or op.kind == "noitems":
                break

            res = op.listitem.resource
            pk = op.listitem.pk
            val = res.get("value", res.get("default"))
            if isinstance(val, datetime):
                f = input.date
                t = "datetime"
            elif isinstance(val, int):
                f = io.inputinteger
                t = "int"
            elif isinstance(val, bool):
                f = io.inputboolean
                t = "bool"
            elif isinstance(val, str):
                f = io.inputstring
                t = "str"
            val = f(f"{{var:promptcolor}}{pk} ({t}): {{var:inputcolor}}", val)
            setattr(self, pk, val)
        return

    def buildrec(self, **kwargs):
        rec = {}
        for name, data in self.attributes.items():
            if name == "datelastplayedlocal":
                continue
            v = data.get("value", data["default"])
            if isinstance(v, datetime):
                io.echo(f"buildrec.attributes.datetime!", level="debug")
                v = v.isoformat()
            rec[name] = v #data.get("value", data["default"])
        resources = copy.copy(self.resources)
        for name, data in resources.items():
            v = data.get("value", data["default"])
            if isinstance(v, datetime):
                io.echo("buildrec.resources.datetime!", level="debug")
                v = v.isoformat()
            resources[name]["value"] = v
        # io.echo(f"empyre.Player.buildrec.200: {resources=}", level="debug")
        rec["resources"] = database.Jsonb(resources)
        return rec

    def update(self, conn):
        def _work(conn):
            database.update(self.args, "empyre.__player", self.moniker, self.buildrec(), primarykey="moniker", conn=conn, mogrify=True)
            return True

        if conn is None:
            io.echo(f"empyre.Player.update.160: {conn=}", level="error")
            return False

        return _work(conn)

    def isdirty(self):
        if self.debug is True:
            if self.verify_consistency(verbose=True) is True:
                io.echo("Player.isdirty.300: player data integrity failure", level="warn")
        def getresval(name):
            if name in self.resources:
                r = self.resources[name]
                return r.get("value", r.get("default"))
            return None

        def getattrval(name):
            if name in self.attributes.keys():
                r = self.attributes.get(name)
                return r.get("value", r.get("default"))
            return None

        dirty = False
        for name, data in self.resources.items():
            curval = getattr(self, name)
            oldval = data.get("value", data.get("default"))
            if self.debug is True:
                io.echo(f"{name=} {curval=} {oldval=}", level="debug")
            if curval != oldval:
                io.echo(f"player.isdirty.100: {name=} {oldval=} {curval=}", level="debug")
                dirty = True

        for name, data in self.attributes.items():
            curval = getattr(self, name)
            oldval = data.get("value", data.get("default"))
            if self.debug is True:
                io.echo(f"{name=} {curval=} {oldval=}", level="debug")
            if curval != oldval:
                io.echo(f"player.isdirty.100: {name=} {oldval=} {curval=}", level="debug")
                dirty = True

        io.echo(f"Player.isdirty.140: {dirty=}", level="debug")
        return dirty

    def save(self, force=False, commit=True):
        if self.args.debug is True:
            io.echo(f"player.save.100: {self.moniker=}", level="debug")
        if self.moniker is None:
            io.echo(f"player moniker is not set. save aborted.", level="error")
            return None
        if self.membermoniker is None:
            io.echo("empyre.lib.save.120: You do not exist! Go away!", level="error")
            return None

        if force is True or self.isdirty() is True:
            io.echo(f"{{var:labelcolor}}saving {{var:valuecolor}}{self.moniker}{{var:labelcolor}}: ", end="")
            with database.connect(self.args, pool=self.pool) as conn:
                self.sync()
                self.update(conn)
                conn.commit()
            io.echo(" ok ", level="ok")
            return True

    def status(self):
        MAX_LABEL_WIDTH = 12
        DATETIME_FMT = "%m/%d@%H%M%Z"
        TRUNCATED_LABEL_SUFFIX = '..'
        TRUNCATED_LABEL_WIDTH = MAX_LABEL_WIDTH
        LABEL_DISPLAY_WIDTH = MAX_LABEL_WIDTH + len(TRUNCATED_LABEL_SUFFIX)

        LAYOUT = "column"

        MAX_STR_VALUE_WIDTH = 10

        TRUNCATED_STR_SUFFIX = '..'
        TRUNCATED_STR_WIDTH = MAX_STR_VALUE_WIDTH
        STR_DISPLAY_WIDTH = MAX_STR_VALUE_WIDTH + len(TRUNCATED_STR_SUFFIX)

        COLUMN_SEPARATOR = "  "

        util.heading(f"player status for {self.moniker}")

        terminal_width = io.getterminalwidth()-2

        io.echo(f"empyre.player.status.100: {self.resources=}", level="debug")
        # io.echo(f"empyre.player.status.120: {self.attributes=}", level="debug")

        data = self.resources
        data.update(self.attributes)

        sorted_items = sorted(data.items())

        # Set locale for thousands separator
        # locale.setlocale(locale.LC_ALL, '')

        def truncate_label(label):
            return label if len(label) <= MAX_LABEL_WIDTH else label[:TRUNCATED_LABEL_WIDTH-len(TRUNCATED_LABEL_SUFFIX)] + TRUNCATED_LABEL_SUFFIX

        def truncate_str_value(s):
            return s if len(s) <= MAX_STR_VALUE_WIDTH else s[:TRUNCATED_STR_WIDTH] + TRUNCATED_STR_SUFFIX

        def format_value(value):
            if value is None:
                return ""
            if isinstance(value, bool):
                return "yes" if value else "no"
            elif isinstance(value, int):
                return f"{value:n}"
            elif isinstance(value, datetime):
                return value.strftime(DATETIME_FMT)
            elif isinstance(value, str):
                return truncate_str_value(value).rstrip()
            else:
                return str(value)

        sorted_items = sorted(data.items())

        # determine max widths
        formatted = []
        max_value_width = 0
        max_label_width = 0

        for label, data in sorted_items:
            label_display = truncate_label(label)
            resource_value = data.get("value")
            attr_value = getattr(self, label, None)

            if label in self.resources:
                if label == "beheaded":
                    value_str = f"{format_value(bool(attr_value))} [{format_value(bool(resource_value))}]"
                else:
                    # Show both stored resource value and current attribute
                    value_str = f"{format_value(attr_value)} [{format_value(resource_value)}]"
            else:
                value_str = format_value(resource_value)

            formatted.append((label_display, value_str))
            max_label_width = max(max_label_width, len(label))
            max_value_width = max(max_value_width, len(value_str))

        key_width = MAX_LABEL_WIDTH
        column_width = key_width + len(COLUMN_SEPARATOR) + max_value_width  # ": " separator

        lines = [ f"{{var:labelcolor}}{label:<{key_width}}: {{var:valuecolor}}{value:>{max_value_width}}" for label, value in formatted ]

        num_columns = max(1, terminal_width // (column_width + 2))
        num_rows = (len(lines) + num_columns - 1) // num_columns  # ceiling division

        if LAYOUT == "row":
            for row in range(num_rows):
                line = ""
                for col in range(num_columns):
                    idx = row * num_columns + col
                    if idx < len(lines):
                        line += lines[idx].ljust(column_width) + COLUMN_SEPARATOR
                io.echo(line.rstrip())
        elif LAYOUT == "column":
            for row in range(num_rows):
                line = ""
                for col in range(num_columns):
                    idx = col * num_rows + row
                    if idx < len(lines):
                        line += lines[idx].ljust(column_width) + COLUMN_SEPARATOR
                io.echo(line.rstrip())
        else:
            raise ValueError("valid layouts are 'column' and 'row'")

    def adjust(self):
        # io.echo(f"empyre.Player.adjust.100: {self.grain=} {self.land=}", level="debug")
        if self.grain < 0:
            io.echo("less than zero bushels of grain. glitch corrected.")
            self.grain = 0

        soldierpay = (self.soldiers*(self.combatvictorycount+2))+(self.taxrate*self.palaces*10)//40 # py

        a = 0
        if soldierpay < 1 and soldiers >= 500:
            io.echo("soldierpay < 1, soldiers >= 500", level="debug")
            a += soldiers//5
            io.echo("adjust.100: a=%d soldiers=%d" % (a, soldiers), level="debug")
#        io.echo("adjust.160: a=%d" % (a), level="debug")

        if self.nobles < 1:
            io.echo("You have no nobles!")
            self.nobles = 0
            a += self.soldiers
            self.soldiers = 0

        if self.soldiers < 1:
            self.soldiers = 0
            io.echo("You have no soldiers!")

        soldierres = self.getresource("soldiers")
        if self.soldiers > (self.nobles*SOLDIERSPERNOBLE)+1:
            a +=  abs(self.nobles*SOLDIERSPERNOBLE - self.soldiers)
            io.echo(f"Not enough nobles for your {util.pluralize(soldiers, **soldierres)}!") # "soldier", "soldiers", emoji=":military-helmet:")))
        self.soldiers -= a
#        ttyio.echo("adjust.180: a=%d" % (a), level="debug")

        if a > 0:
            io.echo("{valuecolor}{util.pluralize(a, 'soldier deserts', 'soldiers desert', **soldierres)}{/all}{labelcolor} your army")

        if self.land < 0:
            landres = player.getresource("land")
            io.echo(f"You lost {util.pluralize(abs(self.land), **landres)}.")
            self.land = 0

        if self.land == 0:
            io.echo("You have no land!")

        shipyardsres = self.getresource("shipyards")
        shipres = self.getresource("ships")
        shipsisare = self.getresource("ships", singular="ship is", plural="ships are")

        if self.shipyards > libship.MAXSHIPYARDS: # > 400
            a = int(self.shipyards / 1.1)
            io.echo(f"{{labelcolor}}Your kingdom cannot support {{valuecolor}}{util.pluralize(self.shipyards, **shipyardsres)}{{labelcolor}}! {{valuecolor}}{util.pluralize(self.shipyards, singular='shipyard is', plural='shipyards are', **shipyardsres)}{{labelcolor}} closed.{{/all}}")
            self.shipyards -= a

        if self.shipyards == 0:
            if self.ships > 0:
                io.echo(f"{{normalcolor}}You do not have enough shipyards! {{valuecolor}}{util.pluralize(self.ships, **shipsisare)}{{normalcolor}} scrapped.")
                diff = self.ships - self.shipyards*libship.SHIPSPERSHIPYARD
                self.ships -= diff
        # take away the ship if there isn't enough shipyard capacity
        if self.ships > self.shipyards*libship.SHIPSPERSHIPYARD:
            a = self.ships - self.shipyards*libship.SHIPSPERSHIPYARD
            io.echo(f"{{normalcolor}}Your {{valuecolor}}{util.pluralize(self.shipyards, **shipyardsres)}{{normalcolor}} cannot support {{valuecolor}}{util.pluralize(self.ships, **shipres)}{{normalcolor}}, {{normalcolor}} {{valuecolor}}{util.pluralize(a, **shipsisare)} {{normalcolor}} scrapped.")
            self.ships -= a

        coinsres = self.getresource("coins")

        # if pn>1e6 then a%=pn/1.5:pn=pn-a%:&"{f6}{lt. blue}You pay {lt. green}${pound}%f {lt. blue}to the monks for this{f6}year's provisions for your subjects' survival.{f6}"

#        io.echo(f"{self.resources['coins']['value']=} {self.coins=}", level="debug")
        if self.coins > MAXCOINS:
            a = int(self.coins / 1.5)
            self.coins -= a
            io.echo(f"{{normalcolor}}You donate {{valuecolor}}{util.pluralize(a, **coinsres)}{{normalcolor}} to the monks.")

        if self.coins < 0:
            io.echo(f"{{normalcolor}}You lost your last {{valuecolor}}{util.pluralize(abs(self.coins), **coinsres)}{{normalcolor}}.")
            self.coins = 0

        landres = self.getresource("land")
        if self.land > MAXLAND:
            a = int(self.land / 2.5)
            self.land -= a
            io.echo(f"{{normalcolor}}You donate {{valuecolor}}{util.pluralize(a, **landres)}{{normalcolor}} to the monks.")

        if self.foundries > MAXFOUNDRIES:
            a = self.foundries // 3
            self.foundries -= a
            io.echo(f"{{green}}{{empyre.highlightcolor}} MAJOR EXPLOSION! {{/all}}{{valuecolor}}{util.pluralize(a, 'foundry is', 'foundries are', **foundryres)} destroyed.")

        marketres = self.getresource("markets", singular="market is", plural="markets are")
        if self.markets > MAXMARKETS:
            a = self.markets // 5
            self.markets -= a
            io.echo(f"{{red}}Some market owners retire; {util.pluralize(a, **marketres)} closed.")

        if self.mills > MAXMILLS:
            a = self.mills // 4
            self.mills -= a
            millres = player.getresource("mills")
            if a == 1:
                io.echo(f"{{normalcolor}}The mill is overworked! {util.pluralize(a, 'The mill has a broken millstone and is closed', '', quantity=False, **millres)}")
            else:
                io.echo(f"{{normalcolor}}The mills are overworked! {util.pluralize(a, '', 'mills have broken millstones and are closed', **millres)}")
#            io.echo("{green}The mills are overworked! {util.pluralize(a, 'mill has a broken millstone and is closed', 'mills have broken millstones and are closed', **millres)} and are closed.{/all}")

        if self.coins < 0:
            io.echo(f"{lightred}You are overdrawn by {util.pluralize(abs(self.coins), **coinres)}")
            self.coins = 1

        horseres = self.getresource("horses")
        stableres = self.getresource("stables")
        if self.horses > self.stables*HORSESPERSTABLE:
            a = self.horses - self.stables*HORSESPERSTABLE
            io.echo(f"{{valuecolor}}{util.pluralize(self.stables, **stableres)}{{labelcolor}} is not enough for {{valuecolor}}{util.pluralize(self.horses, **horseres)}{{labelcolor}}, {{valuecolor}}{util.pluralize(a, **horseres)}{{labelcolor}} set free.")
            self.horses -= a

        lost = []
        for name, data in self.resources.items():
            value = data.get("value", data.get("default", None))
            if isinstance(value, int) is False:
                continue
            # ttyio.echo("player.adjust.100: name=%r" % (name), level="debug")
            if value < 0:
                lost.append(util.pluralize(abs(val), data.get("singular", "FIXME"), data.get("plural", "FIXME")))
                setattr(player, name, 0)

        if len(lost) > 0:
            io.echo(f"You have lost {util.oxfordcomma(lost)}")

        self.previousrank = self.rank
        self.rank = calculaterank(self.args, self)

        if self.serfs < 100:
            self.beheaded = True
            io.echo("{normalcolor}You haven't enough serfs to maintain the empyre! It's turned over to King George and you are {highlightcolor}beheaded{normalcolor}.{/all}")

        return

class completePlayerName(object):
    def __init__(self, args):
        self.args = args
        self.matches = []
        self.debug = args.debug if "debug" in args else False

    def complete(self:object, text:str, state:int):
        dbh = database.connect(self.args)

        vocab = []
        sql:str = "select name from empyre.player"
        dat:tuple = ()
        cur = dbh.cursor()
        cur.execute(sql, dat)
        for rec in database.resultiter(cur):
            vocab.append(rec["name"])
        results = [x for x in vocab if x.startswith(text)] + [None]
        return results[state]

def verifyPlayerNameFound(name:str, **kwargs:dict) -> bool:
    import argparse
    args = kwargs["args"] if "args" in kwargs else Namespace()

    dbh = database.connect(args)

    cur = dbh.cursor()
    sql:str = "select 1 from empyre.player where moniker=%s"
    dat:tuple = (name,)
    cur.execute(sql, dat)
    if cur.rowcount == 0:
        return False
    return True

def verifyPlayerNameFound(moniker:str, **kwargs:dict) -> bool:
    import argparse
    args = kwargs.get("args", argparse.Namespace())
    def _work(conn):
        sql:str = "select 1 from empyre.player where moniker=%s"
        dat:tuple = (moniker,)
        with database.cursor(conn) as cur:
            cur.execute(sql, dat)
            io.echo(f"verifyPlayerNameNotFound.100: mogrify={database.mogrifysql(cur, sql, dat)}", level="debug")
            if cur.rowcount == 0:
                return False
            return True

    io.echo(f"verifyPlayerNameNotFound.120: {args=} {moniker=}", level="debug")
    pool = kwargs.get("pool", None)
    if pool is None:
        io.echo(f"empyre.player.verifyPlayerNameNotFound.160: {pool=}", level="error")
        return False

    with database.connect(args, pool=pool) as conn:
        return _work(conn)

def verifyPlayerNameNotFound(moniker:str, **kwargs:dict) -> bool:
    import argparse
    args = kwargs.get("args", argparse.Namespace())
    def _work(conn):
        sql:str = "select 1 from empyre.player where moniker=%s"
        dat:tuple = (moniker,)
        with database.cursor(conn) as cur:
            cur.execute(sql, dat)
            io.echo(f"verifyPlayerNameNotFound.100: mogrify={database.mogrifysql(cur, sql, dat)}", level="debug")
            if cur.rowcount == 0:
                return True
            return False

    io.echo(f"verifyPlayerNameNotFound.120: {args=} {moniker=}", level="debug")
    pool = kwargs.get("pool", None)
    if pool is None:
        io.echo(f"empyre.player.verifyPlayerNameNotFound.160: {pool=}", level="error")
        return False

    with database.connect(args, pool=pool) as conn:
        return _work(conn)

def build(args, rec:dict, **kwargs) -> Player:
    p = Player(args, **kwargs) # Player(args, **kwargs)
    for name, data in p.attributes.items():
        v = rec.get(name, data["default"])
        if v is None:
            v = data["default"]
        # io.echo(f"empyre.player.build.120: {name=} {v=}", level="debug")
        setattr(p, name, v)

    # io.echo(f"empyre.player.build.200: {rec=}", level="debug")

    for name, data in p.resources.items():
        v = rec["resources"].get(name, data["default"])["value"]
        if v is None:
            v = data["default"]

        setattr(p, name, v)
        io.echo(f"empyre.player.build.220: {p.foundries=}", level="debug")

    return p

def load(args, moniker:str, **kwargs) -> Player:
    def _work(conn):
        sql:str = "select * from empyre.player where moniker=%s"
        dat:tuple = (moniker,)
        
        with database.cursor(conn) as cur:
            cur.execute(sql, dat)
            if cur.rowcount == 0:
                io.echo(f"empyre.player.load.300: {moniker=} not found", level="info")
                return None

            rec = cur.fetchone()
            io.echo(f"empyre.player.load.320: {rec['resources']['foundries']['value']=}", level="debug")
            p = build(args, rec, **kwargs)
            io.echo(f"empyre.player.load.340: {p.foundries=}", level="debug")
            p.sync()
            io.echo(f"empyre.player.load.360: {p.foundries=}", level="debug")
            return p
        
    pool = kwargs.get("pool", None)
    if pool is None:
        io.echo(f"empyre.player.load.500: {pool=}", level="error")
        return False

    with database.connect(args, pool=pool) as conn:
        return _work(conn)

#def update(self, moniker, player, **kwargs):
#    def _work(conn):
#        for name in self.resources.keys():
#            v = getattr(self, name)
#            player.setresourcevalue(name, v)
#
#        p = {}
#        for attr in ("moniker", "membermoniker", "rank", "previousrank", "turncount", "soldierpromotioncount", "datepromoted", "combatvictorycount", "weatherconditions", "beheaded", "datelastplayed", "coins", "taxrate", "resources"):
#            p[attr] = getattr(player, attr)
#
#        return database.update(self.args, "empyre.__player", moniker, p, primarykey="moniker", conn=conn)
#
#    conn = kwargs.get("conn", None)
#    if conn is None:
#        pool = kwargs.get("pool", None)
#        if pool is None:
#            io.echo(f"empyre.player.update.200: {pool=}", level="error")
#            return False
#        with database.connect(pool=pool) as conn:
#            return _work(conn)
#    else:
#        return _work(conn)

def select(args, title:str="select player", prompt:str="player: ", membermoniker:str=None, **kwargs) -> Player:
    pool = kwargs.get("pool", None)
    if pool is None:
        io.echo(f"empyre.player.select.300: {pool=}", level="error")

    class EmpyrePlayerListbox(listbox.Listbox):
        def __init__(self, args, **kwargs):
            self.cur = kwargs.get("cur", None)
            self.pool = kwargs.get("pool", None)
            io.echo(f"player.EmpyrePlayerListbox.100: {self.cur=} {self.pool=}", level="debug")
            super().__init__(args, **kwargs)

        def fetchpage(self):
            if self.cur is None:
                io.echo(f"bbsengine.listbox.Listbox.fetchpage.200: {cur=}", level="error")
                return None
            self.cur.scroll(self.page*self.pagesize, mode="absolute")
            self.items = []
            for rec in self.cur.fetchmany(self.pagesize):
                self.items.append(EmpyrePlayerListboxItem(rec, pool=self.pool))
            self.numitems = len(self.items)
            return self.items

    class EmpyrePlayerListboxItem(listbox.ListboxItem):
        def __init__(self, rec:dict, **kwargs):
            self.pool = kwargs.get("pool", None)
            # io.echo(f"empyre.lib.EmpyreListboxItem.200: {kwargs=}", level="debug")
            width = kwargs.get("width", io.terminal.width())
            height = 1
            super().__init__(self, width, height, **kwargs)
            # io.echo(f"empyre.player.EmpyrePlayerListboxItem.300: {rec=}", level="debug")
            self.player = load(args, rec["moniker"], **kwargs)
            if self.player is None:
                io.echo(f"empyre.player.select.240: {self.player=}", level="error")
                return

            landres = self.player.getresource("land")
            if "emoji" in landres:
                landres["emoji"] = ""

            acres = landres["value"] if "value" in landres else 0

            left:str = f"{self.player.moniker}"
            lastplayed:str = util.datestamp(self.player.datelastplayedlocal, format="%m/%d @ %I%M%P")
            right:str = f"{util.pluralize(acres, **landres)} {lastplayed}"
            rightlen:int = len(right)
            self.label:str = f"{left.ljust(width-rightlen-10)}{right}" # %s%s {{/all}}{{var:acscolor}}{{acs:vline}}" % (left.ljust(width-rightlen-4), right)

            self.status = ""
            self.pk:str = self.player.moniker
            self.rec:dict = rec
            self.width:int = width
        def help(self):
            io.echo(f"{{var:labelcolor}}use {{var:valuecolor}}KEY_ENTER{{var:labelcolor}} to select one of your players")
            return

        def display(self):
            io.echo(f"{{/all}}{{cha}} {{engine.menu.cursorcolor}}{{engine.menu.color}} {{engine.menu.boxcharcolor}}{{acs:vline}}{{cic}} {self.label.ljust(self.width-9, ' ')} {{/all}}{{engine.menu.boxcharcolor}}{{acs:vline}}{{engine.menu.shadowcolor}} {{engine.menu.color}} {{/all}}{{cha}}", end="", flush=True)
            return

    def empyreplayerkeyhandler(args, ch:str, lb:listbox.Listbox) -> bool:
        io.echo("inside empyreplayerkeyhandler")
        currentitem = lb.currentitem
        if ch == "KEY_ENTER":
            io.setvar("cic", "{currentitemcolor}")
            currentitem.display()
            io.echo(f"{restorecursor}{currentitem.player.moniker}", end="", flush=True)
            return False
        elif ch == "KEY_INS":
            io.echo("{restorecursor}add player")
            return False

    with database.connect(args, pool=pool) as conn:
        io.echo(f"selectplayer.100: {conn=} {membermoniker=}", level="debug")

        if membermoniker is None:
            membermoniker = member.getcurrentmoniker(args, conn=conn)
        io.echo(f"empyre.player.select.220: {membermoniker=}", level="debug")

        sql:str = "select moniker from empyre.player where membermoniker=%s order by datelastplayed desc"
        dat:tuple = (membermoniker,)

        totalitems = count(args, membermoniker, conn=conn)
        with database.cursor(conn) as cur:
            if args.debug is True:
                io.echo(f"getplayer.110: {database.mogrifysql(cur, sql, dat)=}", level="debug")
            cur.execute(sql, dat)
            if cur.rowcount == 0:
                io.echo("no player record.")
                return None

            lb = EmpyrePlayerListbox(args, title=title, keyhandler=None, totalitems=totalitems, cur=cur, **kwargs)
            op = lb.run(prompt)
            if op.kind == "select":
                io.echo(f"{op.listitem.player.moniker}")
                return op.listitem.player
            elif op.kind == "exit":
                return None

def count(args, membermoniker:str, **kwargs) -> int:
    def _work(conn):
        sql:str = "select count(moniker) from empyre.player where membermoniker=%s"
        dat:tuple = (membermoniker,)
        with database.cursor(conn) as cur:
            cur.execute(sql, dat)
            if cur.rowcount == 0:
                io.echo(f"empyre.player.count.160: returning None", level="debug")
                return None
            rec = cur.fetchone()
            count = rec["count"] if rec["count"] > 0 else None
            io.echo(f"empyre.player.count.120: {count=}", level="error")
            return count
    
    conn = kwargs.get("conn", None)
    if conn is None:
        io.echo(f"empyre.player.count.140: {conn=}", level="error")
        pool = kwargs.get("pool", None)
        if pool is None:
            io.echo(f"empyre.player.count.160: {pool=}")
            return None
        conn = database.connect(args, pool=pool)
        with conn:
            return _work(conn)
    else:
        return _work(conn)

def inputplayername(prompt:str="player name: ", oldvalue:str="", **kwargs:dict):
    multiple:bool = kwargs.get("multiple", False)
    args = kwargs["args"] if "args" in kwargs else argparse.Namespace()
    noneok:bool = kwargs.get("noneok", True)
    verify = kwargs.pop("verify", verifyPlayerNameFound)
    name = io.inputstring(prompt, oldvalue, verify=verify, completer=completePlayerName(args), completerdelims="", **kwargs)
    io.echo(f"inputplayername.160: {name=}", level="debug")
    return name

def create(args, **kwargs):
    pool = kwargs.get("pool", None)
    if pool is None:
        io.echo("empyre.player.create.140: {pool=}", level="error")
        return False
    def _work(conn, playermoniker, membermoniker) -> str:
        p = Player(args, pool=pool)
        p.moniker = playermoniker
        p.membermoniker = membermoniker
        p.datecreated = "now()"

        io.echo(f"empyre.player.create.100: {p.attributes=}", level="debug")
        rec = p.buildrec()
        rec["moniker"] = playermoniker
        rec["membermoniker"] = membermoniker
        rec["datecreated"] = "now()"
        io.echo(f"{rec=}", level="debug")

        database.insert(args, "empyre.__player", rec, primarykey="moniker", mogrify=True, conn=conn)
        return p

#    io.echo(f"player.new.100: {currentmembermoniker=}", level="debug")

    currentmembermoniker = member.getcurrentmoniker(args, **kwargs)
    playermoniker = inputplayername("new player moniker: ", currentmembermoniker, verify=verifyPlayerNameNotFound, multiple=False, args=args, returnseq=False, **kwargs)
    if playermoniker == "":
        io.echo("aborted.")
        return None

    try:
        conn = kwargs.get("conn", None)
        if conn is None:
            pool = kwargs.get("pool", None)
            if pool is None:
                io.echo(f"empyre.lib.create.140: {pool=}", level="error")
                return False
            with database.connect(args, pool=pool) as conn:
                return _work(conn, playermoniker, currentmembermoniker)
        else:
            return _work(conn, playermoniker, currentmembermoniker)
    except Exception as e:
        io.echo(f"empyre.lib.create.100: exception {e}", level="error")
        raise

    io.echo(f"player.create.100: {self.moniker=}", level="debug")
    return p

def generate(self, rank=0):
    # http://donjon.bin.sh/fantasy/name/#type=me;me=english_male -- ty ryan
    #        namelist = ("Richye", "Gerey", "Andrew", "Ryany", "Mathye Burne", "Enryn", "Andes", "Piersym Jordye", "Vyncis", "Gery Aryn", "Hone Sharcey", "Kater", "Erix", "Abell", "Wene Noke", "Jane Folcey", "Abel", "Bilia", "Cilia", "Joycie")
    self.moniker = generatename(self.args) # namelist[random.randint(0, len(namelist)-1)]
    if rank == 1:
        self.markets = random.randint(10, 15)
        self.mills = random.randint(6, 9)
        self.diplomats = random.randint(1, 2)
        # self.serfs = random.randint()
    return

def getranktitle(args, rank:int):
    if args.debug is True:
        io.echo("getranktitle.100: rank=%r" % (rank), level="debug")
    if rank == 0:
        return "lord"
    elif rank == 1:
        return "prince"
    elif rank == 2:
        return "king"
    elif rank == 3:
        return "emperor"
    return "rank-error"

def calculaterank(args:object, player:Player) -> int:
    #i1=f%(1) palaces
    #i2=f%(2) markets
    #i3=f%(3) mills
    #i4=f%(4) foundries
    #i5=f%(5) shipyards
    #i6=f%(6) diplomats

    rank = 0

    if (player.markets > 23 and
        player.mills >= 10 and
        player.foundries > 13 and
        player.shipyards > 11 and
        player.palaces > 9 and
        player.land / player.serfs > 23.4 and
        player.serfs >= 2500): # b? > 62
            rank = 3 # emperor
    elif (player.markets > 15 and
        player.mills >= 10 and
        player.diplomats > 2 and
        player.foundries > 6 and
        player.shipyards > 4 and
        player.palaces > 6 and
        player.land / player.serfs > 10.5 and
        player.serfs > 3500 and
        player.nobles > 30):
            rank = 2 # king
    elif (player.markets >= 10 and
        player.diplomats > 0 and
        player.mills > 5 and
        player.foundries > 1 and
        player.shipyards > 1 and
        player.palaces > 2 and
        player.land / player.serfs > 5.1 and
        player.nobles > 15 and
        player.serfs > 3000):
            rank = 1 # prince

    return rank
