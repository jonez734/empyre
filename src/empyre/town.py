#
# @since 20220728
#

import random

import ttyio5 as ttyio
import bbsengine5 as bbsengine

from . import lib

def init(args, **kw):
    pass

def access(args, op, **kw):
    return True

def main(args, **kwargs):
    player = kwargs["player"] if "player" in kwargs else None

    # @since 20200816
    # @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_town.lbl#L293
    def naturaldisasterbank(args, player):
        bbsengine.title("natural disaster bank") # , titlecolor="{bggray}{white}", hrcolor="{darkgreen}")
        lib.setarea(args, player, "natural disaster bank") # "{bggray}{white}%s{/all}" % ("bank".ljust(terminalwidth)))
        ttyio.echo()
        exchangerate = 3 #:1 -- 3 coins per credit
        credits = bbsengine.getmembercredits(args)
        buf = "You have :moneybag: {var:empyre.highlightcolor}%s{/all} and {var:empyre.highlightcolor}%s{/all}" % (bbsengine.pluralize(player.coins, "coin", "coins"), bbsengine.pluralize(credits, "credit", "credits"))
        ttyio.echo(buf)
        if credits is not None and credits > 0:
            ttyio.echo("The exchange rate is {var:empyre.highlightcolor}%s per credit{/all}.{F6}"  % (bbsengine.pluralize(exchangerate, "coin", "coins")))
            amount = ttyio.inputinteger("{cyan}Exchange how many credits?: {lightgreen}")
            ttyio.echo("{/all}")
        else:
            ttyio.echo("You have no credits")
            return
        if amount is None or amount < 1:
            return

        credits = bbsengine.getmembercredits(args, player.memberid)

        if amount > credits:
            ttyio.echo("Get REAL! You only have {var:empyre.highlightcolor} %s {/all}!" % (bbsengine.pluralize(amount, "credit", "credits")))
            return

        credits -= amount
        player.coins += amount*exchangerate

        bbsengine.setmembercredits(args, player.memberid, credits)

        ttyio.echo("You now have {var:empyre.highlightcolor}%s{/all} and {var:empyre.highlightcolor}%s{/all}" % (bbsengine.pluralize(player.coins, "coin", "coins"), bbsengine.pluralize(credits, "credit", "credits")))

    # @since 20200803
    # @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_town.lbl#L90
    def changetaxrate(args, player):
        ttyio.echo("current tax rate: %s" % (player.taxrate))
        x = ttyio.inputinteger("{green}tax rate: {lightgreen}", player.taxrate)
        ttyio.echo("{/all}")
        if x is None or x < 1:
            ttyio.echo("no change")
            return
        if x > 50:
            ttyio.echo("King George looks at you sternly for trying to set such an exhorbitant tax rate, and vetoes the change.", level="error")
            return
            
        player.taxrate = x
        return

    # @since 20200830
    # @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_town.lbl#L244
    def trainsoldiers(args, player):
        bbsengine.title(": Soldier Training :")
        lib.setarea(args, player, "town -> train soldiers")
        ttyio.echo()
        eligible = int(player.nobles*20-player.soldiers)
        ttyio.echo("empyre.trainsoldiers.100: eligible=%d" % (eligible), level="debug")
        if player.serfs < 1500 or eligible > (player.serfs // 2):
            ttyio.echo("You do not have enough serfs of training age.")
            return
        
        #&"{f6}{white}You have"+str$(wb)+" serfs that meet the requirement to be trained"
        #&" as warriors.{f6:2}Training cost is one acre per serf.{f6}"
        #&"{f6}{lt. green}Do you want them trained (Y/N) >> ":gosub 1902
        #if a then sf=sf-wb:la=la-wb:wa=wa+wb:&"{f6:2}{pound}w2{yellow}Ok, all serfs have been trained.{f6}{pound}q1"
#        ttyio.echo("{f6}{white}You have %s requirements to be trained %s." % (bbsengine.pluralize(eligible, "serf that meets", "serfs that meet"), bbsengine.pluralize(eligible, "as a soldier", "as soldiers", quantity=False)))
        ttyio.echo("{f6}{var:normalcolor}You have %s requirments to be trained as %s. Training cost is 1 acre per serf." % (bbsengine.pluralize(eligible, "serf that meets", "serfs that meet"), bbsengine.pluralize(eligible, "a :military-helmet: warrior", ":military-helmet: warriors", quantity=False)))
        if eligible > 0:
            ttyio.echo("Training cost is 1 acre per serf.")
            if ttyio.inputboolean("Do you wish them trained? [yN]: ", "N") is True:
                player.serfs -= eligible
                player.land -= eligible
                player.soldiers += eligible
                ttyio.echo("Promotions completed.")
            else:
                ttyio.echo("No promotions performed.")

    optiontable = (
        ("C", ":bank: Cyclone's Natural Disaster Bank", naturaldisasterbank),
        ("L", ":fire: Lucifer's Den", "town.lucifersden"), # lucifersden),
        ("P", ":prince: Soldier Promotion to Noble", "town.soldierpromotion"),
        ("R", ":house: Realtor's Advice", realtorsadvice),
#        ("S", "   Slave Market", None),
        ("T", ":receipt: Change Tax Rate", changetaxrate),
#        ("U", "   Utopia's Auction", None),
#        ("W", "   Buy Soldiers", None),
        ("X", ":military-helmet: Train Serfs to Soldiers", trainsoldiers),
        ("Y", "   Your Status", lib.playerstatus)
    )

    # @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_town.lbl#L130
    # @since 20200830
    def menu():
        bbsengine.title("town menu")

        for hotkey, description, func in optiontable:
            if callable(func):
                ttyio.echo("{var:empyre.highlightcolor}[%s]{/all} {green}%s" % (hotkey, description))
        ttyio.echo("{/all}")
        ttyio.echo("{var:empyre.highlightcolor}[Q]{/all} :door: {green}Return to the Empyre{/all}{f6}")
    
    terminalwidth = bbsengine.getterminalwidth()

    hotkeys = "Q"
    for hotkey, desc, func in optiontable:
        if callable(func):
            hotkeys+= hotkey
            ttyio.echo("empyre.town.menu.100: adding hotkey %r" % (hotkey), level="debug")

    loop = True
    while loop:
        lib.setarea(args, player, "town menu")
        player.save()
        menu()
        ch = ttyio.inputchar(f"town [{hotkeys}]: ", hotkeys, "Q")
        if ch == "Q":
            ttyio.echo(":door: {green}Return to the Empyre{/all}")
            loop = False
            continue
        else:
            for key, desc, func in optiontable:
                if ch == key:
                    ttyio.echo(desc)
                    if callable(func):
                        func(args, player)
                    elif type(func) is str:
                        lib.runsubmodule(args, player, func)
                    else:
                        ttyio.echo("No Function Defined for this option", level="error")
                    break
    return True
