import random

import ttyio5 as ttyio
import bbsengine5 as bbsengine

from . import lib

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

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

    if ttyio.inputboolean("{var:promptcolor}add this npc? {var:optioncolor}[yN]{var:normalcolor}: {var:inputcolor}", "N") is False:
        return True

    res = nonplayerchar.insert()
    if args.debug is True:
        ttyio.echo("generatenpc.100: otherplayer.insert=%r" % (res), level="debug")
    bbsengine.logentry(f"{player.name} created an NPC called {nonplayerchar.name}")
    dbh = bbsengine.databaseconnect(args)
    dbh.commit()
    return True
