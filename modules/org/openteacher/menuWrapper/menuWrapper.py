#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2012, Marten de Vries
#
#	This file is part of OpenTeacher.
#
#	OpenTeacher is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	OpenTeacher is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with OpenTeacher.  If not, see <http://www.gnu.org/licenses/>.

#FIXME: make sure it's possible for the module which wraps the menu to
#specify the place to insert new actions/menus

class Menu(object):
	def __init__(self, menu, *args, **kwargs):
		super(Menu, self).__init__(*args, **kwargs)

		self._menu = menu

	def addAction(self, action):
		self._menu.addAction(action)

	def addMenu(self, menu):
		self._menu.addMenu(menu)

	def removeAction(self, action):
		self._menu.removeAction(action)

	def removeMenu(self, menu):
		menu.hide()

class MenuWrapperModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(MenuWrapperModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "menuWrapper"

	def enable(self):
		self.active = True

	def wrapMenu(self, menu):
		return Menu(menu)

	def disable(self):
		self.active = False

def init(moduleManager):
	return MenuWrapperModule(moduleManager)
