from bbsengine6 import io


def init(args, **kw):
    return True


def access(args, op, **kw):
    return True


def buildargs(args, **kw):
    return None


def main(args, **kw):
    ship = kw.get("ship")
    if ship is None:
        io.echo("Ship does not exist", level="error")
        return False
    io.echo(f"ship {ship.moniker} manifest{{f6:2}}")
    # TODO: Implement ship manifest viewer
    return True
