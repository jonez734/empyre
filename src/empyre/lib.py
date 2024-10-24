import time
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

TURNSPERDAY:int = 10
PACKAGENAME:str = "empyre"
SHIPSPERSHIPYARD:int = 10
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
MAXSHIPYARDS:int = 10

class Weather(Enum):
    POOR:int = 1
    ARID:int = 2
    RAIN:int = 3
    AVERAGE:int = 4
    LONGSUMMER:int = 5
    FANTASTIC:int = 6
    @classmethod
    def display(self, val:int):
        if val == self.POOR:
            io.echo(":desert: Poor Weather. No Rain. Locusts Migrate")
        elif val == self.ARID:
            io.echo(":cactus: Early Frosts. Arid Conditions")
        elif val == self.RAIN:
            io.echo(":thunder-cloud-and-rain: Flash Floods. Too Much Rain")
        elif val == self.AVERAGE:
            io.echo("Average Weather. Good Year")
        elif val == self.LONGSUMMER:
            io.echo("Fine Weather. Long Summer")
        elif val == self.FANTASTIC:
            io.echo(":sun: Fantastic Weather! Great Year!")

class Island(object):
    def __init__(self, args):
        self.args = args
        self.playerid:int = None
        self.memberid:int = None
        self.trees:int = 500

class Colony(object):
    def __init__(self, args):
        self.args = args

class Player(object):
    def __init__(self, args):
        self.playerid = None
        self.moniker:str = None # member moniker by default
        self.memberid:int = member.getcurrentid(args)
        self.args = args
        self.rank:int = 0
        self.previousrank:int = 0
        self.turncount:int = 0
        self.soldierpromotioncount:int = 0
        self.datepromoted = None
        self.combatvictorycount:int = 0
        self.weatherconditions:int = 0
        self.beheaded:bool = False
        self.datelastplayed = "now()"
        self.coins:int = COINS
        self.taxrate:int = TAXRATE
        self.training:int = 1 # z9
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
        self.resources = {
            "coins":      {"type": "int",  "default":COINS, "price":1, "singular": "coin", "plural":"coins", "emoji":":moneybag:", "ship":None},
            "serfs":      {"type": "int",  "default":SERFS+random.randint(0, 200), "singular": "serf", "plural": "serfs", "ship":"passenger", "emoji":":person:"}, # sf x(19)
            "land":       {"type": "int",  "default":LAND, "singular":"acre", "plural":"acres", "determiner":"an", "ship":None, "emoji":":farmer:"}, # la x(2)
            "grain":      {"type": "int",  "default":GRAIN, "singular": "bushel", "plural": "bushels", "emoji":":crop:", "ship":"cargo"}, # gr
            "soldiers":   {"type": "int",  "default":SOLDIERS, "price":20, "singular":"soldier", "plural":"soldiers", "ship":"millitary passenger"},
            "nobles":     {"type": "int",  "default":3, "price":25000, "singular":"noble", "plural":"nobles", "ship":"passenger"}, # x(6)
            "palaces":    {"type": "int",  "default":1, "price":20, "singular":"palace", "plural":"palaces", "ship":None}, # f%(1)
            "markets":    {"type": "int",  "default":1, "price":1000, "singular":"market", "plural":"markets", "ship":None}, # f%(2) x(7)
            "mills":      {"type": "int",  "default":1, "price":2000, "singular":"mill", "plural":"mills", "ship":None}, # f%(3) x(8)
            "foundries":  {"type": "int",  "default":2, "price":7000, "singular":"foundry", "plural":"foundries", "ship":None}, # f%(4) x(9)
            "shipyards":  {"type": "int",  "default":0, "price":8000, "singular":"shipyard", "plural":"shipyards", "ship":None}, # yc or f%(5)? x(10)
            "diplomats":  {"type": "int",  "default":0, "price":50000, "singular":"diplomat", "plural":"diplomats", "ship":"passenger millitary"}, # f%(6) 0
            "ships":      {"type": "int",  "default":0, "price":5000, "singular":"ship", "plural":"ships", "emoji":":anchor:", "ship":None}, # 5000 each, yc? x(12)
            "navigators": {"type": "int",  "default":0, "price":500, "singular": "navigator", "plural": "navigators", "emoji":":compass:"}, # @since 20220907
            "stables":    {"type": "int",  "default":1, "price":10000, "singular": "stable", "plural":"stables", "ship":None}, # x(11)
            "colonies":   {"type": "int",  "default":0, "ship":None, "singular": "colony", "plural":"colonies"}, # i8
#            "warriors":   {"type": "int",  "default":0, "singular":"warrior", "plural":"warriors", "ship":"millitary passenger"}, # wa soldier -> warrior or noble?
            "spices":     {"type": "int",  "default":0, "singular":"ton", "plural":"tons", "ship":"cargo"}, # x(25)
            "cannons":    {"type": "int",  "default":0, "singular":"cannon", "plural":"cannons","ship":"any"}, # x(14)
            "forts":      {"type": "int",  "default":0, "singular":"fort", "plural":"forts", "ship":None}, # x(13)
            "dragons":    {"type": "int",  "default":0, "singular":"dragon", "plural":"dragons", "emoji":":dragon:"},
            "horses":     {"type": "int",  "default":50,"emoji":":horse:", "ship":"cargo", "singular":"horse", "plural":"horses"}, # x(23)
            "timber":     {"type": "int",  "default":0, "singular":"log", "plural":"logs", "emoji":":wood:", "ship":"cargo"}, # x(16)
            "rebels":     {"type": "int",  "default":0, "singular":"rebel", "plural":"rebels", "ship":None},
            "exports":    {"type": "int",  "default":0, "singular":"ton", "plural":"tons","emoji": ":package:"},
            "islands":    {"type": "int",  "default":0, "singular":"island", "plural":"islands", "emoji":"palmtree"},
        }
        for name, data in self.resources.items():
            setattr(self, name, data["default"])
#        tz=0:i1=self.palaces:i2=self.markets:i3=self.mills:i4=self.foundries:i5=self.shipyards:i6=self.diplomats
    def getresource(self, name, **kw):
        debug = False # if self.args.debug
        if debug:
            io.echo(f"getattribute.100: {name=}")
        if name in self.resources:
            _r = self.resources[name]
            r = copy.copy(_r)
            v = getattr(self, name)
            if r["type"] == "int":
                if v is None:
                    v = 0
                else:
                    v = int(v)
            r["value"] = v
            if "emoji" not in r or r["emoji"] is None:
                r["emoji"] = ""
            elif "emoji" in kw:
                r["emoji"] = kw["emoji"]
            if "singular" in kw:
                r["singular"] = kw["singular"]
            if "plural" in kw:
                r["plural"] = kw["plural"]
            #if "value" in r:
            #    del r["value"]
            if debug:
                io.echo(f"{r=}", level="debug")
            return r
        return None
    # @since 20240706 new
    def setresourcevalue(self, name:str, value) -> bool:
        if name in self.resources:
            self.resources[name]["value"] = value
            return True
        return False
    # @since 20200901
    # @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_maint.lbl#L22
    def edit(self):
        done = False
        while not done:
            setarea(self.args, f"edit player resources for {self.moniker}", player=self)
            op = selectresource(self.args, "select player resource", self.resources)
            io.echo(f"{op=}", level="debug")
            if op.kind == "exit" or op.kind == "noitems":
                break

            r = op.listitem.resource
            n = op.listitem.pk
            t = r["type"] if "type" in r else "int"
            v = r["value"] if "value" in r else None
            if t == "datetime":
                x = input.date(f"{n} (date): ", v)
            elif t == "int":
                x = io.inputinteger(f"{n} (int): ", v)
            elif t == "bool":
                if v is True:
                    default = "Y"
                    prompt = "{promptcolor}{n} (bool)? {optioncolor}[{currentoptioncolor}Y{optioncolor}n]{promptcolor}: {inputcolor}"
                elif v is False:
                    default = "N"
                    prompt = f"{promptcolor}{n} (bool)? {optioncolor}[y{{currentoptioncolor}}N]{promptcolor}: {inputcolor}"
                x = io.inputboolean(prompt, default)
            else:
                io.echo(f"invalid resource type for {n=} {t=}", level="error")
                return
            setattr(self, n, x)
            r["value"] = x
        return

    def load(self, playerid:int):
        if self.args.debug is True:
            io.echo(f"player.load.100: {playerid=}", level="debug")

        self.playerid = playerid

        dbh = database.connect(self.args)
        sql:str = "select * from empyre.player where id=%s"
        dat:tuple = (playerid,)
        cur = dbh.cursor()
        cur.execute(sql, dat)
        player = cur.fetchone()

        if self.args.debug is True:
            io.echo(f"player.load.120: {rec=}", level="debug") # strip=True, interpret=False)

        if player is None:
            io.echo("player.load.140: player is None", level="debug")
            return False

        if self.args.debug is True:
            io.echo(f"{player['resources']=}", level="debug")

        for attr in ("id", "moniker", "memberid", "rank", "previousrank", "turncount", "soldierpromotioncount", "datepromoted", "combatvictorycount", "weatherconditions", "beheaded", "datelastplayed", "taxrate", "training", "datelastplayedlocal"):
            if attr in player:
                setattr(self, attr, player[attr])

        for name in self.resources.keys():
            if name not in player["resources"]:
                v = self.resources[name]["default"]
            else:
                v = player["resources"][name]["value"]
                if v is None:
                    v = self.resources[name]["default"]
                    io.echo(f"{v=}", level="debug")
            setattr(self, name, v)
        return True

    def update(self):
        if self.playerid < 1:
            io.echo("invalid playerid passed to Player.update.", level="error")
            return False

        for name in self.resources.keys():
            v = getattr(self, name)
            self.setresourcevalue(name, v)
            io.echo(f"syncresvalues.100: {name=} {v=}", level="debug")

        player = {}
        for attr in ("id", "moniker", "memberid", "rank", "previousrank", "turncount", "soldierpromotioncount", "datepromoted", "combatvictorycount", "weatherconditions", "beheaded", "datelastplayed", "coins", "taxrate", "resources"):
            player[attr] = getattr(self, attr)
        return database.update(self.args, "empyre.__player", self.playerid, player)

    def isdirty(self):
        def getattrval(name):
            if name in self.resources:
                r = self.resources[name]
                return r["value"] if "value" in r else r["default"]
            return None

        for name in self.resources.keys():
            curval = getattr(self, name)
            oldval = getattrval(name)
            if self.args.debug is True:
                io.echo(f"{name=} {curval=} {oldval=}", level="debug")
            if curval != oldval:
                if "debug" in self.args and self.args.debug is True:
                    io.echo(f"player.isdirty.100: {name=} {oldval=} {curval=}", level="debug")
                return True
        return False

    def save(self, force=False, commit=True):
        if self.args.debug is True:
            io.echo(f"player.save.100: {self.playerid=}", level="debug")
        if self.playerid is None:
            io.echo("player id is not set. aborted.", level="error")
            return None
        if self.memberid is None:
            io.echo("memberid is not set. aborted.", level="error")
            return None

        if force is True:
            self.update()
            if commit is True:
                database.commit(self.args)
            io.echo(f"{self.moniker} force saved.")
            return

        if self.isdirty() is False:
            io.echo(f"{self.moniker}: clean. no save.")
            return
        io.echo(f"{self.moniker}: dirty. saving.")

        self.update()
        if commit is True:
            database.commit(self.args)
        return

    def insert(self):
        resources = {}
        for name, data in self.resources.items():
            attr = self.getresource(name)
            value = attr["default"] if "default" in attr else None
            io.echo(f"player.insert.100: resources {name=} {value=}", level="debug")
            resources[name] = value

#        ttyio.echo(f"{resources.name=}", level="debug")

        player = {}
        player["coins"] = COINS
        player["resources"] = resources
        player["datelastplayed"] = self.datelastplayed
        player["rank"] = self.rank
        player["previousrank"] = self.previousrank
        player["turncount"] = self.turncount
        player["weatherconditions"] = self.weatherconditions
        player["soldierpromotioncount"] = self.soldierpromotioncount
        player["combatvictorycount"] = self.combatvictorycount
        player["datepromoted"] = self.datepromoted
        player["moniker"] = self.moniker
        player["memberid"] = self.memberid

        player["datecreated"] = "now()"

        playerid = database.insert(self.args, "empyre.__player", player, returnid=True, mogrify=True)

        self.playerid = playerid
        io.echo(f"player.insert.100: {playerid=}", level="debug")
        return playerid


    def status(self):
        if self.args.debug is True:
            io.echo(f"{member.getcurrentid()=}", level="debug")
            io.echo(f"{player.playerid=}, {player.memberid=}, {player.moniker=}", level="debug")

        util.heading(f"player status for {self.moniker}")

        terminalwidth = io.getterminalwidth()-2

        maxwidth = 0
        maxlabellen = 0
        for name, data in self.resources.items():
            label = name
            label = label[:12] + (label[12:] and '..')
            if len(label) > maxlabellen:
                maxlabellen = len(label)
            attr = self.getresource(name)
            v = getattr(self, name)
            if v is not None:
                t = data["type"] if "type" in data else "int"
                if t == "int":
                    v = f"{v:>6n}"
                elif t == "datetime":
                    if label == "datelastplayed":
                        v = attr["datelastplayedlocal"]
                    v = util.datestamp(v, format="%m/%d@%H%M%P%Z")

            buf = f"{label.ljust(maxlabellen)}: {v}"
            buflen = len(io.tostr(buf))
            if buflen > maxwidth:
                maxwidth = buflen
#                io.echo(f"player.status.160: {maxwidth=} {buflen=}", level="debug")
#        ttyio.echo(f"terminalwidth={terminalwidth} maxwidth={maxwidth}", level="debug")
        columns = math.floor(terminalwidth / maxwidth) - 3
        if columns < 1:
            columns = 1
#        ttyio.echo("columns=%d" % (columns), level="debug")


        currentcolumn = 0
        for name, data in self.resources.items():
            n = name
            # https://stackoverflow.com/questions/2872512/python-truncate-a-long-string
            n = n[:12] + (n[12:] and '..')

            res  = self.getresource(name) # getattr(self, a["name"])
            v = getattr(self, name)
#            v = attr["value"]
            if v is not None:
                t = data["type"] if "type" in data else "int"
                if t == "int":
                    v = f"{int(v):>6n}"
                elif t == "datetime":
                    v = util.datestamp(v, format="%m/%d@%I%M%P%Z")

            if name == "soldiers" and self.nobles*SOLDIERSPERNOBLE < self.soldiers:
                buf = f"{{labelcolor}}{n.ljust(maxlabellen)}: {{highlightcolor}}{v}{{normalcolor}}" # % (n.ljust(maxlabellen), v)
            elif name == "horses" and self.stables*HORSESPERSTABLE < self.horses:
                buf = f"{{labelcolor}}{n.ljust(maxlabellen)}: {{highlightcolor}}{v}{{normalcolor}}" # % (n.ljust(maxlabellen), v)
            else:
                buf = f"{{labelcolor}}{n.ljust(maxlabellen)}: {{valuecolor}}{v}{{normalcolor}}" # % (n.ljust(maxlabellen), v)

            buflen = len(io.tostr(buf, exclude=("COLOR",), strip=True)) # ttyio.interpret(buf, strip=True, wordwrap=False))
            if currentcolumn == columns-1:
                io.echo(f"{buf}")
            else:
                io.echo(f" {buf}{' '*(maxwidth-buflen)} ", end="")

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
        if self.taxrate is None or self.taxrate == "":
            io.echo("updated taxrate", level="debug")
            self.taxrate = 15
            self.save(force=True)

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

        if self.shipyards > MAXSHIPYARDS: # > 400
            a = int(self.shipyards / 1.1)
            io.echo(f"{{labelcolor}}Your kingdom cannot support {{valuecolor}}{util.pluralize(self.shipyards, **shipyardsres)}{labelcolor}! {{valuecolor}}{util.pluralize(self.shipyards, singular='shipyard is', plural='shipyards are', **shipyardsres)}{{labelcolor}} closed.{{/all}}")
            self.shipyards -= a

        if self.shipyards == 0:
            if self.ships > 0:
                io.echo(f"{{normalcolor}}You do not have enough shipyards! {{valuecolor}}{util.pluralize(self.ships, **shipsisare)}{{normalcolor}} scrapped.")
                diff = self.ships - self.shipyards*SHIPSPERSHIPYARD
                self.ships -= diff
        # take away the ship if there isn't enough shipyard capacity
        if self.ships > self.shipyards*SHIPSPERSHIPYARD:
            a = self.ships - self.shipyards*SHIPSPERSHIPYARD
            io.echo(f"{{normalcolor}}Your {{valuecolor}}{util.pluralize(self.shipyards, **shipyardsres)}{{normalcolor}} cannot support {{valuecolor}}{util.pluralize(self.ships, **shipres)}{{normalcolor}}, {{normalcolor}} {{valuecolor}}{util.pluralize(a, **shipsisare)} {{normalcolor}} scrapped.")
            self.ships -= a

        coinsres = self.getresource("coins")

        # if pn>1e6 then a%=pn/1.5:pn=pn-a%:&"{f6}{lt. blue}You pay {lt. green}${pound}%f {lt. blue}to the monks for this{f6}year's provisions for your subjects' survival.{f6}"

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
            type = data["type"] if "type" in data else "int"
            if type != "int":
                continue
            # ttyio.echo("player.adjust.100: name=%r" % (name), level="debug")
            attr = self.getresource(name) # getattr(player, name)
            singular = data["singular"] if "singular" in data else "singular"
            plural = data["plural"] if "plural" in data else "plural"
            default = data["default"] if "default" in data else 0
            val = data["value"] if "value" in data and data["value"] is not None else default
            if val < 0:
                lost.append(util.pluralize(abs(val), singular, plural))
                setattr(player, name, 0)

        if len(lost) > 0:
            io.echo(f"You have lost {util.oxfordcomma(lost)}")

        self.previousrank = self.rank
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
    for name, data in player.resources.items():
        default = data["default"]
        resources[name] = default
        setattr(player, name, default)

    player.memberid = currentmemberid
    player.moniker = playermoniker

    io.echo(f"empyre.lib.newplayer.120: {playermoniker=}", level="debug")

    player.insert()

    if player.playerid is None:
        io.echo("unable to insert player record.", level="error")
        database.rollback(args)
        return None

    database.commit(args)

    if args.debug is True:
        io.echo("newplayer.100: playerid=%r" % (player.playerid), level="debug")
    io.echo("new player!", level="success")

#    setcurrentplayer(args, player)

    return player

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
    args = kwargs["args"] if "args" in kwargs else Namespace()

    dbh = database.connect(args)

    cur = dbh.cursor()
    sql:str = "select 1 from empyre.player where moniker=%s"
    dat:tuple = (name,)
    cur.execute(sql, dat)
    if cur.rowcount == 0:
        return False
    return True

def verifyPlayerNameNotFound(moniker:str, **kwargs:dict) -> bool:
    args = kwargs["args"] if "args" in kwargs else Namespace()

    io.echo(f"verifyPlayerNameNotFound.120: {args=} {moniker=}", level="debug")
    dbh = database.connect(args)
    cur = dbh.cursor()
    sql:str = "select 1 from empyre.player where moniker=%s"
    dat:tuple = (moniker,)
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
    sql:str = "select id from empyre.player where moniker=%s"
    dat:tuple = (name,)
    io.echo("getplayerid.100: {cur.mogrify(sql, dat)=}")
    cur.execute(sql, dat)
    res = cur.fetchone()
    if cur.rowcount == 0:
        return None
    return res["id"]

def inputplayername(prompt:str="player name: ", oldvalue:str="", **kwargs:dict):
    multiple:bool = kw["multiple"] if "multiple" in kw else False
    args = kw["args"] if "args" in kw else argparse.Namespace()
    noneok:bool = kw["noneok"] if "noneok" in kw else True
    if "verify" in kw:
        verify = kw["verify"]
        del kw["verify"]
    else:
        verify = verifyPlayerNameFound

    name = io.inputstring(prompt, oldvalue, verify=verify, completer=completePlayerName(args), completerdelims="", **kw)
    io.echo("inputplayername.160: {name=}", level="debug")
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

            coinres = player.getresource("coins", emoji="")
            coinres["emoji"] = ""
            return f"empyre {{black}}|{{engine.areacolor}} {util.pluralize(turnremain, 'turn remains', 'turns remain')} {{black}}|{{engine.areacolor}} {isdirty}{player.moniker} {{black}}|{{engine.areacolor}} {util.pluralize(player.coins, **coinres)}{debug}"
        else:
            if debug is True:
                return "debug"
            else:
                return ""

    screen.setbottombar(buf, rightside, stack)
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

def trade(args, player:object, name:str, **kw:dict):
    price = kw["price"] if "price" in kw else None
    # name = kw["name"] if "name" in kw else None
    emoji = kw["emoji"] if "emoji" in kw else None
    singular = kw["singular"] if "singular" in kw else None
    plural = kw["plural"] if "plural" in kw else None
    io.echo(f"{price=} {player.coins=}", level="debug")
    if price is None:
        io.echo("this item is not for sale.")
        return None

    morecoinsres = player.getresource("coins", singular="more coin", plural="more coins")

    coinres = player.getresource("coins")
    if price > player.coins:
        io.echo(f"{{labelcolor}}You need {{valuecolor}}{util.pluralize(price - player.coins, **morecoinsres)}{{labelcolor}} to purchase {{valuecolor}}{plural}{{/all}}")

    # ttyio.echo("trade.100: admin=%r" % (bbsengine.checkflag(opts, "ADMIN")), level="debug")

    done = False
    while not done:
        player.adjust()
        player.save()
        setarea(args, f"trade: {plural}", stack=False, player=player)

        # currentvalue = getattr(player, attr)
        # prompt = "You have {reverse}%s{/reverse} and {reverse}%s{/reverse}{F6}" % (pluralize(currentvalue, singular, plural), pluralize(player.coins, "coin", "coins"))
        # ttyio.echo(prompt)

        resource = player.getresource(name)
        if resource is None:
            io.echo(f"resource {name} not found.", level="error")
            return
        value = resource["value"] if "value" in resource else None
        prompt =  f"{{labelcolor}}You have {{valuecolor}}{util.pluralize(value, **resource)}{{labelcolor}} and {{valuecolor}}{util.pluralize(player.coins, 'coin', 'coins', emoji=':moneybag:')}{{F6}}{{promptcolor}}{name}: {{optioncolor}}[B]{{labelcolor}}uy {{optioncolor}}[S]{{labelcolor}}ell {{optioncolor}}[C]{{labelcolor}}ontinue"
#        ttyio.echo("trade.120: prompt=%r" % (prompt), interpret=False)
        choices = "BSCY"
        if member.checkflag(args, "SYSOP") is True:
            prompt += " {optioncolor}[E]{/all}dit"
            choices += "E"

        prompt += " {optioncolor}[Y]{/all}our stats"
        choices += "Y"

        prompt += ": "
        ch = io.inputchar(prompt, choices, "C")
        if ch == "":
            io.echo("{/all}")
        elif ch == "E":
            io.echo("Edit")
            newvalue = io.inputinteger(f"{{promptcolor}}{name}: {{inputcolor}}", value)
            io.echo("{/all}")
            if newvalue < 0:
                newvalue = 0
            setattr(player, name, newvalue)
            io.echo(f"player.{name}={newvalue}{{/all}}", level="debug")
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
            io.echo("Buy{F6}The barbarians will sell their %s to you for {empyre.highlightcolor} %s{/all} each." % (name, util.pluralize(price, **coinres)))
            quantity = io.inputinteger("buy how many?: ")
            if quantity is None or quantity < 1:
                break

            if player.coins < quantity*price:
                io.echo("You have :moneybag: %s and you need %s to complete this transaction." % (util.pluralize(player.coins, **coinres), util.pluralize(abs(player.coins - quantity*price), "more coin", "more coins", **coinres)))
                continue

            a = player.getresource(name) # getattr(player, attr)
            value = a["value"]
            value += quantity
            if args.debug is True:
                io.echo("value=%r" % (value), level="debug")

            setattr(player, name, int(value))
            player.coins -= quantity*price
            io.echo("Bought!")
            break
        elif ch == "S":
            io.echo(f"sell{{F6}}{{labelcolor}}The barbarians will buy your {plural} for {{valuecolor}}{util.pluralize(price, **coinres)}{{labelcolor}} each.")
            quantity = io.inputinteger("{{promptcolor}}sell how many?: {{inputcolor}}")
            if quantity is None or quantity < 1:
                break

            res = player.getresource(name) # getattr(player, attr)
            value = res["value"]
            value -= quantity
            setattr(player, name, value)
            player.coins += quantity*price
            io.echo("Sold!", level="success")
            break

    player.adjust()
    player.save()
    return

def getplayercount(args, memberid:int) -> int:
    sql:str = "select count(moniker) from empyre.player where memberid=%s"
    dat:tuple = (memberid,)
    dbh = database.connect(args)
    cur = dbh.cursor()
    cur.execute(sql, dat)
    if cur.rowcount == 0:
        return 0
    rec = cur.fetchone()
    return rec["count"]

def selectplayer(args, title:str="select player", prompt:str="player: ", memberid:int=None):
    class EmpyrePlayerListboxItem(listbox.ListboxItem):
        def __init__(self, rec:dict, width:int, height:int=1, **kw):
            super().__init__(self, width, height, **kw)
            self.player = Player(args)
            self.player.load(rec["id"])
            self.height:int = 1

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
            io.echo("use KEY_ENTER to select one of your players")
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
            io.echo("{restorecursor}", end="", flush=True)
            io.echo(f"{currentitem.player.moniker}")
            return False
        elif ch == "KEY_INS":
            io.echo("{restorecursor}add player")
            return False

    io.echo(f"selectplayer.100: {memberid=}", level="debug")

    totalitems = getplayercount(args, memberid)

    if memberid is None:
        memberid = member.getcurrentid(args)
    sql:str = "select id from empyre.player where memberid=%s order by datelastplayed desc"
    dat:tuple = (memberid,)
    dbh = database.connect(args)
    cur = dbh.cursor()
    if args.debug is True:
        io.echo(f"getplayer.110: {cur.mogrify(sql, dat)=}", level="debug")
    cur.execute(sql, dat)
    if cur.rowcount == 0:
        io.echo("no player record.")
        return None

    lb = listbox.Listbox(args, title=title, keyhandler=None, totalitems=totalitems, itemclass=EmpyrePlayerListboxItem, cur=cur)
    op = lb.run(prompt) # "player: ")
    if op.kind == "select":
        io.echo(f"{op.listitem.player.moniker}")
        return op.listitem.player
    elif op.kind == "exit":
        return None

def getplayer(args, memberid:int):
    io.echo(f"getplayer.100: {memberid=}", level="debug")
    sql:str = "select * from empyre.player where memberid=%s"
    dat:tuple = (memberid,)
    dbh = database.connect(args)
    cur = dbh.cursor()
    cur.execute(sql, dat)
    if cur.rowcount == 0:
        return None
    
    player = selectplayer(args)
    return player

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
#currentplayer = None

#def setcurrentplayer(args, player):
#    global currentplayer
#    currentplayer = player

#def getcurrentplayer(args):
#    global currentplayer
#    return currentplayer

def getresource(args, name:str, **kw):
    if name in resources:
        res = resources[name]
        if "emoji" not in res or res["emoji"] is None:
            res["emoji"] = ""
        if "singular" in "kw":
            res["singular"] = kw["singular"]
        if "plural" in "kw":
            res["plural"] = kw["plural"]
        return res
    return None

def selectresource(args, title, resources, kind=None, **kw):
    class EmpyreResourceListboxItem(listbox.ListboxItem):
        def __init__(self, name:str, resource:dict, width:int, height:int=1, **kw:dict):
            super().__init__(self, resource, width)
            self.pk:str = name
            self.height:int = height
            self.width:int = width
            self.resource:dict = resource
            value = resource["value"] if "value" in resource else 0
            io.echo(f"{value=}")
            left:str = f"{self.pk}"
#            io.echo(f"{self.res=}", level="debug")
            if resource["type"] == "int":
                right:str = f"{value:>6n}" # {util.pluralize(value, **self.res)}"
            else:
                right:str = f"{value:>6s}"
            rightlen:int = len(right)
            self.label:str = f"{left.ljust(self.width-rightlen-10)}{right}" # %s%s {{/all}}{{var:acscolor}}{{acs:vline}}" % (left.ljust(width-rightlen-4), right)

        def display(self):
            io.echo(f"{{/all}}{{cha}} {{engine.menu.cursorcolor}}{{engine.menu.color}} {{engine.menu.boxcharcolor}}{{acs:vline}}{{cic}} {self.label.ljust(self.width-9, ' ')} {{/all}}{{engine.menu.boxcharcolor}}{{acs:vline}}{{engine.menu.shadowcolor}} {{engine.menu.color}} {{/all}}{{cha}}", end="", flush=True)
            return None

    class EmpyreResourceListbox(listbox.Listbox):
        def __init__(self, args, title:str="select resource", resources:dict={}, **kw):
            self.player = kw["player"] if "player" in kw else None
            self.ship = kw["ship"] if "ship" in kw else None
            # self.itemclass = kw["itemclass"] if "itemclass" in kw else None
            self.pagesize:int = 10
            self.terminalwidth:str = io.getterminalwidth()
            self.title:str = title
            self.resources:dict = resources
            self.filter = None

            self.data = []
            for name, resource in self.resources.items():
                # io.echo(f"{name=} {resource=}", level="debug")
                if self.filter is None:
                    self.data.append(EmpyreResourceListboxItem(name, resource, width=self.terminalwidth))
                else:
                    ship = res["ship"] if "ship" in res else None
                    if ship is not None:
                        self.data.append(EmpyreResourceListboxItem(name, res=res, width=self.terminalwidth, player=self.player))

            super().__init__(args, title=self.title, data=self.data, pagesize=self.pagesize, itemclass=EmpyreResourceListboxItem, totalitems=len(self.data))

        def fetchpage(self):
            self.items:list = []
            n:int = self.page*self.pagesize
            upper:int = self.pagesize+n
            if upper > self.totalitems:
                upper:int = self.totalitems
            for x in range(n, upper):
                self.items.append(self.data[x])
            self.numitems:int = len(self.items) # number of items on the page in case it doesn't equal pagesize
            return self.items

    player = kw["player"] if "player" in kw else None
    lb = EmpyreResourceListbox(args, "select player resource", resources)
    res = lb.run("edit player resource: ")
    return res

def init(args, **kw):
    io.setvar("empyre.highlightcolor", "{highlightcolor}")
    return True

def buildargs(args=None, **kw:dict):
    parser = argparse.ArgumentParser("empyre")
    parser.add_argument("--verbose", action="store_true", dest="verbose")
    parser.add_argument("--debug", action="store_true", dest="debug")

    defaults = {"databasename": "zoid6", "databasehost":"localhost", "databaseuser": None, "databaseport":5432, "databasepassword":None}
    database.buildargs(parser, defaults)

    return parser

def checkmodule(args, modulename:str, **kw:dict):
    x:str = f"{PACKAGENAME}.{modulename}"
#    if args.debug is True:
#    io.echo(f"empyre.lib.checkmodule.100: {x=}", level="debug")
    return module.check(args, x, **kw)

def runmodule(args, modulename:str, **kw:dict):
    x:str = f"{PACKAGENAME}.{modulename}"

#    io.echo(f"empyre.lib.runmodule.120: {x=} {modulename=}", level="debug")

    if checkmodule(args, modulename, **kw) is False:
        io.echo(f"empyre.lib.runmodule.120: check of module {x!r} failed.", level="error")
        return False

    return module.runmodule(args, x, **kw)

# @since 20240414
def countships(args, playermoniker:str=None):
    sql:str = "select count(moniker) from empyre.ship where playermoniker=%s"
    dat:tuple = (playermoniker,)
    dbh = database.connect(args)
    cur = dbh.cursor()
    cur.execute(sql, dat)
    return cur.rowcount
