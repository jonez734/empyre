from bbsengine6 import io, listbox
from . import lib

class EmpyreResourceListboxItem(object):
    def __init__(self, resource):
        self.resource = resource

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

def main(args, **kw):
    ship = kw["ship"] if "ship" in kw else None
    if ship is None:
        io.echo("Ship does not exist", level="error")
        return False
    io.echo(f"ship {ship.moniker} manifest{{f6:2}}")
    lb = listbox.Listbox(args, cur, "select resource", keyhandler=None, totalitems=totalitems, itemclass=EmpyrePlayerListboxItem)
#    op = lb.run()
    return True
