# @since 20220731 created quests.raidpiratecamp.py

def main(args, **kw):
    player = kw["player"] if "player" in kw else None

    ttyio.echo("player.coins=%r" % (player.coins), level="debug")

    if isquestcompleted() is True:
        ttyio.echo("You gain :moneybag: %s." % (bbsengine.pluralize(30000, "coin", "coins")))
        player.coins += 30000
        result = True
    else:
        ttyio.echo("You failed to complete this quest.")
        result = False
    ttyio.echo("after completed check, player.coins=%r" % (player.coins), level="debug")
    return result
