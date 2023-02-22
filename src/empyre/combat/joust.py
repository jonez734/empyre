def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

# @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_tourney.lbl#L2
def main(args, **kw):
    player = kw["player"] if "player" in kw else None
    otherplayer = kw["otherplayer"] if "otherplayer" in kw else None
    if player.playerid == otherplayer.playerid:
        ttyio.echo("You cannot joust against yourself! Big mistake!")
        loss = bbsengine.diceroll(player.land//2)
        player.land -= loss
        ttyio.echo("You lost %s." % (bbsengine.pluralize(loss, "acre", "acres")))
        return True

    lib.setarea(args, player, "joust")

    ttyio.echo("joust.100: otherplayer=%r" % (otherplayer), level="debug")

    if player.horses == 0:
        ttyio.echo("You do not have a :horse: horse for your noble to use!")
        return True

    if player.serfs < 900:
        ttyio.echo("Not enough serfs attend. The joust is cancelled.")
        return True

    if otherplayer is None or otherplayer.nobles < 2:
        ttyio.echo("Your opponent does not have enough nobles.")
        return True

    ttyio.echo("{f6:2}Your Noble mounts his mighty steed and aims his lance... ", end="")
    # @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/plus_emp6_tourney.lbl#L12
    if player.nobles > otherplayer.nobles*2:
        # player.joustwin = True # nj=1
        player.nobles += 1
        otherplayer.nobles -= 1
        ttyio.echo("Your noble's lance knocks their opponent to the ground. They get up and swear loyalty to you!")
        # if nj=1 then tt$="{gray1}"+d2$+"{lt. blue}"+na$+"{white} wins joust - {lt. blue}"+en$+"{white} is shamed."
        lib.newsentry(args, player, "{lightblue}%s{white} wins joust - {lightblue}%s{white} is shamed" % (player.name, otherplayer.name))
        return True

    lost = []
    gained = []
    x = bbsengine.diceroll(10)
    ttyio.echo("x=%r" % (x), level="debug")
    if x == 1:
        player.land += 100
        gained.append("100 acres")
    elif x == 2:
        player.land -= 100
        if player.land < 1:
            lost.append("last acre")
        else:
            lost.append("100 acres")
    elif x == 3:
        player.coins += 1000
        gained.append(bbsengine.pluralize(1000, "coin", "coins"))
    elif x == 4:
        if player.coins >= 1000:
            player.coins -= 1000
            lost.append(bbsengine.pluralize(1000, "coin", "coins"))
    elif x == 5:
        player.nobles += 1
        gained.append("1 noble")
    elif x == 6:
        if player.nobles > 0:
            player.nobles -= 1
            if player.nobles < 1:
                lost.append("your last noble")
                player.nobles = 0
            else:
                lost.append("1 noble")
    elif x == 7:
        player.grain += 7000
        gained.append(bbsengine.pluralize(7000, "bushel", "bushels"))
    elif x == 8:
        if player.grain >= 7000:
            player.grain -= 7000
            lost.append(bbsengine.pluralize(7000, "bushel", "bushels"))
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
        res.append("lost " + bbsengine.oxfordcomma(lost))
    if len(gained) > 0:
        res.append("gained " + bbsengine.oxfordcomma(gained))
    
    if len(res) > 0:
        ttyio.echo("You have %s" % (bbsengine.oxfordcomma(res)))

    player.save()

    otherplayer.save()
    
    return True
