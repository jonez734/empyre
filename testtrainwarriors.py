import ttyio5 as ttyio
import bbsengine5 as bbsengine

eligible = 42 
ttyio.echo("{f6}You have %s requirments to be trained as %s." % (bbsengine.pluralize(eligible, "serf that meets", "serfs that meet"), bbsengine.pluralize(eligible, "a :military-helmet: warrior", ":military-helmet: warriors", quantity=False)), end="")
if eligible > 0:
    ttyio.echo(" Training cost is 1 acre per serf.")
else:
    ttyio.echo()
