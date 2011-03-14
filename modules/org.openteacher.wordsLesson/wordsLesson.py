#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Marten de Vries, Cas Widdershoven
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

from PyQt4 import QtGui

class WordList(list): pass

class Word(object):
	def __init__(self):
		self.questions = []
		self.answers = []

class WordsTextEdit(QtGui.QTextEdit):
	def highlightLine(self, line, qcolor):
		cursor = QtGui.QTextCursor(window.textCursor())
		
		for i in xrange(line - 1):
			cursor.movePosition(QtGui.QTextCursor.Down)
		
		cursor.movePosition(QtGui.QTextCursor.StartOfLine)
		cursor.movePosition(QtGui.QTextCursor.EndOfLine, QtGui.QTextCursor.KeepAnchor)

		format = QtGui.QTextBlockFormat()
		format.setBackground(qcolor)
		cursor.setBlockFormat(format)

class EnterWidget(QtGui.QWidget):
	def __init__(self, *args, **kwargs):
		super(EnterWidget, self).__init__(*args, **kwargs)
		
	def initGUI(self):
		self.titleTextBox = QtGui.QLineEdit(self)
		self.questionSubjectTextBox = QtGui.QLineEdit(self)
		self.answerSubjectTextBox = QtGui.QLineEdit(self)
		
		self.wordsEnterBox = WordsTextEdit(self)

		layout = QtGui.QGridLayout()
		layout.addWidget(QtGui.QLabel(_("Title:")), 0, 0)
		layout.addWidget(self.titleTextBox, 0, 1)

		layout.addWidget(QtGui.QLabel(_("Question language:")), 1, 0)
		layout.addWidget(self.questionSubjectTextBox, 1, 1)

		layout.addWidget(QtGui.QLabel(_("Answer language:")), 2, 0)
		layout.addWidget(self.answerSubjectTextBox, 2, 1)

		vbox = QtGui.QVBoxLayout()
		vbox.addLayout(layout)
		vbox.addWidget(self.wordsEnterBox)

		self.setLayout(vbox)
		

class TeachWidget(QtGui.QWidget):
	def __init__(self, manager, *args, **kwargs):
		super(TeachWidget, self).__init__(*args, **kwargs)
		self.manager = manager
	
	def initGUI(self, lesson):
		self.teachTab = QtGui.QTabWidget(self)
		
		lessonTypeModules = self.manager.mods.supporting('lessonType').items
		lessonTypeModule = lessonTypeModules.pop() #FIXME; user should choose
		
		
		for module in self.manager.mods.supporting('teachType').items: #yeah, still needs a better name
			if module.type == 'words':
				self.teachTab.addTab(module.getWidget(lessonTypeModule.getLessonType(lesson.list)), module.name)
				
		vbox = QtGui.QVBoxLayout()
		vbox.addWidget(self.teachTab)

		self.setLayout(vbox)

class Lesson(object):
	def __init__(self, module, manager, fileTab, enterWidget, *args, **kwargs):
		super(Lesson, self).__init__(*args, **kwargs)
		
		self.module = module
		self.manager = manager
		self.fileTab = fileTab

		self.fileTab.closeRequested.handle(self.stop)
		self.stopped = self.manager.createEvent()
		
		self._enterWidget = enterWidget

	def stop(self):
		self.fileTab.close()
		self.stopped.emit()

	def loadFromList(self, list):
		self._enterWidget.titleTextBox.setText(list.title)
		self._enterWidget.questionSubjectTextBox.setText(list.questionSubject)
		self._enterWidget.answerSubjectTextBox.setText(list.answerSubject)
		
		text = u""
		for word in list:
			text += "%s = %s\n" % (
				u", ".join(word.questions),
				u", ".join(word.answers)
			)
		self._enterWidget.wordsEnterBox.setText(text)

	@property
	def list(self):
		#empty list
		wordList = WordList()
		wordList.title = unicode(self._enterWidget.titleTextBox.text())
		wordList.questionSubject = unicode(self._enterWidget.questionSubjectTextBox.text())
		wordList.answerSubject = unicode(self._enterWidget.answerSubjectTextBox.text())

		enteredWords = unicode(self._enterWidget.wordsEnterBox.toPlainText())
		for line in enteredWords.split("\n"):
			if "=" in line:
				questions, answers = line.split("=")

				stripper = lambda x: x.strip()
				splitter = lambda x: map(stripper, x.split(","))

				word = Word()
				word.questions = splitter(questions)
				word.answers = splitter(answers)

				wordList.append(word)

		return wordList

class WordsLessonModule(object):
	def __init__(self, manager, *args, **kwargs):
		super(WordsLessonModule, self).__init__(*args, **kwargs)

		self.manager = manager
		self.supports = ("state", "lesson", "list", "loadList")
		self.lessonCreated = self.manager.createEvent()
		self.type = "words"

		self._counter = 1
		self._references = set()

	def enable(self):
		for module in self.manager.mods.supporting("ui"):
			event = module.addLessonCreateButton("Create words lesson")
			event.handle(self.createLesson)
			self._references.add(event)

	def disable(self):
		#remove create button
		pass

	def createLesson(self):
		lessons = set()
		for module in self.manager.mods.supporting("ui"):
			enterWidget = EnterWidget()
			teachWidget = TeachWidget(self.manager)
			
			fileTab = module.addFileTab(
				"Word lesson %s" % self._counter,
				enterWidget,
				teachWidget
			)

			lesson = Lesson(self, self.manager, fileTab, enterWidget)
			enterWidget.initGUI()
			teachWidget.initGUI(lesson)
			self._references.add(lesson)
			self.lessonCreated.emit(lesson)
						
			lessons.add(lesson)
		self._counter += 1
		return lessons

	def loadFromList(self, list):
		for lesson in self.createLesson():
			lesson.loadFromList(list)

def init(manager):
	return WordsLessonModule(manager)
