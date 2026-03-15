# from bbsengine6 import io
from .. import lib as libempyre

def checkmodule(args, modulename, **kwargs):
    return libempyre.checkmodule(args, f"island.{modulename}", **kwargs)

def runmodule(args, modulename, **kwargs):
    return libempyre.runmodule(args, f"island.{modulename}", **kwargs)
