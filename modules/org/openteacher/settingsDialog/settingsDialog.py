#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Marten de Vries
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

from PyQt4 import QtCore, QtGui
import sys

class LessonTypeTab(QtGui.QWidget):
	def __init__(self, name, lessonType, *args, **kwargs):
		super(LessonTypeTab, self).__init__(*args, **kwargs)
		
		self.setWindowTitle(name)
		vbox = QtGui.QVBoxLayout()

		for name, category in lessonType.iteritems():
			if name is None:
				name = _("Miscellaneous")

			w = self.createCategoryGroupBox(name, category)
			vbox.addWidget(w)
		
		self.setLayout(vbox)

	def createCategoryGroupBox(self, name, category):
		groupBox = QtGui.QGroupBox(name)
		groupBoxLayout = QtGui.QFormLayout()
		for setting in category.values():
			groupBoxLayout.addRow(
				setting["name"],
				self.createSettingWidget(setting)
			)
		groupBox.setLayout(groupBoxLayout)
		return groupBox
	
	def createSettingWidget(self, setting):
		if setting["type"] == "short_text":
			w = QtGui.QLineEdit()
			w.textChanged.connect(self.shortTextChanged)
			
			w.setting = setting
			if setting["value"] != None:
				w.setText(setting["value"])
			
		elif setting["type"] == "options":
			w = QtGui.QComboBox()
			# Add the options
			for option in setting["options"]:
				w.addItem(option[0], option[1])
			w.currentIndexChanged.connect(self.optionsChanged)
			
			w.setting = setting
			if setting["value"] != None:
				w.setCurrentIndex(w.findData(setting["value"]))
			
		elif setting["type"] == "long_text":
			w = QtGui.QTextEdit()
			w.textChanged.connect(self.longTextChanged)
			
			w.setting = setting
			if setting["value"] != None:
				w.setText(setting["value"])
			
		elif setting["type"] == "number":
			w = QtGui.QSpinBox()
			w.setRange(0, sys.maxint)
			w.valueChanged.connect(self.numberChanged)
			
			w.setting = setting
			if setting["value"] != None:
				w.setValue(setting["value"])
			
		elif setting["type"] == "boolean":
			w = QtGui.QCheckBox()
			w.stateChanged.connect(self.booleanChanged)
			
			w.setting = setting
			if setting["value"] != None:
				# *2 because 2 is checked and 0 is unchecked
				w.setCheckState(setting["value"] * 2)
			
		return w

	def shortTextChanged(self):
		w = self.sender()
		w.setting["value"] = unicode(w.text())

	def longTextChanged(self):
		w = self.sender()
		w.setting["value"] = unicode(w.toPlainText())

	def numberChanged(self):
		w = self.sender()
		w.setting["value"] = int(w.value())
	
	def booleanChanged(self, state):
		w = self.sender()
		# /2 because 2 is checked and 0 is unchecked
		w.setting["value"] = state / 2

	def optionsChanged(self):
		w = self.sender()
		w.setting["value"] = w.itemData(w.currentIndex()).toString()

class SettingsDialog(QtGui.QTabWidget):#FIXME: make sure the 'simple' and 'advanced' buttons are more than stubs
	def __init__(self, settings, *args, **kwargs):
		super(SettingsDialog, self).__init__(*args, **kwargs)

		#Setup widget
		self.setTabPosition(QtGui.QTabWidget.South)
		self.setDocumentMode(True)

		for name, lessonType in settings.iteritems():
			if name is None:
				name = _("Miscellaneous")
			self.createLessonTypeTab(name, lessonType)

		self.advancedButton = QtGui.QPushButton(_("Advanced mode"))
		self.advancedButton.clicked.connect(self.advanced)

		self.simpleButton = QtGui.QPushButton(_("Simple mode"))
		self.simpleButton.clicked.connect(self.simple)

		self.setWindowTitle(_("Settings"))

		self.simple()

	def createLessonTypeTab(self, name, lessonType):
		tab = LessonTypeTab(name, lessonType)
		self.addTab(tab, tab.windowTitle())

	def advanced(self):
		self.setCornerWidget(
			self.simpleButton,
			QtCore.Qt.BottomRightCorner
		)
		self.simpleButton.show()

	def simple(self):
		self.setCornerWidget(
			self.advancedButton,
			QtCore.Qt.BottomRightCorner
		)
		self.advancedButton.show()

class SettingsDialogModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(SettingsDialogModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "settingsDialog"
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.requires = (
			self._mm.mods(type="ui"),
			self._mm.mods(type="settings"),
		)

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self._uiModule = self._modules.default("active", type="ui")

		#install translator
		global _
		global ngettext
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self._uiModule
		del self._ui

	@property
	def _settings(self):
		return self._modules.default("active", type="settings")

	def show(self):
		dialog = SettingsDialog(self._settings.registeredSettings())
		tab = self._uiModule.addCustomTab(dialog.windowTitle(), dialog)
		tab.closeRequested.handle(self._modules.modulesUpdated.send) #FIXME: still needed?
		tab.closeRequested.handle(tab.close)

def init(moduleManager):
	return SettingsDialogModule(moduleManager)
