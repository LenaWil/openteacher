#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Marten de Vries
#	Copyright 2011, Cas Widdershoven
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
import copy

class TeachSettingsWidget(QtGui.QWidget):
	def __init__(self, *args, **kwargs):
		super(TeachSettingsWidget, self).__init__(*args, **kwargs)

		self.lessonTypeComboBox = QtGui.QComboBox()

		#Word modifiers
		self.modifyWordListView = QtGui.QListView()
		self.modifyWordUpButton = QtGui.QPushButton(_("Up"))
		self.modifyWordDownButton = QtGui.QPushButton(_("Down"))

		modifyWordButtonsLayout = QtGui.QVBoxLayout()
		modifyWordButtonsLayout.addStretch()
		modifyWordButtonsLayout.addWidget(self.modifyWordUpButton)
		modifyWordButtonsLayout.addWidget(self.modifyWordDownButton)
		modifyWordButtonsLayout.addStretch()
		modifyWordLayout = QtGui.QHBoxLayout()
		modifyWordLayout.addWidget(self.modifyWordListView)
		modifyWordLayout.addLayout(modifyWordButtonsLayout)

		#Word list modifiers
		self.modifyWordListListView = QtGui.QListView()
		self.modifyWordListUpButton = QtGui.QPushButton(_("Up"))
		self.modifyWordListDownButton = QtGui.QPushButton(_("Down"))

		modifyWordListButtonsLayout = QtGui.QVBoxLayout()
		modifyWordListButtonsLayout.addStretch()
		modifyWordListButtonsLayout.addWidget(self.modifyWordListUpButton)
		modifyWordListButtonsLayout.addWidget(self.modifyWordListDownButton)
		modifyWordListButtonsLayout.addStretch()
		modifyWordListLayout = QtGui.QHBoxLayout()
		modifyWordListLayout.addWidget(self.modifyWordListListView)
		modifyWordListLayout.addLayout(modifyWordListButtonsLayout)
		
		self.dontShowAgainCheckBox = QtGui.QCheckBox(
			_("Don't show this screen again when I start a lesson.")
		)
		self.startLessonButton = QtGui.QPushButton(
			_("I'm ready, start the lesson!")
		)

		gb = QtGui.QGroupBox()
		gb.setTitle(_("Lesson settings"))
		formLayout = QtGui.QFormLayout()
		formLayout.addRow(_("Lesson type"), self.lessonTypeComboBox)
		formLayout.addRow(_("Modify word"), modifyWordLayout)
		formLayout.addRow(_("Modify word list"), modifyWordListLayout)
		formLayout.addRow("", self.dontShowAgainCheckBox)
		formLayout.addRow("", self.startLessonButton)

		gb.setLayout(formLayout)

		mainLayout = QtGui.QVBoxLayout()
		mainLayout.addWidget(gb)
		self.setLayout(mainLayout)

class TeachLessonWidget(QtGui.QSplitter):
	def __init__(self, keyboardWidget, *args, **kwargs):
		super(TeachLessonWidget, self).__init__(*args, **kwargs)

		self.changeSettingsButton = QtGui.QPushButton(
			_("Change lesson settings")
		)
		wordLabel = QtGui.QLabel(_("Word:"))
		self.questionLabel = QtGui.QLabel()
		self.questionLabel.setWordWrap(True)
		if keyboardWidget is not None:
			self.keyboardWidget = keyboardWidget
		self.teachTabWidget = QtGui.QTabWidget()
		self.progressBar = QtGui.QProgressBar()

		leftLayout = QtGui.QVBoxLayout()
		leftLayout.addWidget(wordLabel)
		leftLayout.addWidget(self.questionLabel)
		leftLayout.addStretch()
		leftLayout.addWidget(self.teachTabWidget)
		leftLayout.addWidget(self.progressBar)

		leftWidget = QtGui.QWidget()
		leftWidget.setLayout(leftLayout)
		
		rightLayout = QtGui.QVBoxLayout()
		try:
			rightLayout.addWidget(self.keyboardWidget)
		except AttributeError:
			pass
		rightLayout.addWidget(self.changeSettingsButton)
		
		rightWidget = QtGui.QWidget()
		rightWidget.setLayout(rightLayout)

		self.addWidget(leftWidget)
		self.addWidget(rightWidget)

		self.setStretchFactor(0, 255)
		self.setStretchFactor(1, 1)

class ModifiersListModel(QtCore.QAbstractListModel):
	def __init__(self, modifiers, *args, **kwargs):
		super(ModifiersListModel, self).__init__(*args, **kwargs)
		
		self.modifiers = modifiers

	def rowCount(self, parent=None):
		return len(self.modifiers)

	def data(self, index, role):
		if not index.isValid():
			return
		if role == QtCore.Qt.DisplayRole:
			return self.modifiers[index.row()]["name"]
		elif role == QtCore.Qt.CheckStateRole:
			if self.modifiers[index.row()]["active"]:
				return QtCore.Qt.Checked
			else:
				return QtCore.Qt.Unchecked

	def setData(self, index, value, role):
		if not index.isValid():
			return False
		if role == QtCore.Qt.CheckStateRole:
			if value == QtCore.Qt.Checked:
				self.modifiers[index.row()]["active"] = True
			else:
				self.modifiers[index.row()]["active"] = False
		return False

	def flags(self, index):
		return (
			QtCore.Qt.ItemIsEnabled |
			QtCore.Qt.ItemIsSelectable |
			QtCore.Qt.ItemIsUserCheckable
		)

class TeachWidget(QtGui.QStackedWidget):
	tabChanged = QtCore.pyqtSignal()
	lessonDone = QtCore.pyqtSignal()

	def __init__(self, moduleManager, keyboardWidget, applicationActivityChanged, *args, **kwargs):
		super(TeachWidget, self).__init__(*args, **kwargs)

		self._mm = moduleManager #FIXME: get rid of the moduleManager in this widget! And in all widgets, if possible...
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self._applicationActivityChanged = applicationActivityChanged

		self._buildUi(keyboardWidget)
		self._connectSignals()
		self._createModels()

	def updateList(self, list):
		self.list = list

	def _showSettings(self):
		self.setCurrentWidget(self._settingsWidget)

	def _startLesson(self):
		self.setCurrentWidget(self._lessonWidget)
		self._applicationActivityChanged.handle(self._activityChanged)

		i = self._settingsWidget.lessonTypeComboBox.currentIndex()
		try:
			lessonTypeModule = self._lessonTypeModules[i]
		except IndexError, e:
			#Show nicer error
			raise e

		indexes = range(len(self.list["items"]))

		for listModifier in self._listModifiersModel.modifiers:
			if listModifier["active"]:
				indexes = listModifier["module"].modifyList(
					indexes,
					self.list
				)
		self._lessonType = lessonTypeModule.createLessonType(self.list, indexes)

		self._lessonType.newItem.handle(self._newItem)
		self._lessonType.lessonDone.handle(self._lessonDone)

		for widget in self._teachTypeWidgets:
			widget.updateLessonType(self._lessonType)

		self._lessonType.start()

	def _activityChanged(self, activity):
		if activity == "inactive":
			self._pauseStart = datetime.datetime.now()
		elif activity == "active":
			self._lessonType.addPause({
				"start": self._pauseStart,
				"end": datetime.datetime.now()
			})

	def _newItem(self, item):
		#FIXME!!!: item modifiers should be applied wider, not only for
		#the question label, but also for the answers at least.
		item = copy.copy(item)
		for itemModifier in self._itemModifiersModel.modifiers:
			if itemModifier["active"]:
				item = itemModifier["module"].modifyItem(item)

		composers = set(self._mm.mods("active", type="wordsStringComposer"))
		compose = self._modules.chooseItem(composers).compose
		self._lessonWidget.questionLabel.setText(compose(item["questions"]))
		self._updateProgress()

	def _updateProgress(self):
		self._lessonWidget.progressBar.setMaximum(self._lessonType.totalItems)
		self._lessonWidget.progressBar.setValue(self._lessonType.askedItems)

	def _lessonDone(self):
		self._applicationActivityChanged.unhandle(self._activityChanged)
		self._updateProgress()

		for module in self._mm.mods("active", type="resultsDialog"): #FIXME: only one should remain
			if "words" in module.supports:
				module.showResults(self.list, self.list["tests"][-1])
		self.lessonDone.emit()

	def _buildUi(self, keyboardWidget):
		self._settingsWidget = TeachSettingsWidget()
		self._lessonWidget = TeachLessonWidget(keyboardWidget)

		self.addWidget(self._settingsWidget)
		self.addWidget(self._lessonWidget)

	def _connectSignals(self):
		#tab changed
		self._lessonWidget.teachTabWidget.currentChanged.connect(self.tabChanged.emit)

		#start lesson button
		self._settingsWidget.startLessonButton.clicked.connect(self._startLesson)

		#change lesson settings button
		self._lessonWidget.changeSettingsButton.clicked.connect(self._showSettings)

	def _createModels(self):
		#lessonType
		self._lessonTypeModules = list(self._mm.mods("active", type="lessonType"))

		for module in self._lessonTypeModules:
			self._settingsWidget.lessonTypeComboBox.addItem(module.name)

		#item modifiers
		itemModifiers = []
		for module in self._mm.mods("active", type="itemModifier"):
			module.enable()
			itemModifiers.append({
				"name": module.name,
				"active": False,
				"module": module
			})
		self._itemModifiersModel = ModifiersListModel(itemModifiers)
		self._settingsWidget.modifyWordListView.setModel(self._itemModifiersModel)

		#list modifiers
		listModifiers = []
		for module in self._mm.mods("active", type="listModifier"):
			if not module.dataType in ("all", "words"):
				continue
			listModifiers.append({
				"name": module.name,
				"active": False,
				"module": module
			})
		self._listModifiersModel = ModifiersListModel(listModifiers)
		self._settingsWidget.modifyWordListListView.setModel(self._listModifiersModel)

		#teachType
		self._teachTypeWidgets = []
		for module in self._mm.mods("active", type="teachType"): 
			if module.dataType in ("all", "words"):
				widget = module.createWidget(self.tabChanged)
				self._teachTypeWidgets.append(widget)
				self._lessonWidget.teachTabWidget.addTab(widget, module.name)

class WordsTeacherModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(WordsTeacherModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "wordsTeacher"

	def createWordsTeacher(self):
		return TeachWidget(self._mm, self._onscreenKeyboard, self._applicationActivityChanged)

	@property
	def _onscreenKeyboard(self):
		keyboards = set(self._mm.mods("active", type="onscreenKeyboard"))
		try:
			keyboard = self._modules.chooseItem(keyboards)
		except IndexError:
			return
		return keyboard.createWidget()

	@property
	def _applicationActivityChanged(self):
		uiModule = set(self._mm.mods("active", type="ui")).pop()
		return uiModule.applicationActivityChanged

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()

		#Translations
		translator = set(self._mm.mods("active", type="translator")).pop()
		global _
		global ngettext

		_, ngettext = translator.gettextFunctions(
			self._mm.resourcePath("translations")
		)

		self.active = True

	def disable(self):
		self.active = False
		del self._modules

def init(moduleManager):
	return WordsTeacherModule(moduleManager)
