from bbsengine6 import database, io, member, util

from .. import player as libplayer


def init(args, **kwargs):
    return True


def access(args, op, **kwargs):
    return member.checkflag(args, "SYSOP", **kwargs)


def buildargs(args, **kwargs):
    return None


# @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/Empire6.lbl#L69
def main(args: object, player=None, **kwargs):
    def _work(conn):
        width = io.terminal.width() - 2
        sql = "select membermoniker, moniker from empyre.player order by (resources->'land'->>'value') desc"
        dat = ()
        with database.cursor(conn) as cur:
            cur.execute(sql, dat)
            if cur.rowcount > 0:
                io.echo(
                    f"{{/all}} {{boxcolor}}{{ulcorner}}{{hline:{width - 2}}}{{urcorner}}",
                    wordwrap=False,
                )
                io.echo(
                    f"{{boxcolor}} {{vline}}{{titlecolor}} moniker {'land'.rjust(width - 12)}{{/all}} {{boxcolor}}{{vline}}",
                    wordwrap=False,
                )
                io.echo(f"{{boxcolor}} {{rtee}}{{hline:{width - 2}}}{{ltee}}")

                cycle = 0

                sysop = member.checkflag(args, "SYSOP", conn=conn, **kwargs)

                for rec in database.resultiter(cur):
                    if cycle == 0:
                        color = "{white}"
                    else:
                        color = "{lightgray}"
                    moniker = rec["moniker"]
                    p = libplayer.load(args, moniker, conn=conn, **kwargs)
                    if sysop is True:
                        leftbuf = f"{p.moniker} ({p.membermoniker})"
                    else:
                        leftbuf = f"{p.moniker}"

                    rightbuf = f"{p.land:>6n}"
                    buf = f" {{boxcolor}}{{vline}}{color} {leftbuf}{rightbuf.rjust(width - len(leftbuf) - 4)}{{boxcolor}} {{vline}}"
                    io.echo(buf, wordwrap=False)

                    cycle += 1
                    cycle %= 2

                io.echo(
                    f" {{boxcolor}}{{llcorner}}{{hline:{width - 2}}}{{lrcorner}}",
                    wordwrap=False,
                )
            else:
                io.echo("no other rulers")
            return True

    util.heading("list players")
    pool = kwargs.get("pool", None)
    if pool is None:
        io.echo(f"empyre.maint.listplayer.200: {pool=}", level="error")
        return False
    with database.connect(args, pool=pool) as conn:
        return _work(conn)
