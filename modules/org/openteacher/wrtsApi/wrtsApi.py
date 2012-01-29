#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2012, Marten de Vries
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

#FIXME: replace the missing errors.* module that this module has because
#of 2.x.

class WrtsApiModule(object):
	def __init__(self, moduleManager):
		super(WrtsApiModule, self).__init__()
		self._mm = moduleManager

		self.type = "wrtsApi"
		self.uses = (
			self._mm.mods(type="translator"),
			self._mm.mods(type="dataStore"),
		)
		self.requires = (
			self._mm.mods(type="ui"),
			self._mm.mods(type="loader"),
		)

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self._uiModule = self._modules.default("active", type="ui")
		self._activeDialogs = set()

		self._ui = self._mm.import_("ui")
		self._api = self._mm.import_("api")

		self._button = self._uiModule.addLessonLoadButton()
		self._button.clicked.handle(self.importFromWrts)

		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		self._wrtsConnection = self._api.WrtsConnection(self._mm)

		self.active = True

	def _retranslate(self):
		#Translations
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)
		self._ui._, self._ui.ngettext = _, ngettext

		self._button.text = "Import from WRTS"

		for dialog in self._activeDialogs:
			dialog.retranslate()
			dialog.tab.title = dialog.windowTitle()

	def disable(self):
		self.active = False

		self._button.remove()

		del self._modules
		del self._uiModule
		del self._activeDialogs
		del self._ui
		del self._api
		del self._button
		del self._wrtsConnection

	def importFromWrts(self):
		try:
			dataStore = self._modules.default("active", type="dataStore").store
		except IndexError:
			dataStore = None
		try:
			if dataStore:
				email = dataStore["org.openteacher.wrtsApi.email"]
				password = dataStore["org.openteacher.wrtsApi.password"]
		except KeyError:
			ld = self._ui.LoginDialog(bool(dataStore), self._uiModule.qtParent)
			self._activeDialogs.add(ld)

			tab = self._uiModule.addCustomTab(ld)
			tab.closeRequested.handle(tab.close)
			ld.tab = tab
			ld.rejected.connect(tab.close)
			ld.accepted.connect(tab.close)

			self._retranslate()

			ld.exec_()
			self._activeDialogs.remove(ld)
			if not ld.result():
				return
			
			if ld.saveCheck and dataStore:	
				dataStore["org.openteacher.wrtsApi.email"] = ld.email
				dataStore["org.openteacher.wrtsApi.password"] = ld.password

			email = ld.email
			password = ld.password

		self._wrtsConnection.logIn(email, password)

		listsParser = self._wrtsConnection.listsParser

		ldc = self._ui.ListChoiceDialog(listsParser.lists, self._uiModule.qtParent)
		self._activeDialogs.add(ldc)

		tab = self._uiModule.addCustomTab(ldc)
		tab.closeRequested.handle(tab.close)
		ldc.rejected.connect(tab.close)
		ldc.tab = tab
		ldc.accepted.connect(tab.close)

		self._retranslate()

		ldc.exec_()
		self._activeDialogs.remove(ldc)
		if not ldc.result():
			return

		try:
			listUrl = listsParser.getWordListUrl(ldc.selectedRowIndex)
		except IndexError:
			#FIXME: show error instead: none selected
			return
		list = self._wrtsConnection.importWordList(listUrl)

		self._modules.default(
			"active",
			type="loader"
		).loadFromLesson("words", {
			"list": list,
			"resources": {},
		})

def init(moduleManager):
	return WrtsApiModule(moduleManager)
