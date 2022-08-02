import ttyio4 as ttyio

class completeAttributeName(object):
    def __init__(self, args, attrs):
        self.matches = []
        self.debug = args.debug
        self.attrs = attrs
        ttyio.echo("completeAttributeName.100: called")

    @classmethod
    def completer(self:object, text:str, state:int):
        pas
        ttyio.echo("completeAttributeName.100: text=%r state=%d" % (text, state))
        vocab = []
        for a in self.attrs:
            vocab.append(a["name"])
            ttyio.echo("a=%r" % (a), level="debug")
        ttyio.echo("completeAttributeName.120: vocab=%r" % (vocab))
        results = [x for x in vocab if x.startswith(text)] + [None]
        return results[state]

def inputattributename(args:object, prompt:str="attribute name: ", oldvalue:str="", multiple:bool=False, verify=None, **kw):
    attrs = kw["attrs"] if "attrs" in kw else None
    print("inputattributename.100: attrs="+str(attrs))
    return ttyio.inputstring(prompt, oldvalue, opts=args, verify=verify, multiple=multiple, completer=completeAttributeName(args, attrs), returnseq=False, **kw)

def main():
    # parser = OptionParser(usage="usage: %prog [options] projectid")
    parser = argparse.ArgumentParser("empyre")
    
    # parser.add_option("--verbose", default=True, action="store_true", help="run %prog in verbose mode")
    parser.add_argument("--verbose", action="store_true", dest="verbose")
    
    # parser.add_option("--debug", default=False, action="store_true", help="run %prog in debug mode")
    parser.add_argument("--debug", action="store_true", dest="debug")

    defaults = {"databasename": "zoidweb4", "databasehost":"localhost", "databaseuser": None, "databaseport":5432, "databasepassword":None}
    bbsengine.buildargdatabasegroup(parser, defaults)

    # databaseargs = parser.add_argument_group("database options")
    # databaseargs.add_argument("--databasename", action="store", dest="databasename", default="zoidweb4", help="specify database name")
    # databaseargs.add_argument("--databasehost", action="store", dest="databasehost", default="localhost", help="specify database host")
    # databaseargs.add_argument("--databaseuser", action="store", dest="databaseuser", help="specify database user")
    # databaseargs.add_argument("--databasepassword", action="store", dest="databasepassword", default=None, help="specify database password")
    # databaseargs.add_argument("--databaseport", action="store", dest="databaseport", default=5432, type=int, help="specify database port")

    args = parser.parse_args()
    # ttyio.echo("args=%r" % (args), level="debug")

    locale.setlocale(locale.LC_ALL, "")

    buf = inputattributename(args, "prompt: ")
#    currentplayer = startup(args)
#    mainmenu(args, currentplayer)
    return    

if __name__ == "__main__":
    main()
