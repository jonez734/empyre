from bbsengine6 import io, util, bank

# @since 20220731 created quests.raidpiratecamp.py


def init(args, **kwargs):
    return True


def access(args, op, **kwargs):
    return True


def buildargs(args, **kwargs):
    return None


def main(args, **kwargs):
    player = kwargs["player"] if "player" in kwargs else None
    bank_service = bank.BankService(args)

    io.echo(f"{player.coins=}", level="debug")

    def isquestcompleted():
        return io.inputboolean(
            "{var:promptcolor}quest completed? {var:optioncolor}[Yn]{var:promptcolor}: {var:inputcolor}",
            "Y",
            **kwargs,
        )

    if isquestcompleted() is True:
        coinres = player.getresource("coins")
        io.echo(f"You gain {util.pluralize(30000, **coinres)}")
        bank_service.add_funds(
            player.moniker,
            30000,
            transaction_type="quest_reward",
            description="Raid Pirate Camp quest reward",
        )
        player.coins = bank_service.get_balance(player.moniker)
        result = True
    else:
        io.echo("You failed to complete this quest.")
        result = False
    io.echo(f"after completed check, {player.coins=}", level="debug")
    player.adjust()
    player.save()
    return result
