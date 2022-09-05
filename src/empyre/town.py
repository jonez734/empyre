#
# @since 20220728
#

import ttyio5 as ttyio
import bbsengine5 as bbsengine

from . import lib

def init(args, **kw):
    pass

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
    # @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_town.lbl#L162
    def lucifersden(args, player):
        if player.coins > 10000 or player.land > 15000:
            ttyio.echo("{F6}I checked our inventory and we have plenty of souls. Maybe we can deal some other time.")
            return

        lib.setarea("town: lucifer's den")
        
        bbsengine.title("LUCIFER'S DEN - Where Gamblin's no Sin!", hrcolor="{orange}", titlecolor="{bgred}{yellow}")
        ttyio.echo("{yellow}I will let you play for the price of a few souls!")
        ch = ttyio.inputboolean("{cyan}Will you agree to this? [yN]: {/all} ", "N")
        if ch is False:
            ttyio.echo("Some other time, then.")
            return
        # always win, but it costs 10 serfs, 50 serfs if you guess correctly
        # og=int(3*rnd(0)+2)
        # &"{f6:2}{lt. blue}Odds:"+str$(og)+" to 1"
        done = False
        while not done:
            odds = random.randint(2, 4)
            ttyio.echo("Odds: %s to 1" % (odds))
            if player.serfs < 1000:
                ttyio.echo("You must have at least {var:empyre.highlightcolor}%s{/all} to gamble here!" % bbsengine.pluralize(1000, "serf", "serfs"))
                done = True
                break
            ttyio.echo("{F6}You have :moneybag: {var:empyre.highlightcolor}%s{/all} and {var:empyre.highlightcolor}%s{/all}" % (bbsengine.pluralize(player.coins, "coin", "coins"), bbsengine.pluralize(player.serfs, "serf", "serfs")))
            bet = ttyio.inputinteger("{cyan}Bet how many coins? (No Limit) {blue}-->{green} ")
            ttyio.echo("{/all}")
            if bet is None or bet < 1 or bet > player.coins:
                ttyio.echo("Exiting Lucifer's Den")
                done = True
                break
            
            pick = ttyio.inputinteger("{blue}Pick a number from 1 to 6: ")
            ttyio.echo("{/all}")
            if pick is None or pick < 1:
                ttyio.echo("invalid value")
                done = True
                return
            
            dice = bbsengine.diceroll(6)

            if args.debug is True:
                ttyio.echo("dice=%s" % (dice), level="debug")

            if dice == pick:
                ttyio.echo("{green}MATCH!{/all}{F6}")
                player.coins += bet*odds
                player.serfs -= 50
            else:
                player.coins += bet
                player.serfs -= 10
            ttyio.echo()
                
            # b=int(rnd(.)*(og+1)+1):on-(a=b)goto {:104}:pn=pn+x:sf=sf-10
            # &"{f6}{white}Close Enough!{f6}{pound}q1":goto {:170}
#        bbsengine.poparea()
        return

    # @since 20200830
    # @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_town.lbl#L231
    def soldierpromotion(args, player):
        terminalwidth = ttyio.getterminalwidth()
        
        player.soldierpromotioncount += 1
        if player.turncount > 2:
            if player.soldierpromotioncount > 1:
                ttyio.echo("Nice try, but we keep our promotion records up to date, and they show that your eligible soldiers have already been promoted! Just wait until King George hears about this!")
                player.soldiers -= 20
                if player.soldiers < 0:
                    player.soldiers = 1
                player.land -= 500
                if player.land < 0:
                    player.land = 1
                player.nobles -= 1
                if player.nobles < 0:
                    player.nobles = 0
                player.serfs -= 100
                if player.serfs < 0:
                    player.serfs = 1
                player.save()
                
        if player.soldiers < 10:
            ttyio.echo("None of your soldiers are eligible for promotion to Noble right now.{F6}")
            return
            
        promotable = random.randint(0, 4)
        
        bbsengine.title(": Soldier Promotions :")
#        ttyio.echo("{autogreen}{reverse}%s{/reverse}{/green}" % (": Soldier Promotions :".center(terminalwidth-2)))
        ttyio.echo("{F6}{yellow}Good day, I take it that you are here to see if any of your soldiers are eligible for promotion to the status of noble.{F6}")
        ttyio.echo("Well, after checking all of them, I have found that %s eligible.{f6}" % (bbsengine.pluralize(promotable, "soldier is", "soldiers are")))
        if promotable == 0:
            return

        ch = ttyio.inputboolean("{var:promptcolor}Do you wish them promoted? [var:optioncolor}yN{var:promptcolor}]: {var:inputcolor}", "N")
        ttyio.echo("{/all}")
        if ch is False:
            return

        player.soldiers -= promotable
        player.nobles += promotable

        ttyio.echo("{F6}OK, all have been promoted! We hope they serve you well.")
        
        # &"{f6}{yellow}Good day, I take it that you are here to{pound}$l"
        # &"see if any of your warriors are eligible for promotion{f6}"
        # &"to the status of Noble.{f6:2}"
        # &"{pound}w2Well, after checking all of your{pound}$l"
        # &"warriors, I have found that"+str$(wb)+" of{f6}"
        # &"them are eligible.{f6}"
        # &"{f6:2}{lt. green}Do you wish them promoted? (Y/N) >> ":gosub 1902
        # if a then wa=wa-wb:nb=nb+wb:&"{f6:2}OK, all have been promoted! We hope{pound}$lthey serve you well.{f6}"
        return

    def realtorsadvice(args, player):
        terminalwidth = ttyio.getterminalwidth()-2
        bbsengine.title(": hood's real deals! :")
        lib.setarea(args, player, "town -> hood's real deals!")
        
        # you have 10 shipyards, BSC
        # you have 10 acres of land
        # prompt = "You have {reverse}%s{/reverse} and {reverse}%s{/reverse}" % (pluralize(player.shipyards, "shipyard", "shipyards"), pluralize(player.credits, "credit", "credits"))
        # all of these are ints
        trade(args, player, "shipyards", "shipyards", 2500+player.shipyards//2, "shipyard", "shipyards", "a")
        trade(args, player, "ships", "ships", 5000, "ship", "ships", "a", ":anchor:")
        trade(args, player, "foundries", "foundries", 2000+player.foundries//2, "foundry", "foundries", "a")
        trade(args, player, "mills", "mills", 500+player.mills//2, "mill", "mills", "a")
        trade(args, player, "markets", "markets", 250+player.markets//2, "market", "markets", "a")
        
        player.save()

#        bbsengine.poparea()
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
        ttyio.echo("{f6}{white}You have %s requirements to be trained %s." % (bbsengine.pluralize(eligible, "serf that meets", "serfs that meet"), bbsengine.pluralize(eligible, "as a soldier", "as soldiers", quantity=False)))
        if eligible > 0:
            ttyio.echo("Training cost is 1 acre per serf.")
            if ttyio.inputboolean("Do you wish them trained? [yN]: ", "N") is True:
                player.serfs -= eligible
                player.land -= eligible
                player.soldiers += eligible
                ttyio.echo("Promotions completed.")
            else:
                ttyio.echo("No promotions performed.")

    options = (
        ("C", ":bank: Cyclone's Natural Disaster Bank", naturaldisasterbank),
        ("L", ":fire: Lucifer's Den", lucifersden), # lucifersden),
        ("P", ":prince: Soldier Promotion to Noble", soldierpromotion),
        ("R", ":house: Realtor's Advice", realtorsadvice),
        ("S", "   Slave Market", None),
        ("T", ":receipt: Change Tax Rate", changetaxrate),
        ("U", "   Utopia's Auction", None),
        ("W", "   Buy Soldiers", None),
        ("X", ":military-helmet: Train Serfs to Soldiers", trainsoldiers),
        ("Y", "   Your Status", lib.playerstatus)
    )

    # @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_town.lbl#L130
    # @since 20200830
    def menu():
        bbsengine.title("town menu")

        for hotkey, description, func in options:
            if callable(func):
                ttyio.echo("{var:empyre.highlightcolor}[%s]{/all} {green}%s" % (hotkey, description))
        ttyio.echo("{/all}")
        ttyio.echo("{var:empyre.highlightcolor}[Q]{/all} :door: {green}Return to the Empyre{/all}")
    
    terminalwidth = bbsengine.getterminalwidth()

    hotkeys = "Q"
    for hotkey, desc, func in options:
        if callable(func):
            hotkeys+= hotkey
            ttyio.echo("empyre.town.menu.100: adding hotkey %r" % (hotkey), level="debug")

    done = False
    while not done:
        lib.setarea(args, player, "town menu")
        player.save()
        menu()
        ch = ttyio.inputchar("town [clprstuwxyQ]: ", hotkeys, "Q")
        if ch == "Q":
            ttyio.echo(":door: {green}Return to the Empyre{/all}")
            done = True
            continue
        else:
            for key, desc, func in options:
                if ch == key:
                    if callable(func):
                        ttyio.echo(desc)
                        func(args, player)
                    else:
                        ttyio.echo("No Function Defined for this option", level="error")
                    break
    return True
