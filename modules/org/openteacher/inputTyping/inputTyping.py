#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Cas Widdershoven
#	Copyright 2011-2012, Marten de Vries
#	Copyright 2008-2011, Milan Boers
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
import weakref
import difflib

def getInputTypingWidget():
	class InputTypingWidget(QtGui.QWidget):
		def __init__(self, check, compose, parse, getFadeTime, letterChosen, *args, **kwargs):
			super(InputTypingWidget, self).__init__(*args, **kwargs)

			self._check = check
			self._compose = compose
			self._parse = parse
			self._getFadeTime = getFadeTime

			self.correctLabel = QtGui.QLabel()

			self.inputLineEdit = QtGui.QLineEdit()
			self.inputLineEdit.textEdited.connect(self._textEdited)

			self.skipButton = QtGui.QPushButton()
			self.checkButton = QtGui.QPushButton()
			self.checkButton.setShortcut(QtCore.Qt.Key_Return)
			self.correctButton = QtGui.QPushButton()

			mainLayout = QtGui.QGridLayout()
			mainLayout.addWidget(self.correctLabel, 0, 0, 1, 3)
			mainLayout.addWidget(self.inputLineEdit, 1, 0, 1, 2)
			mainLayout.addWidget(self.checkButton, 1, 2)
			mainLayout.addWidget(self.correctButton, 2, 1)
			mainLayout.addWidget(self.skipButton, 2, 2)
			self.setLayout(mainLayout)
			
			# Make character input work
			letterChosen.handle(self.addLetter)

			#connect events
			self.checkButton.clicked.connect(self.checkAnswer)
			self.correctButton.clicked.connect(self.correctLastAnswer)
			#skip button needs lessontype, so is connected later on

			self.inputLineEdit.returnPressed.connect(self.checkAnswer)

		def retranslate(self):
			self.checkButton.setText(_("Check!"))
			self.correctButton.setText(_("Correct anyway"))
			self.skipButton.setText(_("Skip"))
		
		def addLetter(self, letter):
			# Only the currently visible edit
			if self.inputLineEdit.isVisible():
				self.inputLineEdit.insert(letter)
				self.inputLineEdit.setFocus()

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
			self.lessonType.lessonDone.handle(self.lessonDone)
			self.skipButton.clicked.connect(self.lessonType.skip)

			#disable correct anyway button (no items done yet)
			self.correctButton.setEnabled(False)

		def lessonDone(self):
			self.lessonType.newItem.unhandle(self.newWord)
			self.lessonType.lessonDone.unhandle(self.lessonDone)
			self.skipButton.clicked.disconnect(self.lessonType.skip)
			del self.lessonType

		def newWord(self, word):
			self._start = datetime.datetime.now()
			self.word = word
			self.inputLineEdit.clear()

		def _diff(self, answers, givenAnswer):
			#Check if the input looks like the answer or the second answer.
			try:
				similar = difflib.get_close_matches(givenAnswer, [answers])[0]
			except IndexError:
				#It doesn't, set similar to None
				similar = None

			#If they look like each other.
			if similar:
				#Show the differences graphical
				output = ""
				for item in difflib.ndiff(givenAnswer, similar):
					if item.startswith('+ '):
						output += '<span style="color: #1da90b;"><u>%s</u></span>' % item[2:]
					elif item.startswith('- '):
						output += '<span style="color: #da0f0f;"><s>%s</s></span>' % item[2:]
					else:
						output += item[2:]
				return output

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
			#disable correct anyway button
			self.correctButton.setEnabled(False)

		def checkAnswer(self):
			givenStringAnswer = unicode(self.inputLineEdit.text())
			givenAnswer = self._parse(givenStringAnswer)

			#Collect all possible answers, and add them into a temporary
			#word. This temporary word is then used for checking and
			#displaying a diff.
			#
			#fixes bug #809964: OpenTeacher does not check for double
			#questions
			answers = []
			for item in self.lessonType.list.get("items", []):
				if item["questions"] == self.word["questions"]:
					answers.extend(item["answers"])
				elif item["answers"] == self.word["questions"]:
					#handy in the case that the word list is reversed.
					#FIXME > 3.0: maybe this needs a cleaner solution...
					#
					#uses elif so 'six = six' (english - french) doesn't
					#result in 1. six 2. six
					answers.extend(item["questions"])

			tempWord = self.word.copy()
			tempWord["answers"] = answers

			self._previousResult = self._check(givenAnswer, tempWord)
			try:
				self._end
			except AttributeError:
				self._end = datetime.datetime.now()
			self._previousResult.update({
				"active": {
					"start": self._start,
					"end": self._end,
				},
				"givenAnswer": givenStringAnswer,
			})
			self.enableUi(False)
			if self._previousResult["result"] == "wrong":
				#enable correct anyway button
				self.correctButton.setEnabled(True)

				timeLine = QtCore.QTimeLine(self._getFadeTime(), self)
				timeLine.setFrameRange(0, 255) #256 color steps
				timeLine.frameChanged.connect(self.fade)
				timeLine.finished.connect(self.timerFinished)
				timeLine.start()
				#show diff
				composedAnswers = self._compose(tempWord["answers"])
				diff = self._diff(composedAnswers, givenStringAnswer)
				if diff:
					text = _("Correct answer: <b>{answers}</b> [{diff}]").format(answers=composedAnswers, diff=diff)
				else:
					text = _("Correct answer: <b>{answers}</b>").format(answers=composedAnswers)
				self.correctLabel.setText(text)
			else:
				#disable correct anyway button
				self.correctButton.setEnabled(False)
				#no need to start timer in the first place
				self.timerFinished()

		def enableUi(self, enable):
			self.checkButton.setEnabled(enable)
			self.skipButton.setEnabled(enable)
			self.inputLineEdit.setEnabled(enable)

		def fade(self, step):
			stylesheet = "QLineEdit {color: rgb(%s, %s, %s, %s)}" % (255, 00, 00, 255-step)
			self.inputLineEdit.setStyleSheet(stylesheet)

		def timerFinished(self):
			del self._end
			self.inputLineEdit.setStyleSheet("")
			self.lessonType.setResult(self._previousResult)
			self.enableUi(True)
			self.correctLabel.clear()
			self.inputLineEdit.setFocus()
		
		def showEvent(self, event):
			self.inputLineEdit.setFocus()
	return InputTypingWidget

class InputTypingModule(object):
	_check = property(lambda self: self._modules.default(type="wordsStringChecker").check)
	_compose = property(lambda self: self._modules.default(type="wordsStringComposer").compose)
	_parse = property(lambda self: self._modules.default(type="wordsStringParser").parse)

	def __init__(self, moduleManager, *args, **kwargs):
		super(InputTypingModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "typingInput"
		self.uses = (
			self._mm.mods(type="translator"),
			self._mm.mods(type="settings"),
		)
		self.requires = (
			self._mm.mods(type="ui"),
			self._mm.mods(type="wordsStringChecker"),
			self._mm.mods(type="wordsStringComposer"),
			self._mm.mods(type="wordsStringParser"),
		)
		self.filesWithTranslations = ("inputTyping.py",)

	def enable(self):
		global QtCore, QtGui
		try:
			from PyQt4 import QtCore, QtGui
		except ImportError:
			return
		global InputTypingWidget
		InputTypingWidget = getInputTypingWidget()

		self._modules = set(self._mm.mods(type="modules")).pop()
		self._activeWidgets = set()

		#Register the fade duration setting
		DEFAULT_VALUE = 4000
		try:
			self._fadeDurationSetting = self._modules.default(type="settings").registerSetting(**{
				"internal_name": "org.openteacher.inputTyping.fadeDuration",
				"type": "number",
				"defaultValue": DEFAULT_VALUE,
			})
		except IndexError:
			self._fadeDurationSetting = {
				"value": DEFAULT_VALUE,
			}

		#Translations
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		self.active = True

	def _retranslate(self):
		#Install translator inside the whole of these file
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

		#update all active widgets
		for ref in self._activeWidgets:
			wid = ref()
			if wid is not None:
				wid.retranslate()

		#update the setting
		self._fadeDurationSetting.update({
			"name": _("Fade duration when wrong (milliseconds)"),
			"category": _("Lesson"),
			"subcategory": _("Words lesson"),
		})

	def disable(self):
		self.active = False

		del self._modules
		del self._activeWidgets
		del self._fadeDurationSetting

	def createWidget(self, letterChosen):
		getFadeDuration = lambda: self._fadeDurationSetting["value"]
		it = InputTypingWidget(self._check, self._compose, self._parse, getFadeDuration, letterChosen)
		self._activeWidgets.add(weakref.ref(it))
		it.retranslate()
		return it

def init(moduleManager):
	return InputTypingModule(moduleManager)
