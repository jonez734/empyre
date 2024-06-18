from bbsengine6 import io

from .. import lib as libempyre

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

def main(args, **kw):
    return libempyre.runmodule(args, "main", **kw)
