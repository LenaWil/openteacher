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
		self.type = "about"

	def show(self):
		authorModules = set(self._mm.mods("active", type="authors"))
		try:
			authorModule = self._modules.chooseItem(authorModules)
		except IndexError:
			authors = set()
		else:
			authors = authorModule.registeredAuthors
		for module in self._mm.mods("active", type="ui"):
			dialog = self._ui.AboutDialog(authors, self._mm)
			tab = module.addCustomTab(dialog.windowTitle(), dialog)
			tab.closeRequested.handle(tab.close)

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self._modules.registerModule("About module", self)

		self._ui = self._mm.import_("ui")
		self.active = True

	def disable(self):
		self.active = False
		del self._modules
		del self._ui

def init(moduleManager):
	return AboutModule(moduleManager)
