import random

import ttyio5 as ttyio
import bbsengine5 as bbsengine

from . import lib

def init(args, **kw):
    pass

def plague(player):
    res = []

    x = random.randint(0, player.serfs//4) # int(random.random()*player.serfs/4)
    if x > 0:
        res.append("{var:empyre.highlightcolor}%s{/all}" % (bbsengine.pluralize(x, "serf", "serfs")))
        player.serfs -= x

    x = random.randint(0, player.soldiers//2) # int(random.random()*player.soldiers/2)
    if x > 0:
        player.soldiers -= x
        res.append("{var:empyre.highlightcolor}%s{/all}" % (bbsengine.pluralize(x, "soldier", "soldiers")))

    x = random.randint(0, player.nobles//3) # int(random.random()*player.nobles/3)
    if x > 0:
        player.nobles -= x
        res.append("{var:empyre.highlightcolor}%s{/all}" % (bbsengine.pluralize(x, "noble", "nobles")))

    if len(res) > 0:
        ttyio.echo("P L A G U E ! %s died" % (bbsengine.oxfordcomma(res)))

def rats(player):
    x = random.randint(1, player.grain//3) # int(random.random()*player.grain/3)
    player.grain -= x
    ttyio.echo("EEEK! rats eat :crop: {var:empyre.highlightcolor}%s{/all} of grain!" % (bbsengine.pluralize(x, "bushel", "bushels")))

def earthquake(player):
    x = bbsengine.diceroll(100) # random.randint(1, 100))
    if x < 85:
        return
    if player.palaces > 0 and player.nobles > 0:
        player.palaces -= 1
        player.nobles -= 1
        ttyio.echo("EARTHQUAKE!")
        ttyio.echo()
        ttyio.echo("{orange}1 noble was killed{/all}")
        if player.palaces == 0:
            ttyio.echo("Your last palace has been destroyed!")
        elif player.palaces == 1:
            ttyio.echo("You have one palace remaining!")
        else:
            ttyio.echo("One of your palaces was destroyed")
        # &"{orange}One of your Palace(s) was destroyed!{pound}$l1 noble was killed."

def volcano(player):
    res = []

    x = random.randint(0, player.markets//3) # int(random.random()*player.markets/3)
    if x > 0:
        res.append(bbsengine.pluralize(x, "market", "markets"))
        player.markets -= x

    x = random.randint(0, player.mills//4) # int(random.random()*player.mills/4)
    if x > 0:
        res.append(bbsengine.pluralize(x, "mill", "mills"))
        player.mills -= x

    x = random.randint(0, player.foundries//3) # int(random.random()*player.foundries/3)
    if x > 0:
        res.append(bbsengine.pluralize(x, "foundry", "foundries"))
        player.foundries -= x

    if len(res) > 0:
        ttyio.echo("Mount Apocolypse has erupted!{F6}Lava wipes out %s" % (bbsengine.oxfordcomma(res)))

def tidalwave(player):
    if player.shipyards > 0:
        x = random.randint(0, player.shipyards//2) # int(random.random()*player.shipyards/2)
        if x > 0:
            ttyio.echo("TIDAL WAVE!{F6:2}{blue}{var:empyre.highlightcolor}%s under water!" % (bbsengine.pluralize(x, "shipyard is", "shipyards are")))

def main(args, **kw) -> bool:
    player = kw["player"] if "player" in kw else None
    disaster = kw["disaster"] if "disaster" in kw else bbsengine.diceroll(12)
    if args.debug is True:
        ttyio.echo("disaster.200: disaster=%s" % (disaster), level="debug")
    
    ttyio.echo("{/all}")

    if disaster == 2:
        plague(player)
    elif disaster == 3:
        rats(player)
    elif disaster == 4:
        earthquake(player)
    elif disaster == 5:
        volcano(player)
    elif disaster == 6:
        tidalwave(player)
    ttyio.echo("{/all}")
    return True
