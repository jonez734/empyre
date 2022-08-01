import bbsengine5 as bbsengine

from . import lib

def main(args, **kw):
    bbsengine.filedisplay(args, bbsengine.buildfilepath(lib.DATADIR, "instructions.txt"))
    return True
