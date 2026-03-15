#import ttyio6 as ttyio
#import bbsengine6 as bbsengine
from bbsengine6 import io

from . import lib

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args, **kwargs):
    return None

def main(args, **kwargs):
    io.echo("empyre.maint.__init__.main.100: trace", level="debug")
    return lib.runmodule(args, "main", **kwargs)
