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
			return self._headers[section]
		else:
			return section + 1

	def retranslate(self):
		self._headers = [
			_("Date"),#FIXME: own translator
			_("Note"),
			_("Completed"),
		]

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
				noteCalculator = self._modules.default("active", type="noteCalculator")
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
		
		self.layout = QtGui.QFormLayout()
		self.layout.addRow("", self.highestLabel)#FIXME: own translator
		self.layout.addRow("", self.averageLabel)
		self.layout.addRow("", self.lowestLabel)
		
		self.setLayout(self.layout)

	def retranslate(self):
		self.layout.itemAt(0, QtGui.QFormLayout.LabelRole).setText(
			_("Highest note:")
		)
		self.layout.itemAt(1, QtGui.QFormLayout.LabelRole).setText(
			_("Average note:")
		)
		self.layout.itemAt(2, QtGui.QFormLayout.LabelRole).setText(
			_("Lowest note:")
		)

	def updateList(self, list):
		noteCalculator = self._modules.default("active", type="noteCalculator")

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
		except ZeroDivisionError:
			average = _("-") #FIXME: description + own translator
		self.averageLabel.setText(unicode(average))

class DetailsWidget(QtGui.QWidget):
	def __init__(self, moduleManager, *args, **kwargs):
		super(DetailsWidget, self).__init__(*args, **kwargs)
		
		self._mm = moduleManager
		self.labels = []
		
		self.layout = QtGui.QFormLayout()
		
		self.setLayout(self.layout)

	def updateList(self, list, dataType):
		for module in self._mm.mods("active", type="testType"):
			if module.dataType == dataType:
				# Only if there are any properties in this module
				try:
					module.properties
				except AttributeError:
					pass
				else:
					# If the labels were not made yet, make them
					if len(self.labels) == 0:
						for property in module.properties:
							label = QtGui.QLabel(property[0])
							self.layout.addRow(property[0], label)
							label.setText(list.get(property[1], _("-")))
							self.labels.append(label)
					# Else, update them
					else:
						i = 0
						for property in module.properties:
							self.labels[i].setText(list.get(property[1], _("-")))
							i += 1
					break
		
class TestsViewerWidget(QtGui.QSplitter):
	testActivated = QtCore.pyqtSignal([object, object, object])

	def __init__(self, moduleManager, *args, **kwargs):
		super(TestsViewerWidget, self).__init__(QtCore.Qt.Vertical, *args, **kwargs)

		self._mm = moduleManager
		self._modules = set(self._mm.mods("active", type="modules")).pop()

		self.testsModel = TestsModel(self._mm)
		testsView = QtGui.QTableView()
		testsView.setModel(self.testsModel)
		testsView.doubleClicked.connect(self.showTest)
		self.notesWidget = NotesWidget(moduleManager)
		self.detailsWidget = DetailsWidget(moduleManager)

		horSplitter = QtGui.QSplitter()
		horSplitter.addWidget(testsView)
		horSplitter.addWidget(self.notesWidget)

		self.addWidget(self.detailsWidget)
		self.addWidget(horSplitter)

	def showTest(self, index):
		list = self.testsModel.list
		dataType = self.testsModel.dataType
		test = self.testsModel.testFor(index)
		
		self.testActivated.emit(list, dataType, test)

	def updateList(self, list, dataType):
		self.testsModel.list = list
		self.testsModel.dataType = dataType
		self.notesWidget.updateList(list)
		self.detailsWidget.updateList(list, dataType)
		try:
			self.percentsNotesViewer.hide()
		except AttributeError:
			pass
		try:
			self.percentsNotesViewer = self._modules.default(
				"active",
				type="percentNotesViewer"
			).createPercentNotesViewer(list["tests"])
		except IndexError:
			pass
		else:
			self.addWidget(self.percentsNotesViewer)

	def retranslate(self):
		self.notesWidget.retranslate()
		self.testsModel.retranslate()

class TestViewerWidget(QtGui.QWidget):
	backActivated = QtCore.pyqtSignal()

	def __init__(self, moduleManager, list, dataType, test, *args, **kwargs):
		super(TestViewerWidget, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		self._modules = set(self._mm.mods("active", type="modules")).pop()

		self.backButton = QtGui.QPushButton("")
		self.backButton.clicked.connect(self.backActivated.emit)

		testViewer = self._modules.default(
			"active",
			type="testViewer"
		).createTestViewer(list, dataType, test)

		layout = QtGui.QVBoxLayout()
		layout.addWidget(testViewer)
		layout.addWidget(self.backButton)
		self.setLayout(layout)

	def retranslate(self):
		self.backButton.setText(_("Back"))

class TestsViewer(QtGui.QStackedWidget):
	def __init__(self, moduleManager,  *args, **kwargs):
		super(TestsViewer, self).__init__(*args, **kwargs)

		self._mm = moduleManager

		self.testsViewerWidget = TestsViewerWidget(self._mm)
		self.testsViewerWidget.testActivated.connect(self.showList)
		self.addWidget(self.testsViewerWidget)

	def showList(self, list, dataType, test):
		testViewer = TestViewerWidget(self._mm, list, dataType, test)
		testViewer.backActivated.connect(self.showTests)
		self.addWidget(testViewer)
		self.setCurrentWidget(testViewer)

	def showTests(self):
		self.setCurrentWidget(self.testsViewerWidget)

	def updateList(self, list, dataType):
		self.testsViewerWidget.updateList(list, dataType)

	def retranslate(self):
		for i in range(self.count()):
			self.widget(i).retranslate()

class TestsViewerModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TestsViewerModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "testsViewer"
		self.requires = (#FIXME: make testViewer & noteCalculator unneeded?
			self._mm.mods(type="noteCalculator"),
			self._mm.mods(type="testViewer"),
		)
		self.uses = (
			self._mm.mods(type="percentNoteViewer"),
			self._mm.mods(type="translator"),
		)

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()

		self._testsViewers = set() #FIXME: Should we remove a testsViewer when it's not used anymore? (memory usage)
		try:
			translator = self._modules.default(type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()
		self.active = True

	def disable(self):
		self.active = False
		
		del self._modules
		del self._testsViewers

	def _retranslate(self):
		global _, ngettext
		try:
			translator = self._modules.default(type="translator")
		except IndexError:
			_, ngettext = unicode, lambda x, y, n: x if n == 1 else y
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)
		for tv in self._testsViewers:
			tv.retranslate()

	def createTestsViewer(self):
		tv = TestsViewer(self._mm)#FIXME: moduleManager or pass what's needed? Also on other places...
		self._testsViewers.add(tv)
		return tv

def init(moduleManager):
	return TestsViewerModule(moduleManager)
