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

DOCS_URL = "http://openteacher.org/documentation.html"

class DocumentationModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(DocumentationModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.requires = (1, 0)
		self.supports = ("documentation", "initializing")
		self.active = False

	def initialize(self):
		for module in self._mm.activeMods.supporting("settings"):
			module.registerModule("Documentation module", self)

	def show(self):
		for module in self._mm.activeMods.supporting("ui"):
			dialog = self._ui.DocumentationDialog(DOCS_URL)
			tab = module.addCustomTab(dialog.windowTitle(), dialog)
			tab.closeRequested.handle(tab.close)

	def enable(self):
		self._ui = self._mm.import_("ui")
		self.active = True

	def disable(self):
		self.active = False
		del self._ui

def init(moduleManager):
	return DocumentationModule(moduleManager)
