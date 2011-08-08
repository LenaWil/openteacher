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

class MediaResultsWidget(QtGui.QWidget):
	def __init__(self, results, *args, **kwargs):
		super(MediaResultsWidget, self).__init__(*args, **kwargs)
		
		self.results = results
		
		labelInfo = QtGui.QLabel("Results of this test: \n" + 
								 "Right: " + str(self.amountRight(self.results[0])) + "\n" +
								 "Wrong: " + str(self.amountWrong(self.results[0])))
		
		layout = QtGui.QVBoxLayout()
		layout.addWidget(labelInfo)
		
		self.setLayout(layout)
	
	def amountRight(self, test):
		feedback = 0
		for result in test:
			if result["result"] == "right":
				feedback += 1
		return feedback
	
	def amountWrong(self, test):
		feedback = 0
		for result in test:
			if result["result"] == "wrong":
				feedback += 1
		return feedback

class MediaResultsViewerModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(MediaResultsViewerModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "resultsviewer"

	def enable(self):
		self.active = True

	def disable(self):
		self.active = False
	
	def showResults(self, results, list):
		self.resultsWidget = MediaResultsWidget(results)
		
		for module in self._mm.mods("active", type="ui"):
			self.tab = module.addCustomTab(
				_("Results"),
				self.resultsWidget
			)
			self.tab.closeRequested.handle(self.tab.close)
	
	def supports(self, items):
		for item in items:
			if not (item.has_key("id") and item.has_key("x") and item.has_key("y") and item.has_key("name")):
				return False
		return True

def init(moduleManager):
	return MediaResultsViewerModule(moduleManager)