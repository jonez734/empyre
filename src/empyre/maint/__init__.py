#import ttyio6 as ttyio
#import bbsengine6 as bbsengine
from bbsengine6 import io

from . import lib

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

def main(args, **kw):
    io.echo("empyre.maint.__init__.main.100: trace", level="debug")
    return lib.runmodule(args, "main", **kw)
