#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Cas Widdershoven
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

from PyQt4 import QtGui, QtCore
import random

class ShuffleAnswerTeachWidget(QtGui.QWidget):
	def __init__(self, moduleManager, *args, **kwargs):
		super(ShuffleAnswerTeachWidget, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		
		typingInputs = set(self._mm.mods("active", type="typingInput"))
		try:
			typingInput = self._modules.chooseItem(typingInputs)
		except IndexError, e:
			raise e #FIXME: show a nice error
		else:
			self.inputWidget = typingInput.createWidget()
		
		vbox = QtGui.QVBoxLayout()
		self.hintLabel = QtGui.QLabel()
		vbox.addWidget(self.hintLabel)
		vbox.addWidget(self.inputWidget)
		self.setLayout(vbox)
		
	def setHint(self):
		hint = _("Hint:") + u" "
		answer = self.word["answers"][0][0]#FIXME: use composer
		if len(answer) != 1:
			while True:
				hintList = list(answer)
				random.shuffle(hintList)
				if hintList != list(answer):
					hint += u"".join(hintList)
					break
				else:
					continue
		else:
			hint += u"."
		self.hintLabel.setText(hint)

	def updateLessonType(self, lessonType, *args, **kwargs):
		self.inputWidget.updateLessonType(lessonType, *args, **kwargs)

		lessonType.newItem.handle(self.newWord)

	def newWord(self, word):
		self.word = word
		self.setHint()

class ShuffleAnswerTeachTypeModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(ShuffleAnswerTeachTypeModule, self).__init__(*args, **kwargs)
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
		self.name = _("Shuffle Answer")
		self.active = True

	def disable(self):
		self.active = False
		del self.dataType
		del self.name

	def createWidget(self, tabChanged):
		return ShuffleAnswerTeachWidget(self._mm)

def init(moduleManager):
	return ShuffleAnswerTeachTypeModule(moduleManager)
