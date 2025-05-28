import time
import copy
import math
import random
import argparse
from argparse import Namespace

from enum import Enum

from . import player as libplayer

class ShipKind(str, Enum):
    PASSENGER = "passenger"
    CARGO = "cargo"

# from dateutil.tz import tzlocal

from bbsengine6 import io, member, database, util, screen, module, listbox

from . import player

#TURNSPERDAY:int = 10
PACKAGENAME:str = "empyre"
#SHIPSPERSHIPYARD:int = 10
#HORSESPERSTABLE:int = 50
#SOLDIERSPERNOBLE:int = 20
#SOLDIERS:int = 40
#TAXRATE:int = 15
#COINS:int = 250000
#LAND:int = 5000
#MAXLAND:int = 2500000
#SERFS:int = 2000
#GRAIN:int = 20000
#MAXFOUNDRIES:int = 400
#MAXMARKETS:int = 500
#MAXMILLS:int = 500
#MAXCOINS:int = 1000000
#MAXSHIPYARDS:int = 10

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
        self.playermoniker:str = None
        self.membermoniker:str = None
        self.trees:int = 500

class Colony(object):
    def __init__(self, args):
        self.args = args

def setarea(args, buf, stack=False, **kwargs) -> None:
    player = kwargs.get("player", None)
    help = kwargs.get("help", None)

    def rightside():
        debug = True if args is not None and args.debug is True else False

        if player is not None:
            if player.isdirty() is True:
                isdirty = "*"
            else:
                isdirty = ""

            if player.turncount >= libplayer.TURNSPERDAY:
                player.turncount = libplayer.TURNSPERDAY

            turnremain = libplayer.TURNSPERDAY - player.turncount

            debug = " | debug" if args is not None and args.debug is True else ""

            coinres = player.getresource("coins")
            coinres["emoji"] = ""
            return f"empyre {{black}}|{{engine.areacolor}} {util.pluralize(turnremain, 'turn remains', 'turns remain')} {{black}}|{{engine.areacolor}} {isdirty}{player.moniker} {{black}}|{{engine.areacolor}} {util.pluralize(player.coins, **coinres)}{debug}"
        else:
            if debug is True:
                return "debug"
            else:
                return ""

    screen.setbottombar(buf, rightside, stack)
    #if args.debug is True:
    #    io.echo(f"empyre.setarea.100: {buf=} {stack=} {screen.areastack=}", level="debug")
    return

def generatename(args):
    # @see http://donjon.bin.sh/fantasy/name/#type=me;me=english_male @ty ryan
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
    ne["membermoniker"] = player.membermoniker
    ne["datecreated"] = "now()"
    if args.debug is True:
        io.echo(f"{ne=}", level="debug")
    neid = database.insert(args, "empyre.__newsentry", ne, returnid=True)
    if args.debug is True:
        io.echo(f"{neid=}", level="debug")
    database.commit(args)
    return

def trade(args, player:object, name:str, **kwargs:dict):
    price = kwargs.get("price", None)
    # name = kw["name"] if "name" in kw else None
    emoji = kwargs.get("emoji", "")
    singular = kwargs.get("singular", None)
    plural = kwargs.get("plural", None)
    io.echo(f"empyre.lib.trade.100: {price=} {player.coins=}", level="debug")
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
        value = resource.get("value", resource.get("default"))
        prompt = f"{{labelcolor}}You have {{valuecolor}}{util.pluralize(value, **resource)}{{labelcolor}} and {{valuecolor}}{util.pluralize(player.coins, 'coin', 'coins', emoji=':moneybag:')}{{F6}}{{promptcolor}}{name}: {{optioncolor}}[B]{{labelcolor}}uy {{optioncolor}}[S]{{labelcolor}}ell {{optioncolor}}(C){{labelcolor}}ontinue"
#        ttyio.echo("trade.120: prompt=%r" % (prompt), interpret=False)
        choices = "BSCYE"
        if member.checkflag(args, "SYSOP", **kwargs) is True:
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
            io.echo(f"Buy{{F6}}The barbarians will sell their {name} to you for {{var:valuecolor}}{util.pluralize(price, **coinres)}{{/all}}{{var:labelcolor}} each.")
            quantity = io.inputinteger(f"{{var:promptcolor}}buy how many?: {{var:inputcolor}}")
            if quantity is None or quantity < 1:
                break

            if player.coins < quantity*price:
                io.echo(f"{{var:labelcolor}}You have {{var:valuecolor}}:moneybag: {util.pluralize(player.coins, **coinres)} {{var:labelcolor}}and you need {{var:valuecolor}}:moneybag: {util.pluralize(abs(player.coins - quantity*price), 'more coin', 'more coins', **coinres)} to complete this transaction.")
                continue

            v = getattr(player, name)
            v += quantity

            setattr(player, name, int(v))
            player.coins -= quantity*price
            player.save()
            io.echo("Bought!")
            break
        elif ch == "S":
            io.echo(f"sell{{F6}}{{var:labelcolor}}The barbarians will buy your {plural} for {{var:valuecolor}}{util.pluralize(price, **coinres)}{{var:labelcolor}} each.")
            quantity = io.inputinteger("{{promptcolor}}sell how many?: {{inputcolor}}")
            if quantity is None or quantity < 1:
                break
            v = getattr(player, name)
            v -= quantity
            setattr(player, name, int(v))
            player.coins += quantity*price
            io.echo("Sold!", level="success")
            player.save()
            break

    player.adjust()
    player.save()
    return

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

def selectresource(args, title, resources, kind=None, **kw):
    class EmpyreResourceListboxItem(listbox.ListboxItem):
        def __init__(self, name:str, resource:dict, width:int, height:int=1, **kw:dict):
            super().__init__(self, resource, width)
            self.pk:str = name
            self.height:int = height
            self.width:int = width
            self.resource:dict = resource
            value = resource.get("value", resource.get("default"))
            left:str = f"{self.pk}"
#            io.echo(f"{self.res=}", level="debug")
            if isinstance(value, int) is True:
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
    database.buildargs(parser, defaults, suppress=True)

    return parser

def checkmodule(args, modulename:str, **kwargs:dict):
    x:str = f"{PACKAGENAME}.{modulename}"
#    if args.debug is True:
#    io.echo(f"empyre.lib.checkmodule.100: {x=}", level="debug")
    return module.check(args, x, **kwargs)

def runmodule(args, modulename:str, **kwargs:dict):
    x:str = f"{PACKAGENAME}.{modulename}"

#    io.echo(f"empyre.lib.runmodule.120: {x=} {modulename=}", level="debug")

    if checkmodule(args, modulename, **kwargs) is False:
        # io.echo(f"empyre.lib.runmodule.120: check of module {x!r} failed.", level="error")
        return False

    return module.runmodule(args, x, **kwargs)
