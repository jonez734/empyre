import ttyio5 as ttyio
import bbsengine5 as bbsengine

from .. import lib

def init(args, **kw):
    ttyio.setvariable("acscolor", "{white}")
    return True

# @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/Empire6.lbl#L69
def main(args:object, player=None, **kw):
    lib.setarea(args, player, "list players")
    terminalwidth = ttyio.getterminalwidth()
    dbh = bbsengine.databaseconnect(args)
    sql = "select id, memberid, name from empyre.player order by (attributes->>'land')::integer desc"
    dat = ()
    cur = dbh.cursor()
    cur.execute(sql, dat)
    if cur.rowcount > 0:
        ttyio.echo("{/all}{var:acscolor}{acs:ulcorner}{acs:hline:%s}{acs:urcorner}" % (terminalwidth-2), wordwrap=False)
        ttyio.echo("{var:acscolor}{acs:vline}{gray} name %s{/all} {var:acscolor}{acs:vline}" % ("land".rjust(terminalwidth-len("land")-5)), wordwrap=False)
        ttyio.echo("{var:acscolor}{acs:ltee}%s{var:acscolor}{acs:rtee}" % (bbsengine.hr(chars="-=", color="{var:acscolor}", width=terminalwidth-2)), wordwrap=False)
        player = lib.Player(args)
        sysop = bbsengine.checkflag(args, "SYSOP")
        cycle = 0
        for rec in bbsengine.resultiter(cur):
            if cycle == 0:
                color = "{white}"
            else:
                color = "{lightgray}"
            playerid = rec["id"]
            player.load(playerid)

            membername = bbsengine.getmembername(args, player.memberid)
            if sysop is True:
                leftbuf  = "%s (%s)" % (player.name, membername) # "({:>4n}".format(player.memberid))
            else:
                leftbuf  = "%s" % (player.name) # "({:>4n}".format(player.memberid))

            rightbuf = "%s" % ("{:>6n}".format(player.land))
            rightbuflen = len(rightbuf)
            buf = "{var:acscolor}{acs:vline}%s{var:empyre.highlightcolor} %s%s {/all}{var:acscolor}{acs:vline}" % (color, leftbuf.ljust(terminalwidth-rightbuflen-4), rightbuf)
            ttyio.echo(buf, wordwrap=False)

            cycle += 1
            cycle %= 2

        ttyio.echo("{var:acscolor}{acs:llcorner}%s{acs:lrcorner}" % (bbsengine.hr(chars="-=", color="{var:acscolor}", width=terminalwidth-2)))
    else:
        ttyio.echo("no other rulers")
    return True
