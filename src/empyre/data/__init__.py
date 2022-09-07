import pathlib
import importlib.resources as resources

import ttyio5 as ttyio
import bbsengine5 as bbsengine

# @since 20220810
# @see https://github.com/cirosantilli/python-sample-package-with-data/blob/master/python_sample_package_with_data/__init__.py
# @see https://stackoverflow.com/questions/3596979/manifest-in-ignored-on-python-setup-py-install-no-data-files-installed
# @see https://the-hitchhikers-guide-to-packaging.readthedocs.io/en/latest/quickstart.html
def get(name):
    return resources.open_text("empyre.data", name)
#    ttyio.echo("__name__=%r name=%r" % (__name__, name), level="debug")
#    p = resources.path(__name__, name)
#    ttyio.echo("p=%r (%r)" % (p, type(p)), level="debug")
#    if type(p) == str or type(p) == pathlib.PosixPath:
#        return "/"+bbsengine.buildfilepath(str(p))
#    else:
#        return resources.as_file(resources.files(__name__).joinpath(name))
