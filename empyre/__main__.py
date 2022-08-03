import time
import locale
import argparse

import ttyio5 as ttyio
import bbsengine5 as bbsengine

from . import lib

import _empyreversion

PRG = "empyre"

def init(args=None):
    ttyio.setvariable("empyre.highlightcolor", "{bggray}{white}")
    return True

def buildargs(args=None):
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

    lib.setarea(args, None, "startup")
    # ttyio.echo("empyre.startup.100: args=%r" % (args))
    currentmemberid = bbsengine.getcurrentmemberid(args)
    if args.debug is True:
        ttyio.echo("startup.300: currentmemberid=%r" % (currentmemberid), level="debug")
    player = lib.getplayer(args, currentmemberid)
    if player is None:
        ttyio.echo("startup.200: new player", level="debug")
        player = newplayer(args)
        lib.newsentry(args, player, "New Player %r!" % (player.name))

#    currentplayer = startup(args)
    lib.setarea(args, player, "rev: %s" % (_empyreversion.__version__))
    if lib.runsubmodule(args, player, "mainmenu") is not True:
        ttyio.echo("error running submodule 'mainmenu'", level="error")
    return    

if __name__ == "__main__":
    parser = buildargs()
    args = parser.parse_args()

    ttyio.echo("{f6:3}{cursorup:3}")
    bbsengine.initscreen(bottommargin=1)

    locale.setlocale(locale.LC_ALL, "")
    time.tzset()

    init(args)

    try:
        main(args)
    except KeyboardInterrupt:
        ttyio.echo("{/all}{bold}INTR{bold}")
    except EOFError:
        ttyio.echo("{/all}{bold}EOF{/bold}")
    finally:
        ttyio.echo("{decsc}{curpos:%d,0}{el}{decrc}{reset}{/all}" % (ttyio.getterminalheight()))
