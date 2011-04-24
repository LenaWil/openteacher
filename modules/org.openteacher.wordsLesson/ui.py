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

from PyQt4 import QtCore, QtGui

class WordList(list): pass

class Word(object):
	def __init__(self, *args, **kwargs):
		super(Word, self).__init__(*args, **kwargs)
		
		self.questions = []
		self.answers = []

class WordsTableModel(QtCore.QAbstractTableModel):
	def __init__(self, *args, **kwargs):
		super(WordsTableModel, self).__init__(*args, **kwargs)

		self.updateList(WordList())

	def updateList(self, list):
		self.beginResetModel()
		self.list = list
		self.endResetModel()

	def updateTitle(self, title):
		self.list.title = unicode(title)

	def updateQuestionSubject(self, questionSubject):
		self.list.questionSubject = unicode(questionSubject)

	def updateAnswerSubject(self, answerSubject):
		self.list.answerSubject = unicode(answerSubject)

	def headerData(self, section, orientation, role):
		if role != QtCore.Qt.DisplayRole:
			return
		if orientation == QtCore.Qt.Horizontal:
			return ["Questions", "Answers", "Results"][section]
		else:
			return section +1

	def rowCount(self, parent=None):
		return len(self.list) +1

	def columnCount(self, parent=None):
		return 3

	def data(self, index, role):
		if not (index.isValid() and
			role in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole)):
			return
		try:
			word = self.list[index.row()]
		except IndexError:
			return u"" #last (empty) row
		else:
			if index.column() == 0:
				return u", ".join(word.questions)
			elif index.column() == 1:
				return u", ".join(word.answers)
			elif index.column() == 2:
				return u"0/0"

	def flags(self, index):
		return (QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable |
			QtCore.Qt.ItemIsEditable)

	def setData(self, index, value, role):
		if not(index.isValid() and role == QtCore.Qt.EditRole):
			return False
		while True:
			try:
				word = self.list[index.row()]
				if index.column() == 0:
					word.questions = unicode(value.toString()).split(", ")
				elif index.column() == 1:
					word.answers = unicode(value.toString()).split(", ")
			except IndexError:
				if value == "":
					return False
				word = Word()
				self.beginInsertRows(
					QtCore.QModelIndex(),
					self.rowCount(),
					self.rowCount()
				)
				self.list.append(word)
				self.endInsertRows()
			else:
				break
		return True

class WordsTableItemDelegate(QtGui.QStyledItemDelegate):
	def eventFilter(self, object, event):
		if (event.type() == QtCore.QEvent.KeyPress and
		  event.key() in (QtCore.Qt.Key_Equal, QtCore.Qt.Key_Return)):
			event = QtGui.QKeyEvent(
				event.type(),
				QtCore.Qt.Key_Tab,
				event.modifiers(),
				event.text(),
				event.isAutoRepeat(),
				event.count()
			)
		return super(WordsTableItemDelegate, self).eventFilter(object, event)

class WordsTableView(QtGui.QTableView):
	def __init__(self, *args, **kwargs):
		super(WordsTableView, self).__init__(*args, **kwargs)

		self.setItemDelegate(WordsTableItemDelegate())

	def moveCursor(self, cursorAction, modifiers):
		if cursorAction not in (QtGui.QAbstractItemView.MoveNext, QtGui.QAbstractItemView.MovePrevious):
			return super(WordsTableView, self).moveCursor(cursorAction, modifiers)
		if self.model().columnCount() == 0 or self.model().rowCount() == 0:
			return QtCore.QModelIndex()

		row = self.currentIndex().row()
		column = self.currentIndex().column()
		if cursorAction == QtGui.QAbstractItemView.MoveNext:
			column += 1
			if column > 1:
				column = 0
				row += 1
			if row > self.model().rowCount() -1:
				row = 0
		elif cursorAction == QtGui.QAbstractItemView.MovePrevious:
			column -= 1
			if column < 0:
				column = 1
				row -= 1
			if row < 0:
				row = self.model().rowCount() -1
		
		return self.model().index(row, column)

class EnterWidget(QtGui.QWidget):
	def __init__(self, moduleManager, *args, **kwargs):
		super(EnterWidget, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.titleTextBox = QtGui.QLineEdit(self)
		self.questionSubjectTextBox = QtGui.QLineEdit(self)
		self.answerSubjectTextBox = QtGui.QLineEdit(self)

		self.wordsTableView = WordsTableView()
		self.wordsTableModel = WordsTableModel()
		self.wordsTableView.setModel(self.wordsTableModel)

		self.titleTextBox.textChanged.connect(
			self.wordsTableModel.updateTitle
		)
		self.questionSubjectTextBox.textChanged.connect(
			self.wordsTableModel.updateQuestionSubject
		)
		self.answerSubjectTextBox.textChanged.connect(
			self.wordsTableModel.updateAnswerSubject
		)
		self.wordsTableModel.modelReset.connect(self._updateTextBoxes)

		layout = QtGui.QGridLayout()
		layout.addWidget(QtGui.QLabel(_("Title:")), 0, 0)
		layout.addWidget(self.titleTextBox, 0, 1)

		layout.addWidget(QtGui.QLabel(_("Question language:")), 1, 0)
		layout.addWidget(self.questionSubjectTextBox, 1, 1)

		layout.addWidget(QtGui.QLabel(_("Answer language:")), 2, 0)
		layout.addWidget(self.answerSubjectTextBox, 2, 1)

		vbox = QtGui.QVBoxLayout()
		vbox.addLayout(layout)
		vbox.addWidget(self.wordsTableView)

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

	def _updateTextBoxes(self):
		list = self.wordsTableModel.list
		self.titleTextBox.setText(list.title)
		self.questionSubjectTextBox.setText(list.questionSubject)
		self.answerSubjectTextBox.setText(list.answerSubject)

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
