# @since 20220731 moved out of empyre.py

import ttyio5 as ttyio

from . import lib

def main(args):
    player = lib.Player(args)
    player.new()
    ttyio.echo("newplayer.100: player.name=%r" % (player.name), level="debug")
    return player
    
