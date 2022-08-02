import ttyio5 as ttyio
import bbsengine5 as bbsengine

eligible = 42
ttyio.echo("{f6}You have %s requirments to be trained as warriors. Training cost is 1 acre per serf." % (bbsengine.pluralize(eligible, "serf that meets", "serfs that meet")))
