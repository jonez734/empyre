from bbsengine6 import io

def main(self):
    if "grain" not in self.manifest:
        io.echo("You do not have any grain on board")
        self.manifest["grain"] = 0
        io.echo("aborted.")
        return True

    amount = io.inputinteger(f"{{var:promptcolor}}unload amount of grain: {{var:inputcolor}}", self.player.grain)
    if amount is None:
        io.echo("aborted.")
        return True

    if amount is None or amount == 0:
        io.echo("aborted.")
        return True
        
    if amount < 0:
        io.echo("Must specify an amount greater than zero.")
    elif amount > self.manifest["grain"]:
        io.echo("You only have {} of grain on board.".format(util.pluralize(amount - self.player.grain, "bushel", "bushels", emoji=":crop:")))
    else:
        if self.manifest["grain"] < 0:
            self.manifest["grain"] = 0
        if "grain" in self.manifest:
            self.manifest["grain"] -= amount
        else:
            self.manifest["grain"] = 0

        player.grain += amount

        self.player.adjust()
        self.player.save()
        self.adjust()
        self.update()
