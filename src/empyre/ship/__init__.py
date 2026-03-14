from . import lib
from bbsengine6 import io, listbox

def init(args, **kwargs) -> bool:
    return True

def access(args, op: str, **kwargs) -> bool:
    return True

def buildargs(args, **kwargs):
    return None

def main(args, **kwargs):
    listbox.init()

    io.echo(f"empyre.ship.main.100: {kwargs.get('pool')=}", level="debug")
    return lib.runmodule(args, "main", **kwargs)
