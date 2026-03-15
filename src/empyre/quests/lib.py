from .. import lib as libempyre

def runmodule(args, modulename, **kwargs):
    return libempyre.runmodule(args, f"quests.{modulename}", **kwargs)
