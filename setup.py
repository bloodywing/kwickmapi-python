# -*- coding: utf-8 -*-
"""
Created on Sat Aug 22 02:35:48 2015

@author: bloodywing
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

requires = [
    'requests'
]

setup(
    name='kwickmapi-python',
    version=kwick.__version__,
    description='A python library for kwick.de based on their mapi',
    packages=packages,
    install_requires=requires,
    test_suite = 'nose.collector',
    author=kwick.__author__,
    author_email='bloodywing@tastyespresso.de',
    license='GPL 3.0',
)
