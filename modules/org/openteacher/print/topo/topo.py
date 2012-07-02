#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011-2012, Marten de Vries
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
from PyQt4 import QtGui

class PrintModule(object):
	def __init__(self, moduleManager):
		self._mm = moduleManager

		self.type = "print"
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.filesWithTranslations = ("topo.py",)

	def _retranslate(self):
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
		
	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		self.prints = ["topo"]

		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self.name
		del self.prints
		del self._pyratemp

	def print_(self, type, lesson, printer):
		painter = QtGui.QPainter()
		painter.begin(printer)
		image = QtGui.QImage(lesson.resources["mapScreenshot"])
		painter.drawImage(0, 0, image)
		painter.end()

def init(moduleManager):
	return PrintModule(moduleManager)
