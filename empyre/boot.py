import time
import locale
import argparse

import ttyio5 as ttyio
import bbsengine5 as bbsengine

from . import lib
from . import _version

def init(args=None, **kw):
    ttyio.setvariable("empyre.highlightcolor", "{bggray}{white}")
#    ttyio.echo("empyre.init")
    return True

def buildargs(args=None, **kw):
    parser = argparse.ArgumentParser("empyre")
    parser.add_argument("--verbose", action="store_true", dest="verbose")
    parser.add_argument("--debug", action="store_true", dest="debug")

    defaults = {"databasename": "zoidweb5", "databasehost":"localhost", "databaseuser": None, "databaseport":5432, "databasepassword":None}
    bbsengine.buildargdatabasegroup(parser, defaults)

    return parser
    
def main(args, **kwargs):
    ttyio.echo("empyre.main.140: args=%r" % (args), level="debug")

    if args is not None and "debug" in args and args.debug is True:
        ttyio.echo("empyre.main.100: args=%r" % (args))

    bbsengine.title("empyre")
    if args.debug is True:
        ttyio.echo("database: %s host: %s:%s" % (args.databasename, args.databasehost, args.databaseport), level="debug")

    lib.setarea(args, None, "startup %s rev %s" % (_version.__datestamp__, _version.__version__))

    currentmemberid = bbsengine.getcurrentmemberid(args)
    if args.debug is True:
        ttyio.echo("startup.300: currentmemberid=%r" % (currentmemberid), level="debug")
    player = lib.getplayer(args, currentmemberid)
    if player is None:
        ttyio.echo("startup.200: new player", level="debug")
        player = newplayer(args)
        lib.newsentry(args, player, "New Player %r!" % (player.name))

    if lib.runsubmodule(args, player, "mainmenu") is not True:
        ttyio.echo("error running submodule 'mainmenu'", level="error")
    return    
