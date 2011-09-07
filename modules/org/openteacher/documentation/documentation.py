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

class DocumentationModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(DocumentationModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "documentation"
		self.requires = (
			(
				("active",),
				{"type": "metadata"},
			),
			(
				("active",),
				{"type": "ui"},
			),
		)

	def show(self):
		metadataMod = self._modules.default("active", type="metadata")
		for module in self._mm.mods("active", type="ui"):#FIXME
			dialog = self._ui.DocumentationDialog(
				metadataMod.documentationUrl,
				metadataMod.userAgent,
				"en" #FIXME: language should be dynamic
			)
			tab = module.addCustomTab(dialog.windowTitle(), dialog)
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

		self._ui = self._mm.import_("ui")
		self._ui._, self._ui.ngettext = _, ngettext

		self.name = _("Documentation module")

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self._registry
		del self._ui
		del self.name

def init(moduleManager):
	return DocumentationModule(moduleManager)
