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

from PyQt4 import QtGui

class Printer(object):
	def __init__(self, manager):
		self.manager = manager
		self._pyratemp = self.manager.import_(__file__, "pyratemp")
		self.prints = ["words"]

	def __call__(self, type, list, printer):
		templatePath = self.manager.resourcePath(__file__, "template.txt")
		t = self._pyratemp.Template(open(templatePath).read())
		html = t(**{"list": list})

		doc = QtGui.QTextDocument()
		doc.setHtml(html)
		doc.print_(printer)

class PrintModule(object):
	def __init__(self, manager):
		self.manager = manager
		self.supports = ("print", "state")

	def enable(self):
		self.printer = Printer(self.manager)
	
	def disable(self):
		del self.printer
	
def init(manager):
	return PrintModule(manager)
