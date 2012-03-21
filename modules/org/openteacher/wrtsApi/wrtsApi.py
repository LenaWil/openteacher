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
		)
		self.requires = (
			self._mm.mods(type="ui"),
			self._mm.mods(type="loader"),
			self._mm.mods(type="lessonTracker"),
			self._mm.mods(type="wordsStringComposer"),
		)
		self.filesWithTranslations = ["wrtsApi.py", "ui.py"]

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		self._uiModule = self._modules.default("active", type="ui")
		self._lessonTracker = self._modules.default("active", type="lessonTracker")
		self._activeDialogs = set()

		self._ui = self._mm.import_("ui")
		self._api = self._mm.import_("api")

		self._button = self._uiModule.addLessonLoadButton()
		self._button.clicked.handle(self.importFromWrts)

		self._action = QtGui.QAction(self._uiModule.qtParent)
		self._action.triggered.connect(self.exportToWrts)
		self._uiModule.fileMenu.addAction(self._action)

		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		try:
			self._settings = self._modules.default(type="settings")
		except IndexError:
			self._emailSetting = None
			self._passwordSetting = None
		else:
			self._emailSetting = self._settings.registerSetting(
				internal_name="org.openteacher.wrtsApi.email",
				name=_("Email"),
				type="short_text",
				defaultValue=u"",
				category=_("WRTS"),
				subcategory=_("Login credentials"),
			)
			self._passwordSetting = self._settings.registerSetting(
				internal_name="org.openteacher.wrtsApi.password",
				name=_("Password"),
				type="password",
				defaultValue=u"",
				category=_("WRTS"),
				subcategory=_("Login credentials"),
			)

		self._wrtsConnection = self._api.WrtsConnection(self._mm)

		self.active = True

	def disable(self):
		self.active = False

		self._button.remove()
		self._uiModule.fileMenu.removeAction(self._action)

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

	def _retranslate(self):
		global _, ngettext

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

		self._button.text = _("Import from WRTS")
		self._action.setText(_("Export to WRTS"))

		for dialog in self._activeDialogs:
			dialog.retranslate()
			dialog.tab.title = dialog.windowTitle()

	def _invalidLogin(self):
		QtGui.QMessageBox.warning(
			self._uiModule.qtParent,
			_("Invalid login credentials"),
			_("WRTS didn't accept the login credentials. Are you sure you entered your e-mail and password correctly?")
		)

	def _noConnection(self):
		QtGui.QMessageBox.warning(
			self._uiModule.qtParent,
			_("No WRTS connection"),
			_("WRTS didn't accept the connection. Are you sure that your internet connection works and WRTS is online?")
		)

	def _loginToWrts(self, forceLogin=False):
		if self._emailSetting and self._passwordSetting:
			#settings are enabled
			email = self._emailSetting["value"]
			password = self._passwordSetting["value"]

			valid = email and password #not blank
			settingsEnabled = True
		else:
			valid = False
			settingsEnabled = False

		if forceLogin or not valid:
			ld = self._ui.LoginDialog(settingsEnabled, self._uiModule.qtParent)
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

			if ld.saveCheck and settingsEnabled:
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
				self._loginToWrts(forceLogin=True)
			return
		except self._api.ConnectionError:
			self._noConnection()
			return

	def exportToWrts(self):
		lesson = self._lessonTracker.currentLesson
		if not (lesson and lesson.module.dataType == "words"):
			return #FIXME: menu item should be disabled in this situation
		self._loginToWrts()

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
		#FIXME: inform the user

	def importFromWrts(self):
		self._loginToWrts()

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
		#FIXME: inform the user?

def init(moduleManager):
	return WrtsApiModule(moduleManager)
