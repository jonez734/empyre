import ttyio6 as ttyio
import bbsengine6 as bbsengine

#from .. import data
#from .. import lib
from . import module

def init(args, **kw):
    return True
    
def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

def help(**kw):
    ttyio.echo("[S]et sail to mainland")
# @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/mdl.emp.delx3.txt#L337
def main(args, **kw):
    player = kw["player"] if "player" in kw else None
    
    done = False
    while not done:
        bbsengine.util.heading("island")
        ch = ttyio.inputchar(f"{{var:promptcolor}}island {{var:optioncolor}}[{options}]{{var:promptcolor}}: {{var:inputcolor}}", options, "Q", help=help)
        if ch == "Q":
            ttyio.echo("Q -- quit")
            done = True
            break

    return True
