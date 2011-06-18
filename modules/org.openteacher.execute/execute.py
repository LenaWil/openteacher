#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Marten de Vries
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

class ExecuteModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(ExecuteModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.supports = ("execute",)
		self.requires = (1, 0)
		self.active = False

	def execute(self, ui, path=None):
		#FIXME: one
		for module in self._mm.mods.supporting("uiController"):
			module.enable()
			module.initialize(ui)

		#FIXME: one
		for module in self._mm.mods.supporting("modules"):
			module.enable()
			module.activateModules()

		#FIXME: (the) one
		for module in self._mm.activeMods.supporting("uiController"):
			module.run(path)

	def enable(self):
		self.active = True

	def disable(self):
		self.active = False

def init(moduleManager):
	return ExecuteModule(moduleManager)
