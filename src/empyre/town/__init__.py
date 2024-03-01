#import ttyio6 as ttyio
#import bbsengine6 as bbsengine
from bbsengine6 import io, util

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
        io.echo("You do not exist! Go Away!", level="error")
        return False

    return lib.runmodule(args, "main", **kw)
