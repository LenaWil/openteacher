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

	def setModel(self, model):
		value = super(WordsTableView, self).setModel(model)
		#If the model is empty, let the user start editing
		#(model) has always one starting row.
		if self.model().rowCount() == 1:
			i = self.model().createIndex(0, 0)
			self.setCurrentIndex(i)
			self.edit(i)
		return value

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

class EnterWidget(QtGui.QSplitter):
	def __init__(self, keyboardWidget, *args, **kwargs):
		super(EnterWidget, self).__init__(*args, **kwargs)

		self.titleTextBox = QtGui.QLineEdit(self)
		self.questionLanguageTextBox = QtGui.QLineEdit(self)
		self.answerLanguageTextBox = QtGui.QLineEdit(self)

		self.wordsTableView = WordsTableView()

		topLayout = QtGui.QGridLayout()
		topLayout.addWidget(QtGui.QLabel(_("Title:")), 0, 0)
		topLayout.addWidget(self.titleTextBox, 0, 1)

		topLayout.addWidget(QtGui.QLabel(_("Question language:")), 1, 0)
		topLayout.addWidget(self.questionLanguageTextBox, 1, 1)

		topLayout.addWidget(QtGui.QLabel(_("Answer language:")), 2, 0)
		topLayout.addWidget(self.answerLanguageTextBox, 2, 1)

		leftLayout = QtGui.QVBoxLayout()
		leftLayout.addLayout(topLayout)
		leftLayout.addWidget(self.wordsTableView)

		leftLayoutWidget = QtGui.QWidget()
		leftLayoutWidget.setLayout(leftLayout)

		if keyboardWidget is not None:
			self.keyboardWidget = keyboardWidget
		self.removeSelectedRowsButton = QtGui.QPushButton(
			_("Remove selected row(s)")
		)
		self.removeSelectedRowsButton.setShortcut("Del")

		rightLayout = QtGui.QVBoxLayout()
		try:
			rightLayout.addWidget(self.keyboardWidget)
		except AttributeError:
			pass
		rightLayout.addWidget(self.removeSelectedRowsButton)
		
		rightLayoutWidget = QtGui.QWidget()
		rightLayoutWidget.setLayout(rightLayout)

		self.addWidget(leftLayoutWidget)
		self.addWidget(rightLayoutWidget)

		self.setStretchFactor(0, 255)
		self.setStretchFactor(1, 1)
