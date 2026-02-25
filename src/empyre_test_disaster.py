import argparse
import empyre.player, empyre.lib as libempyre
from bbsengine6 import io, database

def main(args, **kwargs):
    currentplayer = empyre.player.load(args, "jam")
    with database.getpool(args) as pool:
        libempyre.runmodule(args, "disaster", disaster=2, save=False, player=currentplayer, pool=pool)

if __name__ == "__main__":
    parser = libempyre.buildargs()
    args = parser.parse_args()
    main(args)
