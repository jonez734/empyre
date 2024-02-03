from .. import lib as empyre

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

def runmodule(args, modulename, **kw):
    return empyre.runmodule(args, f"ship.{modulename}", **kw)

def main(args, **kw):
    empyre.runmodule(args, "ship.main", **kw)
