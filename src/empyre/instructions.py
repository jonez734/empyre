import bbsengine5 as bbsengine

# from . import lib
from . import data

def main(args, **kw):
    bbsengine.filedisplay(args, data.get("instructions.txt"))
#    bbsengine.filedisplay(args, bbsengine.buildfilepath(lib.DATADIR, "instructions.txt"))
    return True
