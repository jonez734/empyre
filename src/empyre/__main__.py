import time, locale

from bbsengine6 import io, screen, database

from . import lib as libempyre

def main():
    parser = libempyre.buildargs()
    args = parser.parse_args()

#    pool = database.getpool(args)
#    session.start(args, pool=pool)

    screen.init()
    libempyre.init(args)

    locale.setlocale(locale.LC_ALL, "")
    time.tzset()

    try:
        libempyre.runmodule(args, "main") # main(args) # lib.runsubmodule(args, "main") # module.main(args)
    except KeyboardInterrupt:
        io.echo("{/all}*INTR*")
    except EOFError:
        io.echo("{/all}*EOF*")
    finally:
        io.echo("{savecursor}{curpos:%d,0}{el}{reset}{decrc}" % (io.terminal.height()))

if __name__ == "__main__":
    main()
