import random

import ttyio5 as ttyio
import bbsengine5 as bbsengine

# @since 20230106 moved to empyre.town.soldierpromotion
# @since 20200830
# @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_town.lbl#L231
def access(args, op, **kwargs):
    return True

def init(args, **kwargs):
    return True

def main(args, player, **kwargs):
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
    ttyio.echo("{F6}{yellow}Good day, I take it that you are here to see if any of your soldiers are eligible for promotion to the status of noble.{F6}")
    ttyio.echo("Well, after checking all of them, I have found that %s eligible.{f6}" % (bbsengine.pluralize(promotable, "soldier is", "soldiers are")))
    if promotable == 0:
        return

    ch = ttyio.inputboolean("{var:promptcolor}Do you wish them promoted? {var:optioncolor}[yN]{var:promptcolor}: {var:inputcolor}", "N")
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
