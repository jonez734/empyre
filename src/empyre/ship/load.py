from bbsengine6 import io

def main(args, **kw):
    amount = io.inputinteger(f"{{var:promptcolor}}load amount of grain: {{var:inputcolor}}", self.player.grain)
    if amount is None:
        io.echo("aborted.")
        return True
    if amount < 0:
        io.echo("Must specify an amount greater than zero.")
    elif amount > self.player.grain:
        io.echo("You are short by {} of grain.".format(util.pluralize(amount - self.player.grain, "bushel", "bushels", emoji=":crop:")))
    else:
        self.player.grain -= amount
        if "grain" in self.manifest:
            self.manifest["grain"] += amount
        else:
            self.manifest["grain"] = amount
        self.player.adjust()
        self.player.save()
