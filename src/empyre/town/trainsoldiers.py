#import ttyio6 as ttyio
#import bbsengine6 as bbsengine

from .. import lib

from bbsengine6 import io, util

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args, **kw):
    return None

# @since 20200830
# @see https://github.com/Pinacolada64/ImageBBS/blob/master/v1.2/games/empire6/plus_emp6_town.lbl#L244
def main(args, player, **kwargs):
    util.heading(": Soldier Training :")
    lib.setarea(args, player, "town -> train soldiers")
    io.echo()
    eligible = int(player.nobles*20-player.soldiers)
    io.echo("empyre.trainsoldiers.100: eligible=%d" % (eligible), level="debug")
    if player.serfs < 1500 or eligible > (player.serfs // 2):
        io.echo("You do not have enough serfs of training age.")
        return True
    
    #&"{f6}{white}You have"+str$(wb)+" serfs that meet the requirement to be trained"
    #&" as warriors.{f6:2}Training cost is one acre per serf.{f6}"
    #&"{f6}{lt. green}Do you want them trained (Y/N) >> ":gosub 1902
    #if a then sf=sf-wb:la=la-wb:wa=wa+wb:&"{f6:2}{pound}w2{yellow}Ok, all serfs have been trained.{f6}{pound}q1"
    # ttyio.echo("{f6}{white}You have %s requirements to be trained %s." % (bbsengine.pluralize(eligible, "serf that meets", "serfs that meet"), bbsengine.pluralize(eligible, "as a soldier", "as soldiers", quantity=False)))
    io.echo("{f6}{var:normalcolor}You have %s requirments to be trained as %s." % (bbsengine.util.pluralize(eligible, "serf that meets", "serfs that meet"), bbsengine.util.pluralize(eligible, "a :military-helmet: warrior", ":military-helmet: warriors", quantity=False)))
    if eligible > 0:
        io.echo("Training cost is 1 acre per serf.")
        if io.inputboolean("{var:promptcolor}Do you wish them trained? {var:optioncolor}[yN]{var:promptcolor}: {var:inputcolor}", "N") is True:
            player.serfs -= eligible
            player.land -= eligible
            player.soldiers += eligible
            io.echo("Promotions completed.")
        else:
            io.echo("No promotions performed.")

    return True
