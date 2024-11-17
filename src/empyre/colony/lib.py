import copy

from bbsengine6 import database, io

MODULENAME = "colony"

def getcolony(args, name):
    sql = "select * from empyre.__colony where name=%s"
    dat = (name,)
    dbh = database.connect(args)
    cur = dbh.cursor()
    cur.execute(sql, dat)
    if cur.rowcount == 0:
        return None
    res = cur.fetchone()
    
    colony = {}
    for f in ("name", "founderid", "islandname", "resources", "datefounded", "status"):
        colony[f] = res[f]
    return colony

def insert(args, colony):
    return database.insert(args, "empyre.__colony", colony, returnid=True, primarykey="name")

def update(args, name, colony):
    return database.update(args, "empyre.__colony", name, colony, primarykey="name")

def edit(args, colony):
    _colony = copy.deepcopy(colony)
    io.echo(f"{{var:optioncolor}}[N]{{var:labelcolor}}ame: {{var:valuecolor}}{colony['name']}", end="")
    if colony["name"] != _colony["name"}:
        io.echo(f" {{var:labelcolor}}(was {{var:valuecolor}}{_colony['name']}{{var:labelcolor}})")
    else:
        io.echo()
    io.echo(f"{{var:optioncolor}}[I]{{var:labelcolor}}sland ame: {{var:valuecolor}}{colony['islandname']}", end="")
    if colony["islandname"] != _colony["islandname"}:
        io.echo(f" {{var:labelcolor}}(was {{var:valuecolor}}{_colony['islandname']}{{var:labelcolor}})")
    else:
        io.echo()
