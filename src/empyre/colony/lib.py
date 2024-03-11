MODULENAME = "colony"

def getcolony(args, name):
    sql = "select * from empyre.__colony where name=%s"
    dat = (name,)
    dbh = bbsengine.database.connect(args)
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
    return bbsengine.database.insert(args, "empyre.__colony", colony, returnid=True, primarykey="name")

def update(args, name, colony):
    return bbsengine.database.update(args, "empyre.__colony", name, colony, primarykey="name")

def edit(args, colony):
    _colony = copy.deepcopy(colony)
    ttyio.echo(f"{{var:optioncolor}}[N]{{var:labelcolor}}ame: {{var:valuecolor}}{colony['name']}", end="")
    if colony["name"] != _colony["name"}:
        ttyio.echo(f" {{var:labelcolor}}(was {{var:valuecolor}}{_colony['name']}{{var:labelcolor}})")
    else:
        ttyio.echo()
    ttyio.echo(f"{{var:optioncolor}}[I]{{var:labelcolor}}sland ame: {{var:valuecolor}}{colony['islandname']}", end="")
    if colony["islandname"] != _colony["islandname"}:
        ttyio.echo(f" {{var:labelcolor}}(was {{var:valuecolor}}{_colony['islandname']}{{var:labelcolor}})")
    else:
        ttyio.echo()
    