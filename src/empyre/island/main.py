from bbsengine6 import io, util

#from .. import data
#from .. import lib
#from . import module

def init(args, **kwargs):
    return True
    
def access(args, op, **kwargs):
    return True

def buildargs(args, **kwargs):
    return None

def help(**kwargs):
    io.echo("[S]et sail to mainland")

# @see mdl.emp.delx3.txt#L337
def main(args, **kw):
    player = kw["player"] if "player" in kw else None
    
    done = False
    while not done:
        util.heading("island")
        ch = io.inputchar(f"{{promptcolor}}island {{optioncolor}}[{options}]{{promptcolor}}: {{inputcolor}}", options, "XQ", help=help)
        if ch == "Q" or ch == "X":
            io.echo("X -- exit")
            done = True
            break

    return True
