from bbsengine6 import io, util

from .. import lib as libempyre

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

# @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_tourney.lbl#L2
def main(args, **kw):
    player = kw["player"] if "player" in kw else None
    if player is None:
        io.echo("You do not exist! Go Away!")
        return False
    otherplayer = kw["otherplayer"] if "otherplayer" in kw else None
    if player.playerid == otherplayer.playerid:
        io.echo("You cannot joust against yourself! Big mistake!")
        loss = util.diceroll(player.land//2)
        player.land -= loss
        res = player.getresource("land")
        io.echo("You lost %s." % (util.pluralize(loss, **res)))
        return True

    libempyre.setarea(args, "joust", player=player)

    io.echo(f"joust.100: {otherplayer=}", level="debug")

    if player.horses == 0:
        io.echo("You do not have a :horse: horse for your noble to use!")
        return True

    if player.serfs < 900:
        io.echo("Not enough serfs attend. The joust is cancelled.")
        return True

    if otherplayer is None or otherplayer.nobles < 2:
        io.echo("Your opponent does not have enough nobles.")
        return True

    io.echo("{f6:2}Your Noble mounts his mighty steed and aims his lance... ")
    # @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/plus_emp6_tourney.lbl#L12
    if player.nobles > otherplayer.nobles*2:
        # player.joustwin = True # nj=1
        player.nobles += 1
        otherplayer.nobles -= 1
        io.echo("Your noble's lance knocks their opponent to the ground. They get up and swear loyalty to you!")
        # if nj=1 then tt$="{gray1}"+d2$+"{lt. blue}"+na$+"{white} wins joust - {lt. blue}"+en$+"{white} is shamed."
        libempyre.newsentry(args, f"{{lightblue}}{player.moniker}{{white}} wins joust - {{lightblue}}{otherplayer.moniker}{{white}} is shamed", player=player)
        return True

    lost = []
    gained = []
    x = bbsengine.diceroll(10)
    io.echo(f"{x=}", level="debug")
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
            if player.nobles < 1:
                lost.append("your last noble")
                player.nobles = 0
            else:
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
        res.append("lost " + util.oxfordcomma(lost))
    if len(gained) > 0:
        res.append("gained " + util.oxfordcomma(gained))
    
    if len(res) > 0:
        io.echo("You have %s" % (util.oxfordcomma(res)))

    player.adjust()
    player.save()

    otherplayer.adjust()
    otherplayer.save()
    
    return True
