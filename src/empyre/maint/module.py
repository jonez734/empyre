import ttyio6 as ttyio

from .. import module as empyre

SUBMODULENAME = "maint"

def init(args=None, **kw):
#    ttyio.setvariable("empyre.highlightcolor", "{bggray}{white}")
#    ttyio.echo("empyre.boot.init", level="debug")
    return True

def access(args, op, **kw):
    if args.debug is True:
        ttyio.echo(f"empyre.{SUBMODULENAME}.access.100: {args=} {op=} {kw=}", level="debug")
    return True

def buildargs(args=None, **kw):
    return None
    
def checkmodule(args, module, **kw):
    module = f"{SUBMODULENAME}.{module}"
    return empyre.checkmodule(args, module, **kw)

def runmodule(args, module, **kw):
    module = f"{SUBMODULENAME}.{module}"
    if args.debug is True:
        ttyio.echo(f"empyre.{SUBMODULENAME}.runmodule.100: {module=}", level="debug")

    if empyre.checkmodule(args, module, **kw) is False:
        ttyio.echo(f"empyre.{SUBMODULENAME}.runmodule.120: module {module!r} not available", level="error")
        return False

    return empyre.runmodule(args, module, **kw)

def runsubmodule(args, submodule, **kw):
    if args.debug is True:
        ttyio.echo(f"empyre.{SUBMODULENAME}.runsubmodule.100: {submodule=}", level="debug")
    return runmodule(args, submodule, **kw)

def main(args, **kw):
    if runsubmodule(args, "main", player=player, **kw) is False:
        ttyio.echo("error running submodule 'main'", level="error")
    return    
