from .. import lib as libempyre

def runmodule(args, modulename, **kw):
    return libempyre.runmodule(args, f"combat.{modulename}", **kw)
