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

class Result(str):
	pass

class InputTyping(QtGui.QWidget):
	def __init__(self, moduleManager, *args, **kwargs):
		super(InputTyping, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self._mm = moduleManager
		self._modules = set(self._mm.mods("active", type="modules")).pop()

		self.inputLineEdit = QtGui.QLineEdit()

		self.checkButton = QtGui.QPushButton(_(u"Check!"))
		self.checkButton.setShortcut("Return") #FIXME: translatable?
		self.correctButton = QtGui.QPushButton(_(u"Correct anyway"))

		mainLayout = QtGui.QGridLayout()
		mainLayout.addWidget(self.inputLineEdit, 0, 0)
		mainLayout.addWidget(self.checkButton, 0, 1)
		mainLayout.addWidget(self.correctButton, 1, 1)
		self.setLayout(mainLayout)

	def updateLessonType(self, lessonType):
		self.lessonType = lessonType

		self.lessonType.newItem.handle(self.newWord)

		self.checkButton.clicked.connect(self.checkAnswer)
		self.correctButton.clicked.connect(self.correctLastAnswer)

	def newWord(self, word):
		try:
			self.previousWord = self.word
		except AttributeError:
			pass
		self.word = word
		self.inputLineEdit.clear()
		self.inputLineEdit.setFocus()

	def correctLastAnswer(self):
		result = Result("right")
		result.wordId = self.previousWord.id
		result.givenAnswer = _("Correct anyway")
		self.lessonType.correctLastAnswer(result)

	def checkAnswer(self):
		givenStringAnswer = unicode(self.inputLineEdit.text())

		checkers = set(self._mm.mods("active", type="wordsStringChecker"))
		try:
			check = self._modules.chooseItem(checkers).check
		except IndexError, e:
			#FIXME: show nice error? Make typing unusable?
			raise e
		result = check(givenStringAnswer, self.word)

		self.lessonType.setResult(result)

class InputTypingModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(InputTypingModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "typingInput"

	def enable(self):
		self.active = True

		global _
		global ngettext
		#Translations
		translator = set(self._mm.mods("active", type="translator")).pop()
		_, ngettext = translator.gettextFunctions(
			self._mm.resourcePath("translations")
		)

	def disable(self):
		self.active = False

	def createWidget(self):
		return InputTyping(self._mm)

def init(moduleManager):
	return InputTypingModule(moduleManager)
