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

class WordList(list):
	def __init__(self, *args, **kwargs):
		super(WordList, self).__init__(*args, **kwargs)

		self.title = u""
		self.questionSubject = u""
		self.answerSubject = u""

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
		self.indexes = range(len(self.list))
		self.endResetModel()

	def sort(self, column, order):
		if column == 0:
			items = sorted(self.list, key=lambda word: word.questions[0])
		elif column == 1:
			items = sorted(self.list, key=lambda word: word.answers[0])
		elif column == 2:
			items = self.list[:]

		if order == QtCore.Qt.DescendingOrder:
			items.reverse()

		self.layoutAboutToBeChanged.emit()
		self.indexes = [self.list.index(item) for item in items]
		self.layoutChanged.emit()

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
		elif orientation == QtCore.Qt.Vertical:
			return section +1

	def rowCount(self, parent=None):
		return len(self.list) +1

	def columnCount(self, parent=None):
		return 3

	def data(self, index, role=QtCore.Qt.DisplayRole):
		if not (index.isValid() and
			role in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole)):
			return
		try:
			listIndex = self.indexes[index.row()]
		except IndexError:
			return u"" #last (empty) row
		else:
			word = self.list[listIndex]

			if index.column() == 0:
				return u", ".join(word.questions)
			elif index.column() == 1:
				return u", ".join(word.answers)
			elif index.column() == 2:
				return u"0/0"

	def flags(self, index):
		if index.column() != 2:
			return (
				QtCore.Qt.ItemIsEnabled |
				QtCore.Qt.ItemIsSelectable |
				QtCore.Qt.ItemIsEditable
			)
		else:
			return (
				QtCore.Qt.ItemIsEnabled |
				QtCore.Qt.ItemIsSelectable
			)

	def setData(self, index, value, role=QtCore.Qt.EditRole):
		if not (index.isValid() and role == QtCore.Qt.EditRole):
			return False
		#makes calling without a QVariant possible (more dynamic).
		value = QtCore.QVariant(value)
		while True:
			try:
				listIndex = self.indexes[index.row()]
			except IndexError:
				if not unicode(value.toString()):
					return False
				word = Word()
				self.beginInsertRows(
					QtCore.QModelIndex(),
					self.rowCount(),
					self.rowCount()
				)
				self.list.append(word)
				self.indexes.append(self.list.index(word))
				self.endInsertRows()
			else:
				word = self.list[listIndex]

				if index.column() == 0:
					word.questions = unicode(value.toString()).split(", ")
				elif index.column() == 1:
					word.answers = unicode(value.toString()).split(", ")
				break
		return True

	def removeRow(self, row, parent=QtCore.QModelIndex()):
		listIndex = self.indexes[row]
		self.beginRemoveRows(parent, row, row)
		del self.indexes[row]
		#update self.indexes
		for i in xrange(len(self.indexes)):
			if self.indexes[i] > listIndex:
				self.indexes[i] -= 1
		del self.list[listIndex]
		self.endRemoveRows()

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

	def createEditor(self, parent, option, index):
		self.currentEditor = super(WordsTableItemDelegate, self).createEditor(
			parent, option, index
		)
		return self.currentEditor

class WordsTableView(QtGui.QTableView):
	def __init__(self, *args, **kwargs):
		super(WordsTableView, self).__init__(*args, **kwargs)

		self.setItemDelegate(WordsTableItemDelegate())
		self.setAlternatingRowColors(True)
		self.setSortingEnabled(True)

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

		topLayout = QtGui.QGridLayout()
		topLayout.addWidget(QtGui.QLabel(_("Title:")), 0, 0)
		topLayout.addWidget(self.titleTextBox, 0, 1)

		topLayout.addWidget(QtGui.QLabel(_("Question language:")), 1, 0)
		topLayout.addWidget(self.questionSubjectTextBox, 1, 1)

		topLayout.addWidget(QtGui.QLabel(_("Answer language:")), 2, 0)
		topLayout.addWidget(self.answerSubjectTextBox, 2, 1)

		leftLayout = QtGui.QVBoxLayout()
		leftLayout.addLayout(topLayout)
		leftLayout.addWidget(self.wordsTableView)

		leftLayoutWidget = QtGui.QWidget()
		leftLayoutWidget.setLayout(leftLayout)

		keyboards = self._mm.mods.supporting("onscreenKeyboard").items
		for module in keyboards:
			module.enable()
		for module in self._mm.activeMods.supporting("ui"):
			keyboard = module.chooseItem(keyboards)

		self.keyboardWidget = keyboard.getWidget()
		self.removeSelectedRowsButton = QtGui.QPushButton(
			_("Remove selected row(s)")
		)
		self.removeSelectedRowsButton.setShortcut(
			QtGui.QKeySequence(QtCore.Qt.Key_Delete) #FIXME: translatable?
		)

		rightLayout = QtGui.QVBoxLayout()
		rightLayout.addWidget(self.keyboardWidget)
		rightLayout.addWidget(self.removeSelectedRowsButton)
		
		rightLayoutWidget = QtGui.QWidget()
		rightLayoutWidget.setLayout(rightLayout)

		mainSplitter = QtGui.QSplitter()
		mainSplitter.addWidget(leftLayoutWidget)
		mainSplitter.addWidget(rightLayoutWidget)

		mainLayout = QtGui.QVBoxLayout()
		mainLayout.addWidget(mainSplitter)
		self.setLayout(mainLayout)
