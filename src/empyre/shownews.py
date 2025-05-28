from bbsengine6 import io, util, database

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args, **kwargs):
    return None

def main(args:object, player:object, **kwargs):
    pool = kwargs.get("pool", None)
    if pool is None:
        io.echo("empyre.shownews.100: {pool=}", level="error")
        return False

    with database.connect(args, pool=pool) as conn:
        with database.cursor(conn) as cur:
            sql = "select * from empyre.newsentry order by datecreated desc"
            dat = (player.datelastplayed,)
            cur.execute(sql)

            if cur.rowcount == 0:
                io.echo("no entries")
                return True

            util.heading("empyre news")

            for entry in database.resultiter(cur, 10): # iter_news(cur, 10):
                io.echo(f"{{var:valuecolor}}{util.datestamp(entry['datecreated'], format='%d%b%y@%H%M (%a)')} {entry['playermoniker']}: {entry['message']}")
        
    io.echo("{/all}")
    return True
