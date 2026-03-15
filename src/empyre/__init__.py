from . import lib

def init(args, **kwargs):
    return True

def access(args, op, **kwargs):
    return True

def buildargs(args=None, **kwargs):
    return None

def main(args, **kwargs):
    lib.runmodule(args, "main")
