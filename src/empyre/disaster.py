import random

from bbsengine6 import io, util

from . import lib

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args=None, **kwargs):
    return None

def _handle_damage(player, resourcename, amount):
    if not hasattr(player, resourcename):
        io.echo(f"Player {player.moniker} does not have the resource {resourcename}", level="warn")
        return False

    current_value = getattr(player, resourcename)
    new_value = current_value - amount
    setattr(player, resourcename, new_value)

    res = player.getresource(resourcename)
    return util.pluralize(amount, **res)

def plague(player):
    damage = []

    x = random.randint(0, player.serfs//4) # int(random.random()*player.serfs/4)
    if x > 0:
        res = _handle_damage(player, "serfs", x)
        damage.append(res)

    x = random.randint(0, player.soldiers//2) # int(random.random()*player.soldiers/2)
    if x > 0:
        res = _handle_damage(player, "soldiers", x)
        damage.append(res)

    x = random.randint(0, player.nobles//3) # int(random.random()*player.nobles/3)
    if x > 0:
        res = _handle_damage(player, "nobles", x)
        damage.append(res)

    if len(res) > 0:
        io.echo(f"P L A G U E ! {util.oxfordcomma(damage)} died")

def rats(player):
    x = random.randint(1, player.grain//3) # int(random.random()*player.grain/3)
    res = _handle_damage(player, "grain", x)
    io.echo(f"EEEK! rats eat {res} of grain!")

def earthquake(player):
    x = util.diceroll(100) # random.randint(1, 100))
    if x < 85:
        return True

    if player.palaces > 0 and player.nobles > 0:
        player.palaces -= 1
        player.nobles -= 1
        io.echo("EARTHQUAKE!{f6}")
        io.echo("{orange}1 noble was killed{/all}")
        if player.palaces == 0:
            io.echo("Your last palace has been destroyed!")
        elif player.palaces == 1:
            io.echo("You have one palace remaining!")
        else:
            io.echo("One of your palaces was destroyed")
        # &"{orange}One of your Palace(s) was destroyed!{pound}$l1 noble was killed."

def volcano(player):
    damage = []

    x = random.randint(0, player.markets//3) # int(random.random()*player.markets/3)
    if x > 0:
        res = _handle_damage(player, "markets", x)
        damage.append(res)

    x = random.randint(0, player.mills//4) # int(random.random()*player.mills/4)
    if x > 0:
        res = _handle_damage(player, "mills", x)
        damage.append(res)

    x = random.randint(0, player.foundries//3) # int(random.random()*player.foundries/3)
    if x > 0:
        res = _handle_damage(player, "foundries", x)
        damage.append(res)

    if len(damage) > 0:
        io.echo("Mount Apocolypse has erupted!{F6}Lava wipes out %s" % (util.oxfordcomma(damage)))

def tidalwave(player):
    x = random.randint(0, player.shipyards//2) # int(random.random()*player.shipyards/2)
    if player.shipyards >= x:
        shipyardres = player.getresource("shipyards")
        _handle_damage(player, "shipyards", x)
        io.echo("TIDAL WAVE!{F6:2}%s under water!" % (util.pluralize(x, "shipyard is", "shipyards are", emoji=":anchor:")))
    return

def main(args, **kwargs) -> bool:
    player = kwargs.get("player", None)
    disaster = kwargs.get("disaster", util.diceroll(12))
    save = kwargs.get("save", True)
    io.echo(f"disaster.200: {disaster=}", level="debug")
    
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
    io.echo("{/all}", end="", flush=True)
    if save is True:
        player.adjust()
        player.save()
    else:
        io.echo("skipped adjust+save")
    return True
