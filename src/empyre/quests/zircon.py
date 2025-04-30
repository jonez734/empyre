from bbsengine6 import io, util

from .. import lib

#Quest 1: 90,000 gold
#Quest 2: 30 horses
#Quest 3: 15 tons of timber
#Quest 4: 40,000 bushels of grain
#Quest 5: 4,000 acres
#Quest 6: 40 tons of spice
#Quest 7: 4 nobles
#Quest 8: 6 cannons
#Quest 9: Lose 2,000 acres, 600 serfs, 4 Nobles, 9,000 gold

def zircon1(player):
    gifts = []
    x = util.diceroll(40) # random.randint(1, 40)
    if x >= 19:
        return gifts
    io.echo("{purple}Zircon says he must consult the bones...")
    x = util.diceroll(5) # random.randint(1, 5)
    if x == 1:
        landres = player.getresource("land")
        gifts.append(util.pluralize(8000, **landres))
        player.land += 8000 # x(2)
    elif x == 2:
        coinres = player.getresource("coins")
        gifts.append(util.pluralize(30000, **coinres))
        player.coins += 30000 # x(3)
    elif x == 3:
        nobleres = player.getresource("nobles")
        gifts.append(util.pluralize(5, **nobleres))
        player.nobles += 5 # x(6) nobles
    elif x == 4:
        bushelres = player.getresource("grain")
        gifts.append(util.pluralize(40000, **bushelres))
        player.grain += 40000 # x(17)
    return gifts

def zircon2(player):
    gifts = []
    x = util.diceroll(5) # random.randint(1, 5)
    if x == 1:
        serfsres = player.getresource("serfs")
        gifts.append(util.pluralize(1000, **serfsres))
        player.serfs += 1000 # x(19)
    elif x == 2:
        shipyardres = player.getresource("shipyards")
        gifts.append(util.pluralize(4, **shipyardres))
        player.shipyards += 4 # x(10)
    elif x == 3:
        fortres = player.getresource("forts")
        cannonres = player.getresource("cannons")
        gifts.append(util.pluralize(2, **fortres))
        player.forts += 2
        gifts.append(util.pluralize(8, **cannonres))
        player.cannons += 8
    elif x == 4:
        horseres = player.getresource("horses")
        gifts.append(util.pluralize(50, **horseres))
        player.horses += 50
    return gifts

def zircon3(player):
    gifts = []
    x = util.diceroll(5) # random.randint(1, 5)
    if x == 1:
        foundryres = player.getresource("foundries")
        player.foundries += 4 # x(9)
        gifts.append(util.pluralize(4, **foundryres))
    elif x == 2:
        marketres = player.getresource("markets")
        player.markets += 10 # x(7)
        gifts.append(util.pluralize(10, **marketres))
    elif x == 3:
        millsres = player.getresource("mills")
        player.mills += 10 # x(8)
        gifts.append(util.pluralize(10, **millres))
    elif x == 4:
        player.spices += 10 # x(25) spices
    elif x == 5:
        shipres = player.getresource("ships")
        player.ships += 4 # x(12)
        gifts.append(util.pluralize(4, **shipres))
    return gifts

def zircon4(player):
    gifts = []
    if util.diceroll(20) < 5:
        gifts.append("10 tons of spices")
        player.spices += 10 # x(25)
    return gifts

def zircon5(player):
    gifts = []
    if util.diceroll(20) < 4:
        gifts.append("a dragon")
        player.dragons += 1
    return gifts

def zircon6(player):
    gifts = []
    if util.diceroll(20) < 6:
        gifts.append("20 tons of spices")
        player.spices += 20
    return gifts

def zircon7(player):
    gifts = []
    if util.diceroll(20) < 5:
        gifts.append("4 nobles") # x(6)
        player.nobles += 4
    return gifts

def zircon8(player):
    gifts = []
    if util.diceroll(20) < 5:
        gifts.append("6 cannons")
        player.cannons += 6
    return gifts

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

# @see https://github.com/Pinacolada64/ImageBBS/blob/e9f033af1f0b341d0d435ee23def7120821c3960/v1.2/games/empire6/mdl.emp.delx3.txt#L362
def main(args, **kw):
    player = kw["player"] if "player" in kw else None

#    filepath = bbsengine.buildfilepath(lib.QUESTDIR, "zircon-intro.txt")
#    ttyio.echo("filepath=%r" % (filepath), level="debug")
#    bbsengine.filedisplay(args, filepath)
    
    io.echo(f"{player=}", level="debug")

    if io.inputboolean("{var:promptcolor}complete zircon? {var:optioncolor}[Yn]{var:promptcolor}: {var:inputcolor}", "Y") is False:
        land = 2000 if player.land >= 2000 else player.land
        io.echo(f"{land=} {player.land=}", level="debug")
        nobles = 4 if player.nobles >= 4 else player.nobles
        coins = 9000 if player.coins >= 9000 else player.coins
        serfs = 600 if player.serfs >= 600 else player.serfs

        player.land -= land
        player.nobles -= nobles
        player.coins -= coins
        player.serfs -= serfs

        io.echo(f"{player.land=}", level="debug")

        landres = player.getresource("land")
        serfsres= player.getresource("serfs")
        coinsres= player.getresource("coins")
        nobleres= player.getresource("nobles")
        #io.setvariable("land", util.pluralize(land, **landres))
        #io.setvariable("serfs", util.pluralize(serfs, **serfsres))
        #if nobles > 0:
        #    io.setvariable("nobles", util.pluralize(nobles, **nobleres))
        #else:
        #    io.setvariable("nobles", "")
        #io.setvariable("coins", util.pluralize(coins, **coinres))

        player.adjust()
        player.save()
        return True

    gifts = []
    dice = util.diceroll(1, 10)
    if dice == 1:
        gifts += zircon1(player)
    elif dice == 2:
        gifts += zircon2(player)
    elif dice == 3:
        gifts += zircon3(player)
    elif dice == 4:
        gifts += zircon4(player)
    elif dice == 5:
        gifts += zircon5(player)
    elif dice == 6:
        gifts += zircon6(player)
    elif dice == 7:
        gifts += zircon7(player)
    elif dice == 8:
        gifts += zircon8(player)

    if len(gifts) > 0:
        io.echo(f"You are gifted {util.oxfordcomma(gifts)} by Arch-Mage Zircon.")
        lib.newsentry(args, player, "You have completed the Zircon Quest")
    return True
