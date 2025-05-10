# @since 20250226
from . import lib
from bbsengine6 import database, io, listbox, member, util

def build(args, rec, **kwargs):
    p = lib.Player(args, **kwargs)
    for attr in ("moniker", "membermoniker", "rank", "previousrank", "turncount", "soldierpromotioncount", "datepromoted", "combatvictorycount", "weatherconditions", "beheaded", "datelastplayed", "taxrate", "training", "datelastplayedlocal"):
        if attr in rec:
            setattr(p, attr, rec[attr])

    for name in p.resources.keys():
        res = p.resources[name]
        if name not in rec["resources"]:
            setattr(p, name, res.get("default"))
        else:
            setattr(p, name, res.get("value", res.get("default")))

#    io.echo(f"empyre.player.build.200: {p=}", level="debug")
    return p

def buildrec(args, player, **kwargs):
    rec = {}
    return rec

def load(args, moniker, **kwargs):
    def _work(conn):
        sql:str = "select * from empyre.player where moniker=%s"
        dat:tuple = (moniker,)
        
        with database.cursor(conn) as cur:
            cur.execute(sql, dat)
            if cur.rowcount == 0:
                io.echo(f"empyre.player.load.300: {moniker=} not found", level="info")
                return None

            rec = cur.fetchone()
            player = build(args, rec, **kwargs)
#            io.echo(f"empyre.player.load.320: {player=} {rec=}", level="debug")

#            for attr in ("moniker", "membermoniker", "rank", "previousrank", "turncount", "soldierpromotioncount", "datepromoted", "combatvictorycount", "weatherconditions", "beheaded", "datelastplayed", "taxrate", "training", "datelastplayedlocal"):
#                if attr in player:
#                    setattr(player, attr, player[attr])
#
#            for name in self.resources.keys():
#                if name not in player["resources"]:
#                    v = self.resources[name]["default"]
#                else:
#                    v = player["resources"][name]["value"]
#                    if v is None:
#                        v = self.resources[name]["default"]
#                        io.echo(f"{v=}", level="debug")
#                setattr(self, name, v)
            return player
        
    conn = kwargs.get("conn", None)
    if conn is None:
        pool = kwargs.get("pool", None)
        if pool is None:
            io.echo(f"empyre.player.load.200: {pool=}", level="error")
            return None
        with database.connect(pool=pool) as conn:
            p = _work(conn)
    else:
        p = _work(conn)
#    io.echo(f"empyre.player.load.220: {p=}", level="debug")
    return p

def update(self, moniker, player, **kwargs):
    def _work(conn):
        for name in self.resources.keys():
            v = getattr(self, name)
            player.setresourcevalue(name, v)
#            io.echo(f"syncresvalues.100: {name=} {v=}", level="debug")

        p = {}
        for attr in ("moniker", "membermoniker", "rank", "previousrank", "turncount", "soldierpromotioncount", "datepromoted", "combatvictorycount", "weatherconditions", "beheaded", "datelastplayed", "coins", "taxrate", "resources"):
            p[attr] = getattr(player, attr)

        return database.update(self.args, "empyre.__player", moniker, p, primarykey="moniker", conn=conn)
    
    conn = kwargs.get("conn", None)
    if conn is None:
        pool = kwargs.get("pool", None)
        if pool is None:
            io.echo(f"empyre.player.update.200: {pool=}", level="error")
            return False
        with database.connect(pool=pool) as conn:
            return _work(conn)
    else:
        return _work(conn)

def select(args, title:str="select player", prompt:str="player: ", membermoniker:str=None, **kwargs):
    class EmpyrePlayerListboxItem(listbox.ListboxItem):
        def __init__(self, rec:dict, width:int, height:int=1, **kwargs):
            io.echo(f"empyre.lib.EmpyreListboxItem.200: {kwargs=}", level="debug")
            super().__init__(self, width, height, **kwargs)
            self.player = load(args, rec["moniker"], **kwargs)
            if self.player is None:
#                io.echo(f"empyre.player.select.240: {self.player=}", level="error")
                return
            self.pool = kwargs.get("pool", None)
            self.conn = kwargs.get("conn", None)
            
#            io.echo(f"empyre.player.select.200: {self.pool=} {self.conn=}", level="debug")

            landres = self.player.getresource("land")
            if "emoji" in landres:
                landres["emoji"] = ""

            acres = landres["value"] if "value" in landres else 0

            left:str = f"{self.player.moniker}"
            lastplayed:str = util.datestamp(self.player.datelastplayedlocal, format="%m/%d @ %I%M%P")
            right:str = f"{util.pluralize(acres, **landres)} {lastplayed}"
            rightlen:int = len(right)
            self.label:str = f"{left.ljust(width-rightlen-10)}{right}" # %s%s {{/all}}{{var:acscolor}}{{acs:vline}}" % (left.ljust(width-rightlen-4), right)

            self.status = ""
            self.pk:str = self.player.moniker
            self.rec:dict = rec
            self.width:int = width
        def help(self):
            io.echo(f"{{var:labelcolor}}use {{var:valuecolor}}KEY_ENTER{{var:labelcolor}} to select one of your players")
            return

        def display(self):
            io.echo(f"{{/all}}{{cha}} {{engine.menu.cursorcolor}}{{engine.menu.color}} {{engine.menu.boxcharcolor}}{{acs:vline}}{{cic}} {self.label.ljust(self.width-9, ' ')} {{/all}}{{engine.menu.boxcharcolor}}{{acs:vline}}{{engine.menu.shadowcolor}} {{engine.menu.color}} {{/all}}{{cha}}", end="", flush=True)
            return

    def empyreplayerkeyhandler(args, ch:str, lb:listbox.Listbox) -> bool:
        io.echo("inside empyreplayerkeyhandler")
        currentitem = lb.currentitem
        if ch == "KEY_ENTER":
            io.setvar("cic", "{currentitemcolor}")
            currentitem.display()
            io.echo("{restorecursor}", end="", flush=True)
            io.echo(f"{currentitem.player.moniker}")
            return False
        elif ch == "KEY_INS":
            io.echo("{restorecursor}add player")
            return False

    conn = kwargs.get("conn", None)
    if conn is None:
        pool = kwargs.get("pool", None)
        if pool is None:
            io.echo(f"empyre.lib.selectplayer.200: {pool=}", level="error")
            return False
        conn = database.connect(args, pool=pool)

    io.echo(f"selectplayer.100: {conn=} {membermoniker=}", level="debug")

    if membermoniker is None:
        membermoniker = member.getcurrentmoniker(args, conn=conn)
    io.echo(f"empyre.lib.selectplayer.220: {membermoniker=}", level="debug")

    sql:str = "select moniker from empyre.player where membermoniker=%s order by datelastplayed desc"
    dat:tuple = (membermoniker,)

    totalitems = count(args, membermoniker, conn=conn)
    with database.cursor(conn) as cur:
        if args.debug is True:
            io.echo(f"getplayer.110: {cur.mogrify(sql, dat)=}", level="debug")
        cur.execute(sql, dat)
        if cur.rowcount == 0:
            io.echo("no player record.")
            return None

        lb = listbox.Listbox(args, title=title, keyhandler=None, totalitems=totalitems, itemclass=EmpyrePlayerListboxItem, cur=cur, conn=conn, **kwargs)
        op = lb.run(prompt) # "player: ")
        if op.kind == "select":
            io.echo(f"{op.listitem.player.moniker}")
            return op.listitem.player
        elif op.kind == "exit":
            return None

def count(args, membermoniker:str, **kwargs) -> int:
    def _work(conn):
        sql:str = "select count(moniker) from empyre.player where membermoniker=%s"
        dat:tuple = (membermoniker,)
        with database.cursor(conn) as cur:
            cur.execute(sql, dat)
            if cur.rowcount == 0:
                io.echo(f"empyre.player.count.160: returning None", level="debug")
                return None
            rec = cur.fetchone()
            count = rec["count"] if rec["count"] > 0 else None
            io.echo(f"empyre.player.count.120: {count=}", level="error")
            return count
    
    conn = kwargs.get("conn", None)
    if conn is None:
        io.echo(f"empyre.player.count.140: {conn=}", level="error")
        pool = kwargs.get("pool", None)
        if pool is None:
            io.echo(f"empyre.player.count.160: {pool=}")
            return None
        conn = database.connect(args, pool=pool)
        with conn:
            return _work(conn)
    else:
        return _work(conn)
