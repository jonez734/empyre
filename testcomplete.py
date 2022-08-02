import ttyio4 as ttyio

import argparse
import random

class completeAttributeName(object):
    def __init__(self, args, attrs):
        ttyio.echo("completeAttributeName.100: called")
        self.attrs = attrs

    def completer(self:object, text:str, state:int):
      vocab = []
      for c in self.attrs:
        vocab.append(c["name"])
      results = [x for x in vocab if x.startswith(text)] + [None]
      return results[state]

def inputattributename(args:object, prompt:str="attribute name: ", oldvalue:str="", multiple:bool=False, verify=None, **kw):
  attrs = kw["attrs"] if "attrs" in kw else None
  completer = completeAttributeName(args, attrs)
  return ttyio.inputstring(prompt, oldvalue, opts=args, verify=verify, multiple=multiple, completer=foo, returnseq=False, **kw)

attrs = (
        {"name": "taxrate",   "default":15}, # tr
        {"name": "soldiers",  "default":20, "price": 20},
        {"name": "nobles",    "default":2, "price":25000, "singular":"noble", "plural":"nobles"},
        {"name": "palaces",   "default":1, "price":20}, # f%(1)
        {"name": "markets",   "default":1, "price":1000}, # f%(2) x(7)
        {"name": "mills",     "default":1, "price":2000}, # f%(3) x(8)
        {"name": "foundries", "default":0, "price":7000}, # f%(4) x(9)
        {"name": "shipyards", "default":0, "price":8000, "singular":"shipyard", "plural":"shipyards"}, # yc or f%(5)? x(10)
        {"name": "diplomats", "default":0, "price":50000}, # f%(6) 0
        {"name": "ships", "default":0, "price":5000} # 5000 each, yc?
)
print("attrs=%s" % (repr(attrs)))

parser = argparse.ArgumentParser("testcomplete")
parser.add_argument("--verbose", action="store_true", dest="verbose")
parser.add_argument("--debug", action="store_true", dest="debug")

args = parser.parse_args()
buf = inputattributename(args, attrs=attrs)
print(buf)
