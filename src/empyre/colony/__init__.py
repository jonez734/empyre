from bbsengine6 import io, util
from .. import lib as libempyre

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args, **kwargs):
    return None

def main(args, **kwargs):
    util.heading("colony")
    return libempyre.runmodule(args, "colony.main", **kwargs)
