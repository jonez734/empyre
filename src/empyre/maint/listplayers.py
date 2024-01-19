#import ttyio6 as ttyio
#import bbsengine6 as bbsengine
from bbsengine6 import io, member, util, database

from .. import lib

def init(args, **kw):
    io.setvariable("acscolor", "{white}")
    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

# @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/Empire6.lbl#L69
def main(args:object, player=None, **kw):
    lib.setarea(args, player, "list players")
    terminalwidth = io.getterminalwidth()
    dbh = database.connect(args)
    sql = "select id, memberid, moniker from empyre.player order by (resources->>'land')::integer desc"
    dat = ()
    cur = dbh.cursor()
    cur.execute(sql, dat)
    if cur.rowcount > 0:
        io.echo("{/all}{var:acscolor}{acs:ulcorner}{acs:hline:%s}{acs:urcorner}" % (terminalwidth-2), wordwrap=False)
        io.echo("{var:acscolor}{acs:vline}{gray} name %s{/all} {var:acscolor}{acs:vline}" % ("land".rjust(terminalwidth-len("land")-5)), wordwrap=False)
        io.echo("{var:acscolor}{acs:ltee}%s{var:acscolor}{acs:rtee}" % (util.hr(chars="-=", color="{var:acscolor}", width=terminalwidth-2, padding="")), wordwrap=False)
        player = lib.Player(args)
        sysop = member.checkflag(args, "SYSOP")
        cycle = 0
        for rec in database.resultiter(cur):
            if cycle == 0:
                color = "{white}"
            else:
                color = "{lightgray}"
            playerid = rec["id"]
            player.load(playerid)

            membername = member.getcurrentmoniker(args, player.memberid)
            if sysop is True:
                leftbuf  = f"{player.moniker} ({membername})" # "({:>4n}".format(player.memberid))
            else:
                leftbuf  = f"{player.moniker}" # "({:>4n}".format(player.memberid))

            rightbuf = "%s" % ("{:>6n}".format(player.land))
            rightbuflen = len(rightbuf)
            buf = f"{{var:acscolor}}{{acs:vline}}%s %s%s {{/all}}{{var:acscolor}}{{acs:vline}}" % (color, leftbuf.ljust(terminalwidth-rightbuflen-4), rightbuf)
            io.echo(buf, wordwrap=False)

            cycle += 1
            cycle %= 2

        io.echo(f"{{var:acscolor}}{{acs:llcorner}}%s{{acs:lrcorner}}" % (util.hr(chars="-=", color=f"{{var:acscolor}}", width=terminalwidth-2, padding="")))
    else:
        io.echo("no other rulers")
    return True
