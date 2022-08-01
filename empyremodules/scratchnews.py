def scratchnews(args, player):
    dbh = bbsengine.databaseconnect(args)
    cur = dbh.cursor()
    sql = "select count(id) from empyre.newsentry"
    cur.execute(sql)
    res = cur.fetchone()
    newsentries = res["count"]
    ttyio.echo("scratchnews.100: res=%r, newsentries=%r" % (res, newsentries))
    if ttyio.inputboolean("scratch %s? [yN]: " % (bbsengine.pluralize(newsentries, "news entry", "news entries")), "N") is False:
        ttyio.echo("aborted.")
        return

    sql = "delete from engine.__node where prg='empyre.newsentry'"
    cur.execute(sql)
    dbh.commit()
    ttyio.echo("%s scratched." % (bbsengine.pluralize(cur.rowcount, "news entry", "news entries")))
    return
