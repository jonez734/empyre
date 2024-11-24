from bbsengine6 import io, database

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
            
def main(args, **kwargs):
    done = False
    while not done:
        io.echo("[H] Hire Mercs")
        io.echo("[X] Exit Tavern")
        ch = io.inputchoice("{var:promptcolor}juicebar {var:optioncolor}[HX]{var:promptcolor}: {var:inputcolor}", "HXQ", "X")
        if ch == "X" or ch == "Q":
            io.echo("Exit")
            done = True
        elif ch == "H":
            io.echo("Hire Mercs")
            _check(args)
    