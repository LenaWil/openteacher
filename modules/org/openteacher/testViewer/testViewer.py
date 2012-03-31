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
import weakref

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
		self._modules = set(self._mm.mods(type="modules")).pop()

		#Vertical splitter
		tableView = QtGui.QTableView()
		testModel = TestModel(self._mm, list, dataType, test)
		tableView.setModel(testModel)

		self.totalThinkingTimeLabel = QtGui.QLabel()
		vertSplitter = QtGui.QSplitter(QtCore.Qt.Vertical)
		vertSplitter.addWidget(self.totalThinkingTimeLabel)
		vertSplitter.addWidget(tableView)

		#Horizontal splitter
		calculateNote = self._modules.default(
			"active",
			type="noteCalculator"
		).calculateNote

		factsLayout = QtGui.QVBoxLayout()
		self.completedLabel = QtGui.QLabel()
		noteDrawer = QtGui.QLabel(_("Note:") + "<br /><span style=\"font-size: 40px\">%s</span>" % calculateNote(test)) #FIXME: noteDrawer + vertical align top#FIXME:retranslate
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
		factsLayout.addWidget(self.completedLabel)
		factsLayout.addStretch()
		
		factsWidget = QtGui.QWidget()
		factsWidget.setLayout(factsLayout)
		
		horSplitter = QtGui.QSplitter()
		horSplitter.addWidget(vertSplitter)
		horSplitter.addWidget(factsWidget)

		#Main splitter
		try:
			progressWidget = self._modules.default(
				"active",
				type="progressViewer"
			).createProgressViewer(test)
		except IndexError:
			pass

		self.addWidget(horSplitter)
		try:
			self.addWidget(progressWidget)
		except NameError:
			pass

	def retranslate(self):
		self.setWindowTitle(_("Results"))
		try:
			completedText = _("yes") if self.test["finished"] else _("no")
		except KeyError:
			completedText = _("no")
		self.completedLabel.setText(_("Completed: %s") % completedText)

		seconds = int(round(self._totalThinkingTime))
		self.totalThinkingTimeLabel.setText(ngettext(
			"Total thinking time: %s second",
			"Total thinking time: %s seconds",
			seconds
		) % seconds)

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
		self.requires = ( #FIXME: check if all really required, and if so make sure some things aren't.
			self._mm.mods(type="ui"),
			self._mm.mods(type="noteCalculator"),
			self._mm.mods(type="testType"),
			self._mm.mods(type="progressViewer"),
		)
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.filesWithTranslations = ("testViewer.py",)

	def createTestViewer(self, *args, **kwargs):
		tv = TestViewer(self._mm, *args, **kwargs)
		self._testViewers.add(weakref.ref(tv))
		self._retranslate()

		return tv

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()

		self._testViewers = set()
		try:
			translator = self._modules.default(type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()
		self.active = True

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
		for tv in self._testViewers:
			r = tv()
			if r is not None:
				r.retranslate()

	def disable(self):
		self.active = False

def init(moduleManager):
	return TestViewerModule(moduleManager)
