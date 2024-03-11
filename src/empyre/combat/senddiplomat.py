from bbsengine6 import io, util

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

# @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/plus_emp6_combat.lbl#L53
def main(args, **kw):
    player = kw["player"] if "player" in kw else None
    otherplayer = kw["otherplayer"] if "otherplayer" in kw else None
    if player is None:
        io.echo("You do not exist! Go Away!")
        return False

    if player.diplomats < 1:
        io.echo("{F6:2}{yellow}You have no diplomats!{F6:2}{/all}")
        return False

    io.echo("{F6}{purple}Your diplomat rides to the enemy camp...")
    if otherplayer.soldiers < player.soldiers*2:
        land = otherplayer.land // 15
        otherplayer.land -= land
        player.land += land
        res = player.getresource("land")
        io.echo("{F6}{green}Your noble returns with good news! To avoid attack, you have been given {util.pluralize(land, **res)} of land!")
    else:
        player.nobles -= 1
        io.echo(f"{{orange}}{otherplayer.moniker} {{red}}BEHEADS{{orange}} your noble and tosses their corpse into the moat!")
    player.adjust()
    player.save()
    otherplayer.adjust()
    otherplayer.save()
    return
