# @since 20220731 started as part of new submodule called quests

import ttyio5 as ttyio

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def main(args, **kw):
    player = kw["player"] if "player" in kw else None

    if isquestcompleted() is True:
        ttyio.echo("You gain :horse: 30 horses.") # %s." % (bbsengine.pluralize(30, "horse", "horses")))
        player.horses += 30
        return True
    else:
        ttyio.echo("For this attempt, you were not victorious.")
        return False
