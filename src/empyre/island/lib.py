from bbsengine6 import io
from .. import lib as libempyre

def checkmodule(args, modulename, **kw):
    return libempyre.checkmodule(args, f"island.{modulename}", **kw)

def runmodule(args, modulename, **kw):
    return libempyre.runmodule(args, f"island.{modulename}", **kw)
