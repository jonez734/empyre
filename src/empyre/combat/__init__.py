# barbarians are buying
# @since 20201207
# @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/plus_emp6_combat.lbl#L178

from . import lib

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

def main(args, **kw):
    player = kw["player"] if "player" in kw else None
    if player is None:
        ttyio.echo("You do not exist! Go Away!", level="error")
        return False

    return lib.runmodule(args, "main", **kw)
