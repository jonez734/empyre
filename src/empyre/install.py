from bbsengine6 import io, database, util

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args, **kwargs):
    return None

def main(args, **kwargs):
    util.heading("install empyre")
    pool = database.getpool(args)
    with pool:
        conn = database.connect(args, pool=pool)
        with conn:
            if database.schemaexists(args, "empyre") is False:
                io.echo(" FAIL ", level="error")
                return False
            for f in ("player", "ships", "colony", "island":
                if database.importsql(args, f) is False:
                    io.echo(" FAIL ", level="error")
                    return False
