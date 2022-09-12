import bbsengine5 as bbsengine

# from . import lib
from . import data

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def main(args, **kw):
    bbsengine.filedisplay(args, data.get("instructions.txt"))
#    bbsengine.filedisplay(args, bbsengine.buildfilepath(lib.DATADIR, "instructions.txt"))
    return True
