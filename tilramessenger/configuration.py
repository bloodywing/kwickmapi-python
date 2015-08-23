# -*- coding: utf-8 -*-
"""
Created on Sat Aug 22 22:59:21 2015

Copyright (C) 2015  Tilra

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License

@author: tilra
"""

import configparser
import os
from appdirs import *

sep = os.path.sep

class Configuration(object):

    parser = None
    configname = 'settings.ini'
    file = None

    def __init__(self):
        self.parser = configparser.ConfigParser()
        os.makedirs(user_config_dir('tilra', 'tilra'), exist_ok=True)
        self.file = user_config_dir('tilra', 'tilra') + sep + self.configname
        self.parser.read(self.file)


    def __getitem__(self, attr):
        section, name = attr.split('/')
        return self.parser[section][name]

    def __setitem__(self, attr, value):
        section, name = attr.split('/')
        if not self.parser.has_section(section):
            self.parser.add_section(section)
        self.parser[section][name] = value
        with open(self.file, 'w') as f:
            self.parser.write(f)
