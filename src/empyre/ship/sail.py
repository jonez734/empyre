from bbsengine6 import util, io

# from . import lib as libship


def init(args, **kwargs: dict) -> bool:
    return True


def access(args, op: str, **kwargs: dict) -> bool:
    return True


def buildargs(args, **kwargs: dict):
    #    return lib.buildargs(args, **kwargs)
    return None


def main(args, **kwargs):
    player = kwargs["player"] if "player" in kwargs else None
    if player is None:
        io.echo("You do not exist. Go Away!", level="error")
        return False
    ship = kwargs["ship"] if "ship" in kwargs else None
    if ship is None:
        io.echo("Your ship does not exist. Go Away!", level="error")
        return False

    io.echo("sail")
    util.heading("set sail")
    return True
