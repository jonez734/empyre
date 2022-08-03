import ttyio5 as ttyio
import bbsengine5 as bbsengine

from . import lib

def main(args, player):
    dbh = bbsengine.databaseconnect(args)
    cur = dbh.cursor()
    sql = "select count(id) from empyre.newsentry"
    cur.execute(sql)
    res = cur.fetchone()
    newsentries = res["count"]
    ttyio.echo("scratchnews.100: res=%r, newsentries=%r" % (res, newsentries), level="debug")
    if newsentries == 0:
        ttyio.echo("no news entries to scratch")
        return True

    if ttyio.inputboolean("scratch %s? [yN]: " % (bbsengine.pluralize(newsentries, "news entry", "news entries")), "N") is False:
        ttyio.echo("aborted.")
        return True

    sql = "delete from engine.__node where prg='empyre.newsentry'"
    cur.execute(sql)
    dbh.commit()
    ttyio.echo("%s scratched." % (bbsengine.pluralize(cur.rowcount, "news entry", "news entries")))
    lib.newsentry(args, player, "news reset")
    return True
