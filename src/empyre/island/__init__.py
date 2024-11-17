from bbsengine6 import io, util
from . import lib as libisland

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args, **kwargs):
    return None

def main(args, **kwargs):
    util.heading("island")
    player = kw["player"] if "player" in kw else None
    if player is None:
        io.echo("You do not exist! Go Away!", level="error")
        return False
    return libisland.runmodule("main")
