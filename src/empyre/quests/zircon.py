import ttyio5 as ttyio
import bbsengine5 as bbsengine

from .. import lib

def zircon1(player):
    gifts = []
    x = bbsengine.diceroll(40) # random.randint(1, 40)
    if x >= 19:
        return gifts
    ttyio.echo("{purple}Zircon says he must consult the bones...")
    x = bbsengine.diceroll(5) # random.randint(1, 5)
    if x == 1:
        gifts.append(bbsengine.pluralize(8000, "acre", "acres"))
        player.land += 8000 # x(2)
    elif x == 2:
        gifts.append(bbsengine.pluralize(30000, "coin", "coins"))
        player.coins += 30000 # x(3)
    elif x == 3:
        gifts.append(bbsengine.pluralize(5, "noble", "nobles"))
        player.nobles += 5 # x(6) nobles
    elif x == 4:
        gifts.append(bbsengine.pluralize(40000, "bushel", "bushels"))
        player.grain += 40000 # x(17)
    return gifts

def zircon2(player):
    gifts = []
    x = bbsengine.diceroll(5) # random.randint(1, 5)
    if x == 1:
        gifts.append(bbsengine.pluralize(1000, "serf", "serfs"))
        player.serfs += 1000 # x(19)
    elif x == 2:
        gifts.append(bbsengine.pluralize(4, "shipyard", "shipyards"))
        player.shipyards += 4 # x(10)
    elif x == 3:
        gifts.append(bbsengine.pluralize(2, "fort", "forts"))
        player.forts += 2
        gifts.append(bbsengine.pluralize(8, "cannon", "cannons"))
        player.cannons += 8
    elif x == 4:
        gifts.append(bbsengine.pluralize(50, "horse", "horses"))
        player.horses += 50
    return gifts

def zircon3(player):
    gifts = []
    x = bbsengine.diceroll(5) # random.randint(1, 5)
    if x == 1:
        player.foundries += 4 # x(9)
        gifts.append(bbsengine.pluralize(4, "foundry", "foundries"))
    elif x == 2:
        player.markets += 10 # x(7)
        gifts.append(bbsengine.pluralize(10, "market", "markets"))
    elif x == 3:
        player.mills += 10 # x(8)
        gifts.append(bbsengine.pluralize(10, "mill", "mills"))
    elif x == 4:
        player.spices += 10 # x(25) spices
    elif x == 5:
        player.ships += 4 # x(12)
        gifts.append(bbsengine.pluralize(4, "ship", "ships", emoji=":anchor:"))
    return gifts

def zircon4(player):
    gifts = []
    if bbsengine.diceroll(20) < 5:
        gifts.append("10 tons of spices")
        player.spices += 10 # x(25)
    return gifts

def zircon5(player):
    gifts = []
    if bbsengine.diceroll(20) < 4:
        gifts.append("a dragon")
        player.dragons += 1
    return gifts

def zircon6(player):
    gifts = []
    if bbsengine.diceroll(20) < 6:
        gifts.append("20 tons of spices")
        player.spices += 20
    return gifts

def zircon7(player):
    gifts = []
    if bbsengine.diceroll(20) < 5:
        gifts.append("4 nobles") # x(6)
        player.nobles += 4
    return gifts

def zircon8(player):
    gifts = []
    if bbsengine.diceroll(20) < 5:
        gifts.append("6 cannons")
        player.cannons += 6
    return gifts

def init(args, **kw):
    pass

# @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/mdl.emp.delx3.txt#L362
def main(args, **kw):
    player = kw["player"] if "player" in kw else None

#    filepath = bbsengine.buildfilepath(lib.QUESTDIR, "zircon-intro.txt")
#    ttyio.echo("filepath=%r" % (filepath), level="debug")
#    bbsengine.filedisplay(args, filepath)
    
    ttyio.echo("player=%r" % (player), level="debug")

    if ttyio.inputboolean("{var:promptcolor}complete zircon? {var:optioncolor}[Yn]{var:promptcolor}: {var:inputcolor}", "Y") is False:
        land = 2000 if player.land >= 2000 else player.land
        ttyio.echo("land=%d player.land=%d" % (land, player.land), level="debug")
        nobles = 4 if player.nobles >= 4 else player.nobles
        coins = 9000 if player.coins >= 9000 else player.coins
        serfs = 600 if player.serfs >= 600 else player.serfs

        player.land -= land
        player.nobles -= nobles
        player.coins -= coins
        player.serfs -= serfs

        ttyio.echo("player.land=%d" % (player.land), level="debug")

        ttyio.setvariable("land", bbsengine.pluralize(land, "acre", "acres"))
        ttyio.setvariable("serfs", bbsengine.pluralize(serfs, "serf", "serfs"))
        if nobles > 0:
            ttyio.setvariable("nobles", bbsengine.pluralize(nobles, "noble", "nobles"))
        else:
            ttyio.setvariable("nobles", "")
        ttyio.setvariable("coins", bbsengine.pluralize(coins, "coin", "coins", emoji=":moneybag:"))

        player.save()
        return False

    gifts = []
    gifts += zircon1(player)
    gifts += zircon2(player)
    gifts += zircon3(player)
    gifts += zircon4(player)
    gifts += zircon5(player)
    gifts += zircon6(player)
    gifts += zircon7(player)
    gifts += zircon8(player)
    if len(gifts) > 0:
        ttyio.echo("You are gifted %s by Arch-Mage Zircon." % (bbsengine.oxfordcomma(gifts)))
        lib.newsentry(args, player, "You have completed the Zircon Quest")
    return True
