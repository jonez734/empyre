# import ttyio6 as ttyio
# import bbsengine6 as bbsengine
from bbsengine6 import io, member, util, database, bank

from . import lib


def init(args, **kwargs):
    return True


def access(args, op, **kwargs):
    def _work(conn):
        ##        io.echo(f"empyre.sysopoptions.access.120: {op=} {conn=}", level="debug")
        sysop = member.checkflag(args, "sysop", mogrify=True, conn=conn)
        ##        io.echo(f"empyre.sysopoptions.120: {sysop=}", level="debug")
        if sysop is True:
            if args.debug is True:
                io.echo("empyre.sysopoptions.140: access check pass", level="debug")
            return True
        ##        io.echo("empyre.sysopoptions.access.100: permission denied", level="error")
        return False

    # io.echo(f"empyre.sysopoptions.access.180: {kwargs=}", level="debug")
    conn = kwargs.get("conn", None)
    if conn is None:
        pool = kwargs.get("pool", None)
        if pool is None:
            ###            io.echo(f"empyre.sysopoptions.160: {pool=}", level="error")
            return False
        with database.connect(args, pool=pool) as conn:
            return _work(conn)
    return _work(conn)


def buildargs(args, **kwargs):
    return None


def main(args, **kwargs):
    player = kwargs.get("player", None)
    if player is None:
        io.echo("empyre.sysopoptions.100: You do not exist! Go away!", level="error")
        return False

    lib.setbottombar(args, "sysop options", player=player)
    util.heading("sysop options")
    player.turncount = io.inputinteger(
        "{var:promptcolor}turncount: {var:inputcolor}",
        player.turncount,
        args=args,
        **kwargs,
    )
    x = io.inputinteger(
        "{var:promptcolor}:moneybag: coins: {var:inputcolor}", player.coins, **kwargs
    )
    if x is not None and x > 0:
        bank_service = bank.BankService(args)
        current_balance = bank_service.get_balance(player.moniker)
        diff = x - current_balance
        if diff > 0:
            bank_service.add_funds(player.moniker, diff, transaction_type="sysop_set", description="Sysop set coins")
        elif diff < 0:
            bank_service.remove_funds(player.moniker, abs(diff), transaction_type="sysop_set", description="Sysop set coins")
        player.coins = bank_service.get_balance(player.moniker)
    elif x is not None:
        io.echo("coins cannot be less than zero")
    io.echo("{/all}")
    player.adjust()
    player.save()
    io.echo(util.hr())
    return True
