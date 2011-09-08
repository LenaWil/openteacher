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

		self.requires = (
			self._mm.mods(type="ui"),
		)
		self.uses = (
			self._mm.mods(type="translator"),
			self._mm.mods(type="authors"),
		)

	def show(self):
		try:
			module = self._modules.default("active", type="authors")
		except IndexError:
			authors = set()
		else:
			authors = module.registeredAuthors
		dialog = self._ui.AboutDialog(authors, self._mm)
		tab = self._modules.default("active", type="ui").addCustomTab(
			dialog.windowTitle(),
			dialog
		)
		tab.closeRequested.handle(tab.close)

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()

		#load translator
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)

		self.name = _("About module")
	
		self._ui = self._mm.import_("ui")
		self._ui._, self._ui._ngettext = _, ngettext
		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self._registry
		del self.name
		del self._ui

def init(moduleManager):
	return AboutModule(moduleManager)
