# @since 20220729

import ttyio5 as ttyio
import bbsengine5 as bbsengine

def main(args, player):
    ttyio.echo("colony trip... %s{f6}" % (bbsengine.pluralize(player.colonies, "colony", "colonies")))
    if player.colonies > 0:
        ttyio.echo("King George wishes you a safe and prosperous trip to your %s{f6}" % (bbsengine.pluralize(player.colonies, "colony", "colonies", quantity=False)))
    return True

