from bbsengine6 import io, database, member

def init(args, **kwargs):
    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

def checkavailable(args, **kwargs):
    cur = kwargs.get("cur", None)
    def _available(cur):
        sql:str = "select * from empyre.mercs where hiredbymoniker is null"
        dat:tuple = ()

        cur.execute(sql, dat)
        if cur.rowcount == 0:
            io.echo("no teams available for hire")
            return False
        return True

    try:
        if cur is None:
            with database.connect(args) as conn:
                with database.cursor(conn) as cur:
                    available = _available(cur)
        else:
            available = _available(cur)
    except Exception as e:
        io.echo("town.juicebar.checkavailable.100: exception {e}", level="error")
        raise

def z(args, **kwargs):
    def _gettotalmercs(cur):
        sql:str = "select count(moniker) from empyre.mercs"
        dat:tuple = ()
        cur.execute(sql)
        if cur.rowcount == 0:
            return None
        return cur.fetchone()["count"]

    cur = kwargs.get("cur", None)
    if cur is None:
        with database.connect(args) as conn:
            with database.cursor(conn) as cur:
                totalmercs = _gettotalmercs(cur)
    else:
        totalmercs = _gettotalmercs(cur)

    io.echo(f"{{var:valuecolor}}{util.pluralize(totalmercs, 'mercenary team', 'mercenary teams')}{{var:labelcolor}} in the game.")


def juicebarhelp(**kwargs):
    args = kwargs.get("args", None)
    io.echo("[H] Hire Mercs")
    if member.checkflag(args, "sysop", **kwargs) is True:
        io.echo("[Z] Maint")
    io.echo("[X] Exit Juice Bar")

def main(args, **kwargs):
    done = False
    while not done:
        choices = "H"
        if member.checkflag(args, "sysop", **kwargs) is True:
            choices += "Z"
        ch = io.inputchoice(f"{{var:promptcolor}}juicebar {{var:optioncolor}}[HX]{{var:promptcolor}}: {{var:inputcolor}}", choices+"XQ", "X", help=juicebarhelp)
        if ch == "X" or ch == "Q":
            io.echo("Exit")
            done = True
        elif ch == "H":
            io.echo("hire mercs")
            if checkavailable(args) is True:
                hireteam(args)
        elif ch == "Z":
            io.echo("maint")
            z(args)
