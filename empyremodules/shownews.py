import ttyio5 as ttyio
import bbsengine5 as bbsengine

def main(args:object, player:object):
    dbh = bbsengine.databaseconnect(args)
    sql = "select * from empyre.newsentry where (extract(epoch from (coalesce(dateupdated, datecreated)))) > %s"
    dat = (player.datelastplayedepoch,)
    cur = dbh.cursor()
    cur.execute(sql, dat)
    for entry in bbsengine.resultiter(cur, 10): # iter_news(cur, 10):
        ttyio.echo(" %s: %s (#%s): %s" % (bbsengine.datestamp(entry["datecreated"]), entry["createdbyname"], entry["createdbyid"], entry["message"]))
        
    ttyio.echo("{/all}")
    return True

