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
import weakref

#FIXME: split into a separate module?
def byKey(key, items):
	items = items[:]#copy, this is going to be destructive :P
	while items:
		try:
			value = items[0][key]
		except IndexError:
			break
		except KeyError:
			value = None
		havingSameValue = []
		for item in items:
			try:
				if item[key] == value:
					havingSameValue.append(item)
					items.remove(item)
			except KeyError:
				if value is None:
					havingSameValue.append(item)
					items.remove(item)
		yield value, havingSameValue

class CategoryTab(QtGui.QWidget):
	def __init__(self, name, inCategory, *args, **kwargs):
		super(CategoryTab, self).__init__(*args, **kwargs)
		
		self.setWindowTitle(name)
		vbox = QtGui.QVBoxLayout()

		for name, inSubcategory in byKey("subcategory", inCategory):#replace
			if name is None:
				name = _("Miscellaneous") #FIXME: translate live

			w = self.createSubcategoryGroupBox(name, inSubcategory)
			vbox.addWidget(w)
		
		self.setLayout(vbox)

	def createSubcategoryGroupBox(self, name, inSubcategory):
		groupBox = QtGui.QGroupBox(name)
		groupBoxLayout = QtGui.QFormLayout()
		for setting in inSubcategory:
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
			w.setText(setting["value"])
			
		elif setting["type"] == "options":
			w = QtGui.QComboBox()
			# Add the options
			for option in setting["options"]:
				w.addItem(option[0], option[1])
			w.currentIndexChanged.connect(self.optionsChanged)
			
			w.setting = setting
			w.setCurrentIndex(w.findData(setting["value"]))
			
		elif setting["type"] == "long_text":
			w = QtGui.QTextEdit()
			w.textChanged.connect(self.longTextChanged)
			
			w.setting = setting
			w.setText(setting["value"])
			
		elif setting["type"] == "number":
			w = QtGui.QSpinBox()
			w.setRange(-32768, 32767) #FIXME: decide when setting is registered?
			w.valueChanged.connect(self.numberChanged)
			
			w.setting = setting
			w.setValue(setting["value"])
			
		elif setting["type"] == "boolean":
			w = QtGui.QCheckBox()
			w.stateChanged.connect(self.booleanChanged)
			
			w.setting = setting
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

class SettingsDialog(QtGui.QTabWidget):#FIXME: make the 'simple' and 'advanced' buttons actually do something
	def __init__(self, settings, *args, **kwargs):
		super(SettingsDialog, self).__init__(*args, **kwargs)

		#Setup widget
		self.setTabPosition(QtGui.QTabWidget.South)
		self.setDocumentMode(True)

		for name, inCategory in byKey("category", settings):
			if name is None:
				name = _("Miscellaneous")#FIXME: translate live
			self.createCategoryTab(name, inCategory)

		self.advancedButton = QtGui.QPushButton()
		self.advancedButton.clicked.connect(self.advanced)

		self.simpleButton = QtGui.QPushButton()
		self.simpleButton.clicked.connect(self.simple)

		self.simple()

	def retranslate(self):
		self.setWindowTitle(_("Settings"))
		self.simpleButton.setText(_("Simple mode"))
		self.advancedButton.setText(_("Advanced mode"))

	def createCategoryTab(self, name, inCategory):
		tab = CategoryTab(name, inCategory)
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

		self._activeDialogs = set()

		#install translator
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		self.active = True

	def _retranslate(self):
		#Translations
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
		for dialog in self._activeDialogs:
			r = dialog()
			if r is not None:
				r.retranslate()

	def disable(self):
		self.active = False

		del self._modules
		del self._uiModule
		del self._activeDialogs

	@property
	def _settings(self):
		return self._modules.default("active", type="settings")

	def show(self):
		dialog = SettingsDialog(self._settings.registeredSettings)
		self._activeDialogs.add(weakref.ref(dialog))
		self._retranslate()
		tab = self._uiModule.addCustomTab(dialog.windowTitle(), dialog)
		tab.closeRequested.handle(tab.close)

def init(moduleManager):
	return SettingsDialogModule(moduleManager)
