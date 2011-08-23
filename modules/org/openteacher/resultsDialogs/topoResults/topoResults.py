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
from PyQt4 import QtCore
import datetime

class TopoResultsWidget(QtGui.QWidget):
	def __init__(self, test, list, *args, **kwargs):
		super(TopoResultsWidget, self).__init__(*args, **kwargs)
		
		self.test = test
		self.list = list
		
		d = datetime.datetime.now()
		
		labelInfo = QtGui.QLabel("<h1>This test:</h1>" + 
								 "<ul>" +
								   "<li>Date: " + d.strftime("%d/%m/%y") + "</li>" +
								 "</ul>" +
								 "<h2>Results:</h2>" + 
								 "<ul>" +
								   "<li>Right: " + str(self.amountRight(self.test)) + "</li>" +
								   "<li>Wrong: " + str(self.amountWrong(self.test)) + "</li>" + 
								   "<li>%: " + str(self.percentage(self.amountRight(self.test), self.amountWrong(self.test))) + "</li>" +
								 "</ul>" + 
								 "Place most done wrong: " + str(self.getItem(self.mostWrong(self.test))["name"]))
		labelInfo.setStyleSheet("""
								font-size: 15px;
								""")
		
		layout = QtGui.QVBoxLayout()
		layout.setAlignment(QtCore.Qt.AlignTop)
		layout.addWidget(labelInfo)
		
		self.setLayout(layout)
	
	def percentage(self, right, wrong):
		total = right + wrong
		return (float(total) - wrong) / float(total) * 100
	
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
	
	def mostWrong(self, test):
		highestId = 0
		highest = 0
		
		for result in test["results"]:
			count = test["results"].count({
				"itemId": result["itemId"],
				"result": "wrong"
			})
			if count > highest:
				highest = count
				highestId = result["itemId"]
		
		return highestId
	
	def getItem(self, id):
		for item in self.list["items"]:
			if item["id"] == id:
				return item

class TopoResultsViewerModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TopoResultsViewerModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "resultsDialog"
		
		self.supports = ["topo"]

	def enable(self):
		self.active = True

	def disable(self):
		self.active = False
	
	def showResults(self, list, test):
		self.resultsWidget = TopoResultsWidget(test, list)
		
		for module in self._mm.mods("active", type="ui"):
			self.tab = module.addCustomTab(
				_("Topo results"),
				self.resultsWidget
			)
			self.tab.closeRequested.handle(self.tab.close)

def init(moduleManager):
	return TopoResultsViewerModule(moduleManager)
