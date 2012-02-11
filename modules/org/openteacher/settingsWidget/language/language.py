#! /usr/bin/env python
# -*- coding: utf-8 -*-

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

from PyQt4 import QtCore, QtGui
import os
import locale

class SettingsWidget(QtGui.QComboBox):
	def __init__(self, languages, setting, *args, **kwargs):
		super(SettingsWidget, self).__init__(*args, **kwargs)

		self._setting = setting

		for code in sorted(languages):
			self.addItem(languages[code], code)
		self.insertItem(0, _("System default"), None)
		self.insertSeparator(1)

		self.highlighted.connect(self._valueChanged)
		self.setCurrentIndex(self.findData(setting["value"]))

	def _valueChanged(self, index):
		item = self.model().item(index)
		self._setting["value"] = unicode(item.data(QtCore.Qt.UserRole).toString())

class SettingsWidgetModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(SettingsWidgetModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "settingsWidget"
		self.requires = (
			self._mm.mods(type="ui"),
			self._mm.mods(type="translator"),
		)

	@property
	def _languages(self):
		translator = self._modules.default("active", type="translator")
		files = os.listdir(self._mm.resourcePath("translations"))
		files = filter(lambda x: x.endswith(".po"), files)
		codes = map(lambda x: x.split(".")[0], files)
		codes += "C" #English
		languages = {}
		for code in codes:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations"),
				code
			)
			#TRANSLATORS: replace 'English' with the native name of the language you're translating to
			languages[code] = _("I speak English")
		return languages

	def createWidget(self, *args, **kwargs):
		return SettingsWidget(self._languages, *args, **kwargs)

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		self.widgetType = "language"

		global _, ngettext
		translator = self._modules.default("active", type="translator")
		_, ngettext = translator.gettextFunctions(
			self._mm.resourcePath("translations")
		)

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self.widgetType

def init(moduleManager):
	return SettingsWidgetModule(moduleManager)
