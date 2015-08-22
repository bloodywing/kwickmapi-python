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

packages = [
    'kwick',
]

package_data = {
}

requires = [
    'requests'
]

setup(
    name='kwickmapi-python',
    version=kwick.__version__,
    description='A python library for kwick.de based on their mapi',
    packages=packages,
    package_data=package_data,
    install_requires=requires,
    author=kwick.__author__,
    author_email='tilra@tastyespresso.de',
    license='GPL 3.0',
)