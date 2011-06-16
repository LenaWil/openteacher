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

class AboutModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(AboutModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.requires = (1, 0)
		self.supports = ("about", "initializing")
		self.active = False

	def initialize(self):
		for module in self._mm.activeMods.supporting("modules"):
			module.registerModule("About module", self)

	def show(self):
		for module in self._mm.activeMods.supporting("ui"):
			dialog = self._ui.AboutDialog(self._authors, self._mm)
			tab = module.addCustomTab(dialog.windowTitle(), dialog)
			tab.closeRequested.handle(tab.close)

	def enable(self):
		self._ui = self._mm.import_("ui")
		self._authors = []
		self.active = True

		##########DEMO DATA
		self.registerAuthor("Core developer", "Milan Boers")
		self.registerAuthor("Core developer", "Cas Widdershoven")
		self.registerAuthor("Core developer", "Marten de Vries")
		##########END DEMO DATA

	def disable(self):
		self.active = False
		del self._ui
		del self._authors

	def registerAuthor(self, category, name):
		self._authors.append((category, name))

def init(moduleManager):
	return AboutModule(moduleManager)
