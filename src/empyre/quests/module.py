import ttyio6 as ttyio
import bbsengine6 as bbsengine

SUBMODULENAME = "quests"
PACKAGENAME = "empyre"

def init(args=None, **kwargs):
#    ttyio.setvariable("empyre.highlightcolor", "{bggray}{white}")
#    ttyio.echo("empyre.boot.init", level="debug")
    return True

def access(args, op, **kwargs):
    if args.debug is True:
        ttyio.echo(f"empyre.module.access.100: {args=} {op=} {kw=}", level="debug")
    return True

def buildargs(args=None, **kwargs):
    return None
    
def checkmodule(args, module, **kwargs):
    module = f"{PACKAGENAME}.{SUBMODULENAME}.{module}"
    return bbsengine.module.check(args, module, **kwargs)

def runmodule(args, module, **kwargs):
    module = f"{PACKAGENAME}.{SUBMODULENAME}.{module}"
    if args.debug is True:
        ttyio.echo(f"empyre.lib.runmodule.100: {module=}", level="debug")

    if bbsengine.module.check(args, module, **kwargs) is False:
        ttyio.echo(f"empyre.lib.runmodule.120: module {module!r} not available", level="error")
        return False

#    return bbsengine.module.runmodule(args, x, player=player, **kwargs)
    return bbsengine.module.runmodule(args, module, **kwargs)

def runsubmodule(args, submodule, **kwargs):
    if args.debug is True:
        ttyio.echo(f"empyre.module.runsubmodule.100: {submodule=}", level="debug")
    return runmodule(args, submodule, **kwargs)

def main(args, **kwargs):
#    bbsengine.util.heading("empyre combat")
    if runsubmodule(args, "main", player=player, **kwargs) is False:
        ttyio.echo("error running submodule 'main'", level="error")
    return    
