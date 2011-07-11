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

from PyQt4 import QtGui, QtCore

class ThinkWidget(QtGui.QWidget):
	def __init__(self, *args, **kwargs):
		super(ThinkWidget, self).__init__(*args, **kwargs)
		
		self.label = QtGui.QLabel(_("Think about the answer, and press the 'View answer' button when you're done."))
		self.label.setWordWrap(True)
		self.button = QtGui.QPushButton("View answer")
		
		mainLayout = QtGui.QVBoxLayout()
		mainLayout.addWidget(self.label)
		mainLayout.addWidget(self.button)
		
		self.setLayout(mainLayout)

class AnswerWidget(QtGui.QWidget):
	def __init__(self, *args, **kwargs):
		super(AnswerWidget, self).__init__(*args, **kwargs)

		self.label = QtGui.QLabel()
		self.rightButton = QtGui.QPushButton(_("I was right"))
		self.wrongButton = QtGui.QPushButton(_("I was wrong"))

		bottomLayout = QtGui.QHBoxLayout()
		bottomLayout.addWidget(self.rightButton)
		bottomLayout.addWidget(self.wrongButton)

		mainLayout = QtGui.QVBoxLayout()
		mainLayout.addWidget(self.label)
		mainLayout.addLayout(bottomLayout)
		
		self.setLayout(mainLayout)

class Result(str):
	pass

class InMindTeachWidget(QtGui.QStackedWidget):
	def __init__(self, moduleManager, *args, **kwargs):
		super(InMindTeachWidget, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		self._modules = set(self._mm.mods("active", type="modules")).pop()

		self.thinkWidget = ThinkWidget()
		self.answerWidget = AnswerWidget()
		
		self.addWidget(self.thinkWidget)
		self.addWidget(self.answerWidget)

	def updateLessonType(self, lessonType):
		self.lessonType = lessonType

		self.lessonType.newItem.handle(self.newItem)
		self.thinkWidget.button.clicked.connect(self.startAnswering)
		self.answerWidget.rightButton.clicked.connect(self.setRight)
		self.answerWidget.wrongButton.clicked.connect(self.setWrong)

	def setRight(self):
		result = Result("right")
		result.wordId = self._currentWord.id
		self.lessonType.setResult(result)

	def setWrong(self):
		result = Result("wrong")
		result.wordId = self._currentWord.id
		self.lessonType.setResult(result)

	def newItem(self, word):
		self._currentWord = word
		composers = set(self._mm.mods("active", type="wordsStringComposer"))
		try:
			compose = self._modules.chooseItem(composers).compose
		except IndexError, e:
			#FIXME: show a nice error message? Make it impossible to use
			#inMind in another way?
			raise e
		self.answerWidget.label.setText(
			_("Translation: ") + compose(word.answers)
		)
		self.setCurrentWidget(self.thinkWidget)

	def startAnswering(self):
		self.setCurrentWidget(self.answerWidget)

class InMindTeachTypeModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(InMindTeachTypeModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "teachType"

	def enable(self):
		self.dataType = "words"
		self.name = "Think answers"
		self.active = True

	def disable(self):
		self.active = False
		del self.dataType
		del self.name

	def createWidget(self, tabChanged):
		return InMindTeachWidget(self._mm)

def init(moduleManager):
	return InMindTeachTypeModule(moduleManager)
