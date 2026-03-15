import bbsengine6 as bbsengine

# from . import lib
from . import data

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args, **kwargs):
    return None

def main(args, **kwargs):
    bbsengine.util.filedisplay(data.get("instructions.txt"))
#    bbsengine.filedisplay(args, bbsengine.buildfilepath(lib.DATADIR, "instructions.txt"))
    return True
