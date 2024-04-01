from bbsengine6 import io, util

from . import lib as libempyre

def buildinvestmentoptions(player):
    if player is None:
        io.echo("You do not exist! Go Away!", level="error")
        return False

    investmentoptions = {}
    index = 0
    for a in player.resources:
        if "price" in a and a["price"] > 0:
            investmentoptions[chr(65+index)] = a
            index += 1
    return investmentoptions

def displayinvestmentoptions(investmentoptions): # opts, player):
    maxlen = 0
    for ch, a in investopts.items(): # player.attributes:
        name = a["name"] if "name" in a else ""
        if len(name) > maxlen:
            maxlen = len(name)
    
    # investopts = buildinvestopts(opts, player)
    for ch, a in investmentoptions.items():
        name = a["name"].title()
        price = a["price"]
#        buf = "{var:empyre.highlightcolor}[%s]{/all}{green} %s: %s " % (ch, name.ljust(maxlen+2, "-"), " {:>6n}".format(price)) # int(terminalwidth/4)-2)
        buf = f"{{optioncolor}}[{ch}]{{/all}}{{labelcolor}} {name.ljust(maxlen+2, '-')}: {{valuecolor}}{price:>6n} " # % (ch, name.ljust(maxlen+2, "-"), " {:>6n}".format(price))
        io.echo(buf)

    io.echo("{f6}{optioncolor}[Y]{labelcolor} Your stats{f6}{optioncolor}[Q]{labelcolor} Quit{/all}")

    return

def init(args, **kw):
    return True

def help(**kw:dict) -> None:
    player = kw["player"] if "player" in kw else None
    investmentoptions = buildinvestmentoptions(player)
    return displayinvestmentoptions(investmentoptions)

def access(args, op, **kw):
    return True

def buildargs(args, **kw):
    return None

def main(args, **kw):
    player = kw["player"] if "player" in kw else None

    util.heading("investments")

    terminalwidth = io.getterminalwidth()

    investmentoptions = buildinvestmentoptions(player)

    options = ""
    for ch, a in investmentoptions.items():
        options += ch
    options += "YQ?"

    displayinvestmentoptions(investmentoptions)

    done = False
    while not done:
        prompt = "{{promptcolor}}{util.pluralize(player.coins, 'coin', 'coins', emoji=':moneybag:')}{{f6}}Investments {{optioncolor}}[{options}]{{promptcolor}}: {{inputcolor}}"
        ch = io.inputchar(prompt, options, "Q", help=help, args=args, player=player)
        if ch == "Q":
            io.echo(f"{{optioncolor}}Q{{labelcolor}} -- Quit")
            done = True
            continue
#        elif ch == "?":
#            ttyio.echo("{lightgreen}? -- {cyan}Help")
#            displayinvestmentoptions(investopts) # opts, player)
#            continue
        elif ch == "Y":
            io.echo(f"{{optioncolor}}Y{{labelcolor}} -- Your Stats")
            player.status()
        else:
            for opt, r in investopts.items():
                if ch == opt:
                    name = r["name"]
                    price = r["price"]
                    attr = r["name"]
                    singular = r["singular"] if "singular" in r else "singular"
                    plural = r["plural"] if "plural" in r else "plural"
                    io.echo(f"{{optioncolor}}{ch}{{labelcolor}} -- {name.title()} {util.pluralize(price, 'coin', 'coins', emoji=':moneybag:')} each")
                    trade(args, player, attr, name, price, singular, plural)
                    break
            else:
                io.echo("{optioncolor}%r{labelcolor} -- not implemented yet" % (ch))
                continue
    return True
