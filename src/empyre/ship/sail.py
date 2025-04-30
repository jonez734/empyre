from bbsengine6 import util, io

#from . import lib as libship

def init(args, **kw:dict) -> bool:
    return True

def access(args, op:str, **kw:dict) -> bool:
    return True

def buildargs(args, **kw:dict):
#    return lib.buildargs(args, **kw)
    return None

def main(args, **kw):
    player = kw["player"] if "player" in kw else None
    if player is None:
        io.echo("You do not exist. Go Away!", level="error")
        return False
    ship = kw["ship"] if "ship" in kw else None
    if ship is None:
        io.echo("Your ship does not exist. Go Away!", level="error")
        return False
    
    io.echo("sail")
    util.heading("set sail")
    return True
