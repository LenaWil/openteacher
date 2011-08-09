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
		
	def enable(self):
		global _
		global ngettext
		translator = set(self._mm.mods("active", type="translator")).pop()
		_, ngettext = translator.gettextFunctions(
			self._mm.resourcePath("translations")
		)

		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self._modules.registerModule(_("Printing module"), self)

		self._pyratemp = self._mm.import_("pyratemp")
		self.prints = ["words"]
		self.active = True

	def disable(self):
		self.active = False
		del self._modules
		del self.prints
		del self._pyratemp

	def print_(self, type, list, resources, printer):
		composers = set(self._mm.mods("active", type="wordsStringComposer"))
		composer = self._modules.chooseItem(composers)

		class EvalPseudoSandbox(self._pyratemp.EvalPseudoSandbox):
			def __init__(self2, *args, **kwargs):
				self._pyratemp.EvalPseudoSandbox.__init__(self2, *args, **kwargs)

				self2.register("compose", composer.compose)

		templatePath = self._mm.resourcePath("template.html")
		t = self._pyratemp.Template(
			open(templatePath).read(),
			eval_class=EvalPseudoSandbox
		)
		html = t(**{"list": list})
		
		for module in self._mm.mods("active", "name", type="metadata"):
			printer.setCreator(module.name)
		try:
			printer.setDocName(list["title"])
		except KeyError:
			printer.setDocName(_("Untitled word list"))
		
		doc = QtWebKit.QWebView()
		
		self.printer = printer
		self.doc = doc
		doc.loadFinished.connect(self._loadFinished)
		doc.setHtml(html)
	
	def _loadFinished(self, ok):
		#self.printer.setOutputFormat(QtGui.QPrinter.PdfFormat);
		#self.printer.setOutputFileName("B:\Desktop\hi.pdf");
		self.doc.print_(self.printer)

def init(moduleManager):
	return PrintModule(moduleManager)
