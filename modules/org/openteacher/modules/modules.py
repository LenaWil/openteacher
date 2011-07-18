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

class ModulesModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(ModulesModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "modules"
		self.requires = (1, 0)

	def registerModule(self, name, module):
		self._modules[name] = module

	@property
	def registeredModules(self):
		return self._modules.copy()

	def activateModules(self):
		#FIXME: leave modules that the user wants to be disabled disabled...
		modules = set(self._mm.mods) - set(self._mm.mods("active"))
		for module in modules:
			#try/except catches too much here
			if hasattr(module, "enable"):
				module.enable()
		self.modulesUpdated.emit()

	def chooseItem(self, items):
		if len(items) == 0:
			raise IndexError("No items to choose from.")
		elif len(items) == 1:
			return items.pop()
		for module in self._mm.mods("active", type="ui"):
			return module.chooseItem(items)

	def enable(self):
		self._modules = {}
		self.modulesUpdated = self._mm.createEvent()
		self.active = True

	def disable(self):
		self.active = False
		del self._modules
		del self.modulesUpdated

def init(moduleManager):
	return ModulesModule(moduleManager)
