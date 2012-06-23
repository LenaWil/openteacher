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

from PyQt4 import QtGui
import os

class FileDialogsModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(FileDialogsModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "fileDialogs"
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.requires = (
			self._mm.mods(type="ui"),
		)

	def getSavePath(self, startdir, exts, default):
		stringExts = []

		filters = []
		for ext, name in exts:
			filters.append(name + " (*." + ext + ")")

		fileDialog = QtGui.QFileDialog()
		fileDialog.setAcceptMode(QtGui.QFileDialog.AcceptSave)
		fileDialog.setWindowTitle(_("Choose file to save"))
		fileDialog.setNameFilters(filters)
		fileDialog.selectNameFilter(default[1] + " (*." + default[0] + ")")
		fileDialog.setDirectory(startdir)

		tab = self._ui.addCustomTab(fileDialog, previousTabOnClose=True)
		tab.title = fileDialog.windowTitle()
		tab.closeRequested.handle(tab.close)
		fileDialog.rejected.connect(tab.close)
		fileDialog.accepted.connect(tab.close)
		result = fileDialog.exec_()

		if result:
			ext = fileDialog.selectedNameFilter().split("(*")[1].split(")")[0]
			filename = unicode(fileDialog.selectedFiles()[0])
			extensions = ["." + e[0] for e in exts]
 			if os.path.splitext(filename)[1] not in extensions:
				filename += ext
			return unicode(filename)
		else:
			return

	def getLoadPath(self, startdir, exts):
		stringExts = set()
		for ext, name in exts:
			stringExts.add("*." + ext)
		filter = u"Lessons (%s)" % u" ".join(stringExts)

		fileDialog = QtGui.QFileDialog()
		fileDialog.setFileMode(QtGui.QFileDialog.ExistingFile)
		fileDialog.setWindowTitle(_("Choose file to open"))
		fileDialog.setFilter(filter)
		fileDialog.setDirectory(startdir)

		tab = self._ui.addCustomTab(fileDialog)
		tab.title = fileDialog.windowTitle()
		tab.closeRequested.handle(tab.close)
		fileDialog.rejected.connect(tab.close)
		fileDialog.accepted.connect(tab.close)
		if fileDialog.exec_():
			return unicode(fileDialog.selectedFiles()[0])
		else:
			return

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		self._ui = self._modules.default("active", type="ui")

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

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self._ui

def init(moduleManager):
	return FileDialogsModule(moduleManager)
