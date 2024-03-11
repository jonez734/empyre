from bbsengine6 import io

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

def help(**kw):
    io.echo(":compass: {var:optioncolor}[R]{var:labelcolor}ecruit navigator{var:normalcolor}") # show how many are needed per ship
    io.echo(":package: {var:optioncolor}[E]{var:labelcolor}xports{var:normalcolor}")
    io.echo(":anchor: {var:optioncolor}[S]{var:labelcolor}hips{var:normalcolor}")
    io.echo("{f6}:door: {var:optioncolor}[Q]{var:labelcolor}uit{var:normalcolor}")
    return True

def main(args, **kw):
    util.heading("shipyard")
    return True
