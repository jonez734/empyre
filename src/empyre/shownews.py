import ttyio5 as ttyio
import bbsengine5 as bbsengine

def access(args, op, **kw):
    return True

def init(args, **kw):
    return True

def main(args:object, player:object, **kw):
    dbh = bbsengine.databaseconnect(args)
    sql = "select * from empyre.newsentry where coalesce(dateupdated, datecreated) > %s"
#    sql = "select * from empyre.newsentry where (extract(epoch from (coalesce(dateupdated, datecreated)))) > %s"
    dat = (player.datelastplayed,)
    cur = dbh.cursor()
    cur.execute(sql, dat)
    for entry in bbsengine.resultiter(cur, 10): # iter_news(cur, 10):
        ttyio.echo(" %s: %s (#%s): %s" % (bbsengine.datestamp(entry["datecreated"]), entry["createdbyname"], entry["createdbyid"], entry["message"]))
        
    ttyio.echo("{/all}")
    return True
