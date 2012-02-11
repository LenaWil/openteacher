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

from PyQt4 import QtGui

#FIXME: translate module
class TestMenuModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TestMenuModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "testMenu"

		self.requires = (
			self._mm.mods(type="ui"),
			self._mm.mods(type="menuWrapper"),
		)

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		self._ui = self._modules.default("active", type="ui")

		self._qtMenu = QtGui.QMenu("Test mode")
		self.menu = self._modules.default("active", type="menuWrapper").wrapMenu(self._qtMenu)
		self._ui.fileMenu.addMenu(self._qtMenu)

		self.active = True

	def disable(self):
		self.active = False

		self._ui.fileMenu.removeMenu(self._qtMenu)

		del self._qtMenu
		del self._modules
		del self._ui
		del self.menu

def init(moduleManager):
	return TestMenuModule(moduleManager)
