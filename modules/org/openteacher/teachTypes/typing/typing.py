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

class TypingTeachWidget(QtGui.QWidget):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TypingTeachWidget, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		
		typingInputs = set(self._mm.mods("active", type="typingInput"))
		try:
			typingInput = self._modules.chooseItem(typingInputs)
		except IndexError:
			print "IndexError" #FIXME: show a nice error
		else:
			self.inputWidget = typingInput.createWidget()
		
		hbox = QtGui.QHBoxLayout()
		hbox.addWidget(self.inputWidget)
		self.setLayout(hbox)
		
		self.inputWidget.checkAnswer.handle(self.checkAnswer)

	def updateLessonType(self, lessonType):
		self.lessonType = lessonType

		self.lessonType.newItem.handle(self.newWord)

		self.inputWidget.checkButton.clicked.connect(self.checkAnswer)
		self.inputWidget.correctButton.clicked.connect(self.correctLastAnswer)

	def newWord(self, word):
		try:
			self.previousWord = self.word
		except AttributeError:
			pass
		self.word = word
		self.inputWidget.inputLineEdit.clear()
		self.inputWidget.inputLineEdit.setFocus()

	def correctLastAnswer(self):
		result = Result("right")
		result.wordId = self.previousWord.id
		result.givenAnswer = _(u"Correct anyway") #FIXME: own translation
		self.lessonType.correctLastAnswer(result)
		
	def checkAnswer(self):
		givenStringAnswer = unicode(self.inputWidget.inputLineEdit.text())

		checkers = set(self._mm.mods("active", type="wordsStringChecker"))
		try:
			check = self._modules.chooseItem(checkers).check
		except IndexError, e:
			#FIXME: show nice error? Make typing unusable?
			raise e
		result = check(givenStringAnswer, self.word)

		self.lessonType.setResult(result)

class TypingTeachTypeModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TypingTeachTypeModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "teachType"

	def enable(self):
		self.dataType = "words"
		self.name = "Type Answer"
		self.active = True

	def disable(self):
		self.active = False
		del self.dataType
		del self.name

	def createWidget(self):
		return TypingTeachWidget(self._mm)

def init(moduleManager):
	return TypingTeachTypeModule(moduleManager)
