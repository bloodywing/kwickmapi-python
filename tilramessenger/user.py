# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 00:57:58 2015

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

@author: Tilra
"""

from gi.repository import GObject


class User(GObject.GObject):

    username = GObject.property(type=str, default='Ein Mitglied')
    userid = GObject.property(type=int)
    age = GObject.property(type=int, default=99)
    is_buddy = GObject.property(type=bool, default=False)
    firstname = GObject.property(type=str, default='')
    lastname = GObject.property(type=str, default='')
    message_history = None

    def __eq__(self, other):
        return self.userid == other

    def __repr__(self):
        return str(self.userid)

    def __init__(self):
        super(User, self).__init__()