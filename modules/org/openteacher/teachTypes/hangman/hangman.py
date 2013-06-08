#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011-2012, Cas Widdershoven
#	Copyright 2012, Marten de Vries
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

import datetime
import contextlib

def installQtClasses():
	global HangmanTeachWidget

	class HangmanTeachWidget(QtGui.QWidget):
		def __init__(self, wordModule, graphicsWidget, letterChosen, *args, **kwargs):
			super(HangmanTeachWidget, self).__init__(*args, **kwargs)
			self.wordModule = wordModule
			
			self.wrongCharacters = []
			self.guesses = []
			
			self.word = None
			
			self.hgraph = graphicsWidget
			
			letterChosen.handle(self.addLetter)
			
			self.wordLabel = QtGui.QLabel()
			
			self.triedLabel = QtGui.QLabel()
			
			hbox = QtGui.QHBoxLayout()
			
			self.inputLineEdit = QtGui.QLineEdit()
			self.inputLineEdit.textEdited.connect(self._textEdited)
			
			self.checkButton = QtGui.QPushButton()
			self.checkButton.setShortcut(QtCore.Qt.Key_Return)
			
			hbox.addWidget(self.inputLineEdit)
			hbox.addWidget(self.checkButton)
			
			vbox = QtGui.QVBoxLayout()
			vbox.addWidget(self.wordLabel)
			vbox.addWidget(self.triedLabel)
			vbox.addLayout(hbox)
			
			self.setLayout(vbox)
			
			self._retranslate()
			
			self.checkButton.clicked.connect(self.checkGuess)
			self.inputLineEdit.returnPressed.connect(self.checkGuess)
			
		def addLetter(self, letter):
			# Only the currently visible edit
			if self.inputLineEdit.isVisible():
				self.inputLineEdit.insert(letter)
				self.inputLineEdit.setFocus()
		
		def updateLessonType(self, lessonType):
			self.lessonType = lessonType

			self.lessonType.newItem.handle(self.newWord)
			self.lessonType.lessonDone.handle(self.lessonDone)
			
		def newWord(self, word):
			self.otWord = word
			self.guesses = []
			self.wrongCharacters = []
			
			self.triedLabel.setText('')
			self.word = None
			self.wordLabel.setText("")
			self.hgraph.mistakes = 0
			self.hgraph.update()
			
			self._start = datetime.datetime.now()
			self.word = self.wordModule.Word(word["answers"][0][0])
			self.inputLineEdit.clear()
			labelString = "-" * self.word.length
			self.wordLabel.setText(labelString)
			
			self.inputLineEdit.setFocus()
			
		def lessonDone(self):
			self.lessonType.newItem.unhandle(self.newWord)
			self.lessonType.lessonDone.unhandle(self.lessonDone)
			del self.lessonType
			
		def _retranslate(self):
			self.checkButton.setText(_("Check!"))
			
		def _textEdited(self, text):
			try:
				self._end
			except AttributeError:
				self._end = datetime.datetime.now()
			else:
				if not unicode(text).strip():
					del self._end
		
		def checkGuess(self):
			guess = self.inputLineEdit.text()
			if guess in self.guesses:
				self.inputLineEdit.setText(_('You have already tried this character / word'))
				return
			wordLabelList = list(self.wordLabel.text())
			if len(guess) == 1:
				self.guesses.append(guess)
				results = self.word.guessCharacter(guess)
				if results:
					for i in results:
						wordLabelList[i[0]] = i[1]
					resultingString = ""
					for i in wordLabelList:
						resultingString += i
					self.wordLabel.setText(resultingString)
					if resultingString == self.word._word:
						self.showEndOfGame(True)
				else:
					self.wrongCharacters.append(str(guess))
					self.triedLabel.setText(_('Mistakes:  ') + '  |  '.join(self.wrongCharacters))
					self.hgraph.mistakes = self.word.mistakes
					self.hgraph.update()
					if self.word.mistakes >= 6:
						self.showEndOfGame(False)
			elif len(guess) > 1:
				self.guesses.append(guess)
				if self.word.guessWord(guess):
					self.showEndOfGame(True)
				else:
					self.hgraph.mistakes = self.word.mistakes
					self.hgraph.update()
					if self.word.mistakes >= 6:
						self.showEndOfGame(False)
			self.inputLineEdit.clear()
			if self.inputLineEdit.isVisible():
				self.inputLineEdit.setFocus(True)
			
		def showEndOfGame(self, win):
			if win:
				self._previousResult = {"result": "right"}
				givenAnswer = self.word._word
			else:
				self._previousResult = {"result": "wrong"}
				givenAnswer = _("hanged man")
				
			self._previousResult.update({
				"itemId": self.otWord["id"],
				"givenAnswer": givenAnswer,
			})
			
			self.guesses = []
			
			try:
				self._end
			except AttributeError:
				self._end = datetime.datetime.now()
			self._previousResult.update({
				"active": {
					"start": self._start,
					"end": self._end,
				},
			})
			
			
			if win:
				self.timerFinished()
			else:
				self.triedLabel.setText(_("You lose, the answer was: ") + self.word._word)
				timeLine = QtCore.QTimeLine(2000, self)
				timeLine.setFrameRange(0, 255) #256 color steps
				timeLine.frameChanged.connect(self.fade)
				timeLine.finished.connect(self.timerFinished)
				timeLine.start()
				self.inputLineEdit.setEnabled(False)
				
			
		def fade(self, step):
			stylesheet = "QLabel {color: rgb(%s, %s, %s, %s)}" % (255, 00, 00, 255-step)
			self.triedLabel.setStyleSheet(stylesheet)

		def timerFinished(self):
			self.inputLineEdit.setEnabled(True)
			del self._end
			self.triedLabel.setStyleSheet("")
			
			self.guesses = []
			self.wrongCharacters = []
			
			self.triedLabel.setText('')
			self.word = None
			self.wordLabel.setText("")
			self.hgraph.mistakes = 0
			self.hgraph.update()
			
			self.lessonType.setResult(self._previousResult)

class TypingTeachTypeModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TypingTeachTypeModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "teachType"

		self.uses = (
			self._mm.mods(type="translator"),
		)

		self.filesWithTranslations = ("hangman.py",)

		x = 890
		self.priorities = {
			"all": x,
			"selfstudy": x,
			"student@home": x,
			"code-documentation": x,
			"test-suite": x,
			"default": -1,
		}

	def enable(self):
		global QtCore, QtGui
		try:
			from PyQt4 import QtCore, QtGui
		except ImportError:
			return
		installQtClasses()

		self.graphics = self._mm.import_("graphics")
		self.word = self._mm.import_("word")

		self._modules = set(self._mm.mods(type="modules")).pop()

		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		self.dataType = "words"
		self.active = True

	def disable(self):
		self.active = False

		del self.dataType
		del self.name
		del self._modules
		del self.word
		del self.graphics

	def _retranslate(self):
		global _, ngettext
		
		#Translations
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)
		self.name = _("Play hangman")
		with contextlib.ignored(AttributeError):
			self.widget._retranslate()
		
	def addRemoveGraphicsWidget(self, widget):
		if widget == self.widget:
			self.addSideWidget(self.graphicWidget)
		else:
			self.removeSideWidget(self.graphicWidget)

	def createWidget(self, tabChanged, letterChosen, addSideWidget, removeSideWidget):
		self.graphicWidget = self.graphics.HangmanGraphics()
		
		self.addSideWidget = addSideWidget
		self.removeSideWidget = removeSideWidget
		tabChanged.connect(self.addRemoveGraphicsWidget)
		
		self.widget = HangmanTeachWidget(self.word, self.graphicWidget, letterChosen)
		return self.widget

def init(moduleManager):
	return TypingTeachTypeModule(moduleManager)
