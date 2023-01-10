import ttyio5 as ttyio
import bbsengine5 as bbsengine

from . import lib

# @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_maint.lbl#L6
# @since 20200831 written
# @since 20220730 converted to a submodule

def init(args, **kw):
    pass

def access(args, op, **kw):
    ttyio.echo("empyre.maint.access.100: trace")
#    sysop = False
    sysop = bbsengine.checkflag(args, "SYSOP")
    if sysop is True:
        return True
    ttyio.echo("empyre.sysopoptions.access.100: permission denied")
    return False

