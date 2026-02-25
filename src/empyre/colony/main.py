# @since 20220729

from bbsengine6 import io, util

def init(args, **kw):
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args, **kw):
    return None

def stats(args, **kw):
    player = kw["player"] if "player" in kw else None
    if player is None:
        io.echo("you do not exist! go away!")
        return False

    colony = kw["colony"] if "colony" in kw else None

    util.heading("colony stats")
    io.echo(f"{colony.moniker} (#{player.moniker})")
    io.echo(f"Coins:       {player.coins}")
    io.echo(f"Grain:      {player.grain}")
    io.echo(f"Tax Rate:   {player.taxrate}%")
    io.echo(f"Serfs:      {colony.serfs}")
    io.echo(f"Nobles:     {colony.nobles}")
    io.echo(f"Imports:    {colony.imports}")
    io.echo(f"Ships:      {colony.ships}")
    io.echo(f"Navigators: {player.navigator}")
    io.echo(f"Colonies:   {player.colonies}")

def main(args, **kw):
    player = kw["player"] if "player" in kw else None
    if player is None:
        io.echo("you do not exist! go away!", level="error")
        return False

    io.echo(f"empyre.colony.main.100: {player.colonies=}", level="debug")

    if player.colonies > 0:
        io.echo(f"colony trip... {util.pluralize(player.colonies, 'colony', 'colonies')}{{f6}}")
    else:
        return True

    io.echo("King George wishes you a safe and prosperous trip to your %s{f6}" % (util.pluralize(player.colonies, "colony", "colonies", quantity=False)))

    done = False
    while not done:
        prompt = "{var:optioncolor}[C]{var:promptcolor} Continue {var:optioncolor}[1]{var:promptcolor} Grain {var:optioncolor}[2]{var:promptcolor} Serf {var:optioncolor}[3]{var:labelcolor} Noble {var:optioncolor}[4] Navigator{var:promptcolor}: {var:inputcolor}"
        ch = io.inputchar(prompt, "C1234", "C")
        if ch == "C":
            done = True
            break
        elif ch == "1":
            # grain
            io.echo("grain")
        elif ch == "2":
            io.echo("serfs")
        elif ch == "3":
            io.echo("nobles")
        elif ch == "4":
            io.echo("navigators")

    return True
