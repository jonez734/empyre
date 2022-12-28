import time
import locale

import ttyio5 as ttyio
import bbsengine5 as bbsengine

from .boot import *

if __name__ == "__main__":
    parser = buildargs()
    args = parser.parse_args()

    bbsengine.initscreen()

    locale.setlocale(locale.LC_ALL, "")
    time.tzset()

    init(args)

    try:
        main(args)
    except KeyboardInterrupt:
        ttyio.echo("{/all}{bold}INTR{bold}")
    except EOFError:
        ttyio.echo("{/all}{bold}EOF{/bold}")
    finally:
        ttyio.echo("{decsc}{curpos:%d,0}{el}{decrc}{reset}{/all}" % (ttyio.getterminalheight()))
