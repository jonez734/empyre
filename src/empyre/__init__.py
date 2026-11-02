import argparse

from . import lib

MODULE_NAME = "empyre"
MODULE_PATH = "empyre"


def init(args: argparse.Namespace, **kwargs: dict) -> bool | None:
    """Register empyre with bbsengine6 so the module registry reports it."""
    from bbsengine6 import register_module

    from ._version import __version__

    register_module(name=MODULE_NAME, module_path=MODULE_PATH, version=__version__, apis={})
    return True


def access(args, op, **kwargs):
    return True


def buildargs(args: argparse.Namespace, **kwargs: dict) -> argparse.ArgumentParser | None:
    return None


def main(args, **kwargs):
    lib.runmodule(args, "main")
