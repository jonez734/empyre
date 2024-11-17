# @since 20230105 moved to empyre.town.lucifersden
# @since 20200830
# @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_town.lbl#L162

import random

#import ttyio6 as ttyio
#import bbsengine6 as bbsengine
from bbsengine6 import io, util

from .. import lib

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

def main(args, **kw):
    player = kw["player"] if "player" in kw else None
    if player is None:
        io.echo("You do not exist. Go away!", level="error")
        return False

    if player.coins > 10000 or player.land > 15000:
        io.echo("{F6}I checked our inventory and we have plenty of souls. Maybe we can deal some other time.")
        return True

    lib.setarea(args, player, "town: lucifer's den")

    util.heading("LUCIFER'S DEN - Where Gamblin's no Sin!") # , hrcolor="{orange}", titlecolor="{bgred}{yellow}")
    io.echo("{yellow}I will let you play for the price of a few souls!")
    ch = io.inputboolean("{promptcolor}Will you agree to this? [yN]: {inputcolor}", "N")
    if ch is False:
        io.echo("{normalcolor}Some other time, then.")
        return True
    # always win, but it costs 10 serfs, 50 serfs if you guess correctly
    # og=int(3*rnd(0)+2)
    # &"{f6:2}{lt. blue}Odds:"+str$(og)+" to 1"
    io.echo("{f6}this module does not currently save player data after use", level="info")

    done = False
    while not done:
        odds = random.randint(2, 4)
        io.echo("{normalcolor}Odds: {valuecolor}%s to 1{normalcolor}" % (odds))
        if player.serfs < 1000:
            io.echo("{normalcolor}You must have at least {valuecolor}%s{normalcolor} to gamble here!" % util.pluralize(1000, "serf", "serfs"))
            done = True
            break
        io.echo("{F6}{normalcolor}You have :moneybag: {valuecolor}%s{/all} and {valuecolor}%s{normalcolor}" % (util.pluralize(player.coins, "coin", "coins"), util.pluralize(player.serfs, "serf", "serfs")))
        bet = io.inputinteger("{promptcolor}Bet how many coins? (No Limit): {inputcolor} ")
        io.echo("{normalcolor}")
        if bet is None or bet < 1 or bet > player.coins:
            io.echo("Exiting Lucifer's Den")
            done = True
            break
        
        pick = io.inputinteger("{promptcolor}Pick a number from 1 to 6: {inputcolor}")
        if pick is None or pick < 1:
            io.echo("invalid value")
            done = True
            return
        
        dice = util.diceroll(6)

        if args.debug is True:
            io.echo(f"{dice=}", level="debug")

        if dice == pick:
            io.echo("{green}MATCH!{/all}{F6}")
            player.coins += bet*odds
            player.serfs -= 50
        else:
            player.coins += bet
            player.serfs -= 10
            
        # b=int(rnd(.)*(og+1)+1):on-(a=b)goto {:104}:pn=pn+x:sf=sf-10
        # &"{f6}{white}Close Enough!{f6}{pound}q1":goto {:170}
        # bbsengine.poparea()
    return
