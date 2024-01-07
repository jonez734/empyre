import copy
from bbsengine6 import io, member, database

def main(args, **kw):
    io.echo("ships")
    
    player = kw["player"] if "player" in kw else NOne
    if player is None:
        io.echo("You do not exist! Go Away!", level="error")
        return False

    done = False
    while not done:
        io.echo("{var:optioncolor}[M]{var:labelcolor}anifest")
        io.echo("{var:optioncolor}[S]{var:labelcolor}crap")
        io.echo("{var:optioncolor}[Q]{var:labelcolor}uit to dock")
        
        ch = io.inputchar("ship: {var:inputcolor}", "MSQ", "Q")
        if ch == "Q":
            done = True
        elif ch == "M":
            manifest(args, player, 