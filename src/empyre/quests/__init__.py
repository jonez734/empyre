from bbsengine6 import io

from .. import lib as libempyre

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args, **kwargs):
    return None

def main(args, **kwargs):
    return libempyre.runmodule(args, "main", **kwargs)
