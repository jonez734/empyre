# @since 20220731 created quests.raidpiratecamp.py

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

def main(args, **kw):
    player = kw["player"] if "player" in kw else None

    ttyio.echo("player.coins=%r" % (player.coins), level="debug")

    if isquestcompleted() is True:
        ttyio.echo("You gain {}.".format(bbsengine.pluralize(30000, "coin", "coins", emoji=":moneybag:")))
        player.coins += 30000
        result = True
    else:
        ttyio.echo("You failed to complete this quest.")
        result = False
    ttyio.echo(f"after completed check, {player.coins=}", level="debug")
    return result
