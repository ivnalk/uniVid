#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

from setuptools import setup
from setuptools.extension import Extension

import uniVid

# --------------------------------------------------------------------------- #

setup_requires = ['setuptools']
install_requires = ['typing'] if sys.version_info < (3, 5) else []

# --------------------------------------------------------------------------- #

try:
    # begin setuptools installer
    result = setup(
        name=uniVid.__appname__.lower(),
        version=uniVid.__version__,
        author=uniVid.__author__,
        author_email=uniVid.__email__,
        description='media joiner',
        url=uniVid.__website__,
        license='GPLv3+',
        packages=['uniVid', 'uniVid.libs'],
        setup_requires=setup_requires,
        install_requires=install_requires,
        data_files=SetupHelpers.get_data_files(),
        ext_modules=extensions,
        entry_points={'gui_scripts': ['uniVid = uniVid.__main__:main']},
        keywords='pyqt Qt5 media joiner'
    )
except BaseException:
    if uniVid.__ispypi__:
        SetupHelpers.pip_notes()
    raise
