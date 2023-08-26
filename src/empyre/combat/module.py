import argparse

import ttyio6 as ttyio
import bbsengine6 as bbsengine

from . import lib
from . import _version

def init(args=None, **kw):
#    ttyio.setvariable("empyre.highlightcolor", "{bggray}{white}")
#    ttyio.echo("empyre.boot.init", level="debug")
    return True

def access(args, op, **kw):
    if args.debug is True:
        ttyio.echo(f"empyre.module.access.100: {args=} {op=} {kw=}", level="debug")
    return True

def buildargs(args=None, **kw):
    parser = argparse.ArgumentParser("empyre")
    parser.add_argument("--verbose", action="store_true", dest="verbose")
    parser.add_argument("--debug", action="store_true", dest="debug")

    defaults = {"databasename": "zoid6", "databasehost":"localhost", "databaseuser": None, "databaseport":5432, "databasepassword":None}
    bbsengine.database.buildargdatabasegroup(parser, defaults)

    return parser
    
def main(args, **kw):
    if args is not None and "debug" in args and args.debug is True:
        ttyio.echo(f"empyre.main.100: args={args!r}", level="debug")

    bbsengine.util.heading("empyre")

    if args.debug is True:
        ttyio.echo("database: %s host: %s:%s" % (args.databasename, args.databasehost, args.databaseport), level="debug")

    lib.setarea(args, None, "startup %s rev %s" % (_version.__datestamp__, _version.__version__))

    currentmemberid = bbsengine.member.getcurrentid(args)
    if args.debug is True:
        ttyio.echo("startup.300: currentmemberid=%r" % (currentmemberid), level="debug")
    player = lib.getplayer(args, currentmemberid)
    if player is None:
        ttyio.echo("startup.200: new player", level="debug")
        player = lib.Player(args)
        player.new()
        lib.newsentry(args, player, f"New Player {player.name}!")

    if runsubmodule(args, "main", player=player, **kw) is False:
        ttyio.echo("error running submodule 'main'", level="error")
    return    

def checkmodule(args, player, module, **kw):
    module = f"{lib.PACKAGENAME}.{module}"
    return bbsengine.module.check(args, module, **kw)

def runmodule(args, module, **kw):
    x = "%s.%s" % (lib.PACKAGENAME, module)
    if args.debug is True:
        ttyio.echo("empyre.lib.runmodule.100: x=%r" % (x), level="debug")

    if bbsengine.module.check(args, x, **kw) is False:
        ttyio.echo("empyre.lib.runmodule.120: module %r not available" % (x), level="error")
        return False

#    return bbsengine.module.runmodule(args, x, player=player, **kw)
    return bbsengine.module.runmodule(args, x, **kw)

def runsubmodule(args, submodule, **kw):
#    if "player" not in kw:
#        kw["player"] = player

    if args.debug is True:
        ttyio.echo(f"empyre.module.runsubmodule.100: submodule={submodule!r}", level="debug")
    return runmodule(args, submodule, **kw)
