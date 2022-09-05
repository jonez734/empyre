import ttyio5 as ttyio
import bbsengine5 as bbsengine

def main(args, player):
    if ttyio.inputboolean("reset empyre? [yN]: ", "N") is True:
        ttyio.echo("Yes")
        sql = "select id from empyre.player"
        dat = ()
        dbh = bbsengine.databaseconnect(args)
        cur = dbh.cursor()
        cur.execute(sql)
        res = cur.fetchall()
        playerids = []
        for rec in res:
            playerids.append(str(rec["id"]))
        ttyio.echo("playerids=%r" % (playerids))
        if ttyio.inputboolean("proceed? [yN]: ", "N") is True:
            sql = "delete from engine.__node where id in (%s)" % (", ".join(playerids))
            cur.execute(sql)
            dbh.commit()
        else:
            ttyio.echo("aborted.")
    else:
        ttyio.echo("No")
    return True
