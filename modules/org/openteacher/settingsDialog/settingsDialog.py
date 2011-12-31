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
	catItems = dict()
	for item in items:
		if not key in item:
			if "Miscellaneous" not in catItems:
				catItems["Miscellaneous"] = []
			catItems["Miscellaneous"].append(item)
		else:
			if item[key] not in catItems:
				catItems[item[key]] = []
			catItems[item[key]].append(item)
	return catItems
	
class CategoryTab(QtGui.QWidget):
	def __init__(self, widgets, name, inCategory, *args, **kwargs):
		super(CategoryTab, self).__init__(*args, **kwargs)

		self._widgets = widgets

		self.setWindowTitle(name)
		vbox = QtGui.QVBoxLayout()
		
		
		categories = byKey("subcategory", inCategory)
		for name in categories.keys():			
			w = self.createSubcategoryGroupBox(name, categories[name])
			vbox.addWidget(w)
		
		self.setLayout(vbox)

	def createSubcategoryGroupBox(self, name, inSubcategory):
		groupBox = QtGui.QGroupBox(name)
		groupBoxLayout = QtGui.QFormLayout()
		for setting in inSubcategory:
			try:
				createWidget = self._widgets[setting["type"]]
			except KeyError:
				continue #FIXME
			groupBoxLayout.addRow(
				setting["name"],
				createWidget(setting)
			)
		groupBox.setLayout(groupBoxLayout)
		return groupBox

class SettingsDialog(QtGui.QTabWidget):#FIXME: make the 'simple' and 'advanced' buttons actually do something
	def __init__(self, settings, widgets, *args, **kwargs):
		super(SettingsDialog, self).__init__(*args, **kwargs)

		#Setup widget
		self.setTabPosition(QtGui.QTabWidget.South)
		self.setDocumentMode(True)
		
		
		categories = byKey("category", settings)
		for name in categories.keys():
			self.createCategoryTab(widgets, name, categories[name])
		
		self.advancedButton = QtGui.QPushButton()
		self.advancedButton.clicked.connect(self.advanced)

		self.simpleButton = QtGui.QPushButton()
		self.simpleButton.clicked.connect(self.simple)

		self.simple()

	def retranslate(self):
		self.setWindowTitle(_("Settings"))
		self.simpleButton.setText(_("Simple mode"))
		self.advancedButton.setText(_("Advanced mode"))

	def createCategoryTab(self, *args, **kwargs):
		tab = CategoryTab(*args, **kwargs)
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
			self._mm.mods(type="settingsWidgets"),
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

	@property
	def _settingsWidgets(self):
		return self._modules.default("active", type="settingsWidgets")

	def show(self):
		dialog = SettingsDialog(self._settings.registeredSettings, self._settingsWidgets.widgets)
		self._activeDialogs.add(weakref.ref(dialog))
		self._retranslate()
		tab = self._uiModule.addCustomTab(dialog.windowTitle(), dialog)
		tab.closeRequested.handle(tab.close)

def init(moduleManager):
	return SettingsDialogModule(moduleManager)
