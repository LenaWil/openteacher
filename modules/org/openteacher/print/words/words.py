#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Marten de Vries
#	Copyright 2011, Milan Boers
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

from PyQt4 import QtWebKit

class PrintModule(object):
	def __init__(self, moduleManager):
		self._mm = moduleManager

		self.type = "print"
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.requires = (
			self._mm.mods(type="wordsStringComposer"),
			self._mm.mods(type="metadata"),
		)
		
	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()

		global _
		global ngettext
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)

		self.name = _("Printing module")

		self._pyratemp = self._mm.import_("pyratemp")
		self.prints = ["words"]

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self.name
		del self.prints
		del self._pyratemp

	@property
	def compose(self):
		return self._modules.default(
			"active",
			type="wordsStringComposer"
		).compose

	def print_(self, type, list, resources, printer):
		class EvalPseudoSandbox(self._pyratemp.EvalPseudoSandbox):
			def __init__(self2, *args, **kwargs):
				self._pyratemp.EvalPseudoSandbox.__init__(self2, *args, **kwargs)

				self2.register("compose", self.compose)

		templatePath = self._mm.resourcePath("template.html")
		t = self._pyratemp.Template(
			open(templatePath).read(),
			eval_class=EvalPseudoSandbox
		)
		html = t(**{"list": list})

		name = self._modules.default("active", type="metadata").name
		printer.setCreator(name)
		try:
			printer.setDocName(list["title"])
		except KeyError:
			printer.setDocName(_("Untitled word list"))

		self._printer = printer
		self._doc = QtWebKit.QWebView()
		self._doc.loadFinished.connect(self._loadFinished)
		self._doc.setHtml(html)
	
	def _loadFinished(self, ok):
		self._doc.print_(self._printer)

def init(moduleManager):
	return PrintModule(moduleManager)
