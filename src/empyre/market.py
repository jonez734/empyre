from bbsengine6 import io, util

from . import lib as libempyre


def init(args, **kwargs):
    return True


def access(args, op, **kwargs):
    return True


def buildargs(args=None, subparser=None, **kwargs):
    return None


def markethelp(**kwargs):
    player = kwargs.get("player", None)
    if player is None:
        return False

    trades = [
        ("grain", 12, 50),
        ("land", 15, 100),
        ("horses", 80, 20),
        ("timber", 25, 50),
        ("spices", 150, 10),
    ]

    maxlen = max(len(name) for name, _, _ in trades)

    for name, base_price, divisor in trades:
        current = player.getresource(name).get("value", 0)
        price = base_price + current // divisor
        label = f"[{name[0].upper()}] {name.capitalize().ljust(maxlen + 2, '-')}: {price:>6n}"
        io.echo(f"{{optioncolor}}{label}{{valuecolor}}")

    io.echo(
        "{f6}{optioncolor}[Y]{labelcolor} Your stats{f6}{optioncolor}[Q]{labelcolor} Quit{/all}"
    )
    return True


def main(args, **kwargs):
    player = kwargs.get("player", None)
    if player is None:
        io.echo("You do not exist! Go Away!", level="error")
        return False

    util.heading(": corn exchange :")
    libempyre.setbottombar(args, "market", player=player)

    trades = [
        ("grain", 12, 50),
        ("land", 15, 100),
        ("horses", 80, 20),
        ("timber", 25, 50),
        ("spices", 150, 10),
    ]

    options = ""
    for name, _, _ in trades:
        options += name[0].upper()

    options += "YQ?"

    done = False
    while not done:
        markethelp(player=player)

        prompt = f"{{promptcolor}}{util.pluralize(player.coins, 'coin', 'coins', emoji=':moneybag:')}{{f6}}Market {{optioncolor}}[{options}]{{promptcolor}}: {{inputcolor}}"
        ch = io.inputchar(
            prompt,
            options,
            "Q",
            help=markethelp,
            args=args,
            **kwargs,
        )

        if ch == "Q":
            io.echo("{optioncolor}Q{labelcolor} -- Quit")
            done = True
            continue
        elif ch == "Y":
            io.echo("{optioncolor}Y{labelcolor} -- Your Stats")
            player.status()
            continue

        for name, base_price, divisor in trades:
            if ch == name[0].upper():
                res = player.getresource(name)
                current = res.get("value", 0)
                res["price"] = base_price + current // divisor
                io.echo(
                    f"{{optioncolor}}{ch}{{labelcolor}} -- {name.capitalize()} {util.pluralize(res['price'], 'coin', 'coins', emoji=':moneybag:')} each"
                )
                libempyre.trade(args, player, name, **res)
                player.adjust()
                player.save()
                break
        else:
            io.echo("{optioncolor}%r{labelcolor} -- not implemented yet" % (ch))
            continue

    return True
