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

from PyQt4 import QtGui

class WrtsApiModule(object):
	def __init__(self, moduleManager):
		super(WrtsApiModule, self).__init__()
		self._mm = moduleManager

		self.type = "wrtsApi"
		self.uses = (
			self._mm.mods(type="translator"),
			self._mm.mods(type="settings"),
			self._mm.mods(type="lesson"),
		)
		self.requires = (
			self._mm.mods(type="ui"),
			self._mm.mods(type="buttonRegister"),
			self._mm.mods(type="loader"),
			self._mm.mods(type="lessonTracker"),
			self._mm.mods(type="wordsStringComposer"),
			self._mm.mods(type="wordsStringParser"),
		)
		self.filesWithTranslations = ("wrtsApi.py", "ui.py")

	def _updateMenuItemsWrapper(self, *args, **kwargs):
		self._updateMenuItems()

	def _updateMenuItems(self):
		lesson = self._lessonTracker.currentLesson
		canExport = bool(lesson) and lesson.module.dataType == "words"
		self._action.enabled = canExport

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		self._uiModule = self._modules.default("active", type="ui")
		self._lessonTracker = self._modules.default("active", type="lessonTracker")
		self._activeDialogs = set()

		self._ui = self._mm.import_("ui")
		self._api = self._mm.import_("api")

		self._button = self._modules.default("active", type="buttonRegister").registerButton("load")
		self._button.clicked.handle(self.importFromWrts)

		self._action = self._uiModule.fileMenu.addAction()
		self._action.triggered.handle(self.exportToWrts)

		self._uiModule.tabChanged.handle(self._updateMenuItems)
		self._updateMenuItems()

		for module in self._mm.mods("active", type="lesson"):
			module.lessonCreationFinished.handle(self._updateMenuItemsWrapper)

		try:
			self._settings = self._modules.default(type="settings")
		except IndexError:
			self._emailSetting = {
				"value": u"",
			}
			self._passwordSetting = {
				"value": u"",
			}
			self._storeEnabled = False
		else:
			self._emailSetting = self._settings.registerSetting(**{
				"internal_name": "org.openteacher.wrtsApi.email",
				"type": "short_text",
				"defaultValue": u"",
			})
			self._passwordSetting = self._settings.registerSetting(**{
				"internal_name": "org.openteacher.wrtsApi.password",
				"type": "password",
				"defaultValue": u"",
			})
			self._storeEnabled = True

		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		parse = self._modules.default(
			"active",
			type="wordsStringParser"
		).parse
		self._wrtsConnection = self._api.WrtsConnection(parse)

		self.active = True

	def disable(self):
		self.active = False

		self._action.remove()

		self._uiModule.tabChanged.unhandle(self._updateMenuItems)

		for module in self._mm.mods("active", type="lesson"):
			module.lessonCreationFinished.unhandle(self._updateMenuItemsWrapper)

		del self._modules
		del self._uiModule
		del self._lessonTracker
		del self._activeDialogs
		del self._ui
		del self._api
		del self._button
		del self._settings
		del self._emailSetting
		del self._passwordSetting
		del self._wrtsConnection
		del self._storeEnabled

	def _retranslate(self):
		global _
		global ngettext

		#Install translator
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)
		self._ui._, self._ui.ngettext = _, ngettext

		#Translate button + menu action
		self._button.changeText.send(_("Import from WRDS"))
		self._action.text = _("Export to WRDS")

		#Translate settings
		self._emailSetting.update({
			"name": _("Email"),
			"category": _("WRDS"),
			"subcategory": _("Login credentials"),
		})

		self._passwordSetting.update({
			"name": _("Password"),
			"category": _("WRDS"),
			"subcategory": _("Login credentials"),
		})

		#Translate all active dialogs
		for dialog in self._activeDialogs:
			dialog.retranslate()
			dialog.tab.title = dialog.windowTitle()

	def _invalidLogin(self):
		QtGui.QMessageBox.warning(
			self._uiModule.qtParent,
			_("Invalid login credentials"),
			_("WRDS didn't accept the login credentials. Are you sure you entered your e-mail and password correctly?")
		)

	def _noConnection(self):
		QtGui.QMessageBox.warning(
			self._uiModule.qtParent,
			_("No WRDS connection"),
			_("WRDS didn't accept the connection. Are you sure that your internet connection works and WRDS is online?")
		)

	def _loginToWrts(self, forceLogin=False):
		"""Returns True if login succeeded, and False if it didn't."""
		email = self._emailSetting["value"]
		password = self._passwordSetting["value"]

		valid = email and password #not blank

		if forceLogin or not valid:
			ld = self._ui.LoginDialog(self._storeEnabled, self._uiModule.qtParent)
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

			if ld.saveCheck:
				self._emailSetting["value"] = ld.email
				self._passwordSetting["value"] = ld.password

			email, password = ld.email, ld.password

		try:
			self._wrtsConnection.logIn(email, password)
		except self._api.LoginError:
			if forceLogin or not valid:
				#if tried
				self._invalidLogin()
			else:
				#just the setting, let the user try
				return self._loginToWrts(forceLogin=True)
			return False
		except self._api.ConnectionError:
			self._noConnection()
			return False
		else:
			return True

	def exportToWrts(self):
		lesson = self._lessonTracker.currentLesson

		if not self._loginToWrts():
			return

		try:
			self._wrtsConnection.exportWordList(
				lesson.list,
				self._modules.default("active", type="wordsStringComposer").compose
			)
		except self._api.NotEnoughMetadataError:
			QtGui.QMessageBox.warning(
				self._uiModule.qtParent,
				_("No word list metadata given."),
				_("Please fill in the wordlist title, question language and answer language first. Then try again.")
			)
		except self._api.LoginError:
			self._invalidLogin()
			return
		except self._api.ConnectionError:
			self._noConnection()
			return

		self._uiModule.statusViewer.show(_("Word list succesfully exported to WRDS."))

	def importFromWrts(self):
		if not self._loginToWrts():
			return

		ldc = self._ui.ListChoiceDialog(
			self._wrtsConnection.listsParser.lists,
			self._uiModule.qtParent
		)
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
			listUrl = self._wrtsConnection.listsParser.getWordListUrl(ldc.selectedRowIndex)
		except IndexError:
			#No list selected, report.
			QtGui.QMessageBox.warning(
				self._uiModule.qtParent,
				_("No list selected"),
				_("No list was selected. Please try again.")
			)
			return
		try:
			list = self._wrtsConnection.importWordList(listUrl)
		except self._api.LoginError:
			self._invalidLogin()
			return
		except self._api.ConnectionError:
			self._noConnection()
			return

		self._modules.default(
			"active",
			type="loader"
		).loadFromLesson("words", {
			"list": list,
			"resources": {},
		})
		self._uiModule.statusViewer.show(_("The word list was imported from WRDS successfully."))

def init(moduleManager):
	return WrtsApiModule(moduleManager)
