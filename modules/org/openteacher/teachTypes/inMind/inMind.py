#! /usr/bin/env python
# -*- coding: utf-8 -*-

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
import datetime

class ThinkWidget(QtGui.QWidget):
	def __init__(self, *args, **kwargs):
		super(ThinkWidget, self).__init__(*args, **kwargs)
		
		self.label = QtGui.QLabel(_("Think about the answer, and press the 'View answer' button when you're done."))
		self.label.setWordWrap(True)
		self.button = QtGui.QPushButton(_("View answer"))
		
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
	def __init__(self, compose, *args, **kwargs):
		super(InMindTeachWidget, self).__init__(*args, **kwargs)

		self._compose = compose

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

	def _constructResult(self):
		return {
			"itemId": self._currentWord["id"],
			"active": {
				"start": self.start,
				"end": self.end,
			},
		}

	def setRight(self):
		result = self._constructResult()
		result["result"] = "right"
		self.lessonType.setResult(result)

	def setWrong(self):
		result = self._constructResult()
		result["result"] = "wrong"
		self.lessonType.setResult(result)

	def newItem(self, word):
		self._currentWord = word
		self.answerWidget.label.setText(
			_("Translation: ") + self._compose(word["answers"])
		)
		self.start = datetime.datetime.now()
		self.setCurrentWidget(self.thinkWidget)

	def startAnswering(self):
		self.end = datetime.datetime.now()
		self.setCurrentWidget(self.answerWidget)

class InMindTeachTypeModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(InMindTeachTypeModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "teachType"
		self.uses = (
			(
				("active",),
				{"type": "translator"},
			),
		)
		self.requires = (
			(
				("active",),
				{"type": "wordsStringComposer"}
			),
		)

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()

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
		self.dataType = "words"
		self.name = _("Think answer")
		self.active = True

	def disable(self):
		self.active = False

		del self.uses
		del self._modules
		del self.dataType
		del self.name

	@property
	def _compose(self):
		return self._modules.default(
			"active",
			type="wordsStringComposer"
		).compose

	def createWidget(self, tabChanged):
		return InMindTeachWidget(self._compose)

def init(moduleManager):
	return InMindTeachTypeModule(moduleManager)
