def resetempire(args, player):
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
        sql = "delete from engine.__node where id in (%s)" % (", ".join(playerids))
        # ttyio.echo(sql)
        cur.execute(sql)
        dbh.commit()
    else:
        ttyio.echo("No")
    return
