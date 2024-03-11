from bbsengine6 import io, util

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

def main(args, **kw):
    player = kw["player"] if "player" in kw else None
    if player is None:
        io.echo("you do not exist! go away!")
        return False

    otherplayer = kw["otherplayer"] if "otherplayer" in kw else None

#    player.adjust()
#    player.save()

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
        damages.append("baked {} of grain".format(util.pluralize(x, **res)))

    n = otherplayer.serfs//10
    x = util.diceroll(n)
    if x > 0:
        otherplayer.serfs -= x
        res = player.getresource("serfs")
        damages.append("BBQ'd {}".format(util.pluralize(x, **res)))

    n = otherplayer.horses//10
    x = util.diceroll(n)
    if x > 0:
        otherplayer.horses -= x
        res = player.getresource("horses")
        damages.append("roasted {}".format(util.pluralize(x, **res)))
    n = otherplayer.acres//10
    x = util.diceroll(n)
    if x > 0:
        otherplayer.acres -= x
        res = player.getresource("land")
        damages.append("incinerated {}".format(util.pluralize(x, **res)))

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
