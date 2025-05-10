from bbsengine6 import io, database

from . import lib

def main(args, player):
    dbh = database.connect(args)
    cur = dbh.cursor()
    sql = "select count(id) from empyre.newsentry"
    cur.execute(sql)
    res = cur.fetchone()
    newsentries = res["count"]
    io.echo(f"scratchnews.100: {res=}, {newsentries=}", level="debug")
    if newsentries == 0:
        io.echo("no news entries to scratch")
        return True

    if io.inputboolean("{promptcolor}scratch {valuecolor}%s{promptcolor}? {optioncolor}[yN]{promptcolor}: {inputcolor}" % (bbsengine.pluralize(newsentries, "news entry", "news entries")), "N") is False:
        io.echo("aborted.")
        return True

    sql = "delete from empyre.__newsentry"
    cur.execute(sql)
    dbh.commit()
    io.echo("%s scratched." % (bbsengine.util.pluralize(cur.rowcount, "news entry", "news entries")))
    lib.newsentry(args, player, "news reset")
    return True
