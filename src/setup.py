#!/usr/bin/env python

import os
import time
from setuptools import setup

r = 1
v = time.strftime("%Y%m%d%H%M")

projectname = "empyre"

# os.system("./updateversion.sh") use Makefile!

setup(
  name=projectname,
  version=v,
  url=f"https://repo.zoidtechnologies.com/{projectname}/",
  author="zoidtechnologies.com",
  author_email=f"{projectname}@projects.zoidtechnologies.com",
  requires=["bbsengine6", ],
  scripts=["bin/empyre"],
  license="GPLv2",
  provides=[projectname],
  packages=["empyre", "empyre.ship", "empyre.combat", "empyre.maint", "empyre.island", "empyre.quests", "empyre.data", "empyre.town", "empyre.sql" ],
  long_description = """empyre -- turn-based strategy game based on several versions of empire and built upon bbsengine6""",
  include_package_data = True,
  classifiers=[
    "Programming Language :: Python :: 3.12",
    "Environment :: Console",
    "Development Status :: 3 - Alpha",
    "Intended Audience :: End Users/Desktop",
    "Operating System :: POSIX",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Terminals",
    "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    "Topic :: Communications :: BBS",
  ],
)
