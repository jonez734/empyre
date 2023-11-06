import random
import argparse

from dateutil.tz import tzlocal

import ttyio6 as ttyio
import bbsengine6 as bbsengine

TURNSPERDAY = 4

# @since 20220813
PACKAGENAME = "empyre"
# QUESTDIR = "~/projects/empyre/data/quests/"
PRG = "empyre"

class Ship(object):
    def __init__(self, args):
        self.args = args
        self.playerid = None
        self.name = None
        self.timber = 0
        self.lumber = 0
        self.navigator = False

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
        # self.name = None # na$
        self.memberid = bbsengine.member.getcurrentid(args)
        self.args = args
        self.rank = 0
        self.previousrank = 0
        self.turncount = 0
        self.soldierpromotioncount = 0
        self.weatherconditions = 0

        #self.datelastplayed = "now()"
        #self.acres = 5000 # la
        #self.soldiers = 20 # wa
        #self.serfs = 2000+random.randint(0, 200) # sf
        #self.nobles = 2 # nb
        #self.grain = 10000 # gr
        #self.taxrate = 15 # tr
        #self.coins = 1000 # pn
        #self.palaces = 0 # f%(1) 0
        #self.markets = 0 # f%(2) 0
        #self.mills = 0 # f%(3) 0
        #self.foundries = 2 # f%(4) 0
        #self.shipyards = 0 # f%(5) 0 or yc
        #self.diplomats = 0 # f%(6) 0
        #self.ships = 0 # yc?
        #self.colonies = 0 # i8
        #self.training = 1 # z9

        # @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/mdl.emp.delx2.txt#L25
        self.attributes = [
            {"type": "playername", "name": "name", "default": "a. nonymous"}, # na$
            {"type": "int",  "name": "serfs", "default": 2000+random.randint(0, 200)}, # sf x(19)
            {"type": "int",  "name": "soldierpromotioncount", "default":0},
            {"type": "int",  "name": "turncount", "default":0},
            {"type": "int",  "name": "rank", "default":0},
            {"type": "int",  "name": "previousrank", "default":0},
            {"type": "int",  "name": "memberid", "default": bbsengine.member.getcurrentid(self.args)},
            {"type": "int",  "name": "weatherconditions", "default":0},
            {"type": "int",  "name": "land", "default":5000, "singular":"acre", "plural":"acres"}, # la x(2)
            {"type": "int",  "name": "coins", "default":250000, "singular":"coin", "plural":"coins"}, # pn x(3)
            {"type": "int",  "name": "grain", "default":20000, "singular": "bushel", "plural": "bushels", "emoji":":crop:"}, # gr
            {"type": "int",  "name": "taxrate", "default":15}, # tr
            {"type": "int",  "name": "soldiers", "default":40, "price": 20, "singular":"soldier", "plural":"soldiers"},
            {"type": "int",  "name": "nobles", "default":3, "price":25000, "singular":"noble", "plural":"nobles"}, # x(6)
            {"type": "int",  "name": "palaces", "default":1, "price":20, "singular":"palace", "plural":"palaces"}, # f%(1)
            {"type": "int",  "name": "markets", "default":1, "price":1000, "singular":"market", "plural":"markets"}, # f%(2) x(7)
            {"type": "int",  "name": "mills", "default":1, "price":2000, "singular":"mill", "plural":"mills"}, # f%(3) x(8)
            {"type": "int",  "name": "foundries", "default":2, "price":7000, "singular":"foundry", "plural":"foundries"}, # f%(4) x(9)
            {"type": "int",  "name": "shipyards", "default":0, "price":8000, "singular":"shipyard", "plural":"shipyards"}, # yc or f%(5)? x(10)
            {"type": "int",  "name": "diplomats", "default":0, "price":50000, "singular":"diplomat", "plural":"diplomats"}, # f%(6) 0
            {"type": "int",  "name": "ships", "default":0, "price":5000, "singular":"ship", "plural":"ships", "emoji":":anchor:"}, # 5000 each, yc? x(12)
            {"type": "int",  "name": "navigators", "default":0, "price":500, "singular": "navigator", "plural": "navigators", "emoji":":compass:"}, # @since 20220907
            {"type": "int",  "name": "stables", "default":1, "price": 10000, "singular": "stable", "plural":"stables"}, # x(11)
            {"type": "int",  "name": "colonies", "default":0}, # i8
            {"type": "int",  "name": "training", "default":1}, # z9 - number of units for training
            {"type": "int",  "name": "warriors", "default":0}, # wa soldier -> warrior or noble?
            {"type": "int",  "name": "combatvictory", "default":0},
            {"type": "int",  "name": "spices", "default":0}, # x(25)
#            {"type": "int",  "name": "cannons", "default":0}, # x(14)
            {"type": "int",  "name": "forts", "default":0}, # x(13)
            {"type": "int",  "name": "dragons", "default":0, "emoji":":dragon:"},
            {"type": "int",  "name": "horses", "default":50, "emoji":":horse:"}, # x(23)
            {"type": "int",  "name": "timber", "default":0, "emoji":":wood:"}, # x(16)
#            {"type": "epoch","name": "datelastplayedepoch", "default":0},
#            {"type": "datetime", "name": "datelastplayed", "default":"now"},
            {"type": "int",  "name": "rebels", "default":0},
            {"type": "int",  "name": "exports", "default":0, "emoji": ":package:"},
        ]

        for a in self.attributes:
            setattr(self, a["name"], a["default"])

#        if self.playerid is not None:
#            ttyio.echo("Player.__init__.100: calling load()", level="debug")
#            self.load(self.playerid)

#        tz=0:i1=self.palaces:i2=self.markets:i3=self.mills:i4=self.foundries:i5=self.shipyards:i6=self.diplomats
    def getattribute(self, name):
#        ttyio.echo("getattribute.100: name=%s" % (name))
        for a in self.attributes:
            if a["name"] == name:
                v = getattr(self, name)
                if a["type"] == "int":
                    v = int(v)
                a["value"] = v
                return a
        return None

    def setattribute(self, name, value):
        for a in self.attributes:
            ttyio.echo("player.setattribute.120: name=%r" % (a["name"]), level="debug")
            if a["name"] == name:
                if a["type"] == "int":
                    value = int(value)
                a["value"] = value
                ttyio.echo("player.setattribute.100: name=%r value=%r" % (a["name"], value))
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
 
    def verifyPlayerAttributeName(self, name:str, **kw):
        found = False
        for a in self.attributes:
            n = a["name"]
            if n == name:
                found = True
                break
        return found

    # @since 20200901
    # @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_maint.lbl#L22
    def edit(self):
        done = False
        while not done:
            setarea(self.args, self, "edit player attributes")
            attrname = inputattributename(self.args, "attribute: ", multiple=False, noneok=True, attrs=self.attributes, verify=self.verifyPlayerAttributeName)
            ttyio.echo("attrname=%r" % (attrname), level="debug")
            if attrname is None or attrname == "":
                done = True
                break

            a = self.getattribute(attrname)
            if a is None:
                ttyio.echo("unknown attribute %r." % (attrname), level="error")
                continue

            n = a["name"]
            t = a["type"] if "type" in a else "int"
            v = a["value"] if "value" in a else None
            if t == "playername":
                x = inputplayername(f"{n} (playername): ", v, args=self.args, verify=verifyPlayerNameNotFound, name=name)
                ttyio.echo("player.edit.100: playername=%r" % (x), level="debug")
#                if x is not None:
#                    x = getplayerid(args, playername)
            elif t == "epoch":
                x = bbsengine.inputdate("%s (date): " % (n), v)
            elif t == "int":
                x = ttyio.inputinteger("%s (int): " % (n), v)
            elif t == "bool":
                if v is True:
                    default = "Y"
                    prompt = "%s (bool)? [{var:engine.currentoptioncolor}Y{/all}n]: "
                elif v is False:
                    default = "N"
                    prompt = "%s (bool)? [y{var:engine.currentoptioncolor}N{/all}]: "
                x = ttyio.inputboolean(prompt % (n), default)
            else:
                ttyio.echo("invalid attribute type for n=%r t=%r" % (n, t), level="error")
                return
            setattr(self, n, x)
            ttyio.echo("player.edit.120: n=%r x=%r" % (n, x), level="debug")
            self.setattribute(n, x)
            ttyio.echo("player.edit.140: %s=%r" % (n, self.getattribute(n)["value"]), level="debug")

        return

    def load(self, playerid:int):
        if self.args.debug is True:
            ttyio.echo("player.load.100: playerid=%r" % (playerid), level="debug")
        dbh = bbsengine.database.connect(self.args)
        sql = "select * from empyre.player where id=%s"
        dat = (playerid,)
        cur = dbh.cursor()
        cur.execute(sql, dat)
        res = cur.fetchone()

        if self.args.debug is True:
            ttyio.echo(f"player.load.res={res!r}", level="debug") # strip=True, interpret=False)

        if res is None:
            return False

        attributes = res["attributes"] if "attributes" in res else {}
        if self.args.debug is True:
            ttyio.echo("attributes=%r" % (attributes), level="debug")

        for a in self.attributes:
            # ttyio.echo("player.load.120: a=%r" % (a), level="debug")
            
            name = a["name"]
            default = a["default"]

            if name not in attributes:
                if self.args.debug is True:
                    ttyio.echo("name %s not in database record" % (name), level="warning")
                value = default
            else:
                value = attributes[name]

            if self.args.debug is True:
                ttyio.echo("player.load.140: name=%s default=%s value=%s" % (name, default, value), level="debug")
            setattr(self, name, value)

        self.playerid = playerid
        
        newsentry(self.args, self, f"player {self.name} loaded.")

        return True

    def update(self):
        if self.playerid < 1:
            ttyio.echo("invalid playerid passed to Player.update.", level="error")
            return False

        attributes = {}
        for a in self.attributes:
            name = a["name"]
            attr = self.getattribute(name)
            if attr is None:
                ttyio.echo(f"invalid attribute {name=}")
                continue
            if attr["type"] == "datetime":
#                tz = tzlocal()
                attributes[name] = attr["value"]
            else:
                attributes[name] = attr["value"] # self.getattribute(name) # getattr(self, name)

        return bbsengine.blurb.updateattributes(self.args, self.playerid, attributes)

    def isdirty(self):
        def getattrval(name):
            for a in self.attributes:
                if a["name"] == name:
                    return a["value"] if "value" in a else a["default"]

        for a in self.attributes:
            name = a["name"]
            curval = getattr(self, name)
            oldval = getattrval(name)
            if self.args.debug is True:
                ttyio.echo("name=%r curval=%r oldval=%r" % (name, curval, oldval), level="debug")
            if curval != oldval:
                if "debug" in self.args and self.args.debug is True:
                    ttyio.echo("player.isdirty.100: name=%r oldval=%r curval=%r" % (name, oldval, curval), level="debug")
                return True
        return False

    def save(self):
        if self.args.debug is True:
            ttyio.echo("player.save.100: playerid=%r" % (self.playerid), level="debug")
        if self.playerid is None:
            ttyio.echo("player id is not set. aborted.", level="error")
            return None

        if self.memberid is None:
            ttyio.echo("memberid is not set. aborted.", level="error")
            return None

#        if ttyio.inputboolean("continue to save? [Yn]: ", "Y") is False:
#            ttyio.echo("save aborted")
#            return

        if self.isdirty() is False:
            if "debug" in self.args and self.args.debug is True:
                ttyio.echo("%s: clean. no save." % (self.name))
            return
        ttyio.echo("%s: dirty. saving." % (self.name))

        self.update()
        bbsengine.database.commit(self.args)
        return

    def insert(self):
        attributes = {}
        for a in self.attributes:
            name = a["name"]
            attr = self.getattribute(name)
            value = attr["value"]
            ttyio.echo("player.insert.100: %r=%r" % (name, value), level="debug")
            attributes[name] = value

        ttyio.echo("attributes.name=%r" % (attributes["name"]), level="debug")

        blurb = {}
        blurb["attributes"] = attributes

        blurbid = bbsengine.blurb.insert(self.args, blurb, prg="empyre.player", mogrify=True)
        self.playerid = blurbid
        ttyio.echo(f"player.insert.100: playerid={self.playerid!r}", level="debug")
        return blurbid

    def new(self):
        setarea(self.args, self, "new player!")
        # ttyio.echo("player.new() called!")

        currentmemberid = bbsengine.member.getcurrentid(self.args)
        currentmembername = bbsengine.member.getcurrentmoniker(self.args)
        ttyio.echo(f"player.new.100: currentmemberid={currentmemberid}, currentmembername={currentmembername}", level="debug")
        # if self.args.debug is True:
        #     ttyio.echo("new.100: currentmemberid=%r" % (currentmemberid), level="debug")
        # attributes["memberid"] = currentmemberid

        playername = inputplayername("new player name: ", currentmembername, verify=verifyPlayerNameNotFound, multiple=False, args=self.args, returnseq=False)
        if playername is None:
            ttyio.echo("aborted.")
            return None

        attributes = {}
        for a in self.attributes:
            name = a["name"]
            default = a["default"]
            attributes[name] = default
            setattr(self, name, default)

        self.memberid = currentmemberid

        ttyio.echo("player.new.120: playername=%r" % (playername))
        self.setattribute("name", playername)
        setattr(self, "name", playername)

        self.insert()

        if self.playerid is None:
            ttyio.echo("unable to insert player record.", level="error")
            bbsengine.database.rollback(self.args)
            return None

        bbsengine.database.commit(self.args)

        if self.args.debug is True:
            ttyio.echo("Player.new.100: playerid=%r" % (self.playerid), level="debug")
        ttyio.echo("new player!", level="success")
        return

    def status(self):
        if self.args.debug is True:
            ttyio.echo("bbsengine.member.getcurrentid()=%r" % (bbsengine.member.getcurrentid(self.args)), level="debug")
            ttyio.echo("player.playerid=%r, player.memberid=%r, player.name=%r" % (self.playerid, self.memberid, self.name), level="debug")

        bbsengine.util.heading("player status for %r" % (self.name))

        terminalwidth = ttyio.getterminalwidth()-2

        maxwidth = 0
        maxlabellen = 0
        for a in self.attributes:
            n = a["name"]
            n = n[:12] + (n[12:] and '..')
            if len(n) > maxlabellen:
                maxlabellen = len(n)
            attr = self.getattribute(a["name"])
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
                    ttyio.echo(f"---> player.status.120: {v=} {type(v)=}", level="debug")
                    v = bbsengine.util.datestamp(v, format="%m/%d@%H%M%P%Z")
                    ttyio.echo(f"{v=}", level="debug")

            buf = "%s: %s" % (n.ljust(maxlabellen), v)
            buflen = len(ttyio.tostr(buf))
            if buflen > maxwidth:
                maxwidth = buflen
                ttyio.echo("player.status.160: maxwidth=%s buflen=%s" % (maxwidth, buflen), level="debug")
#        ttyio.echo(f"terminalwidth={terminalwidth} maxwidth={maxwidth}", level="debug")
        columns = terminalwidth // maxwidth
        if columns < 1:
            columns = 1
#        ttyio.echo("columns=%d" % (columns), level="debug")

        currentcolumn = 0
        for a in self.attributes:
            n = a["name"]
            # https://stackoverflow.com/questions/2872512/python-truncate-a-long-string
            n = n[:12] + (n[12:] and '..')

            attr  = self.getattribute(a["name"]) # getattr(self, a["name"])
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
                        v = "%s" % (bbsengine.util.datestamp(v))
                elif t == "datetime":
                    v = bbsengine.util.datestamp(v, format="%m/%d@%I%M%P%Z")

            if a["name"] == "soldiers" and self.nobles*20 < self.soldiers:
                buf = f"{{var:labelcolor}}{n.ljust(maxlabellen)}: {{var:highlightcolor}}{v}{{var:normalcolor}}" # % (n.ljust(maxlabellen), v)
            elif a["name"] == "horses" and self.stables*5 < self.horses:
                buf = f"{{var:labelcolor}}{n.ljust(maxlabellen)}: {{var:highlightcolor}}{v}{{var:normalcolor}}" # % (n.ljust(maxlabellen), v)
            else:
                buf = f"{{var:labelcolor}}{n.ljust(maxlabellen)}: {{var:valuecolor}}{v}{{var:normalcolor}}" # % (n.ljust(maxlabellen), v)

            buflen = len(ttyio.tostr(buf, strip=True)) # ttyio.interpret(buf, strip=True, wordwrap=False))
            if currentcolumn == columns-1:
                ttyio.echo("%s" % (buf))
            else:
                ttyio.echo(" %s%s " % (buf, " "*(maxwidth-buflen)), end="")

            currentcolumn += 1
            currentcolumn = currentcolumn % columns
        ttyio.echo()
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
        self.name = generatename(self.args) # namelist[random.randint(0, len(namelist)-1)]
        if rank == 1:
            self.markets = random.randint(10, 15)
            self.mills = random.randint(6, 9)
            self.diplomats = random.randint(1, 2)
            # self.serfs = random.randint()
        return
    def adjust(self):
        soldierpay = (self.soldiers*(self.combatvictory+2))+(self.taxrate*self.palaces*10)/40 # py
        ttyio.echo("adjust.140: soldierpay=%d" % (soldierpay), level="debug")

        # soldiers = self.soldiers
        soldiers = ttyio.inputinteger("soldiers=", self.soldiers)

        a = 0
        if soldierpay < 1 and soldiers >= 500:
            ttyio.echo("soldierpay < 1, soldiers >= 500", level="debug")
            a += soldiers//5
            ttyio.echo("adjust.100: a=%d soldiers=%d" % (a, soldiers), level="debug")
        ttyio.echo("adjust.160: a=%d" % (a), level="debug")

        if self.nobles < 1:
            ttyio.echo("You have no nobles!")
            self.nobles = 0
            a += soldiers
            soldiers = 0

        if soldiers < 1:
            soldiers = 0
            ttyio.echo("You have no soldiers!")

        if soldiers > (self.nobles*20)+1:
            a +=  abs(self.nobles*20 - soldiers)
            ttyio.echo("Not enough nobles for your %s!" % (bbsengine.util.pluralize(soldiers, "soldier", "soldiers", emoji=":military-helmet:")))
        soldiers -= a
        ttyio.echo("adjust.180: a=%d" % (a), level="debug")

        if a > 0:
            ttyio.echo("{var:valuecolor}{}{/all} your army".format((bbsengine.util.pluralize(a, "soldier deserts", "soldiers desert", emoji=":military-helmet:"))))

        if self.land < 0:
            ttyio.echo("You lost your last %s." % (bbsengine.util.pluralize(abs(self.land), "acre", "acres")))
            self.land = 0

        if self.land == 0:
            ttyio.echo("You have no land!")

        if self.shipyards > 10: # > 400
            a = int(self.shipyards / 1.1)
            ttyio.echo("{cyan}Your kingdom cannot support %s! %s closed.{/all}" % (bbsengine.util.pluralize(self.shipyards, "shipyard", "shipyards"), bbsengine.util.pluralize(self.shipyards, "shipyard is", "shipyards are")))
            self.shipyards -= a

        if self.shipyards == 0:
            if self.ships > 0:
                ttyio.echo("{cyan}You do not have any shipyards! %s scrapped." % (bbsengine.util.pluralize(self.ships, "ship is", "ships are", emoji=":anchor:")))
                diff = self.ships - self.shipyards*10
                self.ships -= diff
        # take away the ship if there isn't enough shipyard capacity
        if self.ships > self.shipyards*10:
            a = self.ships - self.shipyards*10
            ttyio.echo("{cyan}Your {var:empyre.highlightcolor}%s{/all} cannot support {var:empyre.highlightcolor}%s{/all}! %s scrapped{/all}" % (bbsengine.util.pluralize(self.shipyards, "shipyard", "shipyards"), bbsengine.util.pluralize(self.ships, "ship", "ships", emoji=":anchor:"), bbsengine.util.pluralize(a, "ship is", "ships are", emoji=":anchor:")))
            self.ships -= a

        # if pn>1e6 then a%=pn/1.5:pn=pn-a%:&"{f6}{lt. blue}You pay {lt. green}${pound}%f {lt. blue}to the monks for this{f6}year's provisions for your subjects' survival.{f6}"
        if self.coins > 1000000:
            a = int(self.coins / 1.5)
            self.coins -= a
            ttyio.echo("{cyan}You donate {var:empyre.highlightcolor}%s{/all} to the monks." % (bbsengine.util.pluralize(a, "coin", "coins")))

        if self.coins < 0:
            ttyio.echo("You lost your last %s." % (bbsengine.util.pluralize(abs(self.coins), "coin", "coins")))
            self.coins = 0

        if self.land > 2500000:
            a = int(self.land / 2.5)
            self.land -= a
            ttyio.echo("{cyan}You donate {var:empyre.highlightcolor}%s{/all} to the monks." % (bbsengine.util.pluralize(a, "acre", "acres")))

        if self.foundries > 400:
            a = self.foundries // 3
            self.foundries -= a
            ttyio.echo("{green}{var:empyre.highlightcolor} MAJOR EXPLOSION! {/all} %s destroyed." % (bbsengine.util.pluralize(a, "foundry is", "foundries are")))

        if self.markets > 500:
            a = self.markets // 5
            self.markets -= a
            ttyio.echo("{red}Some market owners retire; %s closed." % (bbsengine.util.pluralize(a, "market is", "markets are")))

        if self.mills > 500:
            a = self.mills // 4
            self.mills -= a
            ttyio.echo("{green}The mills are overworked! %s mills have broken millstones and are closed.{/all}" % (bbsengine.util.pluralize(a, "mill has a broken millstone", "mills have broken millstones")))

        if self.coins < 0:
            ttyio.echo("{lightred}You are overdrawn by %s!{/all}" % (bbsengine.util.pluralize(abs(self.coins), "coin", "coins")))
            self.coins = 1

        if self.horses > self.stables*50:
            a = self.horses - self.stables*50
            ttyio.echo("{green}You have %s for %s, %s set free." % (bbsengine.util.pluralize(self.stables, "stable", "stables"), bbsengine.util.pluralize(self.horses, "horse", "horses", emoji=":horse:"), bbsengine.util.pluralize(a, "horse is", "horses are", emoji=":horse:")))
            # self.horses -= a

        lost = []
        for a in self.attributes:
            type = a["type"] if "type" in a else "int"
            if type != "int":
                continue
            name = a["name"]
            # ttyio.echo("player.adjust.100: name=%r" % (name), level="debug")
            attr = self.getattribute(name) # getattr(player, name)
            singular = a["singular"] if "singular" in a else "singular"
            plural = a["plural"] if "plural" in a else "plural"
            val = a["value"] if "value" in a else a["default"]
            if val < 0:
                lost.append(bbsengine.util.pluralize(abs(val), singular, plural))
                self.setattribute(name, 0) # setattr(player, name, 0)
        if len(lost) > 0:
            ttyio.echo("You have lost %s" % (bbsengine.oxfordcomma(lost)))

        self.rank = calculaterank(self.args, self)
        # player.save()

        return

    def revert(self):
        pass

class completePlayerName(object):
    def __init__(self, args):
        self.args = args
        self.matches = []
        self.debug = args.debug if "debug" in args else False

    def complete(self:object, text:str, state:int):
        dbh = bbsengine.database.connect(self.args)

        vocab = []
        sql = "select name from empyre.player"
        dat = ()
        cur = dbh.cursor()
        cur.execute(sql, dat)
        for rec in bbsengine.resultiter(cur):
            vocab.append(rec["name"])
        results = [x for x in vocab if x.startswith(text)] + [None]
        return results[state]

def verifyPlayerNameFound(name:str, **kwargs) -> bool:
    args = kwargs["args"] if "args" in kwargs else Namespace()

    dbh = bbsengine.database.connect(args)

    cur = dbh.cursor()
    sql = "select 1 from empyre.player where name=%s"
    dat = (name,)
    cur.execute(sql, dat)
    if cur.rowcount == 0:
        return False
    return True

def verifyPlayerNameNotFound(moniker:str, **kwargs) -> bool:
    args = kwargs["args"] if "args" in kwargs else Namespace()

    ttyio.echo(f"verifyPlayerNameNotFound.120: {args=} {moniker=}", level="debug")
    dbh = bbsengine.database.connect(args)
    cur = dbh.cursor()
    sql = "select 1 from empyre.player where moniker=%s"
    dat = (moniker,)
    cur.execute(sql, dat)
    ttyio.echo("verifyPlayerNameNotFound.100: mogrify={cur.mogrify(sql, dat)}", level="debug")
    if cur.rowcount == 0:
        return True
    return False

def getplayerid(args:object, name:str) -> int:
    if name is None or name == "":
        return None

    dbh = bbsengine.database.connect(args)
    cur = dbh.cursor()
    sql = "select id from empyre.player where name=%s"
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

    name = ttyio.inputstring(prompt, oldvalue, verify=verify, completer=completePlayerName(args), completerdelims="", **kw)
    ttyio.echo("inputplayername.160: name=%r" % (name), level="debug")
    return name
#    playerid = getplayerid(args, name)
#    ttyio.echo("inputplayername.140: name=%r, playerid=%r" % (name, playerid), level="debug")
#    return playerid

def setarea(args, player, buf, stack=False) -> None:
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
            return "empyre {black}|{var:engine.areacolor} %s {black}|{var:engine.areacolor} %s%s {black}|{var:engine.areacolor} %s%s" % (bbsengine.util.pluralize(turnremain, "turn remains", "turns remain"), isdirty, player.name, bbsengine.util.pluralize(player.coins, "coin", "coins"), debug)
        else:
            if debug is True:
                return "debug"
            else:
                return ""

    bbsengine.screen.setarea(buf, rightside, stack)
    if args.debug is True:
        ttyio.echo("empyre.setarea.100: buf=%r stack=%r areastack=%r" % (buf, stack, bbsengine.screen.areastack), level="debug")
    return

def playerstatus(args, player):
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
        ttyio.echo("getranktitle.100: rank=%r" % (rank), level="debug")
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
    # http://donjon.bin.sh/fantasy/name/#type=me;me=english_male ty ryan
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

def newsentry(args:object, player:object, message:str, otherplayer:object=None):
    attributes = {}
    attributes["message"] = message
    attributes["playerid"] = player.playerid
    attributes["memberid"] = player.memberid

    blurb = {}
    blurb["attributes"] = attributes

    nodeid = bbsengine.blurb.insert(args, blurb, "empyre.newsentry", mogrify=False)
    if args.debug is True:
        ttyio.echo(f"added newsentry for player {player.name!r} with message {message!r}", level="debug")
    bbsengine.blurb.commit(args)
    return

def trade(args, player:object, attr:str, name:str, price:int, singular:str="singular", plural:str="plural", determiner:str="a", emoji=""):
#    setarea(player, "trade: %s" % (name))
    if price > player.coins:
        ttyio.echo("You need {var:empyre.highlightcolor}%s{/all} to purchase {var:empyre.highlightcolor}%s %s{/all}" % (bbsengine.util.pluralize(price - player.coins, "more coin", "more coins"), determiner, singular))

    # ttyio.echo("trade.100: admin=%r" % (bbsengine.checkflag(opts, "ADMIN")), level="debug")

    done = False
    while not done:
        player.save()
        setarea(args, player, "trade: %s" % (name), stack=False)

        # currentvalue = getattr(player, attr)
        # prompt = "You have {reverse}%s{/reverse} and {reverse}%s{/reverse}{F6}" % (pluralize(currentvalue, singular, plural), pluralize(player.coins, "coin", "coins"))
        # ttyio.echo(prompt)

        attribute = player.getattribute(attr)
        if attribute is None:
            ttyio.echo("attribute %r not found.")
            return
        currentvalue = attribute["value"] if "value" in attribute else None
        prompt =  "You have %s {var:empyre.highlightcolor}%s{/all} and :moneybag: {var:empyre.highlightcolor}%s{/all}{F6}%s: {var:empyre.highlightcolor}[B]{/all}uy {var:empyre.highlightcolor}[S]{/all}ell {var:empyre.highlightcolor}[C]{/all}ontinue" % (emoji, bbsengine.util.pluralize(currentvalue, singular, plural), bbsengine.util.pluralize(player.coins, "coin", "coins"), name)
#        ttyio.echo("trade.120: prompt=%r" % (prompt), interpret=False)
        choices = "BSCY"
        if bbsengine.member.checkflag(args, "SYSOP") is True:
            prompt += " {var:empyre.highlightcolor}[E]{/all}dit"
            choices += "E"

        prompt += " {var:empyre.highlightcolor}[Y]{/all}our stats"
        choices += "Y"

        prompt += ": "
        ch = ttyio.inputchar(prompt, choices, "C")
        if ch == "":
            ttyio.echo("{/all}")
        elif ch == "E":
            ttyio.echo("Edit")
            newvalue = ttyio.inputinteger("{var:promptcolor}%s: {var:inputcolor}" % (name), currentvalue)
            ttyio.echo("{/all}")
            if newvalue < 0:
                newvalue = 0
            setattr(player, attr, newvalue)
            ttyio.echo("player.%s=%s{/all}" % (attr, newvalue), level="debug")
        elif ch == "C":
            ttyio.echo("Continue")
            done = True
            break
        elif ch == "Y":
            ttyio.echo("Your Stats")
            player.status()
            continue
        elif ch == "B":
            # price = currentplayer.weathercondition*3+12
            ttyio.echo("Buy{F6}The barbarians will sell their %s to you for {var:empyre.highlightcolor} %s{/all} each." % (name, bbsengine.util.pluralize(price, "coin", "coins", emoji=":moneybag:")))
            quantity = ttyio.inputinteger("buy how many?: ")
            if quantity is None or quantity < 1:
                break

            if player.coins < quantity*price:
                ttyio.echo("You have :moneybag: %s and you need %s to complete this transaction." % (bbsengine.util.pluralize(player.coins, "coin", "coins"), bbsengine.util.pluralize(abs(player.coins - quantity*price), "more coin", "more coins", emoji=":moneybag")))
                continue

            a = player.getattribute(attr) # getattr(player, attr)
            value = a["value"]
            value += quantity
            if args.debug is True:
                ttyio.echo("value=%r" % (value), level="debug")

            setattr(player, attr, int(value))
            player.coins -= quantity*price
            ttyio.echo("Bought!")
            break
        elif ch == "S":
            ttyio.echo("sell{F6}The barbarians will buy your %s for {var:empyre.highlightcolor}%s{/all} each." % (plural, bbsengine.util.pluralize(price, "coin", "coins", emoji=":moneybag:")))
            quantity = ttyio.inputinteger("sell how many?: ")
            if quantity is None or quantity < 1:
                break

            attr = player.getattribute(attr) # getattr(player, attr)
            value = attr["value"]
            value -= quantity
            setattr(player, attr, value)
            player.coins += quantity*price
            ttyio.echo("Sold!", level="success")

            break

    player.save()
    return

def getplayer(args, memberid:int):
    ttyio.echo("getplayer.100: memberid=%r" % (memberid), level="debug")
    sql = "select * from empyre.player where memberid=%s"
    dat = (memberid,)
    dbh = bbsengine.database.connect(args)
    cur = dbh.cursor()
    ttyio.echo("getplayer.110: %s" % (cur.mogrify(sql, dat)), level="debug")
    cur.execute(sql, dat)
    if cur.rowcount == 0:
        ttyio.echo("no player record.")
        return None
    
    res = cur.fetchall()
    default = ""
    if cur.rowcount == 1:
        rec = res[0]
        playerid = rec["id"]
        playername = rec["name"]
    else:
        playername = inputplayername("use player: ", default, multiple=False, noneok=False, args=args)
    ttyio.echo("getplayer.120: playername=%r" % (playername), level="debug")
#    if playername == "" or playername is None:
#        ttyio.echo("aborted.")
#        return None

    playerid = getplayerid(args, playername)
    ttyio.echo("getplayer.140: playerid=%r" % (playerid), level="debug")
    if playerid is None:
        return None

    player = Player(args)
    if player.load(playerid) is False:
        ttyio.echo("could not load player record for #%r" % (playerid), level="error")
        return None
        
#    res = cur.fetchone()
#    if res is None:
#        return None
#    playerid = res["id"]
#    if args.debug is True:
#        ttyio.echo("getplayer.120: res=%r" % (res), level="debug")
#        ttyio.echo("getplayer.100: playerid=%r" % (playerid), level="debug")
    
    return player

class completeAttributeName(object):
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
def inputattributename(args:object, prompt:str="attribute name: ", oldvalue:str="", multiple:bool=False, verify=None, **kw):
    attrs = kw["attrs"] if "attrs" in kw else None
    completer = completeAttributeName(args, attrs)
    return ttyio.inputstring(prompt, oldvalue, opts=args, verify=verify, multiple=multiple, completer=completer, returnseq=False, **kw)

# @since 20220731
currentplayer = None

def setcurrentplayer(args, player):
    global currentplayer
    currentplayer = player

def getcurrentplayer(args):
    global currentplayer
    return currentplayer

class Ship(object):
    def __init__(self, args):
        self.args = args
        self.shipyardid = None
        self.portid = None
        self.playerid = None
        self.cannons = 2
        self.manifest = {}
#        self.hitpoints = 100
#        self.weaponclass = 0
#        self.armorclass = 0

class Port(object):
    def __init__(self, args):
        self.args = args
        self.location = None # mainland, island
        self.dockcount = 10
        self.ships = []

class Island(object):
    def __init__(self, args):
        pass

def init(args, **kw):
    ttyio.setvar("empyre.highlightcolor", "{var:highlightcolor}")
    return True
