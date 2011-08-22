#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2009-2011, Marten de Vries
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
	QUESTION, ANSWER, GIVEN_ANSWER, CORRECT = xrange(4)#FIXME: QUESTION, ANSWER and GIVEN_ANSWER aren't guaranteed to exist?

	def __init__(self, moduleManager, list, test, *args, **kwargs):
		super(TestModel, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		self._modules = set(self._mm.mods("active", type="modules")).pop()

		self._list = list
		self._test = test

	def headerData(self, section, orientation, role):
		if role != QtCore.Qt.DisplayRole:
			return
		if orientation == QtCore.Qt.Horizontal:
			return [
				_("Question"),#FIXME: own translator
				_("Answer"),
				_("Given answer"),
				_("Correct"),
			][section]
		else:
			return section + 1

	def _itemForResult(self, result):
		for item in self._list["items"]:
			if result["itemId"] == item["id"]:
				return item

	def data(self, index, role):
		if not index.isValid():
			return

		try:
			compose = self._modules.chooseItem(
				set(self._mm.mods("active", type="wordsStringComposer"))
			).compose
		except IndexError:
			#FIXME: nice error handling
			pass
		else:
			if compose is None:
				pass
				#FIXME: nice error handling

		result = self._test["results"][index.row()]
		if role == QtCore.Qt.DisplayRole:
			item = self._itemForResult(result)
			if index.column() == self.QUESTION:
				try:
					return compose(item["questions"])
				except KeyError:
					return compose([])
			elif index.column() == self.ANSWER:
				try:
					return compose(item["answers"])
				except KeyError:
					return compose([])
			elif index.column() == self.GIVEN_ANSWER:
				try:
					return result["givenAnswer"]
				except KeyError:
					return _("-")
		elif role == QtCore.Qt.CheckStateRole and index.column() == self.CORRECT:
			return result["result"] == "right"

	def rowCount(self, parent):
		return len(self._test["results"])

	def columnCount(self, parent):
		return 4

class TestViewer(QtGui.QSplitter):
	def __init__(self, moduleManager, list, test, *args, **kwargs):
		super(TestViewer, self).__init__(QtCore.Qt.Vertical, *args, **kwargs)

		self._mm = moduleManager
		self._modules = set(self._mm.mods("active", type="modules")).pop()

		#Vertical splitter
		tableView = QtGui.QTableView()
		testModel = TestModel(self._mm, list, test)
		tableView.setModel(testModel)

		completedText = _("yes") if test["finished"] else _("no") #FIXME: own translator
		completedLabel = QtGui.QLabel(_("Completed: %s") % completedText)
		try:
			#end of last result - start of first result
			totalTime = test["results"][-1]["active"]["end"] - test["results"][0]["active"]["start"]
		except IndexError:
			totalTime = datetime.timedelta()
		seconds = totalTime.total_seconds()
		totalTimeLabel = QtGui.QLabel(_("Total time: %s seconds") % seconds)
		vertSplitter = QtGui.QSplitter(QtCore.Qt.Vertical)
		vertSplitter.addWidget(totalTimeLabel)
		vertSplitter.addWidget(tableView)

		#Horizontal splitter
		calculateNote = self._modules.chooseItem(
			set(self._mm.mods("active", type="noteCalculator"))
		).calculateNote

		noteDrawer = QtGui.QLabel(_("Note: %s") % calculateNote(test)) #FIXME: noteDrawer + vertical align top
		horSplitter = QtGui.QSplitter()
		horSplitter.addWidget(vertSplitter)
		horSplitter.addWidget(noteDrawer)

		#Main splitter
		progressWidget = self._modules.chooseItem(
			set(self._mm.mods("active", type="progressViewer"))
		).createProgressViewer(test)

		self.addWidget(horSplitter)
		self.addWidget(progressWidget)

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
