def init(args, **kw):
    pass

def main(args, **kw):
    player = kw["player"] if "player" in kw else None
    player.status()
    return True
