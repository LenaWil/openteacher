#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2009-2011, Marten de Vries
#	Copyright 2008-2011, Milan Boers
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

from PyQt4 import QtCore, QtGui
import datetime

class TestModel(QtCore.QAbstractTableModel):
	def __init__(self, moduleManager, list, dataType, test, *args, **kwargs):
		super(TestModel, self).__init__(*args, **kwargs)

		self._mm = moduleManager

		self._list = list
		self._test = test
		
		for module in self._mm.mods("active", type="testType"):
			if dataType == module.dataType:
				self.testTable = module
				self.testTable.updateList(self._list, self._test)
				break

	def headerData(self, section, orientation, role):
		if role != QtCore.Qt.DisplayRole:
			return
		if orientation == QtCore.Qt.Horizontal:
			return self.testTable.header[section]
		else:
			return section + 1

	def data(self, index, role):
		if not index.isValid():
			return
		
		if type(self.testTable.data(index.row(), index.column())) == type(True):
			# Boolean
			if role == QtCore.Qt.CheckStateRole:
				return self.testTable.data(index.row(), index.column())
		else:
			# Non-Boolean
			if role == QtCore.Qt.DisplayRole:
				return self.testTable.data(index.row(), index.column())

	def rowCount(self, parent):
		return len(self._test["results"])

	def columnCount(self, parent):
		return len(self.testTable.header)

class TestViewer(QtGui.QSplitter):
	def __init__(self, moduleManager, list, dataType, test, *args, **kwargs):
		super(TestViewer, self).__init__(QtCore.Qt.Vertical, *args, **kwargs)
		
		self.test = test

		self._mm = moduleManager
		self._modules = set(self._mm.mods("active", type="modules")).pop()

		#Vertical splitter
		tableView = QtGui.QTableView()
		testModel = TestModel(self._mm, list, dataType, test)
		tableView.setModel(testModel)

		try:
			completedText = _("yes") if test["finished"] else _("no") #FIXME: own translator
		except KeyError:
			completedText = _("no")
		completedLabel = QtGui.QLabel(_("Completed: %s") % completedText)
		
		totalThinkingTimeLabel = QtGui.QLabel(_("Total thinking time: %s seconds") % self._totalThinkingTime)
		vertSplitter = QtGui.QSplitter(QtCore.Qt.Vertical)
		vertSplitter.addWidget(totalThinkingTimeLabel)
		vertSplitter.addWidget(tableView)

		#Horizontal splitter
		calculateNote = self._modules.chooseItem(
			set(self._mm.mods("active", type="noteCalculator"))
		).calculateNote

		factsLayout = QtGui.QVBoxLayout()
		noteDrawer = QtGui.QLabel(_("Note:") + "<br /><span style=\"font-size: 40px\">%s</span>" % calculateNote(test)) #FIXME: noteDrawer + vertical align top
		factsLayout.addWidget(noteDrawer, 0, QtCore.Qt.AlignTop)
		for module in self._mm.mods("active", type="testType"):
			if module.dataType == dataType:
				try:
					module.funFacts
				except AttributeError:
					pass
				else:
					for fact in module.funFacts:
						if fact[1] == None:
							label = QtGui.QLabel("%s<br />-" % fact[0])
						else:
							label = QtGui.QLabel("%s<br /><span style=\"font-size: 14px\">%s</span>" % (fact[0], fact[1]))
						factsLayout.addWidget(label, 0, QtCore.Qt.AlignTop)
				break
		factsLayout.addStretch()
		
		factsWidget = QtGui.QWidget()
		factsWidget.setLayout(factsLayout)
		
		horSplitter = QtGui.QSplitter()
		horSplitter.addWidget(vertSplitter)
		horSplitter.addWidget(factsWidget)

		#Main splitter
		progressWidget = self._modules.chooseItem(
			set(self._mm.mods("active", type="progressViewer"))
		).createProgressViewer(test)

		self.addWidget(horSplitter)
		self.addWidget(progressWidget)
	
	@property
	def _totalThinkingTime(self):
		totalThinkingTime = datetime.timedelta()
		for result in self.test["results"]:
			totalThinkingTime += result["active"]["end"] - result["active"]["start"]
		return totalThinkingTime.total_seconds()

class TestViewerModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TestViewerModule, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		self.type = "testViewer"

	def createTestViewer(self, *args, **kwargs):
		return TestViewer(self._mm, *args, **kwargs)

	def enable(self):
		self.active = True

	def disable(self):
		self.active = False

def init(moduleManager):
	return TestViewerModule(moduleManager)
