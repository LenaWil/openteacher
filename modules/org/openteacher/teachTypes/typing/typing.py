#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Cas Widdershoven
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

from PyQt4 import QtGui, QtCore

class TypingTeachTypeModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TypingTeachTypeModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager
		self.type = "teachType"

	def enable(self):
		global _
		global ngettext

		translator = set(self._mm.mods("active", type="translator")).pop()
		_, ngettext = translator.gettextFunctions(
			self._mm.resourcePath("translations")
		)

		self.dataType = "words"
		self.name = _("Type Answer")
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self.active = True

	def disable(self):
		self.active = False
		del self.dataType
		del self.name
		del self._modules

	def createWidget(self, tabChanged):
		typingInputs = set(self._mm.mods("active", type="typingInput"))
		try:
			typingInput = self._modules.chooseItem(typingInputs)
		except IndexError, e:
			raise e #FIXME: show a nice error
		else:
			return typingInput.createWidget()

def init(moduleManager):
	return TypingTeachTypeModule(moduleManager)
