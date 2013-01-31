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

class TestMenuModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TestMenuModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "testMenu"
		x = 728
		self.priorities = {
			"all": x,
			"student@school": x,
			"teacher": x,
			"code-documentation": x,
			"default": -1,
		}

		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.requires = (
			self._mm.mods(type="ui"),
		)
		self.filesWithTranslations = ("menu.py",)

	def enable(self):
		global QtGui
		try:
			from PyQt4 import QtGui
		except ImportError:
			return
		self._modules = set(self._mm.mods(type="modules")).pop()

		ui = self._modules.default("active", type="ui")
		self.menu = ui.fileMenu.addMenu(self.priorities["all"])

		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		self.active = True

	def _retranslate(self):
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)

		self.menu.text = _("Test mode")

	def disable(self):
		self.active = False

		self.menu.remove()

		del self._modules
		del self.menu

def init(moduleManager):
	return TestMenuModule(moduleManager)
