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

class LanguageChooser(QtGui.QComboBox):
	languageChanged = QtCore.pyqtSignal([object])

	def __init__(self, languages, i, *args, **kwargs):
		super(LanguageChooser, self).__init__(*args, **kwargs)

		try:
			for code in sorted(languages):
				self.addItem(languages[code], code)
		except TypeError:
			self.setModel(languages)
		else:
			self.insertItem(0, _("System default"), None)
			self.insertSeparator(1)
		self.setCurrentIndex(i)

		self.highlighted.connect(self._indexChanged)

	def _indexChanged(self, index):
		self.languageChanged.emit(index)

class LanguageChooserModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(LanguageChooserModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "languageChooser"
		self.requires = (
			self._mm.mods(type="translator"),
		)

	@property
	def language(self):
		variant = self._model.item(self._index).data(QtCore.Qt.UserRole)
		if variant.isNull():
			return
		else:
			return str(variant.toString())

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

	def _languageChanged(self, index):
		self._index = index
		self._modules.default(type="translator").languageChanged.send()

	def createLanguageChooser(self, *args, **kwargs):
		if self._model:
			lc = LanguageChooser(self._model, self._index, *args, **kwargs)
		else:
			lc = LanguageChooser(self._languages, self._index, *args, **kwargs)
			self._model = lc.model()

		lc.languageChanged.connect(self._languageChanged)
		return lc

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		global _, ngettext
		translator = self._modules.default("active", type="translator")
		_, ngettext = translator.gettextFunctions(
			self._mm.resourcePath("translations")
		)
		
		self._model = None
		self._index = 0

		self.lc = self.createLanguageChooser()
		self.lc.show()

		self.lc2 = self.createLanguageChooser()
		self.lc2.show()

		self.active = True

	def disable(self):
		self.active = False
		
		del self._modules
		del self._model
		del self._index

def init(moduleManager):
	return LanguageChooserModule(moduleManager)
