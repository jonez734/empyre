# @since 20220803 created 'sail' module

from bbsengine6 import io, util
from . import lib

def access(args, op, **kwargs):
    return

def init(args, **kwargs):
    return

def main(args, **kwargs):
    bbsengine.util.heading("sail")
    io.echo(f"setting sail {kwargs=}", level="debug")

    ship = kwargs.get("ship", None)
    if ship is None:
        io.echo("ship must be specified", level="error")
        return False
    return
