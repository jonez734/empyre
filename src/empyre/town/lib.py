from bbsengine6 import io
from .. import lib as empyre

def runmodule(args, modulename, **kwargs):
    return empyre.runmodule(args, f"town.{modulename}", **kwargs)

def checkmodule(args, modulename, **kwargs):
    return empyre.checkmodule(args, f"town.{modulename}", **kwargs)
