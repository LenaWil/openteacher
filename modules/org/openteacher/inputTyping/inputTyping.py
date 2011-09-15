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
	def __init__(self, check, fade, *args, **kwargs):
		super(InputTyping, self).__init__(*args, **kwargs)

		self._check = check

		self.inputLineEdit = QtGui.QLineEdit()
		self.inputLineEdit.textEdited.connect(self._textEdited)

		self.checkButton = QtGui.QPushButton()
		self.checkButton.setShortcut(QtCore.Qt.Key_Return)
		self.correctButton = QtGui.QPushButton()

		self._fade = fade

		mainLayout = QtGui.QGridLayout()
		mainLayout.addWidget(self.inputLineEdit, 0, 0)
		mainLayout.addWidget(self.checkButton, 0, 1)
		mainLayout.addWidget(self.correctButton, 1, 1)
		self.setLayout(mainLayout)

	def _retranslate(self):
		self.checkButton.setText(_(u"Check!"))
		self.correctButton.setText(_(u"Correct anyway"))

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
		try:
			self._previousResult.update({
				"result": "right",
				"givenAnswer": _("Corrected: %s") % self._previousResult["givenAnswer"]
			})
		except KeyError:
			self._previousResult.update({
				"result": "right",
				"givenAnswer": _("Corrected")
			})
		self.lessonType.correctLastAnswer(self._previousResult)

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
		self.timeLine = QtCore.QTimeLine(2000)
		self.timeLine.setFrameRange(0, 1020)
		if result["result"] == "right":
			self.timeLine.frameChanged.connect(lambda x: self._fade(x, [self.inputLineEdit], [0, 255, 0]))
		else:
			self.timeLine.frameChanged.connect(lambda x: self._fade(x, [self.inputLineEdit], [255, 0, 0]))
		self.timeLine.start()
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
			self._mm.mods(type="fader") #FIXME: requires?
		)

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()

		#Translations
		global _
		global ngettext

		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		self.active = True

	def _retranslate(self):
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

	def disable(self):
		self.active = False

		del self._modules

	@property
	def _fade(self):
		return self._modules.default("active", type="fader").fade

	@property
	def _check(self):
		return self._modules.default(type="wordsStringChecker").check

	def createWidget(self):
		return InputTyping(self._check, self._fade)

def init(moduleManager):
	return InputTypingModule(moduleManager)
