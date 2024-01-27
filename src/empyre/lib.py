import copy
import math
import random
import argparse
from argparse import Namespace

from enum import Enum

class ShipKind(str, Enum):
    PASSENGER = "passenger"
    CARGO = "cargo"

# from dateutil.tz import tzlocal

#import ttyio6 as ttyio
#import bbsengine6 as bbsengine
from bbsengine6 import io, member, database, util, screen, blurb, module, listbox

TURNSPERDAY = 4
PACKAGENAME = "empyre"

class Island(object):
    def __init__(self, args):
        self.args = args
        self.playerid = None
        self.memberid = None
        self.trees = 500

class Colony(object):
    def __init__(self, args):
        self.args = args

class Player(object):
    def __init__(self, args):
        self.playerid = None
        self.moniker = None # member moniker by default
        self.memberid = member.getcurrentid(args)
        self.args = args
        self.rank = 0
        self.previousrank = 0
        self.turncount = 0
        self.soldierpromotioncount = 0
        self.datepromoted = None
        self.combatvictorycount = 0
        self.weatherconditions = 0
        self.beheaded = False
        self.datelastplayed = "now()"
        self.coins = 250000
        self.taxrate = 15
        self.training = 1 # z9
        #self.acres = 5000 # la
        #self.soldiers = 20 # wa
#        self.serfs = 2000+random.randint(0, 200) # sf
#        self.nobles = 2 # nb
#        self.grain = 10000 # gr
#        self.taxrate = 15 # tr
#        self.coins = 1000 # pn
#        self.palaces = 0 # f%(1) 0
#        self.markets = 0 # f%(2) 0
#        self.mills = 0 # f%(3) 0
#        self.foundries = 2 # f%(4) 0
#        self.shipyards = 0 # f%(5) 0 or yc
#        self.diplomats = 0 # f%(6) 0
#        self.ships = 0 # yc?
#        self.colonies = 0 # i8

        # @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/mdl.emp.delx2.txt#L25
        currentmoniker = member.getcurrentmoniker(args)
        self.resources = [
            {"type": "int",  "name": "serfs",      "default":2000+random.randint(0, 200), "ship":"passenger"}, # sf x(19)
            {"type": "int",  "name": "land",       "default":5000, "singular":"acre", "plural":"acres", "ship":None}, # la x(2)
            {"type": "int",  "name": "grain",      "default":20000, "singular": "bushel", "plural": "bushels", "emoji":":crop:", "ship":"cargo"}, # gr
            {"type": "int",  "name": "soldiers",   "default":40, "price":20, "singular":"soldier", "plural":"soldiers", "ship":"millitary passenger"},
            {"type": "int",  "name": "nobles",     "default":3, "price":25000, "singular":"noble", "plural":"nobles", "ship":"passenger"}, # x(6)
            {"type": "int",  "name": "palaces",    "default":1, "price":20, "singular":"palace", "plural":"palaces", "ship":None}, # f%(1)
            {"type": "int",  "name": "markets",    "default":1, "price":1000, "singular":"market", "plural":"markets", "ship":None}, # f%(2) x(7)
            {"type": "int",  "name": "mills",      "default":1, "price":2000, "singular":"mill", "plural":"mills", "ship":None}, # f%(3) x(8)
            {"type": "int",  "name": "foundries",  "default":2, "price":7000, "singular":"foundry", "plural":"foundries", "ship":None}, # f%(4) x(9)
            {"type": "int",  "name": "shipyards",  "default":0, "price":8000, "singular":"shipyard", "plural":"shipyards", "ship":None}, # yc or f%(5)? x(10)
            {"type": "int",  "name": "diplomats",  "default":0, "price":50000, "singular":"diplomat", "plural":"diplomats", "ship":"passenger millitary"}, # f%(6) 0
            {"type": "int",  "name": "ships",      "default":0, "price":5000, "singular":"ship", "plural":"ships", "emoji":":anchor:", "ship":None}, # 5000 each, yc? x(12)
            {"type": "int",  "name": "navigators", "default":0, "price":500, "singular": "navigator", "plural": "navigators", "emoji":":compass:"}, # @since 20220907
            {"type": "int",  "name": "stables",    "default":1, "price":10000, "singular": "stable", "plural":"stables", "ship":None}, # x(11)
            {"type": "int",  "name": "colonies",   "default":0, "ship":None}, # i8
            {"type": "int",  "name": "warriors",   "default":0, "ship":"millitary passenger"}, # wa soldier -> warrior or noble?
            {"type": "int",  "name": "spices",     "default":0, "ship":"cargo"}, # x(25)
            {"type": "int",  "name": "cannons",    "default":0, "ship":"millitary"}, # x(14)
            {"type": "int",  "name": "forts",      "default":0, "ship":None}, # x(13)
            {"type": "int",  "name": "dragons",    "default":0, "emoji":":dragon:"},
            {"type": "int",  "name": "horses",     "default":50,"emoji":":horse:", "ship":"cargo", "singular":"horse", "plural":"horses"}, # x(23)
            {"type": "int",  "name": "timber",     "default":0, "emoji":":wood:", "ship":"cargo"}, # x(16)
            {"type": "int",  "name": "rebels",     "default":0, "ship":None},
            {"type": "int",  "name": "exports",    "default":0, "emoji": ":package:"},
        ]

        for a in self.resources:
            setattr(self, a["name"], a["default"])

#        if self.playerid is not None:
#            ttyio.echo("Player.__init__.100: calling load()", level="debug")
#            self.load(self.playerid)

#        tz=0:i1=self.palaces:i2=self.markets:i3=self.mills:i4=self.foundries:i5=self.shipyards:i6=self.diplomats
    def getresource(self, name):
#        ttyio.echo("getattribute.100: name=%s" % (name))
        for r in self.resources:
            if r["name"] == name:
                v = getattr(self, name)
                if r["type"] == "int":
                    v = int(v)
                r["value"] = v
                if "emoji" not in r:
                    r["emoji"] = ""
                return r
        return None

    def setresource(self, name, value):
        for a in self.resources:
            io.echo("player.setresource.120: name=%r" % (a["name"]), level="debug")
            if a["name"] == name:
                if a["type"] == "int":
                    value = int(value)
                a["value"] = value
                io.echo("player.setresource.100: name=%r value=%r" % (a["name"], value))
                break
        return

#    def __setattr__(self, name, value):
#        ttyio.echo("setattr: name=%s value=%s" % (name, value), level="debug")
#        ttyio.echo("attributes=%r" % (self.attributes), level="debug")
#        for a in self.attributes:
#            ttyio.echo("player.setattribute.120: name=%r" % (a["name"]), level="debug")
#            if a["name"] == name:
#                if a["type"] == "int":
#                    value = int(value)
#                a["value"] = value
#                ttyio.echo("player.setattribute.100: name=%r value=%r" % (a["name"], value))
#                break
#        return

#    def remove(self):
#        self.memberid = None
#        return
 
    def verifyPlayerResourceName(self, name:str, **kw):
        for r in self.resources:
            n = r["name"]
            if n == name:
                return True
        return False

    # @since 20200901
    # @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_maint.lbl#L22
    def edit(self):
        done = False
        while not done:
            setarea(self.args, self, "edit player resources")
            attrname = inputresourcename(self.args, "resource: ", multiple=False, noneok=True, attrs=self.resources, verify=self.verifyPlayerResourceName)
            io.echo("attrname=%r" % (attrname), level="debug")
            if attrname is None or attrname == "":
                done = True
                break

            a = self.getresource(attrname)
            if a is None:
                io.echo("unknown resource %r." % (attrname), level="error")
                continue

            n = a["name"]
            t = a["type"] if "type" in a else "int"
            v = a["value"] if "value" in a else None
            if t == "playername":
                x = inputplayername(f"{n} (playername): ", v, args=self.args, verify=verifyPlayerNameNotFound, name=name)
                io.echo("player.edit.100: playername=%r" % (x), level="debug")
#                if x is not None:
#                    x = getplayerid(args, playername)
            elif t == "epoch":
                x = input.date("%s (date): " % (n), v)
            elif t == "int":
                x = io.inputinteger("%s (int): " % (n), v)
            elif t == "bool":
                if v is True:
                    default = "Y"
                    prompt = "%s (bool)? [{var:engine.currentoptioncolor}Y{/all}n]: "
                elif v is False:
                    default = "N"
                    prompt = "%s (bool)? [y{var:engine.currentoptioncolor}N{/all}]: "
                x = io.inputboolean(prompt % (n), default)
            else:
                io.echo("invalid resource type for n=%r t=%r" % (n, t), level="error")
                return
            setattr(self, n, x)
            io.echo("player.edit.120: n=%r x=%r" % (n, x), level="debug")
            self.setresource(n, x)
            io.echo("player.edit.140: %s=%r" % (n, self.getresource(n)["value"]), level="debug")

        return

    def load(self, playerid:int):
        if self.args.debug is True:
            io.echo("player.load.100: playerid=%r" % (playerid), level="debug")
        dbh = database.connect(self.args)
        sql = "select * from empyre.player where id=%s"
        dat = (playerid,)
        cur = dbh.cursor()
        cur.execute(sql, dat)
        rec = cur.fetchone()

        if self.args.debug is True:
            io.echo(f"player.load.120: {rec=}", level="debug") # strip=True, interpret=False)

        if rec is None:
            return False

        for attr in ("moniker", "memberid", "rank", "previousrank", "turncount", "soldierpromotioncount", "datepromoted", "combatvictorycount", "weatherconditions", "beheaded", "datelastplayed", "coins", "taxrate", "training"):
            if attr in rec:
                setattr(self, attr, rec[attr])
        self.playerid = playerid
#        self.playerid = playerid
#        self.moniker = res["moniker"]

        resources = rec["resources"] if "resources" in rec else {}
        if self.args.debug is True:
            io.echo(f"{resources=}", level="debug")

        for a in self.resources:
            name = a["name"]
            default = a["default"]

            if name not in resources:
                if self.args.debug is True:
                    io.echo(f"name {name} not in database record", level="warning")
                value = default
            else:
                value = resources[name]

            if self.args.debug is True:
                io.echo("player.load.140: {name=} {default=} {value=}", level="debug")
            setattr(self, name, value)

        
#        newsentry(self.args, self, f"player {self.moniker} loaded.")

        return True

    def update(self):
        if self.playerid < 1:
            io.echo("invalid playerid passed to Player.update.", level="error")
            return False

        resources = {}
        for a in self.resources:
            name = a["name"]
            res = self.getresource(name)
            if res is None:
                io.echo(f"invalid resource {name=}")
                continue
            if res["type"] == "datetime":
#                tz = tzlocal()
                resources[name] = res["value"]
            else:
                resources[name] = res["value"] # self.getattribute(name) # getattr(self, name)

        player = {}
        player["resources"] = resources

        for attr in ("moniker", "memberid", "rank", "previousrank", "turncount", "soldierpromotioncount", "datepromoted", "combatvictorycount", "weatherconditions", "beheaded", "datelastplayed", "coins", "taxrate", "training"):
            if attr in res:
                player[attr] = getattr(self, attr)
#        player["playerid"] = self.playerid

#        player["datelastplayed"] = self.datelastplayed
#        player["rank"] = self.rank
#        player["previousrank"] = self.previousrank
#        player["turncount"] = self.turncount
#        player["weatherconditions"] = self.weatherconditions
#        player["soldierpromotioncount"] = self.soldierpromotioncount
#        player["combatvictorycount"] = self.combatvictorycount
#        player["datepromoted"] = self.datepromoted
#        player["coins"] = self.coins

        return database.update(self.args, "empyre.__player", self.playerid, player)
#        return bbsengine.blurb.updateattributes(self.args, self.playerid, attributes)

    def isdirty(self):
        def getattrval(name):
            for r in self.resources:
                if r["name"] == name:
                    return r["value"] if "value" in r else r["default"]

        for r in self.resources:
            name = r["name"]
            curval = getattr(self, name)
            oldval = getattrval(name)
            if self.args.debug is True:
                io.echo(f"{name=} {curval=} {oldval=}", level="debug")
            if curval != oldval:
                if "debug" in self.args and self.args.debug is True:
                    io.echo("player.isdirty.100: name=%r oldval=%r curval=%r" % (name, oldval, curval), level="debug")
                return True
        return False

    def save(self):
        if self.args.debug is True:
            io.echo("player.save.100: playerid=%r" % (self.playerid), level="debug")
        if self.playerid is None:
            io.echo("player id is not set. aborted.", level="error")
            return None

        if self.memberid is None:
            io.echo("memberid is not set. aborted.", level="error")
            return None

#        if ttyio.inputboolean("continue to save? [Yn]: ", "Y") is False:
#            ttyio.echo("save aborted")
#            return

        if self.isdirty() is False:
            if "debug" in self.args and self.args.debug is True:
                io.echo("%s: clean. no save." % (self.moniker))
            return
        io.echo(f"{self.moniker}: dirty. saving.")

        self.update()
        database.commit(self.args)
        return

    def insert(self):
        resources = {}
        for r in self.resources:
            name = r["name"]
            attr = self.getresource(name)
            value = attr["value"]
            io.echo(f"player.insert.100: resources {name=} {value=}", level="debug")
            resources[name] = value

#        ttyio.echo(f"{resources.name=}", level="debug")

        player = {}
        player["resources"] = resources
        player["datelastplayed"] = self.datelastplayed
        player["rank"] = self.rank
        player["previousrank"] = self.previousrank
        player["turncount"] = self.turncount
        player["weatherconditions"] = self.weatherconditions
        player["soldierpromotioncount"] = self.soldierpromotioncount
        player["combatvictorycount"] = self.combatvictorycount
        player["datepromoted"] = self.datepromoted
        player["coins"] = self.coins
        player["moniker"] = self.moniker
        player["memberid"] = self.memberid

        player["datecreated"] = "now()"

        playerid = database.insert(self.args, "empyre.__player", player, returnid=True, mogrify=True)

        self.playerid = playerid
        io.echo(f"player.insert.100: {playerid=}", level="debug")
        return playerid


    def status(self):
        if self.args.debug is True:
            io.echo("bbsengine.member.getcurrentid()=%r" % (member.getcurrentid(self.args)), level="debug")
            io.echo(f"{player.playerid=}, {player.memberid=}, {player.moniker=}", level="debug")

        util.heading(f"player status for {self.moniker}")

        terminalwidth = io.getterminalwidth()-2

        maxwidth = 0
        maxlabellen = 0
        for a in self.resources:
            n = a["name"]
            n = n[:12] + (n[12:] and '..')
            if len(n) > maxlabellen:
                maxlabellen = len(n)
            attr = self.getresource(a["name"])
            v = attr["value"]
            # v = getattr(self, name)
            if v is not None:
                t = a["type"] if "type" in a else "int"
                # ttyio.echo("player.status.140: t=%r" % (t), level="debug")
                if t == "int":
                    # ttyio.echo("player.status.100: n=%r t=int v=%r" % (n, v), level="debug")
                    v = f"{v:>6n}"
                    # ttyio.echo("player.status.120: new v=%r" % (v), level="debug")
#                elif t == "epoch":
#                    ttyio.echo("player.status.100: v=%r" % (v), level="debug")
#                    if v < 1:
#                        v = "None"
#                    else:
#                        v = bbsengine.util.datestamp(v, format="%Y%m%d")
                elif t == "datetime":
#                    io.echo(f"---> player.status.120: {v=} {type(v)=}", level="debug")
                    v = util.datestamp(v, format="%m/%d@%H%M%P%Z")
                    io.echo(f"{v=}", level="debug")

            buf = "%s: %s" % (n.ljust(maxlabellen), v)
            buflen = len(io.tostr(buf))
            if buflen > maxwidth:
                maxwidth = buflen
#                io.echo(f"player.status.160: {maxwidth=} {buflen=}", level="debug")
#        ttyio.echo(f"terminalwidth={terminalwidth} maxwidth={maxwidth}", level="debug")
        columns = math.floor(terminalwidth / maxwidth)
        if columns < 1:
            columns = 1
#        ttyio.echo("columns=%d" % (columns), level="debug")

        currentcolumn = 0
        for a in self.resources:
            n = a["name"]
            # https://stackoverflow.com/questions/2872512/python-truncate-a-long-string
            n = n[:12] + (n[12:] and '..')

            attr  = self.getresource(a["name"]) # getattr(self, a["name"])
            v = attr["value"]
            if v is not None:
                t = a["type"] if "type" in a else "int"
                if t == "int":
                    # ttyio.echo("player.status.100: v=%r" % (v), level="debug")
                    v = "{:>6n}".format(int(v))
                    # ttyio.echo("player.status.120: v=%r" % (v), level="debug")
                elif t == "epoch":
                    if v < 1:
                        v = "None"
                    else:
                        v = "%s" % (util.datestamp(v))
                elif t == "datetime":
                    v = util.datestamp(v, format="%m/%d@%I%M%P%Z")

            if a["name"] == "soldiers" and self.nobles*20 < self.soldiers:
                buf = f"{{var:labelcolor}}{n.ljust(maxlabellen)}: {{var:highlightcolor}}{v}{{var:normalcolor}}" # % (n.ljust(maxlabellen), v)
            elif a["name"] == "horses" and self.stables*5 < self.horses:
                buf = f"{{var:labelcolor}}{n.ljust(maxlabellen)}: {{var:highlightcolor}}{v}{{var:normalcolor}}" # % (n.ljust(maxlabellen), v)
            else:
                buf = f"{{var:labelcolor}}{n.ljust(maxlabellen)}: {{var:valuecolor}}{v}{{var:normalcolor}}" # % (n.ljust(maxlabellen), v)

            buflen = len(io.tostr(buf, strip=True)) # ttyio.interpret(buf, strip=True, wordwrap=False))
            if currentcolumn == columns-1:
                io.echo("%s" % (buf))
            else:
                io.echo(" %s%s " % (buf, " "*(maxwidth-buflen)), end="")

            currentcolumn += 1
            currentcolumn = currentcolumn % columns
        io.echo()
        return
        
        #ttyio.echo("acres     : %s" % (currentplayer.acres))
        #ttyio.echo("credits   : %s" % (currentplayer.credits))
        #ttyio.echo("grain     : %s" % (currentplayer.grain))
        #ttyio.echo("tax rate  : %s" % (currentplayer.taxrate))
        #ttyio.echo("soldiers  : %s" % (currentplayer.soldiers))
        #ttyio.echo("nobles    : %s" % (currentplayer.nobles))
        #ttyio.echo("palaces   : %s" % (currentplayer.palaces))
        #ttyio.echo("markets   : %s" % (currentplayer.markets))
        #ttyio.echo("mills     : %s" % (currentplayer.mills))
        #ttyio.echo("foundries : %s" % (currentplayer.foundries))
        #ttyio.echo("diplomats : %s" % (currentplayer.diplomats))
        #ttyio.echo("ships     : %s" % (currentplayer.ships))
        #ttyio.echo("colonies  : %s" % (currentplayer.colonies))
        #ttyio.echo("training  : %s" % (currentplayer.training))
        return

    #a=fn r(300)+2000:w$=na$+r$+"5000"+r$+"20"+r$+str$(a)+r$+"2"
    #	w$=w$+r$+"10000"+r$+"15"+r$+"1000"+r$+"0"+r$+"0"+r$+"0"+r$+"0"+r$+"0"+r$+"0"
    #	w$=w$+r$+"0"+r$+"0"+r$+"1":x=g3:gosub 1001:print# 2,w$:&"{f6:2}{lt. blue}OK, all set..." ':gosub 1001:&,2,2
                
            # &"{f6:2}{cyan}{pound}v2 (#"+str$(g3)+"{f6}{lt. green}":j=. na, playerid
            # &"{f6}Land     : ":x=la:gosub {:sub.comma_value}:&" acres" 5000
            # &"{f6}Money    :$":x=pn:gosub {:sub.comma_value} 20
            # &"{f6}Grain    : ":x=gr:gosub {:sub.comma_value}:&" bushels" 2000+rnd(300)
            # &"{f6}Tax rate : ":x=tr:gosub {:sub.comma_value}:&"%" 15
            # &"{f6}Soldiers : ":x=wa:gosub {:sub.comma_value} 1000
            # &"{f6}Serfs    : ":x=sf:gosub {:sub.comma_value} 0
            # &"{f6}Nobles   : ":x=nb:gosub {:sub.comma_value} 0
            # &"{cyan}{f6}Palaces  : ":x=f%(1):gosub {:sub.comma_value} 0
            # &"{f6}Markets  : ":x=f%(2):gosub {:sub.comma_value} 0
            # &"{f6}Mills    : ":x=f%(3):gosub {:sub.comma_value} 0
            # &"{f6}Foundries: ":x=f%(4):gosub {:sub.comma_value} 0
            # &"{f6}Shipyards: ":x=f%(5):gosub {:sub.comma_value} 0
            # &"{f6}Diplomats: ":x=f%(6):gosub {:sub.comma_value} 0
            # &"{f6}Ships    : ":x=yc:gosub {:sub.comma_value} 0
            # &"{f6}Colonies : ":x=i8:gosub {:sub.comma_value} 0
            # &"{f6}Training : ":x=z9:gosub {:sub.comma_value} 0
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
    def adjust(self):
        soldierpay = (self.soldiers*(self.combatvictorycount+2))+(self.taxrate*self.palaces*10)//40 # py
#        ttyio.echo("adjust.140: soldierpay=%d" % (soldierpay), level="debug")

        if self.grain < 0:
            io.echo("less than zero bushels of grain. glitch corrected.")
            self.grain = 0
        # soldiers = self.soldiers
#        soldiers = ttyio.inputinteger("soldiers=", self.soldiers)

        a = 0
        if soldierpay < 1 and soldiers >= 500:
            io.echo("soldierpay < 1, soldiers >= 500", level="debug")
            a += soldiers//5
            io.echo("adjust.100: a=%d soldiers=%d" % (a, soldiers), level="debug")
        io.echo("adjust.160: a=%d" % (a), level="debug")

        if self.nobles < 1:
            io.echo("You have no nobles!")
            self.nobles = 0
            a += self.soldiers
            self.soldiers = 0

        if self.soldiers < 1:
            self.soldiers = 0
            io.echo("You have no soldiers!")

        if self.soldiers > (self.nobles*20)+1:
            a +=  abs(self.nobles*20 - soldiers)
            io.echo("Not enough nobles for your %s!" % (util.pluralize(soldiers, "soldier", "soldiers", emoji=":military-helmet:")))
        self.soldiers -= a
#        ttyio.echo("adjust.180: a=%d" % (a), level="debug")

        if a > 0:
            io.echo("{var:valuecolor}{}{/all} your army".format((util.pluralize(a, "soldier deserts", "soldiers desert", emoji=":military-helmet:"))))

        if self.land < 0:
            io.echo("You lost your last %s." % (util.pluralize(abs(self.land), "acre", "acres")))
            self.land = 0

        if self.land == 0:
            io.echo("You have no land!")

        if self.shipyards > 10: # > 400
            a = int(self.shipyards / 1.1)
            io.echo("{cyan}Your kingdom cannot support %s! %s closed.{/all}" % (util.pluralize(self.shipyards, "shipyard", "shipyards"), util.pluralize(self.shipyards, "shipyard is", "shipyards are")))
            self.shipyards -= a

        if self.shipyards == 0:
            if self.ships > 0:
                io.echo("{cyan}You do not have any shipyards! %s scrapped." % (util.pluralize(self.ships, "ship is", "ships are", emoji=":anchor:")))
                diff = self.ships - self.shipyards*10
                self.ships -= diff
        # take away the ship if there isn't enough shipyard capacity
        if self.ships > self.shipyards*10:
            a = self.ships - self.shipyards*10
            io.echo("{cyan}Your {var:empyre.highlightcolor}%s{/all} cannot support {var:empyre.highlightcolor}%s{/all}! %s scrapped{/all}" % (util.pluralize(self.shipyards, "shipyard", "shipyards"), util.pluralize(self.ships, "ship", "ships", emoji=":anchor:"), util.pluralize(a, "ship is", "ships are", emoji=":anchor:")))
            self.ships -= a

        # if pn>1e6 then a%=pn/1.5:pn=pn-a%:&"{f6}{lt. blue}You pay {lt. green}${pound}%f {lt. blue}to the monks for this{f6}year's provisions for your subjects' survival.{f6}"
        if self.coins > 1000000:
            a = int(self.coins / 1.5)
            self.coins -= a
            io.echo("{cyan}You donate {var:empyre.highlightcolor}%s{/all} to the monks." % (util.pluralize(a, "coin", "coins", emoji=":moneybag:")))

        if self.coins < 0:
            io.echo("You lost your last %s." % (util.pluralize(abs(self.coins), "coin", "coins")))
            self.coins = 0

        if self.land > 2500000:
            a = int(self.land / 2.5)
            self.land -= a
            io.echo("{cyan}You donate {var:empyre.highlightcolor}%s{/all} to the monks." % (util.pluralize(a, "acre", "acres")))

        if self.foundries > 400:
            a = self.foundries // 3
            self.foundries -= a
            io.echo("{green}{var:empyre.highlightcolor} MAJOR EXPLOSION! {/all} %s destroyed." % (util.pluralize(a, "foundry is", "foundries are")))

        if self.markets > 500:
            a = self.markets // 5
            self.markets -= a
            io.echo("{red}Some market owners retire; %s closed." % (util.pluralize(a, "market is", "markets are")))

        if self.mills > 500:
            a = self.mills // 4
            self.mills -= a
            io.echo("{green}The mills are overworked! %s mills have broken millstones and are closed.{/all}" % (util.pluralize(a, "mill has a broken millstone", "mills have broken millstones")))

        if self.coins < 0:
            io.echo("{lightred}You are overdrawn by %s!{/all}" % (util.pluralize(abs(self.coins), "coin", "coins")))
            self.coins = 1

        if self.horses > self.stables*50:
            a = self.horses - self.stables*50
            io.echo("{green}You have %s for %s, %s set free." % (util.pluralize(self.stables, "stable", "stables"), util.pluralize(self.horses, "horse", "horses", emoji=":horse:"), util.pluralize(a, "horse is", "horses are", emoji=":horse:")))
            # self.horses -= a

        lost = []
        for a in self.resources:
            type = a["type"] if "type" in a else "int"
            if type != "int":
                continue
            name = a["name"]
            # ttyio.echo("player.adjust.100: name=%r" % (name), level="debug")
            attr = self.getresource(name) # getattr(player, name)
            singular = a["singular"] if "singular" in a else "singular"
            plural = a["plural"] if "plural" in a else "plural"
            val = a["value"] if "value" in a else a["default"]
            if val < 0:
                lost.append(util.pluralize(abs(val), singular, plural))
                self.setresource(name, 0) # setattr(player, name, 0)
        if len(lost) > 0:
            io.echo("You have lost %s" % (util.oxfordcomma(lost)))

        self.rank = calculaterank(self.args, self)
        # player.save()

        return

    def revert(self):
        pass

def newplayer(args):
    util.heading("A New Player!")

    currentmemberid = member.getcurrentid(args)
    currentmembermoniker = member.getcurrentmoniker(args)
    io.echo(f"player.new.100: {currentmemberid=}, {currentmembermoniker=}", level="debug")

    playermoniker = inputplayername("new player moniker: ", currentmembermoniker, verify=verifyPlayerNameNotFound, multiple=False, args=args, returnseq=False)
    if playermoniker == "":
        io.echo("aborted.")
        return None

    player = Player(args)

    resources = {}
    for a in player.resources:
        name = a["name"]
        default = a["default"]
        resources[name] = default
        setattr(player, name, default)

    player.memberid = currentmemberid
    player.moniker = playermoniker

    io.echo(f"empyre.lib.newplayer.120: {playermoniker=}", level="debug")

    player.insert()

    if player.playerid is None:
        io.echo("unable to insert player record.", level="error")
        database.rollback(player.args)
        return None

    database.commit(player.args)

    if player.args.debug is True:
        io.echo("newplayer.100: playerid=%r" % (player.playerid), level="debug")
    io.echo("new player!", level="success")

    setcurrentplayer(args, player)

    return player

class completePlayerName(object):
    def __init__(self, args):
        self.args = args
        self.matches = []
        self.debug = args.debug if "debug" in args else False

    def complete(self:object, text:str, state:int):
        dbh = database.connect(self.args)

        vocab = []
        sql = "select name from empyre.player"
        dat = ()
        cur = dbh.cursor()
        cur.execute(sql, dat)
        for rec in database.resultiter(cur):
            vocab.append(rec["name"])
        results = [x for x in vocab if x.startswith(text)] + [None]
        return results[state]

def verifyPlayerNameFound(name:str, **kwargs) -> bool:
    args = kwargs["args"] if "args" in kwargs else Namespace()

    dbh = database.connect(args)

    cur = dbh.cursor()
    sql = "select 1 from empyre.player where moniker=%s"
    dat = (name,)
    cur.execute(sql, dat)
    if cur.rowcount == 0:
        return False
    return True

def verifyPlayerNameNotFound(moniker:str, **kwargs) -> bool:
    args = kwargs["args"] if "args" in kwargs else Namespace()

    io.echo(f"verifyPlayerNameNotFound.120: {args=} {moniker=}", level="debug")
    dbh = database.connect(args)
    cur = dbh.cursor()
    sql = "select 1 from empyre.player where moniker=%s"
    dat = (moniker,)
    cur.execute(sql, dat)
    io.echo(f"verifyPlayerNameNotFound.100: mogrify={cur.mogrify(sql, dat)}", level="debug")
    if cur.rowcount == 0:
        return True
    return False

def getplayerid(args:object, name:str) -> int:
    if name is None or name == "":
        return None

    dbh = database.connect(args)
    cur = dbh.cursor()
    sql = "select id from empyre.player where moniker=%s"
    dat = (name,)
    print("getplayerid.100: mogrify=%r" % (cur.mogrify(sql, dat)))
    cur.execute(sql, dat)
    res = cur.fetchone()
    if cur.rowcount == 0:
        return None
    return res["id"]

def inputplayername(prompt:str="player name: ", oldvalue:str="", **kw):
    multiple = kw["multiple"] if "multiple" in kw else False
    args = kw["args"] if "args" in kw else argparse.Namespace()
    noneok = kw["noneok"] if "noneok" in kw else True
    if "verify" in kw:
        verify = kw["verify"]
        del kw["verify"]
    else:
        verify = verifyPlayerNameFound

    name = io.inputstring(prompt, oldvalue, verify=verify, completer=completePlayerName(args), completerdelims="", **kw)
    io.echo("inputplayername.160: name=%r" % (name), level="debug")
    return name
#    playerid = getplayerid(args, name)
#    ttyio.echo("inputplayername.140: name=%r, playerid=%r" % (name, playerid), level="debug")
#    return playerid

def setarea(args, buf, stack=False, **kw) -> None:
    player = kw["player"] if "player" in kw else None
#    if player is None:
#        io.echo("You do not exist! Go Away!!")
#        return False

    def rightside():
        debug = True if args is not None and args.debug is True else False

        if player is not None:
            if player.isdirty() is True:
                isdirty = "*"
            else:
                isdirty = ""

            if player.turncount >= TURNSPERDAY:
                player.turncount = TURNSPERDAY

            turnremain = TURNSPERDAY - player.turncount
            
            debug = " | debug" if args is not None and args.debug is True else ""
            return "empyre {black}|{var:engine.areacolor} %s {black}|{var:engine.areacolor} %s%s {black}|{var:engine.areacolor} %s%s" % (util.pluralize(turnremain, "turn remains", "turns remain"), isdirty, player.moniker, util.pluralize(player.coins, "coin", "coins"), debug)
        else:
            if debug is True:
                return "debug"
            else:
                return ""

    screen.setarea(buf, rightside, stack)
    if args.debug is True:
        io.echo(f"empyre.setarea.100: {buf=} {stack=} {screen.areastack=}", level="debug")
    return

def playerstatus(args, **kw):
    player = kw["player"] if "player" in kw else None
    if player is None:
        io.echo("You do not exist! Go Away!")
        return

    return player.status()

def calculaterank(args:object, player:object) -> int:
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
        (player.land / player.serfs > 23.4) and
        player.serfs >= 2500): # b? > 62
            rank = 3 # emperor
    elif (player.markets > 15 and
        player.mills >= 10 and
        player.diplomats > 2 and
        player.foundries > 6 and
        player.shipyards > 4 and
        player.palaces > 6 and
        (player.land / player.serfs > 10.5) and
        player.serfs > 3500 and
        player.nobles > 30):
            rank = 2 # king
    elif (player.markets >= 10 and
        player.diplomats > 0 and
        player.mills > 5 and
        player.foundries > 1 and
        player.shipyards > 1 and
        player.palaces > 2 and
        (player.land/player.serfs > 5.1) and
        player.nobles > 15 and
        player.serfs > 3000):
            rank = 1 # prince

    return rank

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

def generatename(args):
    # http://donjon.bin.sh/fantasy/name/#type=me;me=english_male @ty ryan
    namelist = (
        "Richye",
        "Gerey",
        "Andrew",
        "Ryany",
        "Mathye",
        "Burne",
        "Enryn",
        "Andes",
        "Piersym",
        "Jordye",
        "Vyncis",
        "Gery",
        "Aryn",
        "Hone",
        "Sharcey",
        "Kater",
        "Erix",
        "Abell",
        "Wene",
        "Noke",
        "Jane",
        "Folcey",
        "Abel",
        "Bilia",
        "Cilia",
        "Joycie",
        "Vyncis_Potte",
        "Berny",
        "Warder_Eyder",
        "Lesym_Nery",
        "Rarder",
        "Warder_Righte",
        "Drichye_Nyne",
        "Rancent",
        "Ralphye",
        "Gilew_Drete",
        "Elean_Flynsor",
        "Rix",
        "Sarrey",
        "Sabil",
        "Joycie Arron",
        "Bridget",
        "Elen",
        "Jane",
        "Kathel",
        "Icell",
    )
    return namelist[random.randint(0, len(namelist)-1)]

def newsentry(args:object, message:str, player:object=None, otherplayer:object=None):
    ne = {}
    ne["message"] = message
#    ne["playerid"] = player.id
    ne["playermoniker"] = player.moniker
    ne["memberid"] = player.memberid
    ne["datecreated"] = "now()"
    if args.debug is True:
        io.echo(f"{ne=}", level="debug")
    neid = database.insert(args, "empyre.__newsentry", ne, returnid=True)
    if args.debug is True:
        io.echo(f"{neid=}", level="debug")
    database.commit(args)
    return

    attributes = {}
    attributes["message"] = message
    attributes["playerid"] = player.playerid
    attributes["memberid"] = player.memberid

    blurb = {}
    blurb["attributes"] = attributes

    nodeid = blurb.insert(args, blurb, "empyre.newsentry", mogrify=False)
    if args.debug is True:
        io.echo(f"added newsentry for player {player.moniker!r} with message {message!r}", level="debug")
    blurb.commit(args)
    return

def trade(args, player:object, attr:str, name:str, price:int, singular:str="singular", plural:str="plural", determiner:str="a", emoji="", **kw):
#    setarea(player, "trade: %s" % (name))
    if price > player.coins:
        io.echo("{var:labelcolor}You need {var:valuecolor}{}{var:labelcolor} to purchase {var:empyre.highlightcolor}{} {}{/all}".format(util.pluralize(price - player.coins, "more coin", "more coins"), determiner, singular))

    # ttyio.echo("trade.100: admin=%r" % (bbsengine.checkflag(opts, "ADMIN")), level="debug")

    done = False
    while not done:
        player.save()
        setarea(args, player, "trade: %s" % (name), stack=False)

        # currentvalue = getattr(player, attr)
        # prompt = "You have {reverse}%s{/reverse} and {reverse}%s{/reverse}{F6}" % (pluralize(currentvalue, singular, plural), pluralize(player.coins, "coin", "coins"))
        # ttyio.echo(prompt)

        resource = player.getresource(attr)
        if resource is None:
            io.echo("resource %r not found.")
            return
        currentvalue = resource["value"] if "value" in resource else None
        prompt =  "You have %s {var:empyre.highlightcolor}%s{/all} and :moneybag: {var:empyre.highlightcolor}%s{/all}{F6}%s: {var:empyre.highlightcolor}[B]{/all}uy {var:empyre.highlightcolor}[S]{/all}ell {var:empyre.highlightcolor}[C]{/all}ontinue" % (emoji, util.pluralize(currentvalue, singular, plural), util.pluralize(player.coins, "coin", "coins"), name)
#        ttyio.echo("trade.120: prompt=%r" % (prompt), interpret=False)
        choices = "BSCY"
        if member.checkflag(args, "SYSOP") is True:
            prompt += " {var:empyre.highlightcolor}[E]{/all}dit"
            choices += "E"

        prompt += " {var:empyre.highlightcolor}[Y]{/all}our stats"
        choices += "Y"

        prompt += ": "
        ch = io.inputchar(prompt, choices, "C")
        if ch == "":
            io.echo("{/all}")
        elif ch == "E":
            io.echo("Edit")
            newvalue = io.inputinteger("{var:promptcolor}%s: {var:inputcolor}" % (name), currentvalue)
            io.echo("{/all}")
            if newvalue < 0:
                newvalue = 0
            setattr(player, attr, newvalue)
            io.echo("player.%s=%s{/all}" % (attr, newvalue), level="debug")
        elif ch == "C":
            io.echo("Continue")
            done = True
            break
        elif ch == "Y":
            io.echo("Your Stats")
            player.status()
            continue
        elif ch == "B":
            # price = currentplayer.weathercondition*3+12
            io.echo("Buy{F6}The barbarians will sell their %s to you for {var:empyre.highlightcolor} %s{/all} each." % (name, util.pluralize(price, "coin", "coins", emoji=":moneybag:")))
            quantity = io.inputinteger("buy how many?: ")
            if quantity is None or quantity < 1:
                break

            if player.coins < quantity*price:
                io.echo("You have :moneybag: %s and you need %s to complete this transaction." % (util.pluralize(player.coins, "coin", "coins"), util.pluralize(abs(player.coins - quantity*price), "more coin", "more coins", emoji=":moneybag")))
                continue

            a = player.getresource(attr) # getattr(player, attr)
            value = a["value"]
            value += quantity
            if args.debug is True:
                io.echo("value=%r" % (value), level="debug")

            setattr(player, attr, int(value))
            player.coins -= quantity*price
            io.echo("Bought!")
            break
        elif ch == "S":
            io.echo("sell{F6}The barbarians will buy your %s for {var:empyre.highlightcolor}%s{/all} each." % (plural, util.pluralize(price, "coin", "coins", emoji=":moneybag:")))
            quantity = io.inputinteger("sell how many?: ")
            if quantity is None or quantity < 1:
                break

            attr = player.getresource(attr) # getattr(player, attr)
            value = attr["value"]
            value -= quantity
            setattr(player, attr, value)
            player.coins += quantity*price
            io.echo("Sold!", level="success")

            break

    player.save()
    return

def getplayercount(args, memberid:int) -> int:
    sql = "select count(moniker) from empyre.player where memberid=%s"
    dat = (memberid,)
    dbh = database.connect(args)
    cur = dbh.cursor()
    cur.execute(sql, dat)
    if cur.rowcount == 0:
        return 0
    rec = cur.fetchone()
    return rec["count"]

def getplayer(args, memberid:int):
    io.echo(f"getplayer.100: {memberid=}", level="debug")

    totalitems = getplayercount(args, memberid)

    sql = "select id from empyre.player where memberid=%s"
    dat = (memberid,)
    dbh = database.connect(args)
    cur = dbh.cursor()
    io.echo(f"getplayer.110: {cur.mogrify(sql, dat)=}", level="debug")
    cur.execute(sql, dat)
    if cur.rowcount == 0:
        io.echo("no player record.")
        return None
#    elif cur.rowcount == 1:
#        rec = cur.fetchone()
#        playerid = rec["id"]
#        player = Player(args)
#        player.load(playerid)
#        return player
    else:
        class EmpyrePlayerListboxItem(object):
            def __init__(self, rec:dict, width:int):
                self.player = Player(args)
                self.player.load(rec["id"])

                res = self.player.getresource("land")
                left = f"{self.player.moniker}"
                lastplayed = util.datestamp(self.player.datelastplayed, format="%m/%d@%I%M%P")
                right = f"{util.pluralize(res['value'], **res)} {lastplayed}"
                rightlen = len(right)
                self.label = f"{left.ljust(width-rightlen-10)}{right}" # %s%s {{/all}}{{var:acscolor}}{{acs:vline}}" % (left.ljust(width-rightlen-4), right)

                self.status = ""
                self.pk = self.player.moniker
#                self.label = f"{self.player.moniker} {util.pluralize(res['value'], **res)}"
                self.rec = rec
                self.width = width
            def help(self):
                io.echo("use KEY_ENTER to select one of your players")
                return

            def display(self):
                io.echo(f"{{/all}}{{cha}} {{var:engine.menu.cursorcolor}}{{var:engine.menu.color}} {{var:engine.menu.boxcharcolor}}{{acs:vline}}{{var:cic}} {self.label.ljust(self.width-9, ' ')} {{/all}}{{var:engine.menu.boxcharcolor}}{{acs:vline}}{{var:engine.menu.shadowcolor}} {{var:engine.menu.color}} {{/all}}{{cha}}", end="", flush=True)
                return

        def empyreplayerkeyhandler(args, ch, lb):
            io.echo("inside empyreplayerkeyhandler")
            currentitem = lb.currentitem
            if ch == "KEY_ENTER":
                io.setvar("cic", "{var:currentitemcolor}")
                currentitem.display()
                io.echo("{restorecursor}", end="", flush=True)
                io.echo(f"{currentitem.player.moniker}")
                return False

        lb = listbox.Listbox(args, cur, "select player", keyhandler=None, totalitems=totalitems, itemclass=EmpyrePlayerListboxItem)
        op = lb.run()
        if op.kind == "select":
            io.echo(f"{op.listitem.player.moniker}")
            return op.listitem.player
        elif op.kind == "exit":
            return None

    return None

class completeResourceName(object):
    def __init__(self, args, attrs):
        # ttyio.echo("completeAttributeName.100: called")
        self.attrs = attrs

    # @log_exceptions
    def complete(self:object, text:str, state:int):
        vocab = []
        for a in self.attrs:
            vocab.append(a["name"])
        results = [x for x in vocab if x.startswith(text)] + [None]
        return results[state]

# @see https://stackoverflow.com/questions/15304522/how-can-i-make-my-program-properly-crash-when-using-the-cmd-python-module/15304735
def inputresourcename(args:object, prompt:str="resource name: ", oldvalue:str="", multiple:bool=False, verify=None, **kw):
    attrs = kw["attrs"] if "attrs" in kw else None
    completer = completeResourceName(args, attrs)
    return io.inputstring(prompt, oldvalue, opts=args, verify=verify, multiple=multiple, completer=completer, returnseq=False, **kw)

# @since 20220731
currentplayer = None

def setcurrentplayer(args, player):
    global currentplayer
    currentplayer = player

def getcurrentplayer(args):
    global currentplayer
    return currentplayer

def init(args, **kw):
    io.setvar("empyre.highlightcolor", "{var:highlightcolor}")
    return True

def buildargs(args=None, **kw):
    parser = argparse.ArgumentParser("empyre")
    parser.add_argument("--verbose", action="store_true", dest="verbose")
    parser.add_argument("--debug", action="store_true", dest="debug")

    defaults = {"databasename": "zoid6", "databasehost":"localhost", "databaseuser": None, "databaseport":5432, "databasepassword":None}
    database.buildargdatabasegroup(parser, defaults)

    return parser
    
def checkmodule(args, modulename, **kw):
    x = f"{PACKAGENAME}.{modulename}"
    if args.debug is True:
        io.echo("empyre.lib.checkmodule.100: {x=}", level="debug")
    return module.check(args, x, **kw)

def runmodule(args, modulename, **kw):
    x = f"{PACKAGENAME}.{modulename}"
    if args.debug is True:
        io.echo("empyre.lib.runmodule.100: x=%r" % (x), level="debug")

    io.echo(f"empyre.lib.runmodule.120: {x=}", level="debug")

    if checkmodule(args, modulename, **kw) is False:
        io.echo(f"empyre.lib.runmodule.120: check of module {x} failed.", level="error")
        return False

    return module.runmodule(args, x, **kw)
