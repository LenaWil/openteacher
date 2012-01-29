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
		self._activeDialogs = set()

		self._ui = self._mm.import_("ui")

		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		self._api = self._mm.import_("api")
		self._references = set()

		self._wrtsConnection = self._api.WrtsConnection(self._mm)

		event = self._uiModule.addLessonLoadButton("Import from WRTS")#FIXME: (re)translate
		event.handle(self.importFromWrts)
		self._references.add(event)
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

		self.name = _("Wrts API connection")
		for dialog in self._activeDialogs:
			dialog.retranslate()

	@property
	def _uiModule(self):
		return self._modules.default("active", type="ui")

	def disable(self):
		self.active = False

		del self._modules
		del self._activeDialogs
		del self.name
		del self._ui
		del self._api
		del self._references
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
			self._retranslate()

			tab = self._uiModule.addCustomTab(ld.windowTitle(), ld)
			tab.closeRequested.handle(tab.close)
			ld.rejected.connect(tab.close)
			ld.accepted.connect(tab.close)

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
		self._retranslate()

		tab = self._uiModule.addCustomTab(ldc.windowTitle(), ldc)
		tab.closeRequested.handle(tab.close)
		ldc.rejected.connect(tab.close)
		ldc.accepted.connect(tab.close)

		ldc.exec_()
		self._activeDialogs.remove(ldc)
		if not ldc.result():
			return

		listUrl = listsParser.getWordListUrl(ldc.selectedRowIndex)
		list = self._wrtsConnection.importWordList(listUrl)

		self._modules.default(
			"active",
			type="loader"
		).loadFromList("words", list)

def init(moduleManager):
	return WrtsApiModule(moduleManager)
