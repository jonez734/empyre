# @since 20220729

import ttyio5 as ttyio
import bbsengine5 as bbsengine

def init(args, **kw):
    return True

def access(args, op, **kwargs):
    return True

def main(args, **kw):
    player = kw["player"] if "player" in kw else None
    if player is None:
        ttyio.echo("you do not exist! go away!", level="error")
        return False

    ttyio.echo("colony trip... %s{f6}" % (bbsengine.pluralize(player.colonies, "colony", "colonies")))
    if player.colonies > 0:
        ttyio.echo("King George wishes you a safe and prosperous trip to your %s{f6}" % (bbsengine.pluralize(player.colonies, "colony", "colonies", quantity=False)))
    return True
