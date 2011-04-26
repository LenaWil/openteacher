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

class TypingTeachWidget(QtGui.QWidget):
	def __init__(self, *args, **kwargs):
		super(TypingTeachWidget, self).__init__(*args, **kwargs)

		self.wordsLabel = QtGui.QLabel(u"No words added")
		labelSizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
		self.wordsLabel.setSizePolicy(labelSizePolicy)
		
		self.inputLineEdit = QtGui.QLineEdit()

		self.checkButton = QtGui.QPushButton(u"Check!")
		self.correctButton = QtGui.QPushButton(u"Correct anyway")

		self.progressBar = QtGui.QProgressBar()

		mainLayout = QtGui.QVBoxLayout()
		mainLayout.addWidget(self.wordsLabel)
		mainLayout.addWidget(self.inputLineEdit)
		mainLayout.addWidget(self.checkButton)
		mainLayout.addWidget(self.correctButton)
		mainLayout.addWidget(self.progressBar)
		self.setLayout(mainLayout)

	def start(self, lessonType):
		self.lessonType = lessonType

		self.lessonType.newItem.handle(self.newItem)
		self.lessonType.lessonDone.handle(self.lessonDone)

		self.checkButton.clicked.connect(self.checkAnswer)
		self.correctButton.clicked.connect(self.lessonType.correctLastAnswer)

	def updateProgress(self):
		self.progressBar.setValue(self.lessonType.askedQuestions)
		self.progressBar.setMaximum(self.lessonType.totalQuestions)

	def newItem(self, item):
		self.updateProgress()

		self.item = item
		self.wordsLabel.setText(u", ".join(self.item.questions))
		self.inputLineEdit.clear()
		self.inputLineEdit.setFocus()

	def lessonDone(self):
		self.updateProgress()
		print "Done!" #FIXME: QMessageBox?

	def checkAnswer(self):
		if self.inputLineEdit.text() in self.item.answers:
			self.lessonType.setResult("right")
		else:
			self.lessonType.setResult("wrong")

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
		return TypingTeachWidget()

def init(moduleManager):
	return TypingTeachTypeModule(moduleManager)
