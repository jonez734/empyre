import random

import ttyio5 as ttyio
import bbsengine5 as bbsengine

from . import lib

def main(args:object, **kw):
    player = kw["player"] if "player" in kw else None

    bbsengine.title("generate npc")
    lib.setarea(args, player, "generate npc")

    nonplayerchar = lib.Player(args)
    nonplayercharrank = random.randint(0, min(3, player.rank + 1))
    nonplayerchar.generate(nonplayercharrank)
    nonplayerchar.memberid = bbsengine.getcurrentmemberid(args)
#    otherplayer.rank = rank
    nonplayerchar.status()

    if ttyio.inputboolean("add this npc? [yN]: ", "N") is False:
        return True

    res = nonplayerchar.insert()
    ttyio.echo("generatenpc.100: otherplayer.insert=%r" % (res), level="debug")
    nonplayerchar.dbh.commit()
    return True
