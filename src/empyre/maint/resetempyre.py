import ttyio5 as ttyio
import bbsengine5 as bbsengine

def init(args, **kwargs):
    return True

def access(args, ops, **kwargs):
    return True

def main(args, player, **kwargs):
    if ttyio.inputboolean("{var:promptcolor}reset empyre? {var:optioncolor}[yN]{var:promptcolor}: {var:inputcolor}", "N") is True:
        sql = "select id from empyre.player"
        dat = ()
        dbh = bbsengine.databaseconnect(args)
        cur = dbh.cursor()
        cur.execute(sql)
        res = cur.fetchall()
        playerids = []
        for rec in res:
            playerids.append(str(rec["id"]))
        ttyio.echo(f"playerids={playerids!r}", level="debug")
        if ttyio.inputboolean("{var:promptcolor}proceed? {var:optioncolor}[yN]{var:promptcolor}: {var:inputcolor}", "N") is True:
            sql = "delete from engine.__node where id in (%s)" % (", ".join(playerids))
            cur.execute(sql)
            dbh.commit()
            ttyio.echo("empyre reset.")
        else:
            ttyio.echo("aborted.")
    return True
