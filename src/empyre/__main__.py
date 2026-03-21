import time, locale

from bbsengine6 import io, screen

from . import lib as libempyre


def main():
    parser = libempyre.buildargs()
    args = parser.parse_args()

    if args._subparser is not None:
        args.modules = [args._subparser]

    screen.init()
    libempyre.init(args)

    locale.setlocale(locale.LC_ALL, "")
    time.tzset()

    try:
        subkwargs = {}
        if args._subparser is not None:
            for key in ("roll", "choice"):
                val = getattr(args, key, None)
                if val is not None:
                    subkwargs[key] = val
        libempyre.runmodule(args, "main", **subkwargs)
    except KeyboardInterrupt:
        io.echo("{/all}*INTR*")
    except EOFError:
        io.echo("{/all}*EOF*")
    finally:
        io.echo("{savecursor}{curpos:%d,0}{el}{reset}{decrc}" % (io.terminal.height()))


if __name__ == "__main__":
    main()
