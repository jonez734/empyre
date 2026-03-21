import time, locale

from bbsengine6 import io, screen

from . import lib as libempyre


def main():
    parser = libempyre.buildargs()
    args = parser.parse_args()

    screen.init()
    libempyre.init(args)

    locale.setlocale(locale.LC_ALL, "")
    time.tzset()

    try:
        if args._subparser is not None:
            subkwargs = {}
            for key in ("roll", "choice"):
                val = getattr(args, key, None)
                if val is not None:
                    subkwargs[key] = val
            libempyre.runmodule(args, args._subparser, **subkwargs)
        else:
            libempyre.runmodule(args, "main")
    except KeyboardInterrupt:
        io.echo("{/all}*INTR*")
    except EOFError:
        io.echo("{/all}*EOF*")
    finally:
        io.echo("{savecursor}{curpos:%d,0}{el}{reset}{decrc}" % (io.terminal.height()))


if __name__ == "__main__":
    main()
