from bbsengine6 import io


def init(args, **kwargs):
    return True


def access(args, op, **kwargs):
    return True


def buildargs(args, **kwargs):
    return None


def main(args, **kwargs):
    ship = kwargs.get("ship")
    if ship is None:
        io.echo("Ship does not exist", level="error")
        return False
    io.echo(f"ship {ship.moniker} manifest{{f6:2}}")
    # TODO: Implement ship manifest viewer
    return True
