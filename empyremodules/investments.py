import ttyio5 as ttyio
import bbsengine5 as bbsengine

from . import lib

def buildinvestmentoptions(args, player):
    investmentoptions = {}
    index = 0
    for a in player.attributes:
        if "price" in a and a["price"] > 0:
            investmentoptions[chr(65+index)] = a
            index += 1
    return investmentoptions

def displayinvestmentoptions(investopts): # opts, player):
    maxlen = 0
    for ch, a in investopts.items(): # player.attributes:
        name = a["name"] if "name" in a else ""
        if len(name) > maxlen:
            maxlen = len(name)
    
    # investopts = buildinvestopts(opts, player)
    for ch, a in investopts.items():
        name = a["name"].title()
        price = a["price"]
        buf = "{var:empyre.highlightcolor}[%s]{/all}{green} %s: %s " % (ch, name.ljust(maxlen+2, "-"), " {:>6n}".format(price)) # int(terminalwidth/4)-2)
        ttyio.echo(buf)

    ttyio.echo("{f6}{var:empyre.highlightcolor}[Y]{/all}{green} Your stats{f6}{var:empyre.highlightcolor}[Q]{/all}{green} Quit{/all}")

    return

def main(args, player):
    bbsengine.title("investments")
    lib.setarea(args, player, "investments")

    terminalwidth = ttyio.getterminalwidth()

    investopts = buildinvestmentoptions(args, player)

    options = ""
    for ch, a in investopts.items():
        options += ch
    options += "YQ?"
    displayinvestmentoptions(investopts)

    done = False
    while not done:
        lib.setarea(args, player, "investments")
        buf = "{cyan}:moneybag: %s{f6}" % (bbsengine.pluralize(player.coins, "coin", "coins"))
        buf += "Investments [%s]: {lightgreen}" % (options)
        ch = ttyio.inputchar(buf, options, "Q")
        if ch == "Q":
            ttyio.echo("{lightgreen}Q{cyan} -- Quit")
            done = True
            continue
        elif ch == "?":
            ttyio.echo("{lightgreen}? -- {cyan}Help")
            displayinvestmentoptions(investopts) # opts, player)
            continue
        elif ch == "Y":
            ttyio.echo("{lightgreen}Y -- {cyan}Your Stats")
            player.status()
        else:
            for opt, a in investopts.items():
                if ch == opt:
                    name = a["name"]
                    price = a["price"]
                    attr = a["name"]
                    singular = a["singular"] if "singular" in a else "singular"
                    plural = a["plural"] if "plural" in a else "plural"
                    ttyio.echo("{lightgreen}%s{green} -- {cyan}%s{/all} :moneybag: %s each" % (ch, name.title(), bbsengine.pluralize(price, "coin", "coins")))
                    trade(args, player, attr, name, price, singular, plural)
                    break
            else:
                ttyio.echo("{lightgreen}%r -- {cyan}not implemented yet" % (ch))
                continue
    return True
