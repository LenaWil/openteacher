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
import datetime

class InputTyping(QtGui.QWidget):
	def __init__(self, check, *args, **kwargs):
		super(InputTyping, self).__init__(*args, **kwargs)

		self._check = check

		self.inputLineEdit = QtGui.QLineEdit()
		self.inputLineEdit.textEdited.connect(self._textEdited)

		self.checkButton = QtGui.QPushButton(_(u"Check!"))
		self.checkButton.setShortcut("Return") #FIXME: translatable?
		self.correctButton = QtGui.QPushButton(_(u"Correct anyway"))

		mainLayout = QtGui.QGridLayout()
		mainLayout.addWidget(self.inputLineEdit, 0, 0)
		mainLayout.addWidget(self.checkButton, 0, 1)
		mainLayout.addWidget(self.correctButton, 1, 1)
		self.setLayout(mainLayout)

	def _textEdited(self, text):
		try:
			self._end
		except AttributeError:
			self._end = datetime.datetime.now()
		else:
			if not unicode(text).strip():
				del self._end

	def updateLessonType(self, lessonType):
		self.lessonType = lessonType

		self.lessonType.newItem.handle(self.newWord)

		self.checkButton.clicked.connect(self.checkAnswer)
		self.correctButton.clicked.connect(self.correctLastAnswer)

	def newWord(self, word):
		self._start = datetime.datetime.now()
		self.word = word
		self.inputLineEdit.clear()

	def correctLastAnswer(self):
		result = self._previousResult.update({
			"result": "right",
			"givenAnswer": _("Correct anyway")
		})
		self.lessonType.correctLastAnswer(result)

	def checkAnswer(self):
		givenStringAnswer = unicode(self.inputLineEdit.text())

		self._previousResult = result = self._check(givenStringAnswer, self.word)
		try:
			self._end
		except AttributeError:
			self._end = datetime.datetime.now()
		result.update({
			"active": {
				"start": self._start,
				"end": self._end,
			},
		})
		del self._end

		self.lessonType.setResult(result)

class InputTypingModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(InputTypingModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "typingInput"
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.requires = (
			self._mm.mods(type="wordsStringChecker"),
		)

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()

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

		self.active = True

	def disable(self):
		self.active = False

		del self._modules

	@property
	def _check(self):
		return self._modules.default(type="wordsStringChecker").check

	def createWidget(self):
		return InputTyping(self._check)

def init(moduleManager):
	return InputTypingModule(moduleManager)
