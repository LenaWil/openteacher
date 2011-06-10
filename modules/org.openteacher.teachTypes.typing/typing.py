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
		self.inputLineEdit = QtGui.QLineEdit()

		self.checkButton = QtGui.QPushButton(u"Check!")
		self.checkButton.setShortcut(QtCore.Qt.Key_Return) #FIXME: translatable?
		self.correctButton = QtGui.QPushButton(u"Correct anyway")

		mainLayout = QtGui.QGridLayout()
		mainLayout.addWidget(self.inputLineEdit, 0, 0)
		mainLayout.addWidget(self.checkButton, 0, 1)
		mainLayout.addWidget(self.correctButton, 1, 1)
		self.setLayout(mainLayout)

	def updateLessonType(self, lessonType):
		self.lessonType = lessonType

		self.lessonType.newItem.handle(self.newItem)

		self.checkButton.clicked.connect(self.checkAnswer)
		self.correctButton.clicked.connect(self.correctLastAnswer)

	def newItem(self, item):
		try:
			self.previousItem = self.item
		except AttributeError:
			pass
		self.item = item
		self.inputLineEdit.clear()
		self.inputLineEdit.setFocus()

	def correctLastAnswer(self):
		result = Result("right")
		result.itemId = self.previousItem.id
		self.lessonType.correctLastAnswer(self, result)

	def checkAnswer(self):
		givenStringAnswer = unicode(self.inputLineEdit.text())

		#FIXME: only one
		for module in self._mm.activeMods.supporting("wordsStringParser"):
			givenAnswer = module.parse(givenStringAnswer)

		right = False
		compulsoryAnswerCount = 0

		if len(givenAnswer) == 1:
			difference = set(givenAnswer[0])
			for compulsoryAnswer in self.item.answers:
				difference -= set(compulsoryAnswer)
			if len(difference) == 0:
				right = True

		elif len(givenAnswer) > 1:
			for compulsoryGivenAnswer in givenAnswer:
				for compulsoryAnswer in self.item.answers:
					difference = set(compulsoryGivenAnswer) - set(compulsoryAnswer)
					if len(difference) == 0:
						compulsoryAnswerCount += 1

			if compulsoryAnswerCount == len(self.item.answers):
				right = True

		if right:
			result = Result("right")
		else:
			result = Result("wrong")

		result.itemId = self.item.id
		result.givenAnswer = givenStringAnswer
		print result
		print ""
		self.lessonType.setResult(result)

class TypingTeachTypeModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TypingTeachTypeModule, self).__init__(*args, **kwargs)
		self.supports = ("teachType",)
		self.requires = (1, 0)
		self._mm = moduleManager

	def enable(self):
		self.type = "words"
		self.name = "Type Answer"
		self.active = True

	def disable(self):
		self.active = False
		del self.type
		del self.name

	def createWidget(self):
		return TypingTeachWidget(self._mm)

def init(moduleManager):
	return TypingTeachTypeModule(moduleManager)
