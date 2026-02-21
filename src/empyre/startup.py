from bbsengine6 import io, util, member, database, session

from . import lib
from . import player as libplayer

def init(args, **kwargs):
    io.register_emojis({
        "dragon": "\U0001F409",      # 🐉
        "tree": "\U0001F333",        # 🌳
        "wood": "\U0001FAB5",        # 🪵
        "cityscape": "\U0001F3D9",  # 🏙
        "desert": "\U0001F3DC",      # 🏜
        "farmer": "\U0001F9D1",      # 👤
    })
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args, **kwargs):
    return None

def main(args, **kwargs):
    with database.getpool(args, dbname=database.DEFAULTDATABASE) as pool:
        with database.connect(args, pool=pool) as conn:
            io.echo(f"database {{var:valuecolor}}{args.databasename}{{var:labelcolor}}: ", end="", flush=True)
            if database.exists(args, args.databasename, pool=pool) is False:
                io.echo(f"{{var:valuecolor}}fail{{var:labelcolor}}", level="error", flush=True)
                return False
            else:
                io.echo(f" ok ", level="ok", flush=True)

    with database.getpool(args, dbname=args.databasename) as pool:
        with database.connect(args, pool=pool) as conn:
            io.echo(f"schema {{var:valuecolor}}empyre{{var:labelcolor}}: ", end="")
            if database.schemaexists(args, "empyre", conn=conn) is False:
                io.echo(f"create ", end="")
                if database.createschema(args, "empyre", conn=conn) is False:
                    io.echo("fail", level="error")
                    return False
            io.echo(" ok ", level="ok")
            io.echo(f"{{var:labelcolor}}schema {{var:valuecolor}}empyre{{var:labelcolor}} priv: ", end="")
            if database.manage_schema_priv(args, "grant", "usage", "empyre", "term", conn=conn) is False:
                io.echo(f"fail", level="error")
                return False
            else:
                io.echo(" ok ", level="ok")
                conn.commit()
        
            classlist = (
                ("empyre.player",    "player.sql"),
                ("empyre.island",    "island.sql"),
                ("empyre.__ship",    "ship.sql"),
                ("empyre.colony",    "colony.sql"),
                ("empyre.newsentry", "newsentry.sql"),
                ("empyre.ship",      "shipview.sql"),
            )

            failcount = 0
            for (c, sql) in classlist:
                io.echo(f"{{var:labelcolor}}class {{var:valuecolor}}{c}{{var:labelcolor}}: ", end="")
                if database.classexists(args, c, conn=conn) is False:
                    io.echo("import ", end="")
                    if database.importsql(args, sql, conn=conn, package="empyre.sql") is False:
                        failcount += 1
                    else:
                        io.echo(" ok ", level="ok")
                else:
                    io.echo("ok", level="ok")
            
            io.echo(f"{{var:labelcolor}}schema {{var:valuecolor}}empyre {{var:labelcolor}}privs: ", end="")
            for r in ("web", "term", "sysop"):
                if database.manage_schema_priv(args, "grant", "usage", "empyre", r, conn=conn, **kwargs) is False:
                    io.echo(f"fail", level="error")
                    failcount += 1
                else:
                    io.echo(f" ok ", level="ok")

            io.echo(f"{{var:labelcolor}}schema {{var:valuecolor}}empyre {{var:labelcolor}}create priv for sysop: ", end="")
            if database.manage_schema_priv(args, "grant", "create", "empyre", "sysop", conn=conn, **kwargs) is False:
                io.echo(f"fail", level="error")
                failcount += 1
            else:
                io.echo(f" ok ", level="ok")

            if failcount == 0:
                io.echo(" ok ", level="ok")
                conn.commit()
            else:
                io.echo("fail", level="error")
                conn.rollback()

            return True if failcount == 0 else False
