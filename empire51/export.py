from optparse import OptionParser
from os.path import basename

import ttyio3 as ttyio
import bbsengine4 as bbsengine

import pexpect

def processdisk(opts, d):
    if opts.debug is True:
        ttyio.echo("d=%s" % (d), level="debug")
    base = basename(d)
    os.mkdir(base)
    if opts.debug is True:
        ttyio.echo("base=%s" % (base), level="debug")
    return

def main():
    # 'attach' a d64 file
    # mkdir -p basename() of arg
    # save each prg/etc in d64 file to that dir
    # as a bonus, make a way to do it the other way (import.py)
    parser = OptionParser(usage="usage: %prog [options] projectid")
    parser.add_option("--verbose", default=True, action="store_true", help="run %prog in verbose mode")
    parser.add_option("--debug", default=True, action="store_true", help="run %prog in debug mode")

    (opts, args) = parser.parse_args()
    for d in args:
        processdisk(opts, d)

if __name__ == "__main__":
    main()
