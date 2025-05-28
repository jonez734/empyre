from bbsengine6 import io, database

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

def help(**kw):
    io.echo(":compass: {optioncolor}[R]{labelcolor}ecruit navigator{normalcolor}") # show how many are needed per ship
    io.echo(":package: {optioncolor}[E]{labelcolor}xports{normalcolor}")
    io.echo(":anchor: {optioncolor}[S]{labelcolor}hips{normalcolor}")
    io.echo(" {optioncolor}[T]{labelcolor}rade Shipyards{normalcolor}")
    io.echo("{f6}:door: {optioncolor}[Q]{labelcolor}uit{normalcolor}")
    return True


def main(args, **kw):
    util.heading("shipyard")
    done = False
    while not done:
        help()
        ch = io.inputchar(f"shipyard: {{inputcolor}}", "RSTQ", "Q")
        if ch == "Q":
            done = True
            break
        elif ch == "T":
            io.echo("Trade Shipyards")
            res = player.getresource("shipyards")
            lib.trade(args, player, **res)
        elif ch == "S":
            shipslistbox(args, player)
    return True
