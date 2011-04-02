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

class WrtsApiModule(object):
	def __init__(self, moduleManager):
		super(self.__class__, self).__init__()

		self._mm = moduleManager
		self.supports = ("initializing")
		self.requires = (1, 0)
		self.active = False

	def initialize(self):
		for module in self._mm.activeMods.supporting("settings"):
			module.registerModule(_("Wrts API connection"), self)

	def enable(self):
		self._ui = self._mm.import_(__file__, "ui")
		self._api = self._mm.import_(__file__, "api")
		self._references = set()

		self.wrtsConnection = self._api.WrtsConnection()
		
		for module in self._mm.activeMods.supporting("ui"):
			event = module.addLessonLoadButton(_("Import from WRTS")) #FIXME: private gettext!
			event.handle(self.importFromWrts)
			self._references.add(event)
		self.active = True

	def disable(self):
		self.active = False
		del self._ui
		del self._api
		del self._references
		del self.wrtsConnection

	def importFromWrts(self):
		for module in self._mm.mods.supporting("ui"):
			ld = self._ui.LoginDialog(module.qtParent)		

			tab = module.addCustomTab(ld.windowTitle(), ld)
			tab.closeRequested.handle(tab.close)
			ld.rejected.connect(tab.close)
			ld.accepted.connect(tab.close)

			ld.exec_()
			if not ld.result():
				return

			self.wrtsConnection.logIn(ld.email, ld.password)

			listsParser = self.wrtsConnection.listsParser

			ldc = self._ui.ListChoiceDialog(listsParser.lists, module.qtParent)

			tab = module.addCustomTab(ldc.windowTitle(), ldc)
			tab.closeRequested.handle(tab.close)
			ldc.rejected.connect(tab.close)
			ldc.accepted.connect(tab.close)

			ldc.exec_()
			if not ldc.result():
				return

			listUrl = listsParser.getWordListUrl(ldc.selectedRowIndex)
			list = self.wrtsConnection.importWordList(listUrl)

			for module in self._mm.activeMods.supporting("openteacher-core"):
				module.loadList("words", list)

def init(moduleManager):
	return WrtsApiModule(moduleManager)
