# @since 20220731 started as part of new submodule called quests

from bbsengine6 import io, util

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args, **kwargs):
    return None

def main(args, **kwargs):
    player = kwargs["player"] if "player" in kwargs else None
    if player is None:
        io.echo("You do not exist! Go Away!", level="error")
        return False

    if isquestcompleted() is True:
        horseres = player.getresource("horses")
        io.echo(f"{{labelcolor}}You gain {{valuecolor}}{util.pluralize(30, **horseres)}")
        player.horses += 30
        player.adjust()
        player.save()
        return True

    io.echo("For this attempt, you were not victorious.")
    return False
