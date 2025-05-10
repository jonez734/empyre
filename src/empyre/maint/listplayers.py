#import ttyio6 as ttyio
#import bbsengine6 as bbsengine
from bbsengine6 import io, member, util, database

from .. import lib, player as libplayer

def init(args, **kw):
    io.setvariable("acscolor", "{white}")
    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

# @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/Empire6.lbl#L69
def main(args:object, player=None, **kwargs):
    def _work(conn):
        sql = "select membermoniker, moniker from empyre.player order by (resources->'land'->>'value') desc"
        dat = ()
        with database.cursor(conn) as cur:
            cur.execute(sql, dat)
            if cur.rowcount > 0:
                io.echo("{/all}{acscolor}{acs:ulcorner}{acs:hline:%s}{acs:urcorner}" % (terminalwidth-2), wordwrap=False)
                io.echo("{acscolor}{acs:vline}{gray} name %s{/all} {acscolor}{acs:vline}" % ("land".rjust(terminalwidth-len("land")-5)), wordwrap=False)
                io.echo("{acscolor}{acs:ltee}%s{acscolor}{acs:rtee}" % (util.hr(chars="-=", color="{acscolor}", width=terminalwidth-2, padding="")), wordwrap=False)
                # player = lib.Player(args, conn=conn)
                io.echo(f"empyre.maint.listplayers.100: {kwargs=}", level="debug")
                sysop = member.checkflag(args, "SYSOP", conn=conn, **kwargs)
                io.echo(f"empyre.maint.listplayers.120: {sysop=}", level="debug")
                cycle = 0
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

                    rightbuf = "%s" % ("{:>6n}".format(p.land))
                    rightbuflen = len(rightbuf)
                    buf = f"{{acscolor}}{{acs:vline}}%s %s%s {{/all}}{{acscolor}}{{acs:vline}}" % (color, leftbuf.ljust(terminalwidth-rightbuflen-4), rightbuf)
                    io.echo(buf, wordwrap=False)

                    cycle += 1
                    cycle %= 2

                io.echo(f"{{acscolor}}{{acs:llcorner}}%s{{acs:lrcorner}}" % (util.hr(chars="-=", color=f"{{acscolor}}", width=terminalwidth-2, padding="")))
            else:
                io.echo("no other rulers")
            return True
    
    io.echo(f"empyre.maint.listplayers.220: {kwargs=}", level="debug")
    util.heading("list players")
    terminalwidth = io.getterminalwidth()
    conn = kwargs.get("conn", None)
    if conn is None:
        pool = kwargs.get("pool", None)
        if pool is None:
            io.echo(f"empyre.maint.listplayer.200: {pool=}", level="error")
            return False
        with database.connect(args, pool=pool) as conn:
            return _work(conn)
    else:
        return _work(conn)
