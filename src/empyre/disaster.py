import random

from bbsengine6 import io, util

from . import lib

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args=None, **kwargs):
    return None

def plague(player):
    res = []

    x = random.randint(0, player.serfs//4) # int(random.random()*player.serfs/4)
    if x > 0:
        res.append("{empyre.highlightcolor}%s{/all}" % (util.pluralize(x, "serf", "serfs")))
        player.serfs -= x

    x = random.randint(0, player.soldiers//2) # int(random.random()*player.soldiers/2)
    if x > 0:
        player.soldiers -= x
        res.append("{empyre.highlightcolor}%s{/all}" % (util.pluralize(x, "soldier", "soldiers")))

    x = random.randint(0, player.nobles//3) # int(random.random()*player.nobles/3)
    if x > 0:
        player.nobles -= x
        res.append("{empyre.highlightcolor}%s{/all}" % (util.pluralize(x, "noble", "nobles")))

    if len(res) > 0:
        io.echo("P L A G U E ! %s died" % (util.oxfordcomma(res)))

def rats(player):
    x = random.randint(1, player.grain//3) # int(random.random()*player.grain/3)
    player.grain -= x
    io.echo("EEEK! rats eat :crop: {empyre.highlightcolor}%s{/all} of grain!" % (util.pluralize(x, "bushel", "bushels")))

def earthquake(player):
    x = util.diceroll(100) # random.randint(1, 100))
    if x < 85:
        return
    if player.palaces > 0 and player.nobles > 0:
        player.palaces -= 1
        player.nobles -= 1
        io.echo("EARTHQUAKE!")
        io.echo()
        io.echo("{orange}1 noble was killed{/all}")
        if player.palaces == 0:
            io.echo("Your last palace has been destroyed!")
        elif player.palaces == 1:
            io.echo("You have one palace remaining!")
        else:
            io.echo("One of your palaces was destroyed")
        # &"{orange}One of your Palace(s) was destroyed!{pound}$l1 noble was killed."

def volcano(player):
    res = []

    x = random.randint(0, player.markets//3) # int(random.random()*player.markets/3)
    if x > 0:
        res.append(util.pluralize(x, "market", "markets"))
        player.markets -= x

    x = random.randint(0, player.mills//4) # int(random.random()*player.mills/4)
    if x > 0:
        res.append(util.pluralize(x, "mill", "mills"))
        player.mills -= x

    x = random.randint(0, player.foundries//3) # int(random.random()*player.foundries/3)
    if x > 0:
        res.append(util.pluralize(x, "foundry", "foundries"))
        player.foundries -= x

    if len(res) > 0:
        io.echo("Mount Apocolypse has erupted!{F6}Lava wipes out %s" % (util.oxfordcomma(res)))

def tidalwave(player):
    x = random.randint(0, player.shipyards//2) # int(random.random()*player.shipyards/2)
    if player.shipyards >= x:
        shipyardres = player.getresource("shipyards")
        io.echo("TIDAL WAVE!{F6:2}{blue}{var:empyre.highlightcolor}%s under water!" % (util.pluralize(x, "shipyard is", "shipyards are", emoji=":anchor:")))
        shipyardres["value"] -= x
    return

def main(args, **kwargs) -> bool:
    player = kwargs.get("player", None)
    disaster = kwargs.get("disaster", util.diceroll(12))
    io.echo(f"disaster.200: {disaster=}", level="debug")
    
    io.echo("{/all}")

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
    io.echo("{/all}")
    player.adjust()
    player.save()
    return True
