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

from PyQt4 import QtGui

class MediaResultsWidget(QtGui.QWidget):
	def __init__(self, test, *args, **kwargs):
		super(MediaResultsWidget, self).__init__(*args, **kwargs)
		
		self.test = test
		
		labelInfo = QtGui.QLabel("Results of this test: \n" + 
								 "Right: " + str(self.amountRight(self.test)) + "\n" +
								 "Wrong: " + str(self.amountWrong(self.test)))
		
		layout = QtGui.QVBoxLayout()
		layout.addWidget(labelInfo)
		
		self.setLayout(layout)
	
	def amountRight(self, test):
		feedback = 0
		for result in test["results"]:
			if result["result"] == "right":
				feedback += 1
		return feedback
	
	def amountWrong(self, test):
		feedback = 0
		for result in test["results"]:
			if result["result"] == "wrong":
				feedback += 1
		return feedback

class MediaResultsViewerModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(MediaResultsViewerModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "resultsDialog"
		
		self.supports = ["media"]

	def enable(self):
		self.active = True

	def disable(self):
		self.active = False
	
	def showResults(self, list, test):
		self.resultsWidget = MediaResultsWidget(test)
		
		for module in self._mm.mods("active", type="ui"):
			self.tab = module.addCustomTab(
				_("Results"),
				self.resultsWidget
			)
			self.tab.closeRequested.handle(self.tab.close)

def init(moduleManager):
	return MediaResultsViewerModule(moduleManager)
