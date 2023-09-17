import ttyio6 as ttyio
import bbsengine6 as bbsengine

from . import module

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

def main(args, **kw):
    return module.runsubmodule(args, "main", **kw)
