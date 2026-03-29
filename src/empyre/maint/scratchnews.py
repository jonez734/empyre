from bbsengine6 import io, database, member, util

from .. import lib as libempyre


def init(args, **kwargs):
    return True


def access(args, op, **kwargs):
    return member.checkflag(args, "SYSOP", **kwargs)


def main(args, player, **kwargs):
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

    if (
        io.inputboolean(
            "{promptcolor}scratch {valuecolor}%s{promptcolor}? {optioncolor}[yN]{promptcolor}: {inputcolor}"
            % (util.pluralize(newsentries, "news entry", "news entries")),
            "N",
            **kwargs,
        )
        is False
    ):
        io.echo("aborted.")
        return True

    sql = "delete from empyre.__newsentry"
    cur.execute(sql)
    dbh.commit()
    io.echo(
        "%s scratched." % (util.pluralize(cur.rowcount, "news entry", "news entries"))
    )
    libempyre.newsentry(args, "news reset", player=player)
    return True
