# -*- coding: utf-8 -*-
"""
Created on Sat Aug 22 02:35:48 2015

@author: Tilra
"""

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import kwick
import tilramessenger

packages = [
    'kwick',
    'tilramessenger'
]

entry_points = {
    'gui_scripts': [
        'tilramessenger = tilramessenger.__main__:run_main',
    ]
}

package_data = {
    'tilramessenger': ['glade/*.glade'],
}

requires = [
    'requests'
]

setup(
    name='kwickmapi-python',
    version=kwick.__version__,
    description='A python library for kwick.de based on their mapi and a messenger',
    packages=packages,
    package_data=package_data,
    entry_points=entry_points,
    install_requires=requires,
    author=kwick.__author__,
    author_email='tilra@tastyespresso.de',
    license='GPL 3.0',
)