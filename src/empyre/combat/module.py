import argparse

import ttyio6 as ttyio
import bbsengine6 as bbsengine

SUBMODULENAME = "combat"
PACKAGENAME = "empyre"

def init(args=None, **kw):
#    ttyio.setvariable("empyre.highlightcolor", "{bggray}{white}")
#    ttyio.echo("empyre.boot.init", level="debug")
    return True

def access(args, op, **kw):
    if args.debug is True:
        ttyio.echo(f"empyre.module.access.100: {args=} {op=} {kw=}", level="debug")
    return True

def buildargs(args=None, **kw):
    return None
    
def checkmodule(args, module, **kw):
    module = f"{PACKAGENAME}.{SUBMODULENAME}.{module}"
    return bbsengine.module.check(args, module, **kw)

def runmodule(args, module, **kw):
    module = f"{PACKAGENAME}.{SUBMODULENAME}.{module}"
    if args.debug is True:
        ttyio.echo(f"empyre.lib.runmodule.100: {module=}", level="debug")

    if bbsengine.module.check(args, module, **kw) is False:
        ttyio.echo(f"empyre.lib.runmodule.120: module {module!r} not available", level="error")
        return False

#    return bbsengine.module.runmodule(args, x, player=player, **kw)
    return bbsengine.module.runmodule(args, module, **kw)

def runsubmodule(args, submodule, **kw):
    if args.debug is True:
        ttyio.echo(f"empyre.module.runsubmodule.100: {submodule=}", level="debug")
    return runmodule(args, submodule, **kw)

def main(args, **kw):
#    bbsengine.util.heading("empyre combat")
    if runsubmodule(args, "main", player=player, **kw) is False:
        ttyio.echo("error running submodule 'main'", level="error")
    return
