from bbsengine6 import io, database, util

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args=None, **kwargs):
    return None

def removeplayer(args, player):
    sql = "select count(id) from empyre.player"
    dbh = database.connect(args)
    cur = dbh.cursor()
    cur.execute(sql)
    if cur.rowcount == 0:
        io.echo("there are no players")
        return True
    elif cur.rowcount == 1:
        io.echo("there is one player")
    else:
        io.echo("empyre has {util.pluralize(cur.rowcount, 'player', 'players')}")

    if io.inputboolean("{promptcolor}proceed? {optioncolor}[yN]{promptcolor}: {inputcolor}", "N") is True:
        sql = "delete from empyre.__player"
        cur.execute(sql)
        dbh.commit()
        io.echo("player reset.")
    else:
        io.echo("aborted.")

def removeship(args, player, **kw):
    sql = "select count(name) from empyre.ship"
    dbh = database.connect(args)
    cur = dbh.cursor()
    cur.execute(sql)
    rec = cur.fetchone()
    rowcount = rec["count"] if "count" in rec else None
    shipres = player.getresource("ships")
    io.echo(f"{{normalcolor}}empyre has {{valuecolor}}{util.pluralize(rowcount, **shipres)}")
    if rowcount == 0:
        return True
    if io.inputboolean("{promptcolor}remove ships? {optioncolor}[yN]{promptcolor}: {inputcolor}", "N") is True:
        sql = "delete from empyre.__ship"
        cur = dbh.cursor()
        cur.execute(sql)
        dbh.commit()
        io.echo("{} deleted.".format(util.pluralize(cur.rowcount, **shipres)))

def removeisland(args, player):
    sql = "select count(name) from empyre.island"
    dbh = database.connect(args)
    cur = dbh.cursor()
    cur.execute(sql)
    if cur.rowcount == 0:
        return True
    io.echo("empyre has {} {}".format(util.pluralize(cur.rowcount, "island", "islands"), cur.rowcount))
    if io.inputboolean("remove islands? [yN]: {inputcolor}", "N") is True:
        sql = "delete from empyre.__island"
        cur.execute(sql)
        dbh.commit()
        io.echo("{util.pluralize(cur.rowcount, 'island', 'islands')} deleted.")

def main(args, player, **kwargs):
    if io.inputboolean("{promptcolor}reset empyre? {optioncolor}[yN]{promptcolor}: {inputcolor}", "N") is True:
        removeship(args, player=player)
#        removeisland(args, player=player)
        removeplayer(args, player=player)
    return True
