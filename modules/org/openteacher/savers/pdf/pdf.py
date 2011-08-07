#! /usr/bin/env python
# -*- coding: utf-8 -*-

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

import tarfile
import os
import tempfile
from PyQt4 import QtGui

class OpenTeachingTopoSaverModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(OpenTeachingTopoSaverModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "save"

	def enable(self):		
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self._modules.registerModule("Open Teaching Media (.otmd) saver", self)
		self.saves = {"words": ["pdf"]}
		
		self.active = True

	def disable(self):
		self.active = False

	def save(self, type, list, path, resources):
		composers = set(self._mm.mods("active", type="wordsStringComposer"))
		compose = self._modules.chooseItem(composers).compose
		
		printer = QtGui.QPrinter()
		printer.setOutputFileName(path)
		printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
		
		painter = QtGui.QPainter()
		painter.begin(printer)
		
		i = 50
		
		if "title" in list:
			painter.drawText(20, i, list["title"])
			i += 15
		if "questionLanguage" in list and "answerLanguage" in list:
			painter.drawText(20, i, list["questionLanguage"] + "\t" + list["answerLanguage"])
			i += 15
				
		i += 20
		
		for item in list["items"]:
			painter.drawText(20, i, compose(item["questions"]) + "\t" + compose(item["answers"]))
			i += 15
		
		painter.end()

def init(moduleManager):
	return OpenTeachingTopoSaverModule(moduleManager)
