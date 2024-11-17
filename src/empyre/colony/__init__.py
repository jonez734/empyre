from bbsengine6 import io, util
from .. import lib as libempyre

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

def main(args, **kw):
    util.heading("colony")
    return libempyre.runmodule("main")
