import random

# import ttyio6 as ttyio
# import bbsengine6 as bbsengine
from bbsengine6 import io, util

from . import lib
from . import player as libplayer

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args, **kwargs):
    return None

def main(args, **kwargs):
    player = kwargs.get("player", None)
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
        grnres = player.getresource("grain")
        io.echo("You only have {} to give to your people.".format(util.pluralize(grain, **grnres)))

    serfsstarved = 0 # j
    newbornserfs  = int(random.random()*(player.serfs//12)+10) # z(3)
    naturaldeaths = int(random.random()*(player.serfs//10)+30) # z(1)
    immigration = int(random.random()*(player.serfs//15)+10) # z(5)=int(rnd(1)*(x(19)/15)+10)

    srf = player.getresource("serfs")
    io.echo(f"{{labelcolor}}CENSUS   - {util.pluralize(player.serfs, **srf)}")
    io.echo(f"{{labelcolor}}  Serfs Starved  {{valuecolor}}{serfsstarved:>6n}")
    io.echo(f"{{labelcolor}}  Newborn Serfs  {{valuecolor}}{newbornserfs:>6n}")
    io.echo(f"{{labelcolor}}  Natural Deaths {{valuecolor}}{naturaldeaths:>6n}")
    io.echo(f"{{labelcolor}}  Immigration    {{valuecolor}}{immigration:>6n}")
    io.echo(f"{{labelcolor}}EXPENSES - {{valuecolor}}{payables:>6n}{{normalcolor}}")
    io.echo()
    io.echo(f"{{labelcolor}} Soldier's Pay:  {{valuecolor}}{soldierpay:>6n}") # % ("{:>6n}".format(soldierpay)))
    io.echo(f"{{labelcolor}} Palace Rent:    {{valuecolor}}{palacerent:>6n}") # %s" % ("{:>6n}".format(palacerent)))
    io.echo(f"{{labelcolor}} Noble's Gifts:  {{valuecolor}}{noblegifts:>6n}") # % ("{:>6n}".format(noblegifts)))
    io.echo()

    io.echo(f"{{labelcolor}}INCOME --- {{valuecolor}}{receivables:>6n}{{normalcolor}}")
    io.echo()
    io.echo(f"{{labelcolor}} Markets:        {{valuecolor}}{p2:>6n}") # % ("{:>6n}".format(p2))) # p2 markets
    io.echo(f"{{labelcolor}} Mills:          {{valuecolor}}{p3:>6n}") # % ("{:>6n}".format(p3))) # p3 mills
    io.echo(f"{{labelcolor}} Foundries:      {{valuecolor}}{p4:>6n}") # % ("{:>6n}".format(p4))) # p4 foundries
    io.echo(f"{{labelcolor}} Shipyards:      {{valuecolor}}{p5:>6n}") # % ("{:>6n}".format(p5))) # p5 shipyards
    io.echo(f"{{labelcolor}} Taxes:          {{valuecolor}}{taxes:>6n}") # % ("{:>6n}".format(taxes))) # tg/taxes
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

    rank = libplayer.calculaterank(args, player)

    if args.debug is True:
        io.echo(f"{player.rank=} {rank=}", level="debug")
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
