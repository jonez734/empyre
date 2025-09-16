from bbsengine6 import io, util

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args, **kwargs):
    return None

def main(args, **kwargs):
    player = kwargs.get("player", None)
    if player is None:
        io.echo("you do not exist! go away!", level="error")
        return False

    otherplayer = kwargs.get("otherplayer", None)
    
    if otherplayer == player:
        if io.inputboolean("attacking yourself is a bad idea. Are you sure? [yN]: ") is False:
            io.echo("wise choice. aborted")
            return True

    if player.dragons < 0:
        player.dragons = 0
        return True

    if player.dragons == 0:
        io.echo("You do not have any dragons.")
        return True

    dragonsres = player.getresource("dragons")
    io.echo(f"{{var:labelcolor}}You have {{var:valuecolor}}{util.pluralize(player.dragons, **dragonres)}")
    if player.dragons > 0:
        if io.inputboolean("{var:promptcolor}Unleash a dragon? {var:optioncolor}[yN]{var:promptcolor}: {var:inputcolor}", "N") is False:
            return True

    damages = []
    n = otherplayer.grain//10
    x = util.diceroll(n)
    if x > 0:
        otherplayer.grain -= x
        res = player.getresource("grain")
        damages.append(f"baked {util.pluralize(x, **res)} of grain")

    n = otherplayer.serfs//10
    x = util.diceroll(n)
    if x > 0:
        otherplayer.serfs -= x
        res = player.getresource("serfs")
        damages.append(f"BBQ'd {util.pluralize(x, **res)}")

    n = otherplayer.horses//10
    x = util.diceroll(n)
    if x > 0:
        otherplayer.horses -= x
        res = player.getresource("horses")
        damages.append(f"roasted {util.pluralize(x, **res)}")
    n = otherplayer.acres//10
    x = util.diceroll(n)
    if x > 0:
        otherplayer.acres -= x
        res = player.getresource("land")
        damages.append(f"incinerated {util.pluralize(x, **res)}")

#    if util.diceroll(40) < 21 and player.dragons > 0:
#        player.dragons -= 1
#        if player.dragons == 0:
#            io.echo("Your last dragon was killed!")
#        else:
#            io.echo("One of your dragons was killed!")

    if len(damages) == 0:
        io.echo(f"{{var:labelcolor}}Your dragon *did not* damage the empyre of {{var:valuecolor}}{otherplayer.moniker}{{var:normalcolor}}")
        return True

    io.echo(f"Your dragon {util.oxfordcomma(damages)}")
    player.adjust()
    player.save()
    otherplayer.adjust()
    otherplayer.save()
