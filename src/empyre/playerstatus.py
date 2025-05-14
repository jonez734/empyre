def init(args, **kw):
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args, **kwargs):
    return None

def main(args, **kwargs):
    player = kwargs.get("player", None)
    if player is None:
        io.echo(f"empyre.playerstatus.100: {player=}", level="error")
        return False
    player.status()
    return True
