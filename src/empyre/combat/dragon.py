def init(args, **kw):
    return True

def main(args, **kw):
    player = kw["player"] if "player" in kw else None
    if player is None:
        ttyio.echo("you do not exist! go away!")
        return False

    if player.dragons < 0:
        player.dragons = 0
        return True

        ttyio.echo("You do not have any dragons.")
        return True

    ttyio.echo("You have %s" % (bbsengine.pluralize(player.dragons, "dragon", "dragons")))
    if player.dragons > 0:
        if ttyio.inputboolean("Unleash a dragon? [yN]: ", "N") is False:
            return True

    foo = []
    n = otherplayer.grain//10
    x = bbsengine.diceroll(n)
    if x > 0:
        otherplayer.grain -= x
        foo.append(":crop: %s of grain baked" % (bbsengine.pluralize(x, "bushel", "bushels")))

    n = otherplayer.serfs//10
    x = bbsengine.diceroll(n)
    if x > 0:
        otherplayer.serfs -= x
        foo.append("%s BBQ'd" % (bbsengine.pluralize(x, "serf", "serfs")))

    n = otherplayer.horses//10
    x = bbsengine.diceroll(n)
    if x > 0:
        otherplayer.horses -= x
        foo.append(":horse: %s roasted" % (bbsengine.pluralize(x, "horse", "horses")))
    n = otherplayer.acres//10
    x = bbsengine.diceroll(n)
    if x > 0:
        otherplayer.acres -= x
        foo.append("%s incinerated" % (bbsengine.pluralize(x, "acre", "acres")))

    if bbsengine.diceroll(40) < 21 and player.dragons > 0:
        player.dragons -= 1
        if player.dragons == 0:
            foo.append("your last dragon was killed!")
        else:
            foo.append("a dragon was killed!")
    ttyio.echo(bbsengine.oxfordcomma(foo))
    player.adjust()
    player.save()
    otherplayer.adjust()
    otherplayer.save()
