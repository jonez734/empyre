import random

# import ttyio6 as ttyio
# import bbsengine6 as bbsengine
from bbsengine6 import io, util

from . import lib

def init(args, **kw):
    return True

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

def main(args, **kw):
    player = kw["player"] if "player" in kw else None
    if player is None:
        io.echo("You do not exist! Go Away!", level="error")
        return False

    # tr = player.taxrate
    # ff = player.combatvictorycount
    # p1 = palace percentage (up to 10 pieces)
    # p2=int(((rnd(1)*75)+sf/100)*f%(2))
    p2 = int(((random.random()*75)+player.serfs//100)*player.markets)
    # p3=int(((rnd(1)*100)+gr/1000)*f%(3))
    p3 = int(((random.random()*100)+player.grain//1000)*player.mills)
    # p4=((rnd(1)*175)+wa)*f%(4)/(2-ff)
    p4 = ((random.random()*175)+player.soldiers)*player.foundries//(2-player.combatvictorycount)
    # p5=((rnd(1)*200)+la/30)*f%(5)/(2-ff)
    p5 = ((random.random()*200)+player.land//30)*player.shipyards//(2-player.combatvictorycount)
    # p4=int(p4-(p4*tr/200)):p5=int(p5-(p5*tr/150))
    p4 = p4-(p4*player.taxrate//200)
    p5 = p5-(p5*player.taxrate//150)
    # py=(wa*(ff+2))+(tr*f%(1)*10)/40:xx=int(tr*(rnd(0)*nb))*100/4

    noblegifts = int(player.taxrate*(random.random()*player.nobles))*100//4 # xx
    if noblegifts < 1 and player.nobles > 67:
        a = player.nobles // 5
        player.nobles -= a
        io.echo("{blue}%s{/blue}" % (util.pluralize(a, "noble defects", "nobles defect")))

    # pn=int(pn+p2+p3+p4+p5):tg=int((p2+p3+p4+p5)*tr/100):pn=pn+tg
    taxes = (p2+p3+p4+p5)*player.taxrate//100
    # player.credits += (p2+p3+p4+p5+tg)
    receivables = p2+p3+p4+p5+taxes

    # ln=auto-reset land requirement
    # mp=auto-reset emperor status
    # en=bbs credit/coins exchange active
    # nn=bbs credit/coins exchange rate
    palacerent = player.taxrate*player.palaces*10

    soldierpay = int((player.soldiers*(player.combatvictorycount+2))+(player.taxrate*player.palaces*10)//40) # py
    payables = soldierpay+noblegifts+palacerent
    
    util.heading("yearly report")
        # pn=pn-(py+xx-pt)

        # &"{f6:2}{lt. green}PAYABLES{white}"
	# &"{f6:2} Soldiers Pay:"+str$(wa*(ff+2))+"{f6} Palace Rent :"
	# &str$(tr*f%(1)*10)+"{f6} Nobles Gifts:"+str$(x)

#    ttyio.echo("Receivables: %s" % "{:>6n}".format(receivables)) # (pluralize(receivables, "credit", "credits")))
#    ttyio.echo("Payables:    %s" % "{:>6n}".format(payables)) # (pluralize(payables, "credit", "credits")))
    peoplerequire = player.serfs*5+1 # pr plus_emp6_trading.lbl
    armyrequires = player.soldiers*10+1 # ar
    armygiven = armyrequires
    grain = player.grain
    givenpeople = peoplerequire # gp pr
    gd = givenpeople//peoplerequire # no idea of a better name, yet
    ad = givenpeople//peoplerequire # pr
    # bb: babies born
    # dn: died naturally

    pd = 0

    if gd < 1:
        pass

    if player.grain < 0:
        givenpeople = 0
        armygiven = 0
        # goto no_grain
    if givenpeople > grain:
        io.echo("You only have {} to give to your people.".format(util.pluralize(grain, "bushel", "bushels", emoji=":crop:")))


    io.echo(f"{{var:labelcolor}}CENSUS - {util.pluralize(player.serfs, 'serf', 'serf')}")
    io.echo(f"{{var:labelcolor}}EXPENSES - {{var:valuecolor}}{payables:>6n}{{var:normalcolor}}")
    io.echo()
    io.echo(f"{{var:labelcolor}} Soldier's Pay:  {soldierpay:>6n}") # % ("{:>6n}".format(soldierpay)))
    io.echo(f"{{var:labelcolor}} Palace Rent:    {palacerent:>6n}") # %s" % ("{:>6n}".format(palacerent)))
    io.echo(f"{{var:labelcolor}} Noble's Gifts:  {noblegifts:>6n}") # % ("{:>6n}".format(noblegifts)))
    io.echo()

    io.echo(f"{{var:labelcolor}}INCOME --- {{var:valuecolor}}{receivables:>6n}{{var:normalcolor}}")
    io.echo()
    io.echo(f"{{var:labelcolor}} Markets:        {{var:valuecolor}}{p2:>6n}") # % ("{:>6n}".format(p2))) # p2 markets
    io.echo(f"{{var:labelcolor}} Mills:          {{var:valuecolor}}{p3:>6n}") # % ("{:>6n}".format(p3))) # p3 mills
    io.echo(f"{{var:labelcolor}} Foundries:      {{var:valuecolor}}{p4:>6n}") # % ("{:>6n}".format(p4))) # p4 foundries
    io.echo(f"{{var:labelcolor}} Shipyards:      {{var:valuecolor}}{p5:>6n}") # % ("{:>6n}".format(p5))) # p5 shipyards
    io.echo(f"{{var:labelcolor}} Taxes:          {{var:valuecolor}}{taxes:>6n}") # % ("{:>6n}".format(taxes))) # tg/taxes
    io.echo()

    if receivables == payables:
        io.echo(f"{{lightgreen}}Break Even: {payables:>6n}") #%s{/all}" % ("{:>6n}".format(payables)))
    elif receivables > payables:
        io.echo(f"{{lightgreen}}Profit:     {receivables-payables:>6n}") # %s{/all}" % ("{:>6n}".format(receivables-payables))) # (pluralize(receivables-payables, "credit", "credits")))
    elif receivables < payables:
        io.echo(f"{{lightred}}Loss:       {payables-receivables:>6n}") # %s{/all}" % ("{:>6n}".format(payables-receivables))) # pluralize(payables-receivables, "credit", "credits")))
    io.echo("{/all}")

    player.coins += receivables
    player.coins -= payables

    rank = lib.calculaterank(args, player)

    if args.debug is True:
        io.echo(f"player.rank={player.rank} rank={rank}", level="debug")
    # check for > player.rank, < player.rank and write entry to game log
    player.rank = rank

    player.adjust()
    player.save()

    #' ln=auto-reset land requirement
    #' mp=auto-reset emperor status
    #' en=bbs credit/money exchange active
    #' nn=bbs credit/money exchange rate
    # if mp=0 and la>ln then gosub {:486} ' part of sub.rank
    return True
