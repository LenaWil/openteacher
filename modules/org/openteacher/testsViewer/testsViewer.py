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

class TestsModel(QtCore.QAbstractTableModel):
	DATE, NOTE, COMPLETED = xrange(3)

	def __init__(self, moduleManager, *args, **kwargs):
		super(TestsModel, self).__init__(*args, **kwargs)
		self._mm = moduleManager
		self._modules = set(self._mm.mods("active", type="modules")).pop()

		self._list = {
			"tests": [],
			"items": [],
		}

	def headerData(self, section, orientation, role):
		if role != QtCore.Qt.DisplayRole:
			return
		if orientation == QtCore.Qt.Horizontal:
			return [
				_("Date"),#FIXME: own translator
				_("Note"),
				_("Completed"),
			][section]
		else:
			return section + 1

	def data(self, index, role):
		if not index.isValid():
			return
		test = self._list["tests"][index.row()]
		if role == QtCore.Qt.DisplayRole:
			if index.column() == self.DATE:
				try:
					return test["results"][0]["active"]["start"].date().isoformat()
				except (IndexError, KeyError):
					return u""
			elif index.column() == self.NOTE:
				noteCalculator = self._modules.chooseItem(
					set(self._mm.mods("active", type="noteCalculator"))
				)
				return noteCalculator.calculateNote(test)
		elif role == QtCore.Qt.CheckStateRole and index.column() == self.COMPLETED:
			return test["finished"]

	def testFor(self, index):
		if index.isValid():
			return self._list["tests"][index.row()]

	def rowCount(self, parent):
		return len(self._list["tests"])

	def columnCount(self, parent):
		return 3

	def _getList(self):
		return self._list

	def _setList(self, list):
		self.beginResetModel()
		self._list = list
		self.reset()

	list = property(_getList, _setList)

class NotesWidget(QtGui.QWidget):
	def __init__(self, moduleManager, *args, **kwargs):
		super(NotesWidget, self).__init__(*args, **kwargs)
		
		self._mm = moduleManager
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		
		self.highestLabel = QtGui.QLabel()
		self.averageLabel = QtGui.QLabel()
		self.lowestLabel = QtGui.QLabel()
		
		layout = QtGui.QFormLayout()
		layout.addRow(_("Highest note:"), self.highestLabel)#FIXME: own translator
		layout.addRow(_("Average note:"), self.averageLabel)
		layout.addRow(_("Lowest note:"), self.lowestLabel)
		
		self.setLayout(layout)

	def updateList(self, list):
		noteCalculator = self._modules.chooseItem(
			set(self._mm.mods("active", type="noteCalculator"))
		)

		notes = map(noteCalculator.calculateNote, list["tests"])
		try:
			self.highestLabel.setText(unicode(max(notes))) #FIXME: is max and min ok?
		except ValueError:
			self.highestLabel.setText(_("-")) #FIXME: description + own translator
		try:
			self.lowestLabel.setText(unicode(min(notes)))
		except ValueError:
			self.lowestLabel.setText(_("-")) #FIXME: description + own translator
		try:
			average = noteCalculator.calculateAverageNote(list["tests"])
		except TypeError:
			average = _("-") #FIXME: description + own translator
		self.averageLabel.setText(unicode(average))

class DetailsWidget(QtGui.QWidget):
	def __init__(self, *args, **kwargs):
		super(DetailsWidget, self).__init__(*args, **kwargs)
		
		self.titleLabel = QtGui.QLabel()
		self.questionLanguageLabel = QtGui.QLabel()
		self.answerLanguageLabel = QtGui.QLabel()
		
		layout = QtGui.QFormLayout()
		layout.addRow(_("Title:"), self.titleLabel) #FIXME: own translator
		layout.addRow(_("Question language:"), self.questionLanguageLabel) #FIXME: own translator
		layout.addRow(_("Answer language:"), self.answerLanguageLabel) #FIXME: own translator
		self.setLayout(layout)

	def updateList(self, list):
		self.titleLabel.setText(list.get("title", _("-"))) #FIXME: description + own translator
		self.questionLanguageLabel.setText(list.get("questionLanguage", _("-"))) #FIXME: description + own translator
		self.answerLanguageLabel.setText(list.get("answerLanguage", _("-"))) #FIXME: description + own translator

class TestsViewerWidget(QtGui.QSplitter):
	testActivated = QtCore.pyqtSignal([object, object])

	def __init__(self, moduleManager, *args, **kwargs):
		super(TestsViewerWidget, self).__init__(QtCore.Qt.Vertical, *args, **kwargs)

		self.testsModel = TestsModel(moduleManager)
		testsView = QtGui.QTableView()
		testsView.setModel(self.testsModel)
		testsView.doubleClicked.connect(self.showTest)
		self.notesWidget = NotesWidget(moduleManager)
		self.detailsWidget = DetailsWidget()

		horSplitter = QtGui.QSplitter()
		horSplitter.addWidget(testsView)
		horSplitter.addWidget(self.notesWidget)

		self.addWidget(self.detailsWidget)
		self.addWidget(horSplitter)

	def showTest(self, index):
		list = self.testsModel.list
		test = self.testsModel.testFor(index)
		
		self.testActivated.emit(list, test)

	def updateList(self, list):
		self.testsModel.list = list
		self.notesWidget.updateList(list)
		self.detailsWidget.updateList(list)

class TestViewerWidget(QtGui.QWidget):
	backActivated = QtCore.pyqtSignal()

	def __init__(self, moduleManager, list, test, *args, **kwargs):
		super(TestViewerWidget, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		self._modules = set(self._mm.mods("active", type="modules")).pop()

		backButton = QtGui.QPushButton(_("Back")) #FIXME: own translator, nicer button?
		backButton.clicked.connect(self.backActivated.emit)

		testViewer = self._modules.chooseItem(
			set(self._mm.mods("active", type="testViewer"))
		).createTestViewer(list, test)

		layout = QtGui.QVBoxLayout()
		layout.addWidget(backButton)
		layout.addWidget(testViewer)
		self.setLayout(layout)

class TestsViewer(QtGui.QStackedWidget):
	def __init__(self, moduleManager,  *args, **kwargs):
		super(TestsViewer, self).__init__(*args, **kwargs)

		self._mm = moduleManager

		self.testsViewerWidget = TestsViewerWidget(self._mm)
		self.testsViewerWidget.testActivated.connect(self.showList)
		self.addWidget(self.testsViewerWidget)

	def showList(self, list, test):
		testViewer = TestViewerWidget(self._mm, list, test)
		testViewer.backActivated.connect(self.showTests)
		self.addWidget(testViewer)
		self.setCurrentWidget(testViewer)

	def showTests(self):
		self.setCurrentWidget(self.testsViewerWidget)

	def updateList(self, list):
		self.testsViewerWidget.updateList(list)

class TestsViewerModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TestsViewerModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "testsViewer"

	def createTestsViewer(self):
		return TestsViewer(self._mm)#FIXME: moduleManager or pass what's needed? Also on other places...

	def enable(self):
		self.active = True

	def disable(self):
		self.active = False

def init(moduleManager):
	return TestsViewerModule(moduleManager)
