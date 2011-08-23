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

from PyQt4 import QtGui

class ResultsDialogModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(ResultsDialogModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "resultsDialog"

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self.active = True

	def disable(self):
		self.active = False
	
	def showResults(self, list, test):
		self.resultsWidget = self._modules.chooseItem(
			set(self._mm.mods("active", type="testViewer"))
		).createTestViewer(list, test)

		for module in self._mm.mods("active", type="ui"):
			self.tab = module.addCustomTab(
				_("Results"),
				self.resultsWidget
			)
			self.tab.closeRequested.handle(self.tab.close)

def init(moduleManager):
	return ResultsDialogModule(moduleManager)
