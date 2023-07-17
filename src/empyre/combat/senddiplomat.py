import ttyio6 as ttyio

def init(args, **kw):
    return True

# @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/plus_emp6_combat.lbl#L53
def main(args, **kw):
    player = kw["player"] if "player" in kw else None
    otherplayer = kw["otherplayer"] if "otherplayer" in kw else None
    if player is None:
        ttyio.echo("You do not exist! Go Away!")
        return False

    if player.diplomats < 1:
        ttyio.echo("{F6:2}{yellow}You have no diplomats!{F6:2}{/all}")
        return False
    ttyio.echo("{F6}{purple}Your diplomat rides to the enemy camp...")
    if otherplayer.soldiers < player.soldiers*2:
        land = otherplayer.land // 15
        otherplayer.land -= land
        player.land += land
        ttyio.echo("{F6}{green}Your noble returns with good news! To avoid attack, you have been given %s of land!" % (bbsengine.pluralize(land, "acre", "acres")))
    else:
        player.nobles -= 1
        ttyio.echo("{orange}%s {red}BEHEADS{orange} your noble and tosses their corpse into the moat!" % (otherplayer.name))
    player.adjust()
    player.save()
    otherplayer.adjust()
    otherplayer.save()
    return

