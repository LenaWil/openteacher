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

class InMindTeachWidget(QtGui.QStackedWidget):
	def __init__(self, *args, **kwargs):
		super(InMindTeachWidget, self).__init__(*args, **kwargs)

		self.thinkWidget = ThinkWidget()
		self.answerWidget = AnswerWidget()
		
		self.addWidget(self.thinkWidget)
		self.addWidget(self.answerWidget)

	def updateLessonType(self, lessonType):
		self.lessonType = lessonType

		self.lessonType.newItem.handle(self.newItem)
		self.thinkWidget.button.clicked.connect(self.startAnswering)
		self.answerWidget.rightButton.clicked.connect(
			lambda: self.lessonType.setResult("right")
		)
		self.answerWidget.wrongButton.clicked.connect(
			lambda: self.lessonType.setResult("wrong")
		)

	def newItem(self, item):
		answers = u", ".join(item.answers)
		self.answerWidget.label.setText(
			_("Translation: ") + answers
		)
		self.setCurrentWidget(self.thinkWidget)

	def startAnswering(self):
		self.setCurrentWidget(self.answerWidget)

class InMindTeachTypeModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(InMindTeachTypeModule, self).__init__(*args, **kwargs)
		self.supports = ("teachType",)
		self.requires = (1, 0)
		self._mm = moduleManager

	def enable(self):
		self.type = "words"
		self.name = "Think answers"
		self.active = True

	def disable(self):
		self.active = False
		del self.type
		del self.name

	def createWidget(self):
		return InMindTeachWidget()

def init(moduleManager):
	return InMindTeachTypeModule(moduleManager)
