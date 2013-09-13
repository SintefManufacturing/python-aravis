from setuptools import setup
from distutils.command.install_data import install_data


import glob
import os
import subprocess

import make_deb



setup (name = "aravis", 
        version = make_deb.DEBVERSION,
        description = "pythonic interface to auto-generated aravis python bindings",
        author = "Olivier Roulet-Dubonnet",
        url = 'https://github.com/oroulet/python-aravis',
        py_modules=["aravis"],
        license = "GNU General Public License",
        )


