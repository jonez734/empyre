#import ttyio6 as ttyio
#import bbsengine6 as bbsengine
from bbsengine6 import io, member, util, database

from .. import player as libplayer

def init(args, **kw):
##    io.setvariable("acscolor", "{white}")
    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

# @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/Empire6.lbl#L69
def main(args:object, player=None, **kwargs):
    def _work(conn):
        width = io.terminal.width() - 2
        sql = "select membermoniker, moniker from empyre.player order by (resources->'land'->>'value') desc"
        dat = ()
        with database.cursor(conn) as cur:
            cur.execute(sql, dat)
            if cur.rowcount > 0:
                io.echo(f"{{/all}} {{boxcolor}}{{ulcorner}}{{hline:{width-2}}}{{urcorner}}", wordwrap=False)
                io.echo(f"{{boxcolor}} {{vline}}{{titlecolor}} moniker {'land'.rjust(width-12)}{{/all}} {{boxcolor}}{{vline}}", wordwrap=False)
                io.echo(f"{{boxcolor}} {{rtee}}{{hline:{width-2}}}{{ltee}}")

                cycle = 0

                sysop = member.checkflag(args, "SYSOP", conn=conn, **kwargs)
###                io.echo(f"empyre.maint.listplayers.120: {sysop=}", level="debug")

                for rec in database.resultiter(cur):
                    if cycle == 0:
                        color = "{white}"
                    else:
                        color = "{lightgray}"
                    moniker = rec["moniker"]
                    p = libplayer.load(args, moniker, conn=conn, **kwargs)
                    if sysop is True:
                        leftbuf  = f"{p.moniker} ({p.membermoniker})" # "({:>4n}".format(player.memberid))
                    else:
                        leftbuf  = f"{p.moniker}" # "({:>4n}".format(player.memberid))

                    rightbuf = f"{p.land:>6n}"
                    rightbuflen = len(rightbuf)
                    buf = f" {{boxcolor}}{{vline}}{color} {leftbuf}{rightbuf.rjust(width-len(leftbuf)-4)}{{boxcolor}} {{vline}}"
                    io.echo(buf, wordwrap=False)

                    cycle += 1
                    cycle %= 2

                io.echo(f" {{boxcolor}}{{llcorner}}{{hline:{width-2}}}{{lrcorner}}", wordwrap=False)
            else:
                io.echo("no other rulers")
            return True
    
###    io.echo(f"empyre.maint.listplayers.220: {kwargs=}", level="debug")
    util.heading("list players")
    terminalwidth = io.terminal.width()
    pool = kwargs.get("pool", None)
    if pool is None:
        io.echo(f"empyre.maint.listplayer.200: {pool=}", level="error")
        return False
    with database.connect(args, pool=pool) as conn:
        return _work(conn)
