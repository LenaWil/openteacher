#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Milan Boers
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

from PyQt4 import QtGui, QtWebKit

class PdfSaverModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(PdfSaverModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "save"
		self.priorities = {
			"student@home": 784,
			"student@school": 784,
			"teacher": 784,
			"wordsonly": 784,
			"selfstudy": 784,
			"testsuite": 784,
			"codedocumentation": 784,
			"all": 784,
		}

		self.requires = (
			self._mm.mods(type="wordsHtmlGenerator"),
		)

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		self.name = "Portable Document Format"
		self.saves = {"words": ["pdf"]}
		
		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self.name
		del self.saves

	def save(self, type, lesson, path):
		self._printer = QtGui.QPrinter()
		self._printer.setOutputFileName(path)
		self._printer.setOutputFormat(QtGui.QPrinter.PdfFormat)

		html = self._modules.default(
			"active",
			type="wordsHtmlGenerator"
		).generate(lesson)

		self._doc = QtWebKit.QWebView()
		self._doc.loadFinished.connect(self._loadFinished)
		self._doc.setHtml(html)

	def _loadFinished(self, ok):
		self._doc.print_(self._printer)

def init(moduleManager):
	return PdfSaverModule(moduleManager)
