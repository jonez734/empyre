import bbsengine6 as bbsengine

# from . import lib
from . import data

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

def main(args, **kw):
    bbsengine.util.filedisplay(data.get("instructions.txt"))
#    bbsengine.filedisplay(args, bbsengine.buildfilepath(lib.DATADIR, "instructions.txt"))
    return True
