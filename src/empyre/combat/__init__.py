# barbarians are buying
# @since 20201207
# @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/plus_emp6_combat.lbl#L178

from bbsengine6 import io
from . import lib


def init(args, **kwargs):
    return True


def access(args, op, **kwargs):
    return True


def buildargs(args=None, subparser=None, **kwargs):
    return None


def main(args, **kwargs):
    player = kwargs["player"] if "player" in kwargs else None
    if player is None:
        io.echo("You do not exist! Go Away!", level="error")
        return False

    return lib.runmodule(args, "main", **kwargs)
