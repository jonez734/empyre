from . import lib

def init(args, **kw:dict) -> bool:
    return True

def access(args, op:str, **kw:dict) -> bool:
    return True

def buildargs(args, **kw:dict):
    return None

def main(args, **kw):
    return lib.runmodule(args, "main", **kw)
