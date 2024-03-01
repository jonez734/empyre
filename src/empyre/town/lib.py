from bbsengine6 import io
from .. import lib as empyre

def runmodule(args, modulename, **kw):
    return empyre.runmodule(args, f"town.{modulename}", **kw)

def checkmodule(args, modulename, **kw):
    return empyre.checkmodule(args, f"town.{modulename}", **kw)
