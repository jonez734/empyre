# from optparse import OptionParser
import time
import argparse
import random
import locale

import ttyio4 as ttyio
import bbsengine4 as bbsengine
from bbsengine4 import pluralize

class completePlayerName(object):
    def __init__(self, args):
        self.dbh = bbsengine.databaseconnect(args)
        self.matches = []
        self.debug = args.debug

    def getmatches(self, text):
        if text == "":
            sql = "select name from empire.player"
            dat = ()
        else:
            sql = "select name from empire.player where name ~ %s"
            dat = (text,)
        
        cur = self.dbh.cursor()
        cur.execute(sql, dat)
        if cur.rowcount == 0:
            cur.close()
            return []

        res = cur.fetchall()
        cur.close()
        foo = []
        for rec in res:
            foo.append(rec["name"])
        ttyio.echo("completePlayerName.getmatches.100: foo=%r" % (foo), level="debug")
        return foo

    @classmethod 
    def completer(self, text, state):
        if state == 0:
            self.matches = self.getmatches(text)
        return self.matches[state]

def inputplayername(args:object, prompt:str="player name: ", oldvalue:str="", multiple:bool=False, verify=None, **kw):
    name = ttyio.inputstring(prompt, oldvalue, opts=args, verify=verify, multiple=multiple, completer=completePlayerName(args), returnseq=False, **kw)

    dbh = bbsengine.databaseconnect(args)
    sql = "select id from empire.player where name=%s"
    dat = (name,)
    cur = dbh.cursor()
    cur.execute(sql, dat)
    if cur.rowcount == 0:
        return None

    res = cur.fetchone()
    cur.close()
    return res["id"]
    
class completeAttributeName(object):
    def __init__(self, args, attrs):
        ttyio.echo("completeAttributeName.100: called")
        self.attrs = attrs

    def completer(self:object, text:str, state:int):
      vocab = []
      for c in self.attrs:
        vocab.append(c["name"])
      results = [x for x in vocab if x.startswith(text)] + [None]
      return results[state]

def inputattributename(args:object, prompt:str="attribute name: ", oldvalue:str="", multiple:bool=False, verify=None, **kw):
  attrs = kw["attrs"] if "attrs" in kw else None
  completer = completeAttributeName(args, attrs)
  return ttyio.inputstring(prompt, oldvalue, opts=args, verify=verify, multiple=multiple, completer=completer, returnseq=False, **kw)

# @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_tourney.lbl#L2
def tourney(args, player, otherplayer):
    # otherplayer = Player(opts)
    # otherplayerid = None
    # otherplayerid = inputplayername(opts, "Attack Whom? >> ", multiple=False) # , verify=verifyOpponent)
    if player.playerid == otherplayerid:
        ttyio.echo("You cannot joust against yourself!")
        return

    ttyio.echo("tourney.100: otherplayerid=%r, otherplayer=%r" % (otherplayerid, otherplayer), level="debug")

    en = otherplayer.nobles
    nb = player.nobles

    if nb == 0:
        ttyio.echo("You haven't a noble to challenge anyone with!")
        return
    
    if player.serfs < 900:
        ttyio.echo("Not enough serfs attend. The joust is cancelled.")
        return

    if en < 2:
        ttyio.echo("Your opponent does not have enough nobles.")
        return

    ttyio.echo("{f6:2}Your Noble mounts his mighty steed and aims his lance...")
    # @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/plus_emp6_tourney.lbl#L12
    #if en*2 < nb:
    #    nb += 1
    #    en -= 1
    #    ttyio.echo("Your noble's lance knocks their opponent to the ground. They get up and swear loyalty to you!")
    #    return

    lost = []
    gained = []
    x = bbsengine.diceroll(10)
    if x == 1:
        player.land += 100
        gained.append("100 acres")
    elif x == 2:
        player.land -= 100
        lost.append("100 acres")
    elif x == 3:
        player.coins += 1000
        gained.append("1000 coins")
    elif x == 4:
        if player.coins >= 1000:
            player.coins -= 1000
            lost.append("1000 coins")
    elif x == 5:
        player.nobles += 1
        gained.append("1 noble")
    elif x == 6:
        if player.nobles > 0:
            player.nobles -= 1
            lost.append("1 noble")
    elif x == 7:
        player.grain += 7000
        gained.append("7000 bushels")
    elif x == 8:
        if player.grain >= 7000:
            player.grain -= 7000
            lost.append("7000 bushels")
    elif x == 9:
        player.shipyards += 1
        gained.append("1 shipyard")
        player.land += 100
        gained.append("100 acres")
    elif x == 10:
        if player.shipyards > 0:
            player.shipyards -= 1
            lost.append("1 shipyard")
        if player.land >= 100:
            player.land -= 100
            lost.append("100 acres")
    
    res = []
    if len(lost) > 0:
        res.append("lost " + ttyio.readablelist(lost))
    if len(gained) > 0:
        res.append("gained " + ttyio.readablelist(gained))
    
    ttyio.echo("You have %s" % (ttyio.readablelist(res)))
    adjust(args, player)
    
    return

    if player.land < 0:
        ttyio.echo("You lost your last %s." % (pluralize(abs(player.land), "acre", "acres")))
        player.land = 0
    if player.coins < 0:
        ttyio.echo("You lost your last %s." % (pluralize(abs(player.coins), "coin", "coins")))
        player.coins = 0

def newsentry(args:object, player:object, message:str, otherplayer:object=None):
    attributes = {}
    attributes["message"] = message
    attributes["playerid"] = player.playerid
    attributes["memberid"] = player.memberid
#    attributes["otherplayer"] = otherplayer.memberid

    node = {}
    node["attributes"] = attributes

    dbh = bbsengine.databaseconnect(args)
    nodeid = bbsengine.insertnode(dbh, args, node, mogrify=True)
    if args.debug is True:
        ttyio.echo("added newsentry for player %r with message %r" % (player.name, message), level="debug")
    dbh.commit()
    return

def shownews(args:object, player:object):
    dbh = bbsengine.databaseconnect(args)
    sql = "select * from empire.newsentry where (extract(epoch from (coalesce(dateupdated, datecreated)))) > %s"
    dat = (player.datelastplayedepoch,)
    cur = dbh.cursor()
    cur.execute(sql, dat)
    res = cur.fetchall()
    # ttyio.echo("shownews.100: res=%r" % (res), level="debug")
    for rec in res:
        ttyio.echo(" %s: %s (#%s): %s" % (bbsengine.datestamp(rec["datecreated"]), rec["createdbyname"], rec["createdbyid"], rec["message"]))
    ttyio.echo("{/all}")
    
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

def getranktitle(args, rank):
    if rank == 0:
        return "lord"
    elif rank == 1:
        return "prince"
    elif rank == 2:
        return "king"
    elif rank == 3:
        return "emperor"
    else:
        return "rank-error"

def generatename(args):
    # http://donjon.bin.sh/fantasy/name/#type=me;me=english_male ty ryan
    namelist = ("Richye", "Gerey", "Andrew", "Ryany", "Mathye Burne", "Enryn", "Andes", "Piersym Jordye", "Vyncis", "Gery Aryn", "Hone Sharcey", "Kater", "Erix", "Abell", "Wene Noke", "Jane Folcey", "Abel", "Bilia", "Cilia", "Joycie")
    return namelist[random.randint(0, len(namelist)-1)]

class Player(object):
    def __init__(self, args, playerid:int=None, rank=0, npc=False):
        self.playerid = playerid
        self.name = None # na$
        self.memberid = bbsengine.getcurrentmemberid()
        self.args = args
        self.rank = rank
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

        self.attributes = (
            {"name": "name", "default": "a. nonymous", "type":"name"}, # na$
            {"name": "serfs", "default": 2000+random.randint(0, 200), "type":"int"}, # sf x(19)
            {"name": "soldierpromotioncount", "default":0},
            {"name": "turncount", "default":0},
            {"name": "rank", "default":rank},
            {"name": "previousrank", "default":0},
            {"name": "memberid", "default":None},
            {"name": "weatherconditions", "default":0},
            {"name": "land", "default":5000, "singular":"acre", "plural":"acres"}, # la x(2)
            {"name": "coins", "default":1000, "singular":"coin", "plural":"coins"}, # pn x(3)
            {"name": "grain", "default":10000, "singular": "bushel", "plural": "bushels"}, # gr
            {"name": "taxrate", "default":15}, # tr
            {"name": "soldiers", "default":20, "price": 20},
            {"name": "nobles", "default":2, "price":25000, "singular":"noble", "plural":"nobles"},
            {"name": "palaces", "default":1, "price":20}, # f%(1)
            {"name": "markets", "default":1, "price":1000}, # f%(2) x(7)
            {"name": "mills", "default":1, "price":2000}, # f%(3) x(8)
            {"name": "foundries", "default":0, "price":7000}, # f%(4) x(9)
            {"name": "shipyards", "default":0, "price":8000, "singular":"shipyard", "plural":"shipyards"}, # yc or f%(5)? x(10)
            {"name": "diplomats", "default":0, "price":50000}, # f%(6) 0
            {"name": "ships", "default":0, "price":5000}, # 5000 each, yc?
            {"name": "colonies", "default":0}, # i8
            {"name": "training", "default":1}, # z9
            {"name": "warriors", "default":0}, # wa soldier -> warrior or noble?
            {"name": "combatvictory", "default":0},
            {"name": "spices", "default":0}, # 
            {"name": "stables", "default":0, "price": 10000},
            {"name": "cannons", "default":0},
            {"name": "forts", "default":0},
            {"name": "dragons", "default":0},
            {"name": "horses", "default":0}, # x(23)
            {"name": "timber", "default":0},
            {"name": "datelastplayedepoch", "default":0, "type": "epoch"}
            # {"name": "datelastplayed", "default":None, "type":"date"}
        )

        for a in self.attributes:
            setattr(self, a["name"], a["default"])

        if self.playerid is not None:
            ttyio.echo("Player.__init__.100: calling load()", level="debug")
            self.load(self.playerid)

#        tz=0:i1=self.palaces:i2=self.markets:i3=self.mills:i4=self.foundries:i5=self.shipyards:i6=self.diplomats
    def remove(self):
        self.memberid = None
        return
 
    def verifyPlayerAttributeName(args, name):
        return False

    # @since 20200901
    # @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_maint.lbl#L22
    def edit(self):
        done = False
        while not done:
            attrname = inputattributename(self.args, "attribute: ", multiple=False, noneok=True, attrs=self.attributes)
            ttyio.echo("attrname=%r" % (attrname), level="debug")
            if attrname is None or attrname == "":
                done = True
                break

            for a in self.attributes:
                n = a["name"]
                if n != attrname:
                    continue
                t = a["type"] if "type" in a else "int"
                v = getattr(self, n)
                if t == "name":
                    x = ttyio.inputstring("%s: " % (n), v)
                elif t == "epoch":
                    x = bbsengine.inputdate("%s: " % (n), v)
                else:
                    x = ttyio.inputinteger("%s: " % (n), v)
                setattr(self, n, x)

        self.save()
        return

    def load(self, playerid):
        if self.args.debug is True:
            ttyio.echo("player.load.100: playerid=%r" % (playerid), level="debug")
        dbh = bbsengine.databaseconnect(self.args)
        sql = "select * from empire.player where id=%s"
        dat = (playerid,)
        cur = dbh.cursor()
        cur.execute(sql, dat)
        res = cur.fetchone()

        if self.args.debug is True:
            ttyio.echo("player.load.res=%r" % (res), level="debug")

        if res is None:
            return None

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

        return

    def save(self, updatecredits=False):
        if self.args.debug is True:
            ttyio.echo("player.save.100: playerid=%r" % (self.playerid), level="debug")
        if self.playerid is None:
            ttyio.echo("player id is not set. aborted.", level="error")
            return None

        if self.memberid is None:
            ttyio.echo("memberid is not set. aborted.", level="error")
            return None

        attributes = {}
        for a in self.attributes:
            n = a["name"]
            t = a["type"] if "type" in a else "int"
            v = getattr(self, n)
            # ttyio.echo("player.save.100: v=type(%r)" % (type(v)))
            attributes[n] = v # getattr(self, n)
        # node = {}
        # node["attributes"] = attributes
        if self.args.debug is True:
            ttyio.echo("Player.save.120: attributes=%r" % (attributes), level="debug")
        dbh = bbsengine.databaseconnect(self.args)
        res = bbsengine.updatenodeattributes(dbh, self.args, self.playerid, attributes)
        if updatecredits is True:
            bbsengine.setmembercredits(self.args, self.memberid, self.credits)
        dbh.commit()
        ttyio.echo("player record saved", level="success")
        return None

    def verifyNameNotFound(self, args, name):
        dbh = bbsengine.databaseconnect(args)
        cur = dbh.cursor()
        sql = "select 1 from empire.player where attributes->>'name'=%s"
        dat = (name,)
        cur.execute(sql, dat)
        if cur.rowcount == 0:
            return True
        return False

    def new(self):
        ttyio.echo("player.new() called!")
        attributes = {}
        for a in self.attributes:
            name = a["name"]
            default = a["default"]
            attributes[name] = default
            setattr(self, name, default)

        currentmemberid = bbsengine.getcurrentmemberid()
        if self.args.debug is True:
            ttyio.echo("new.100: currentmemberid=%r" % (currentmemberid), level="debug")
        attributes["memberid"] = currentmemberid
        self.memberid = currentmemberid

        name = bbsengine.getcurrentmembername(self.args, currentmemberid)
        buf = ttyio.inputstring("name: ", name, verify=self.verifyNameNotFound, multiple=False, args=self.args)
        name = buf[0]
        attributes["name"] = name
        self.name = name
        # sync member.credits w player.credits?

        node = {}
        node["attributes"] = attributes
        dbh = bbsengine.databaseconnect(self.args)
        res = bbsengine.insertnode(dbh, self.args, node, mogrify=True)
        self.playerid = res
        dbh.commit()
        if self.args.debug is True:
            ttyio.echo("Player.new.100: res=%r" % (res), level="debug")
        ttyio.echo("{F6}new player!{F6}", level="success")
        return

    def status(self):
        if self.args.debug is True:
            ttyio.echo("bbsengine.getcurrentmemberid()=%r" % (bbsengine.getcurrentmemberid()), level="debug")
            ttyio.echo("player.playerid=%r, player.memberid=%r, player.name=%r" % (self.playerid, self.memberid, self.name), level="debug")

        bbsengine.title("player status for %s (#%d)" % (self.name, self.playerid), titlecolor="{bggray}{white}", hrcolor="{green}")

        maxlen = 0
        for a in self.attributes:
            name = a["name"]
            if len(name) > maxlen:
                maxlen = len(name)
        
        for a in self.attributes:
            n = a["name"]
            v  = getattr(self, n)
            t = a["type"] if "type" in a else "int"
            if t == "int":
                v = "{:n}".format(v)
            elif t == "epoch":
                v = "%d %s" % (v, bbsengine.datestamp(v))
            ttyio.echo("{yellow}%s : %s{/yellow}" % (n.ljust(maxlen), v))
        ttyio.echo("{/all}")
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
    def generate(self, rank=1):
        self.name = generatename(self.args)
        if rank == 1:
            self.markets = random.randint(10, 15)
            self.mills = random.randint(6, 9)
            self.diplomats = random.randint(1, 2)
            # self.serfs = random.randint()
            self.nobles = 2
            self.horses = 2
        return
    

def yourstatus(args, player):
    return player.status()

# @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/mdl.emp.delx3.txt#L337
def quests(args, player):
    # @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/emp.menu5.txt
    def menu():
        ttyio.echo("{bggray}{white}[1]{/bgcolor} {green}Raid the Pirates Camp")
        ttyio.echo("{bggray}{white}[2]{/bgcolor} {green}Mystery of the Haunted Cave")
        ttyio.echo("{bggray}{white}[3]{/bgcolor} {green}Rescue the Maiden's Sister")
        ttyio.echo("{bggray}{white}[4]{/bgcolor} {green}The Quest of the Gods")
        ttyio.echo("{bggray}{white}[5]{/bgcolor} {green}Eradicate the Evil Cult")
        ttyio.echo("{bggray}{white}[6]{/bgcolor} {green}Search for the Island of Spice")
        ttyio.echo("{bggray}{white}[7]{/bgcolor} {green}Quest for the Legendary Bird City")
        ttyio.echo("{bggray}{white}[8]{/bgcolor} {green}Look for the Mountain Side Ship")
        ttyio.echo("{bggray}{white}[9]{/bgcolor} {green}Seek Arch-Mage Zircon's Help {yellow}Warning: Zircon's Help is a {blink}GAMBLE{/blink}")
        ttyio.echo("{/all}")
    def zircon1():
        x = bbsengine.diceroll(40) # random.randint(1, 40)
        if x >= 19:
            return
        gifts = []
        ttyio.echo("{purple}Zircon says he must consult the bones...")
        x = bbsengine.diceroll(5) # random.randint(1, 5)
        if x == 1:
            gifts.append(pluralize(8000, "acre", "acres"))
            player.land += 8000 # x(2)
        elif x == 2:
            gifts.append(pluralize(30000, "coin", "coins"))
            player.coins += 30000 # x(3)
        elif x == 3:
            gifts.append(pluralize(5, "noble", "nobles"))
            player.nobles += 5 # x(6)
        elif x == 4:
            gifts.append(pluralize(40000, "bushel", "bushels"))
            player.grain += 40000 # x(17)
        return gifts
    def zircon2():
        gifts = []
        x = bbsengine.diceroll(5) # random.randint(1, 5)
        if x == 1:
            gifts.append(pluralize(1000, "serf", "serfs"))
            player.serfs += 1000 # x(19)
        elif x == 2:
            gifts.append(pluralize(4, "shipyard", "shipyards"))
            player.shipyards += 4 # x(10)
        elif x == 3:
            gifts.append(pluralize(2, "fort", "forts"))
            player.forts += 2
            gifts.append(pluralize(8, "cannon", "cannons"))
            player.cannons += 8
        elif x == 4:
            gifts.append(pluralize(50, "horse", "horses"))
            player.horses += 50
        return gifts
    def zircon3():
        gifts = []
        x = bbsengine.diceroll(5) # random.randint(1, 5)
        if x == 1:
            player.foundries += 4 # x(9)
            gifts.append(pluralize(4, "foundry", "foundries"))
        elif x == 2:
            player.markets += 10 # x(7)
            gifts.append(pluralize(10, "market", "markets"))
        elif x == 3:
            player.mills += 10 # x(8)
            gifts.append(pluralize(10, "mill", "mills"))
        elif x == 4:
            player.spices += 10 # x(25)
        elif x == 5:
            player.ships += 4 # x(12)
            gifts.append(pluralize(4, "ship", "ships"))
        return gifts
    def zircon4():
        gifts = []
        x = bbsengine.diceroll(20) # random.randint(1, 20)
        if x < 4:
            return gifts
        gifts.append(pluralize(10, "ton of spices", "tons of spices"))
        player.spices += 10 # x(15)
        return gifts
    def zircon5():
        gifts = []
        x = bbsengine.diceroll(50) # random.randint(1, 50)
        if x > 3:
            return gifts
        gifts.append("a dragon")
        player.dragons += 1
        return gifts
    def zircon6():
        x = bbsengine.diceroll(30) # random.randint(1, 30)
        return

    menu()
    done = False
    while not done:
        ch = ttyio.inputchar("quest [1-9,Q]: ", "123456789Q", "Q")
        if ch == "9":
            # @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/mdl.emp.delx3.txt#L362
            ttyio.echo("9 -- zircon")
            ttyio.echo("""
    Your rivals are pressing you hard!  In desperation, you have undertaken
a long and dangerous journey.  Now at last you stand before Castle
Dragonmare, the home of Arch-mage Zircon.  It is your hope that you can
convince him to help you..{F6:2}""")
            remuneration = []
            remuneration += zircon1(args, player)
            remuneration += zircon2(args, player)
            remuneration += zircon3(args, player)
            remuneration += zircon4(args, player)
            remuneration += zircon5(args, player)
            if len(remuneration) > 0:
                ttyio.echo("remuneration=%r" % (remuneration))
                # newsentry()
            continue

        if bbsengine.diceroll(20) > 5: # random.randint(1, 20) > 5:
            ttyio.echo("You failed to complete the quest.")
            return

        if ch == "1":
            ttyio.echo("1 -- Raid the Pirates Camp")
            ttyio.echo("""    
You have heard that a band of pirates has been raiding the area recently, causing much strife to the poor serfs in your dominion. Thus it is with a stout heart and a sharp sword that you determine to rid your kingdom of these pests once and for all.{F6:2}
After a meeting with your nobles, you decide that the best route of invasion would be through a secret tunnel which one of your spies discovered about a month ago.  It leads into a storage room to the north of the pirates' main cave.{F6:2}
This course determined, your hardy band sets out for the cave less than a week later.  You arrive at the secret tunnel and, after checking for sentries, enter the passage.{F6:2}
Your invasion is swift and merciless, and the pirate camp is soon under your control.  Flushed with victory, your band counts the treasure which you have received.{F6:2}
You gain 30,000 coins!{F6:2}
""")
            ttyio.echo("You win quest #1")
            player.coins += 30000
        elif ch == "2":
            ttyio.echo("""
With the need for good horses, and also having heard of wild horses in the mountains, you set out with some of your Nobles to try to find them.{F6:2}
Questioning the people you meet you discover that the horses have been seen near a haunted cave.  Not believing in ghosts, you head for the location.{F6:2}
Finally, you find the cave, seeing one of the horses entering it.  Quietly you and your men approach the cave.  You are within a hundred yards when you hear some spooky sounds coming from it.{F6:2}
Determined to discover the secret of the sounds, you advance toward the cave.  Upon reaching the cave's entrance, you see daylight quite far back. Boldly entering, you discover a tunnel through a mountain.  The tunnel distorted the sounds you heard, producing the "ghostly" manifestations!{F6:2}
There is a hidden valley on the other end of the tunnel.  In the valley you find a herd of horses.{F6:2}
You gain 30 horses!{F6:2}
""")
            ttyio.echo("You win quest #2")
            player.horses += 30 # x(23)
        elif ch == "3":
            ttyio.echo("""
You are in need of timber for your forts and ships.  Your land is well-suited for growing grain, but you have very little timber.{F6:2}
So, at last you decide if your empire is to survive, you must find a source of timber.  Discussing this with your Nobles, you decide to lead an expedition into the mountains. Though most of the trees are bent from the high winds, you have heard of a small valley, with good timber.{F6:2}
You and your men have been searching for some weeks, when you come upon a young woman.  She is in tears, explaining a band of brigands had captured her and her sister.  They were being used as slave labor at the brigands' camp. She further explains she managed to slip away, and begs you to come and free her sister.{F6:2}
Considering that these brigands may some day become a threat to your land, you agree.  So it was that when you and your men came upon the brigands, you were prepared to fight. The brigands, believing themselves safe, were caught off guard.{F6:2}
Your seasoned troops make quick work of the task.  But you have found something more.  The brigands' camp is in a small valley with good timber!{F6:2}
You gain 15 tons of timber!{F6:2}
""")
            ttyio.echo("You win quest #3")
            player.timber += 15 # x(16)
        elif ch == "4":
            ttyio.echo("You win quest #4")
            player.grain += 30000
        elif ch == "5":
            ttyio.echo("You win quest #5")
            player.acres += 4000
        elif ch == "6":
            ttyio.echo("You win quest #6")
            player.spices += 20 # x(25)
        elif ch == "7":
            ttyio.echo("You win quest #7")
            player.nobles += 4 # x(6)
        elif ch == "8":
            ttyio.echo("You win quest #8")
            player.cannons += 6 # x(14)


def town(args, player):
    # @since 20200816
    # @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_town.lbl#L293
    def bank(args, player):
        bbsengine.title("bank", titlecolor="{bggray}{white}", hrcolor="{green}")
        ttyio.echo()
        exchangerate = 3 #:1 -- 3 coins per credit
        credits = bbsengine.getmembercredits(args)
        ttyio.echo("You have {reverse}%s{/reverse} and {reverse}%s{/reverse}" % (pluralize(player.coins, "coin", "coins"), pluralize(credits, "credit", "credits")))
        ttyio.echo("The exchange rate is {reverse}%s per credit{/reverse}."  % (pluralize(exchangerate, "coin", "coins")))
        ttyio.echo()
        amount = ttyio.inputinteger("{cyan}Exchange how many credits?: {lightgreen}")
        ttyio.echo("{/all}")
        if amount is None or amount < 1:
            return

        credits = bbsengine.getmembercredits(args, player.memberid)

        if amount > credits:
            ttyio.echo("Get REAL! You only have {reverse} %s {/reverse}!" % (pluralize(amount, "credit", "credits")))
            return

        credits -= amount
        player.coins += amount*exchangerate

        bbsengine.setmembercredits(args, player.memberid, credits)

        ttyio.echo("You now have {reverse}%s{/reverse} and {reverse}%s{/reverse}" % (pluralize(player.coins, "coin", "coins"), pluralize(credits, "credit", "credits")))

    # @since 20200803
    # @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_town.lbl#L90
    def changetaxrate(args, player):
        ttyio.echo("current tax rate: %s" % (player.taxrate))
        x = ttyio.inputinteger("{green}tax rate: {lightgreen}", player.taxrate)
        ttyio.echo("{/all}")
        if x is None or x < 1:
            ttyio.echo("no change")
            return
        if x > 50:
            ttyio.echo("King George looks at you sternly for trying to set such an exhorbitent tax rate, and vetoes the change.", level="error")
            return
            
        player.taxrate = x
        return

    # @since 20200830
    # @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_town.lbl#L162
    def lucifersden(args, player):
        if player.coins > 10000 or player.land > 15000:
            ttyio.echo("{F6}I checked our inventory and we have plenty of souls. Maybe we can deal some other time.")
            return

        buf = "LUCIFER'S DEN - Where Gamblin's no Sin!"
        terminalwidth = ttyio.getterminalwidth()

        bbsengine.title(buf, hrcolor="{red}", titlecolor="{yellow}")
        # ttyio.echo("{autored}{reverse}%s{/reverse}{/red}" % (buf.center(terminalwidth-2)))
        # ttyio.echo("{autored}%s{/red}" % ("Where gambling is no sin!".center(terminalwidth-2)))
        ttyio.echo("{yellow}I will let you play for the price of a few souls!{/yellow}")
        ch = ttyio.inputboolean("{cyan}Will you agree to this?{/cyan} ")
        if ch is False:
            ttyio.echo("Some other time, then.")
            return
        # always win, but it costs 10 serfs, 50 serfs if you guess correctly
        # og=int(3*rnd(0)+2)
        # &"{f6:2}{lt. blue}Odds:"+str$(og)+" to 1"
        done = False
        while not done:
            odds = random.randint(2, 4)
            ttyio.echo("Odds: %s to 1" % (odds))
            if player.serfs < 1000:
                ttyio.echo("You must have at least {reverse}%s{/reverse} to gamble here!" % pluralize(1000, "serf", "serfs"))
                done = True
                break
            ttyio.echo("{F6}You have {reverse}%s{/reverse} and {reverse}%s{/reverse}" % (pluralize(player.coins, "coin", "coins"), pluralize(player.serfs, "serf", "serfs")))
            bet = ttyio.inputinteger("{cyan}Bet how many coins? (No Limit){/cyan} {blue}-->{/blue}{green} ")
            ttyio.echo("{/all}")
            if bet is None or bet < 1 or bet > player.coins:
                ttyio.echo("Exiting Lucifer's Den")
                done = True
                break
            
            pick = ttyio.inputinteger("{blue}Pick a number from 1 to 6: ")
            ttyio.echo("{/all}")
            if pick is None or pick < 1:
                ttyio.echo("invalid value")
                done = True
                return
            
            dice = bbsengine.diceroll(6) # random.randint(1, 6)

            if args.debug is True:
                ttyio.echo("dice=%s" % (dice), level="debug")

            if dice == pick:
                ttyio.echo("{green}MATCH!{/green}{F6}")
                player.coins += bet*odds
                player.serfs -= 50
            else:
                player.coins += bet
                player.serfs -= 10
            ttyio.echo()
                
            # b=int(rnd(.)*(og+1)+1):on-(a=b)goto {:104}:pn=pn+x:sf=sf-10
            # &"{f6}{white}Close Enough!{f6}{pound}q1":goto {:170}
        return

    # @since 20200830
    # @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_town.lbl#L231
    def soldierpromotion(args, player):
        terminalwidth = ttyio.getterminalwidth()
        
        player.soldierpromotioncount += 1
        if player.turncount > 2:
            if player.soldierpromotioncount > 1:
                ttyio.echo("Nice try, but we keep our promotion records up to date, and they show that your eligible soldiers have already been promoted! Just wait until King George hears about this!")
                player.soldiers -= 20
                if player.soldiers < 0:
                    player.soldiers = 1
                player.land -= 500
                if player.land < 0:
                    player.land = 1
                player.nobles -= 1
                if player.nobles < 0:
                    player.nobles = 0
                player.serfs -= 100
                if player.serfs < 0:
                    player.serfs = 1
                player.adjust()
                
        if player.soldiers < 10:
            ttyio.echo("None of your soldiers are eligible for promotion to Noble right now.{F6}")
            return
            
        promotable = random.randint(0, 4)
        
        bbsengine.title(": Soldier Promotions :", titlecolor="{bggray}{white}", hrcolor="{green}")
#        ttyio.echo("{autogreen}{reverse}%s{/reverse}{/green}" % (": Soldier Promotions :".center(terminalwidth-2)))
        ttyio.echo("{F6}{yellow}Good day, I take it that you are here to see if any of your soldiers are eligible for promotion to the status of noble.{F6}")
        ttyio.echo("Well, after checking all of them, I have found that ", end="")
        if promotable == 1:
            ttyio.echo("{reverse}1 soldier{/reverse} is eligible.{/yellow}")
        elif promotable == 0:
            ttyio.echo("{reverse}no soldiers{/reverse} are eligible.")
            return
        else:
            ttyio.echo("{reverse}%s soldiers{/reverse} are eligible." % (promotable))

        ch = ttyio.inputboolean("{green}Do you wish them promoted? ")
        ttyio.echo("{/all}")
        if ch is False:
            return

        player.soldiers -= promotable
        player.nobles += promotable

        ttyio.echo("{F6}OK, all have been promoted! We hope they serve you well.")
        
        # &"{f6}{yellow}Good day, I take it that you are here to{pound}$l"
        # &"see if any of your warriors are eligible for promotion{f6}"
        # &"to the status of Noble.{f6:2}"
        # &"{pound}w2Well, after checking all of your{pound}$l"
        # &"warriors, I have found that"+str$(wb)+" of{f6}"
        # &"them are eligible.{f6}"
        # &"{f6:2}{lt. green}Do you wish them promoted? (Y/N) >> ":gosub 1902
        # if a then wa=wa-wb:nb=nb+wb:&"{f6:2}OK, all have been promoted! We hope{pound}$lthey serve you well.{f6}"
        return
    def realtorsadvice(args, player):
        terminalwidth = ttyio.getterminalwidth()-2
        buf = " : Hood's Real Deals! : "
        bbsengine.title(buf, titlecolor="{bggray}{white}", hrcolor="{green}")
        
        # you have 10 shipyards, BSC
        # you have 10 acres of land
        # prompt = "You have {reverse}%s{/reverse} and {reverse}%s{/reverse}" % (pluralize(player.shipyards, "shipyard", "shipyards"), pluralize(player.credits, "credit", "credits"))
        trade(args, player, "shipyards", "shipyards", 2500+player.shipyards//2, "shipyard", "shipyards", "a")
        trade(args, player, "ships", "ships", 5000, "ship", "ships", "a")
        trade(args, player, "foundries", "foundries", 2000+player.foundries//2, "foundry", "foundries", "a")
        trade(args, player, "mills", "mills", 500+player.mills//2, "mill", "mills", "a")
        trade(args, player, "markets", "markets", 250+player.markets//2, "market", "markets", "a")
        
        player.save()
        return

    # @since 20200830
    # @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_town.lbl#L244
    def trainwarriors(args, player):
        bbsengine.title(": Warrior Training :", hrcolor="{green}", titlecolor="{bggray}{white}")
        ttyio.echo()
        eligible = int(player.nobles*20-player.soldiers)
        if player.serfs < 1500 or eligible > (player.serfs // 2):
            ttyio.echo("You do not have enough serfs of training age.")
            return

    options = (
        ("C", "Cyclone's Natural Disaster Bank", bank),
        ("L", "Lucifer's Den", None), # lucifersden),
        ("P", "Soldier Promotion", soldierpromotion),
        ("R", "Realtor's Advice", realtorsadvice),
        ("S", "Slave Market", None),
        ("T", "Change Tax Rate", changetaxrate),
        ("U", "Utopia's Auction", None),
        ("W", "Buy Warriors", None),
        ("X", "Train Warriors", trainwarriors),
        ("Y", "Your Status", yourstatus)
    )

    # @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_town.lbl#L130
    # @since 20200830
    def menu():
        ttyio.echo("town...")
        ttyio.echo()
        bbsengine.title("Town Menu", hrcolor="{green}", titlecolor="{bggray}{white}")

        for hotkey, description, func in options:
            if callable(func):
                ttyio.echo("{bggray}{white}[%s]{/bgcolor} {green}%s" % (hotkey, description))
        ttyio.echo("{/all}")
        ttyio.echo("{cyan}[Q]{/cyan} {lightblue}Return to the Empire{/lightblue}{/all}")
    
    hotkeys = "Q"
    for hotkey, desc, func in options:
        if callable(func):
            hotkeys+= hotkey

    done = False
    while not done:
        player.save()
        menu()
        ch = ttyio.inputchar("Town: ", hotkeys, "")
        if ch == "Q":
            ttyio.echo("Return to the Empire")
            done = True
            continue
        else:
            for key, desc, func in options:
                if ch == key:
                    if callable(func):
                        ttyio.echo(desc)
                        func(args, player)
                    else:
                        ttyio.echo("No Function Defined for this option", level="error")
                    break

# barbarians are buying
def trade(args, player:object, attr:str, name:str, price:int, singular:str="singular", plural:str="plural", determiner:str="a"):
    if price > player.coins:
        ttyio.echo("You need {reverse}%s{/reverse} to purchase {reverse}%s %s{/reverse}" % (pluralize(price - player.coins, "more coin", "more coins"), determiner, singular))

    # ttyio.echo("trade.100: admin=%r" % (bbsengine.checkflag(opts, "ADMIN")), level="debug")

    done = False
    while not done:
        currentvalue = getattr(player, attr)
        prompt = "You have {reverse}%s{/reverse} and {reverse}%s{/reverse}" % (pluralize(currentvalue, singular, plural), pluralize(player.coins, "coin", "coins"))
        ttyio.echo(prompt)
        ttyio.echo()

        prompt =  "%s: {reverse}[B]{/reverse}uy {reverse}[S]{/reverse}ell {reverse}[C]{/reverse}ontinue" % (name)
        choices = "BSC"
        if bbsengine.checkflag(args, "ADMIN") is True:
            prompt += " {reverse}[E]{/reverse}dit"
            choices += "E"
        prompt += ": "
        ch = ttyio.inputchar(prompt, choices, "C")
        if ch == "":
            ttyio.echo("{/all}")
        elif ch == "E":
            ttyio.echo("Edit")
            newvalue = ttyio.inputinteger("{cyan}%s: {lightgreen}" % (name), currentvalue)
            ttyio.echo("{/all}")
            if newvalue < 0:
                newvalue = 0
            setattr(player, attr, newvalue)
            ttyio.echo("player.%s=%s{/all}" % (attr, newvalue), level="success")
        elif ch == "C":
            ttyio.echo("Continue")
            done = True
            break
        elif ch == "B":
            # price = currentplayer.weathercondition*3+12
            ttyio.echo("Buy")
            ttyio.echo()
            ttyio.echo("The barbarians will sell their %s to you for {reverse}%s{/reverse} each." % (name, pluralize(price, "coin", "coins")))
            quantity = ttyio.inputinteger("buy how many?: ")
            if quantity is None or quantity < 1:
                break

            if player.coins < quantity*price:
                ttyio.echo("You have %s and you need %s to complete this transaction." % (pluralize(player.coins, "coin", "coins"), pluralize(abs(player.coins - quantity*price), "more coin", "more coins")))
                continue

            value = getattr(player, attr)
            value += quantity
            if args.debug is True:
                ttyio.echo("value=%r" % (value), level="debug")

            setattr(player, attr, int(value))
            player.coins -= quantity*price
            ttyio.echo("Bought!")
            player.status() # status(opts, currentplayer)
            break
        elif ch == "S":
            ttyio.echo("sell")
            ttyio.echo()
            ttyio.echo("The barbarians will buy your %s for {reverse}%s{/reverse} each." % (plural, pluralize(price, "coin", "coins")))
            quantity = ttyio.inputinteger("sell how many?: ")
            if quantity is None or quantity < 1:
                break

            value = getattr(player, attr)
            value -= quantity
            setattr(player, attr, value)
            player.coins += quantity*price
            ttyio.echo("Sold!", level="success")

            break
    
    ttyio.echo()
    player.save()
    return

# barbarians are selling
def buy(singular, plural, price, available):
    pass

def trading(args, player):
    ttyio.echo("trading...")
    
    prompt = "You have {reverse}%s of land{/reverse} and {reverse}%s{/reverse}" % (pluralize(player.land, "acre", "acres"), pluralize(player.coins, "coin", "coins"))
    price = player.weathercondition*3+12
    trade(args, player, "land", "land", price, "acre", "acres")

    ttyio.echo()

    prompt = "You have {reverse}%s of grain{/reverse} and {reverse}%s{/reverse}" % (pluralize(player.grain, "bushel", "bushels"), pluralize(player.coins, "coin", "coins"))
    price = price//(player.land//875)+1
    trade(args, player, "grain", "grain", price, "bushel", "bushels")
    return

def colonytrip(args, player):
    ttyio.echo("colony trip...")
    ttyio.echo()
    if player.colonies > 0:
        ttyio.echo("King George wishes you a safe and prosperous trip to your %s" % (pluralize(player.colonies, "colony", "colonies", quantity=False)))
        ttyio.echo()
    return

# @since 20201207
# @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/plus_emp6_combat.lbl#L178
def combat(args, player):
    def menu():
        bbsengine.title("Fight Menu", hrcolor="{green}", titlecolor="{bggray}{white}")
        ttyio.echo("{bggray}{white}[1]{/bgcolor} {green}Attack Army")
        ttyio.echo("{bggray}{white}[2]{/bgcolor} {green}Attack Palace")
        ttyio.echo("{bggray}{white}[3]{/bgcolor} {green}Attack Nobles")
        ttyio.echo("{bggray}{white}[4]{/bgcolor} {green}Cease Fighting")
        ttyio.echo("{bggray}{white}[5]{/bgcolor} {green}Send Diplomat")
        ttyio.echo("{bggray}{white}[6]{/bgcolor} {green}Joust")
        ttyio.echo("{bggray}{white}[7]{/bgcolor} {green}Donate to {yellow}%s %s{/all}" % (getranktitle(args, otherplayer.rank).title(), otherplayer.name))
        ttyio.echo()
        return

    def senddiplomat(args, player, otherplayer):
        if player.diplomats < 1:
            ttyio.echo("{F6:2}{yellow}You have no diplomats!{F6:2}")
            return
        ttyio.echo("{F6}{purple}Your diplomat rides to the enemy camp...")
        if otherplayer.soldiers < player.soldiers*2:
            land = otherplayer.land // 15
            otherplayer -= land
            player += land
            ttyio.echo("{F6}{green}Your noble returns with good news! To avoid attack, you have been given %s of land!" % (pluralize(land, "acre", "acres")))
        else:
            player.nobles -= 1
            ttyio.echo("{orange}%s {red}BEHEADS{orange} your diplomat and tosses their corpse into the moat!" % (otherplayer.name.title()))
        player.save()
        otherplayer.save()
    
    # @todo: len(otherplayers) > 0: roll 1d<len+1>; generate NPC if x = len+1
    otherplayerrank = random.randint(0, min(3, player.rank + 1))
    otherplayer = Player(args, npc=True)
    otherplayer.generate(otherplayerrank)
    # otherplayer.new()
    menu()

    done = False
    while not done:
        ch = ttyio.inputchar("combat [1-7,?]: ", "1234567Q?")
        if ch == "Q" or ch == "4":
            ttyio.echo("{lightgreen}%s{cyan} -- Cease Fighting" % (ch))
            done = True
            continue
        elif ch == "5":
            senddiplomat(args, player, otherplayer)
        elif ch == "6":
            tourney(args, player, otherplayer)
            continue
        elif ch == "?":
            menu()
            continue
        else:
            ttyio.echo("{lightgreen}%s{cyan} -- Not Yet Implemented" % (ch))
            continue
    return

def newplayer(args):
    player = Player(args)
    player.new()
    return player
    
def getplayer(args, memberid):
    sql = "select id from empire.player where memberid=%s"
    dat = (memberid,)
    dbh = bbsengine.databaseconnect(args)
    cur = dbh.cursor()
    cur.execute(sql, dat)
    res = cur.fetchone()
    if res is None:
        return None
    playerid = res["id"]
    if args.debug is True:
        ttyio.echo("getplayer.120: res=%r" % (res), level="debug")
        ttyio.echo("getplayer.100: playerid=%r" % (playerid), level="debug")
    player = Player(args)
    player.load(playerid)
    
    return player

def startup(args):
    currentmemberid = bbsengine.getcurrentmemberid()
    if args.debug is True:
        ttyio.echo("startup.300: currentmemberid=%r" % (currentmemberid), level="debug")
    player = getplayer(args, currentmemberid)
    if player is None:
        ttyio.echo("startup.200: new player", level="debug")
        player = newplayer(args)
        newsentry(args, player, "New Player %r!" % (player.name))
    player.credits = bbsengine.getmembercredits(args, currentmemberid)
    # honour
    # wall
    # newplayer if needed
    newsentry(args, player, "player %r loaded." % (player.name))
    return player

# @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_startturn.lbl#L6
# @since 20200913
def mainmenu(args, player):
    options = (
        ("I", "Instructions", None), # instructions),
        ("M", "Maintenance", maint),
        ("N", "News", shownews),
        ("O", "Other Rulers", otherrulers),
        ("P", "Play Empire", play),
        ("T", "Town Activities", town),
        ("Y", "Your Stats", yourstatus),
        ("Q", "Quit Game", None)
    )
    done = False
    while not done:
        bbsengine.title("empyre main menu", hrcolor="{green}", titlecolor="{bggray}{white}")
        ttyio.echo()
        for opt, title, callback in options:
            ttyio.echo("{bggray}{white}[%s]{/bgcolor}{green} %s{/all}" % (opt, title))
        ttyio.echo("{/all}")

        try:
            ch = ttyio.inputchar("{green}Your command, %s %s? {lightgreen}" % (getranktitle(args, player.rank).title(), player.name.title()), "IMNOPTYQ", "")

            if ch == "Q":
                ttyio.echo("{lightgreen}Q{cyan} -- quit game{/all}")
                return False
            else:
                for opt, title, callback in options:
                    if opt == ch:
                        ttyio.echo("{lightgreen}%s{cyan} -- %s{/all}" % (opt, title), end="")
                        if callable(callback) is True:
                            ttyio.echo()
                            callback(args, player)
                        else:
                            ttyio.echo(" (not yet implemented)")
                        ttyio.echo()
                        break
        except EOFError:
            ttyio.echo("{lightgreen}EOF{/all}")
            return False
        except KeyboardInterrupt:
            ttyio.echo("{lightgreen}INTR{/all}")
            return False

    player.save()
    return True

def startturn(args, player):
    ttyio.echo()
    ttyio.echo("{cyan}it is a new year...{/all}")
    ttyio.echo()

    player.turncount += 1

    admin = bbsengine.checkflag(args, "ADMIN")
    ttyio.echo("startturn.100: admin=%r" % (admin), level="debug")
    if admin is True:
        bbsengine.title(": SysOp Options :", titlecolor="{bggray}{white}", hrcolor="{green}")
        player.turncount = ttyio.inputinteger("{cyan}turncount: {lightgreen}", player.turncount)
        player.coins = ttyio.inputinteger("{cyan}coins: {lightgreen}", player.coins)
        ttyio.echo("{/all}")
        player.save()

    if player.turncount > 4:
        ttyio.echo("{red}The other rulers unite against you for hogging the game!{/red}")
        return False

#    if mainmenu(opts, player) is True:
#        return True
#    return False
    return True

def adjust(args, player):
    soldierpay = (player.soldiers*(player.combatvictory+2))+(player.taxrate*player.palaces*10)/40 # py
    a = 0
    if soldierpay < 1 and player.soldiers >= 500:
        a += player.soldiers/5
        player.soldiers -= a
    if player.soldiers > (player.nobles*20)+1:
        a += player.soldiers - (player.nobles*20)
        player.soldiers -= a
    if a > 0: 
        ttyio.echo("{blue}%s{/blue} your army" % (pluralize(a, "soldier deserts", "soldiers desert")))

    if player.shipyards > 10: # > 400
        a = int(player.shipyards / 1.1)
        ttyio.echo("{cyan}Your kingdom cannot support %s shipyards! %s are closed.{/cyan}" % (player.shipyards, a))
        player.shipyards -= a
    if player.ships > player.shipyards*10:
        a = player.ships - player.shipyards*10
        ttyio.echo("{cyan}Your {reverse}%s{/reverse} cannot support {reverse}%s{/reverse}! %s scrapped{/cyan}" % (pluralize(player.shipyards, "shipyard", "shipyards"), pluralize(player.ships, "ship", "ships"), pluralize(a, "ship is", "ships are")))
        player.ships -= a

    # if pn>1e6 then a%=pn/1.5:pn=pn-a%:&"{f6}{lt. blue}You pay {lt. green}${pound}%f {lt. blue}to the monks for this{f6}year's provisions for your subjects' survival.{f6}"        
    if player.coins > 1000000:
        a = player.coins / 1.5
        player.coins -= a
        ttyio.echo("You donate {reverse}%s{/reverse} to the monks." % (pluralize(a, "coin", "coins")))

    if player.land > 2500000:
        a = player.land / 2.5
        player.land -= a
        ttyio.echo("You donate {reverse}%s{/reverse} to the monks." % (pluralize(a, "acre", "acres")))

    if player.foundries > 400:
        a = player.foundries / 3
        player.foundries -= a
        ttyio.echo("{green}{reverse} MAJOR EXPLOSION! {/reverse} %s destroyed." % (pluralize(a, "foundry is", "foundries are")))

    if player.markets > 500:
        a = player.markets / 5
        player.markets -= a
        ttyio.echo("{red}Some market owners retire; %s closed." % (pluralize(a, "market is", "markets are")))
 
    if player.mills > 500:
        a = player.mills // 4
        player.mills -= a
        ttyio.echo("{green}The mills are overworked! %s mills have broken millstones and are closed.{/green}" % (a))

    if player.coins < 0:
        ttyio.echo("{red}You are overdrawn by %s!{/red}" % (pluralize(abs(player.coins), "coin", "coins")))
        player.coins = 0

    lost = []
    for a in player.attributes:
        type = a["type"] if "type" in a else "int"
        if type != "int":
            continue
        name = a["name"]
        attr = getattr(player, name)
        singular = a["singular"] if "singular" in a else "singular"
        plural = a["plural"] if "plural" in a else "plural"
        if attr < 0:
            lost.append(pluralize(abs(attr), singular, plural))
            setattr(player, name, 0)
    if len(lost) > 0:
        ttyio.echo("You have lost %s" % (ttyio.readablelist(lost)))

    player.rank = calculaterank(args, player)
    player.save()
    
    return

def endturn(args, player):
    ttyio.echo("end turn...{F6}")
    
    if player.serfs < 100:
        ttyio.echo("{green}You haven't enough serfs to maintain the empire! It's turned over to King George and you are {yellow}beheaded{/fgcolor}{green}.{/green}")
        player.memberid = None
        player.save(updatecredits=True)
        return
        
    adjust(args, player)
    
    # tr = taxrate
    # ff = "combat victory" flag
    # p1 = palace percentage (up to 10 pieces)
    # p2=int(((rnd(1)*75)+sf/100)*f%(2))
    p2 = int(((random.random()*75)+player.serfs/100)*player.markets)
    # p3=int(((rnd(1)*100)+gr/1000)*f%(3))
    p3 = int(((random.random()*100)+player.grain/1000)*player.mills)
    # p4=((rnd(1)*175)+wa)*f%(4)/(2-ff)
    p4 = ((random.random()*175)+player.soldiers)*player.foundries/(2-player.combatvictory)
    # p5=((rnd(1)*200)+la/30)*f%(5)/(2-ff)
    p5 = ((random.random()*200)+player.land/30)*player.shipyards/(2-player.combatvictory)
    # p4=int(p4-(p4*tr/200)):p5=int(p5-(p5*tr/150))
    p4 = p4-(p4*player.taxrate//200)
    p5 = p5-(p5*player.taxrate//150)
    # py=(wa*(ff+2))+(tr*f%(1)*10)/40:xx=int(tr*(rnd(0)*nb))*100/4

    noblegifts = int(player.taxrate*(random.random()*player.nobles))*100/4 # xx
    if noblegifts < 1 and player.nobles > 67:
        a = player.nobles // 5
        player.nobles -= a
        ttyio.echo("{blue}%s{/blue}" % (pluralize(a, "noble defects", "nobles defect")))

    # pn=int(pn+p2+p3+p4+p5):tg=int((p2+p3+p4+p5)*tr/100):pn=pn+tg
    taxes = (p2+p3+p4+p5)*player.taxrate//100
    # player.credits += (p2+p3+p4+p5+tg)
    receivables = p2+p3+p4+p5+taxes

    # ln=auto-reset land requirement
    # mp=auto-reset emperor status
    # en=bbs credit/coins exchange active
    # nn=bbs credit/coins exchange rate
    palacerent = player.taxrate*player.palaces*10

    soldierpay = int((player.soldiers*(player.combatvictory+2))+(player.taxrate*player.palaces*10)/40) # py
    payables = soldierpay+noblegifts+palacerent
    
    adjust(args, player)

    bbsengine.title("Yearly Report", titlecolor="{bggray}{white}", hrcolor="{green}")
        # pn=pn-(py+xx-pt)

        # &"{f6:2}{lt. green}PAYABLES{white}"
	# &"{f6:2} Soldiers Pay:"+str$(wa*(ff+2))+"{f6} Palace Rent :"
	# &str$(tr*f%(1)*10)+"{f6} Nobles Gifts:"+str$(x)

#    ttyio.echo("Receivables: %s" % "{:>6n}".format(receivables)) # (pluralize(receivables, "credit", "credits")))
#    ttyio.echo("Payables:    %s" % "{:>6n}".format(payables)) # (pluralize(payables, "credit", "credits")))

    ttyio.echo("{cyan}EXPENSES - %s{/cyan}" % ("{:>6n}".format(payables)))
    ttyio.echo()
    ttyio.echo(" Soldier's Pay:  %s" % ("{:>6n}".format(soldierpay)))
    ttyio.echo(" Palace Rent:    %s" % ("{:>6n}".format(palacerent)))
    ttyio.echo(" Noble's Gifts:  %s" % ("{:>6n}".format(noblegifts)))
    ttyio.echo()

    ttyio.echo("{cyan}INCOME --- %s{/cyan}" % ("{:>6n}".format(receivables)))
    ttyio.echo()
    ttyio.echo(" Markets:        %s" % ("{:>6n}".format(p2))) # p2 markets
    ttyio.echo(" Mills:          %s" % ("{:>6n}".format(p3))) # p3 mills
    ttyio.echo(" Foundries:      %s" % ("{:>6n}".format(p4))) # p4 foundries
    ttyio.echo(" Shipyards:      %s" % ("{:>6n}".format(p5))) # p5 shipyards
    ttyio.echo(" Taxes:          %s" % ("{:>6n}".format(taxes))) # tg/taxes
    ttyio.echo()

    if receivables > payables:
        ttyio.echo("{lightgreen}Profit:               %s{/green}" % ("{:>6n}".format(receivables-payables))) # (pluralize(receivables-payables, "credit", "credits")))
    elif receivables < payables:
        ttyio.echo("{lightred}Loss:                -%s{/red}" % ("{:>6n}".format(payables-receivables))) # pluralize(payables-receivables, "credit", "credits")))
    ttyio.echo("{/all}")

    player.coins += receivables
    player.coins -= payables

    #' ln=auto-reset land requirement
    #' mp=auto-reset emperor status
    #' en=bbs credit/money exchange active
    #' nn=bbs credit/money exchange rate
    # if mp=0 and la>ln then gosub {:486} ' part of sub.rank
    adjust(args, player) #  player.adjust() # calculaterank(opts, player)
    
    if args.debug is True:
        ttyio.echo("player.rank=%d rank=%d" % (player.rank, rank), level="debug")
    # check for > player.rank, < player.rank and write entry to game log
    player.rank = calculaterank(args, player)
    
    player.save(updatecredits=True)
    
    ttyio.echo("turn complete!", level="success")
    ttyio.echo("{/all}")

    return

def disaster(args:object, player:object, disaster:int=None):
    if disaster is None:
        disaster = bbsengine.diceroll(12) # int(random.random()*12)+1

    if args.debug is True:
        ttyio.echo("disaster.200: disaster=%s" % (disaster), level="debug")
    
    ttyio.echo("{/all}")

    if disaster == 2:
        res = []
        
        x = random.randint(0, player.serfs//4) # int(random.random()*player.serfs/4)
        player.serfs -= x
        if x > 0:
            res.append("{reverse}%s{/reverse}" % (pluralize(x, "serf", "serfs")))

        x = random.randint(0, player.soldiers//2) # int(random.random()*player.soldiers/2)
        if x > 0:
            player.soldiers -= x
            res.append("{reverse}%s{/reverse}" % (pluralize(x, "soldier", "soldiers")))

        x = random.randint(0, player.nobles//3) # int(random.random()*player.nobles/3)
        if x > 0:
            player.nobles -= x
            res.append("{reverse}%s{/reverse}" % (pluralize(x, "noble", "nobles")))
        
        if len(res) > 0:
            ttyio.echo("P L A G U E ! %s died" % (ttyio.readablelist(res)))
    elif disaster == 3:
        x = random.randint(1, player.grain//3) # int(random.random()*player.grain/3)
        player.grain -= x
        ttyio.echo("EEEK! rats eat {reverse}%s{/reverse} of grain!" % (pluralize(x, "bushel", "bushels")))
        return
    elif disaster == 4:
        x = bbsengine.diceroll(100) # random.randint(1, 100))
        if x < 85:
            return
        if player.palaces > 0 and player.nobles > 0:
            player.palaces -= 1
            player.nobles -= 1
            ttyio.echo("EARTHQUAKE!")
            ttyio.echo()
            ttyio.echo("{orange}1 noble was killed{/orange}")
            if player.palaces == 0:
                ttyio.echo("Your last palace has been destroyed!")
            elif player.palaces == 1:
                ttyio.echo("You have one palace remaining!")
            else:
                ttyio.echo("One of your palaces was destroyed")
            # &"{orange}One of your Palace(s) was destroyed!{pound}$l1 noble was killed."
    elif disaster == 5:
        res = []

        x = random.randint(0, player.markets//3) # int(random.random()*player.markets/3)
        if x > 0:
            res.append(pluralize(x, "market", "markets"))

        x = random.randint(0, player.mills//4) # int(random.random()*player.mills/4)
        if x > 0:
            res.append(pluralize(x, "mill", "mills"))

        x = random.randint(0, player.foundries//3) # int(random.random()*player.foundries/3)
        if x > 0:
            res.append(pluralize(x, "foundry", "foundries"))

        if len(res) > 0:
            ttyio.echo("Mount Apocolypse has erupted!{F6}Lava wipes out %s" % (ttyio.readablelist(res)))
    elif disaster == 6:
        if player.shipyards > 0:
            x = random.randint(0, player.shipyards//2) # int(random.random()*player.shipyards/2)
            if x > 0:
                ttyio.echo("TIDAL WAVE!{F6:2}{blue}{reverse}%s under water!" % (pluralize(x, "shipyard is", "shipyards are")))
    ttyio.echo("{/all}")
    return

def weather(args, player):
    # if you are a KING, you only get average weather
    if player.rank == 2:
        weathercondition = bbsengine.diceroll(4) # random.randint(1, 4)
    else:
        weathercondition = bbsengine.diceroll(6) # random.randint(1, 6)

    ttyio.echo("{cyan}")
    if weathercondition == 1:
        ttyio.echo("Poor Weather. No Rain. Locusts Migrate")
    elif weathercondition == 2:
        ttyio.echo("Early Frosts. Arid Conditions")
    elif weathercondition == 3:
        ttyio.echo("Flash Floods. Too Much Rain")
    elif weathercondition == 4:
        ttyio.echo("Average Weather. Good Year")
    elif weathercondition == 5:
        ttyio.echo("Fine Weather. Long Summer")
    elif weathercondition == 6:
        ttyio.echo("Fantastic Weather! Great Year!")
        
    ttyio.echo("{/all}")
    player.weathercondition = weathercondition

    return

def menu():
    ttyio.echo("empire menu")
    ttyio.echo()
    ttyio.echo("{reverse}[Y]{/reverse}our stats")
    ttyio.echo("{reverse}[O]{/reverse}ther rulers")
    ttyio.echo("{reverse}[P]{/reverse}lay empire")
    ttyio.echo("{reverse}[N]{/reverse}ews")
    ttyio.echo("{reverse}[T]{/reverse}own activities")
    ttyio.echo("Instructions")
    options = "YOPNT"
    if bbsengine.checkflag("ADMIN"):
        ttyio.echo("{reverse}[M]{/reverse}aint")
        options += "M"
    ttyio.echo()
    ttyio.echo("{reverse}[Q]{/reverse}uit")
    ttyio.echo()

# @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/Empire6.lbl#L69
def otherplayers(args, player):
    bbsengine.title("Other Players", titlecolor="{bggray}{white}", hrcolor="{green}")
    return

# @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_maint.lbl#L6
# @since 20200831
def maint(args, player):
    done = False
    while not done:
        bbsengine.title("Empire Maintenance", titlecolor="{bggray}{white}", hrcolor="{green}")
        ttyio.echo()
        ttyio.echo("{purple}Options:{/purple}")
        ttyio.echo("{yellow}[D]{gray} Auto-Reset")
        ttyio.echo("{yellow}[X]{gray} bbs credit / empyre coin exchange rate")
        ttyio.echo("{yellow}[E]{gray} Edit Player's profile")
        ttyio.echo("{yellow}[L]{gray} List Players")
        # ttyio.echo("[P] Play Empire")
        ttyio.echo("{yellow}[R]{gray} Reset Empire")
        ttyio.echo("{yellow}[S]{gray} Scratch News")
        ttyio.echo("{F6}{yellow}[Q]{gray} Quit{F6}")

        ch = ttyio.inputchar("{cyan}Maintenance: {lightgreen}", "DXELRSQ", "")

        if ch == "Q":
            ttyio.echo("Quit")
            done = True
            continue
        elif ch == "D":
            ttyio.echo("Auto-Reset")
            continue
        elif ch == "E":
            ttyio.echo("Edit Player's Profile")
            player.edit()
            continue
        elif ch == "L":
            ttyio.echo("List Players")
            ttyio.echo()
            otherplayers(args, player)
        elif ch == "P":
            ttyio.echo("Play Empire")
            continue
        elif ch == "R":
            ttyio.echo("Reset Empire")
            continue
        elif ch == "S":
            ttyio.echo("Scratch News")
            continue
        elif ch == "X":
            ttyio.echo("bbs credit -> empyre coin exchange rate")
            continue
    ttyio.echo()
    return
    
def harvest(args, player):
    x = int((player.land*player.weathercondition+(random.random()*player.serfs)+player.grain*player.weathercondition)/3)
    x = min(x, player.land+player.serfs*4)
    #if x > (player.land+player.serfs)*4:
    #    x = (player.land+player.serfs)*4
    ttyio.echo()
    ttyio.echo("{lightblue}This year's harvest is {reverse}%s{/reverse}{/all}" % (pluralize(x, "bushel", "bushels")))
    ttyio.echo()

    # https://github.com/Pinacolada64/ImageBBS/blob/cb68d111c2527470218aedb94b93e7f4b432c345/v1.2/web-page/imageprg-chap5.html#L69
    player.grain += x # "pl=1"? <-- has to do with imagebbs input routines accepting upper/lower case vs only upper

    serfsrequire = player.serfs*5+1
    ttyio.echo("{cyan}Your people require {reverse}%s{/reverse} of grain this year{/all}" % (pluralize(serfsrequire, "bushel", "bushels")))
    ttyio.echo()
    price = player.weatherconditions*3+12
    price = int(price/(int(player.land/875)+1))
    # prompt = "You have {reverse}%s{/reverse} and {reverse}%s{/reverse}" % (pluralize(player.grain, "bushel", "bushels"), pluralize(player.credits, "credit", "credits"))
    trade(args, player, "grain", "grain", price, "bushel", "bushels")
    howmany = serfsrequire if player.grain >= serfsrequire else player.grain
    serfsgiven = ttyio.inputinteger("{cyan}Give them how many? {/cyan}{lightgreen}", howmany)
    ttyio.echo("{/all}")
    if serfsgiven < 1:
        ttyio.echo("(Giving {reverse}%s{/reverse} of grain)" % (pluralize(howmany, "bushel", "bushels")))
        serfsgiven = 0
    if serfsgiven > player.grain:
        serfsgiven = player.grain
    player.grain -= serfsgiven
    if player.grain < 1:
        player.grain = 0
        
    armyrequires = player.soldiers*10+1
    done = False
    ttyio.echo("{cyan}Your army requires {reverse}%s{/reverse} this year." % (pluralize(armyrequires, "bushel", "bushels")))
    ttyio.echo("{/all}")
    price = int(6/player.weathercondition)
    price = int(price/int(player.land/875)+1)
    if price > player.coins:
        trade(args, player, "grain", "bushel", price, "bushel", "bushels")
    if armyrequires > player.grain:
        armyrequires = player.grain

    armygiven = ttyio.inputinteger("{cyan}Give them how many? {/cyan}{lightgreen}", armyrequires)
    ttyio.echo("{/all}")
    if armygiven < 1:
        armygiven = 0
    player.grain -= armygiven
    if player.grain < 0:
        player.grain = 0
    return

def buildinvestopts(args, player):
    investopts = {}
    index = 0
    for a in player.attributes:
        if "price" in a and a["price"] > 0:
            investopts[chr(65+index)] = a
            index += 1
    return investopts

def displayinvestmentoptions(investopts): # opts, player):
    maxlen = 0
    for ch, a in investopts.items(): # player.attributes:
        name = a["name"] if "name" in a else ""
        if len(name) > maxlen:
            maxlen = len(name)

    ttyio.echo("{/all}")
    
    # investopts = buildinvestopts(opts, player)
    for ch, a in investopts.items():
        name = a["name"].title()
        price = a["price"]
        buf = "{bggray}{white}[%s]{/all}{green} %s: %s " % (ch, name.ljust(maxlen+2, "-"), " {:>6n}".format(price)) # int(terminalwidth/4)-2)
        ttyio.echo(buf)
    return

def investments(args, player):
    bbsengine.title("Investments", hrcolor="{green}", titlecolor="{bggray}{white}")

    terminalwidth = ttyio.getterminalwidth()

    investopts = buildinvestopts(args, player)

    options = ""
    for ch, a in investopts.items():
        options += ch
    options += "Q?"

    displayinvestmentoptions(investopts)

    done = False
    while not done:
        ttyio.echo()
        ttyio.echo(pluralize(player.coins, "coin", "coins"))
        ch = ttyio.inputchar("{cyan}Investments [%s]: {lightgreen}" % (options), options, "")
        if ch == "Q":
            ttyio.echo("{lightgreen}Q{cyan} -- Quit")
            done = True
            continue
        elif ch == "?":
            ttyio.echo("{lightgreen}? -- {cyan}Help")
            displayinvestmentoptions(investopts) # opts, player)
            continue
        else:
            for opt, a in investopts.items():
                if ch == opt:
                    name = a["name"]
                    price = a["price"]
                    attr = a["name"]
                    singular = a["singular"] if "singular" in a else "singular"
                    plural = a["plural"] if "plural" in a else "plural"
                    ttyio.echo("{lightgreen}%s{green} -- {cyan}%s{/all} %s" % (ch, name.title(), pluralize(price, "coin", "coins")))
                    trade(args, player, attr, name, price, singular, plural)
                    break
            else:
                ttyio.echo("{lightgreen}%s -- {cyan}not implemented yet")
                continue
    ttyio.echo("{/all}leaving investments...")
    return

# @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/Empire6.lbl#L69
def otherrulers(args:object, player=None):
    terminalwidth = ttyio.getterminalwidth()
    dbh = bbsengine.databaseconnect(args)
    sql = "select id from empire.player where memberid > 0 limit 25"
    dat = ()
    cur = dbh.cursor()
    cur.execute(sql, dat)
    res = cur.fetchall()
    #ttyio.echo("res=%r" % (res), level="debug")
    ttyio.echo("{green} ####  name %s{/green}" % ("land".rjust(terminalwidth-len("land")-2-8)))
    ttyio.echo(bbsengine.hr(chars="-=", color="{yellow}"))
    player = Player(args)
    sysop = bbsengine.checkflag(args, "ADMIN")
    cycle = 1
    for rec in res:
        if cycle == 1:
            color = "green"
        else:
            color = "yellow"
        cycle = abs(1 - cycle)
        playerid = rec["id"]
        player.load(playerid)
        if sysop is True:
            if player.memberid is None:
                color = "red"
        buf = " {reverse}{%s} %s  %s %s{/%s}{/reverse}" % (color, "{:>4n}".format(player.playerid), player.name.ljust(terminalwidth-6-10-1), "{:>6n}".format(player.land), color)
        ttyio.echo(buf)
    ttyio.echo(bbsengine.hr(chars="-=", color="yellow"))
    return

def play(args, player):
    player.datelastplayedepoch = time.time()
    startturn(args, player)
    weather(args, player)
    disaster(args, player)
    trading(args, player)
    harvest(args, player)
    colonytrip(args, player)
    town(args, player)
    combat(args, player)
    # tourney(opts, player)
    investments(args, player)
    endturn(args, player)
    return

def main():
    # parser = OptionParser(usage="usage: %prog [options] projectid")
    parser = argparse.ArgumentParser("empyre")
    
    # parser.add_option("--verbose", default=True, action="store_true", help="run %prog in verbose mode")
    parser.add_argument("--verbose", action="store_true", dest="verbose")
    
    # parser.add_option("--debug", default=False, action="store_true", help="run %prog in debug mode")
    parser.add_argument("--debug", action="store_true", dest="debug")

    defaults = {"databasename": "zoidweb4", "databasehost":"localhost", "databaseuser": None, "databaseport":5432, "databasepassword":None}
    bbsengine.buildargdatabasegroup(parser, defaults)

    # databaseargs = parser.add_argument_group("database options")
    # databaseargs.add_argument("--databasename", action="store", dest="databasename", default="zoidweb4", help="specify database name")
    # databaseargs.add_argument("--databasehost", action="store", dest="databasehost", default="localhost", help="specify database host")
    # databaseargs.add_argument("--databaseuser", action="store", dest="databaseuser", help="specify database user")
    # databaseargs.add_argument("--databasepassword", action="store", dest="databasepassword", default=None, help="specify database password")
    # databaseargs.add_argument("--databaseport", action="store", dest="databaseport", default=5432, type=int, help="specify database port")

    args = parser.parse_args()
    # ttyio.echo("args=%r" % (args), level="debug")

    locale.setlocale(locale.LC_ALL, "")

    currentplayer = startup(args)
    mainmenu(args, currentplayer)
    return    

if __name__ == "__main__":
    main()
