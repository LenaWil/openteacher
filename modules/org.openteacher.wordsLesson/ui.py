#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Marten de Vries
#	Copyright 2011, Cas Widdershoven
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
	def __init__(self, moduleManager, *args, **kwargs):
		super(EnterWidget, self).__init__(*args, **kwargs)
		self._mm = moduleManager

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

		vboxWidget = QtGui.QWidget()
		vboxWidget.setLayout(vbox)

		keyboards = self._mm.mods.supporting("onscreenKeyboard").items
		for module in keyboards:
			module.enable()
		for module in self._mm.activeMods.supporting("ui"):
			keyboard = module.chooseItem(keyboards)

		keyboardWidget = keyboard.getWidget()
		keyboardWidget.letterChosen.handle(self.addLetter)

		splitter = QtGui.QSplitter()
		splitter.addWidget(vboxWidget)
		splitter.addWidget(keyboardWidget)

		mainVBox = QtGui.QVBoxLayout()
		mainVBox.addWidget(splitter)
		self.setLayout(mainVBox)

	def addLetter(self, letter):
		self.wordsEnterBox.setText(self.wordsEnterBox.toPlainText() + letter)

class TeachWidget(QtGui.QWidget):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TeachWidget, self).__init__(*args, **kwargs)
		self._mm = moduleManager
		self.teachTypeWidgets = []

		self.teachTab = QtGui.QTabWidget(self)

		for module in self._mm.mods.supporting("teachType").items: #yeah, still needs a better name
			if module.type == "words":
				widget = module.createWidget()
				self.teachTypeWidgets.append(widget)
				self.teachTab.addTab(widget, module.name)

		vbox = QtGui.QVBoxLayout()
		vbox.addWidget(self.teachTab)

		self.setLayout(vbox)
