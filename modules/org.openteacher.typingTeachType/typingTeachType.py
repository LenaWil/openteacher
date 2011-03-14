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

		#FIXME: add progressview

		vbox = QtGui.QVBoxLayout()
		vbox.addWidget(self.wordsLabel)
		vbox.addWidget(self.inputLineEdit)
		vbox.addWidget(self.checkButton)
		vbox.addWidget(self.correctButton)
		self.setLayout(vbox)

	def start(self, lessonTypeModule):
		self.lessonTypeModule = lessonTypeModule
		
		self.lessonTypeModule.newItem.handle(self.newItem)
		self.lessonTypeModule.lessonDone.handle(self.lessonDone)

		self.checkButton.clicked.connect(self.checkAnswer)
		self.correctButton.clicked.connect(self.lessonTypeModule.correctLastAnswer)

	def newItem(self, item):
		self.item = item
		self.wordsLabel.setText(u", ".join(self.item.questions))
		self.inputLineEdit.clear()
		self.inputLineEdit.setFocus()

	def lessonDone(self): print "Done!"

	def checkAnswer(self):
		if self.inputLineEdit.text() in self.item.answers:
			self.lessonTypeModule.setResult(self.lessonTypeModule.RIGHT)
		else:
			self.lessonTypeModule.setResult(self.lessonTypeModule.WRONG)

class TypingTeachTypeModule(object):
	def __init__(self, manager, *args, **kwargs):
		super(TypingTeachTypeModule, self).__init__(*args, **kwargs)
		self.supports = ("teachType")
		self.type = "words"
		self.name = "Normal lesson"
		self.manager = manager

	def createWidget(self):
		return TypingTeachWidget()

def init(manager):
	return TypingTeachTypeModule(manager)
