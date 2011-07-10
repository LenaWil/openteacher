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

from PyQt4 import QtWebKit

class PrintModule(object):
	def __init__(self, moduleManager):
		self._mm = moduleManager

		self.type = "print"
		
	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self._modules.registerModule("Printing module", self)

		self._pyratemp = self._mm.import_("pyratemp")
		self.prints = ["words"]
		self.active = True

	def disable(self):
		self.active = False
		del self._modules
		del self.prints
		del self._pyratemp

	def print_(self, type, list, printer):
		composers = set(self._mm.mods("active", type="wordsStringComposer"))
		composer = self._modules.chooseItem(composers)

		class EvalPseudoSandbox(self._pyratemp.EvalPseudoSandbox):
			def __init__(self2, *args, **kwargs):
				self._pyratemp.EvalPseudoSandbox.__init__(self2, *args, **kwargs)

				self2.register("compose", composer.compose)
				self2.register("hasattr", hasattr)

		templatePath = self._mm.resourcePath("template.html")
		t = self._pyratemp.Template(
			open(templatePath).read(),
			eval_class=EvalPseudoSandbox
		)
		html = t(**{"list": list})

		doc = QtWebKit.QWebView()
		doc.setHtml(html)

		for module in self._mm.mods("active", "name", type="metadata"):
			printer.setCreator(module.name)
		try:
			printer.setDocName(list.title)
		except AttributeError:
			printer.setDocName(_("Untitled word list")) #FIXME: own translator
		doc.print_(printer)

def init(moduleManager):
	return PrintModule(moduleManager)
