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

from PyQt4 import QtCore
import copy

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

class ModifiersListModel(QtCore.QAbstractListModel):
	def __init__(self, modifiers, *args, **kwargs):
		super(ModifiersListModel, self).__init__(*args, **kwargs)
		
		self.modifiers = modifiers

	def rowCount(self, parent=None):
		return len(self.modifiers)

	def data(self, index, role):
		if not index.isValid():
			return
		if role == QtCore.Qt.DisplayRole:
			return self.modifiers[index.row()]["name"]
		elif role == QtCore.Qt.CheckStateRole:
			if self.modifiers[index.row()]["active"]:
				return QtCore.Qt.Checked
			else:
				return QtCore.Qt.Unchecked

	def setData(self, index, value, role):
		if not index.isValid():
			return False
		if role == QtCore.Qt.CheckStateRole:
			if value == QtCore.Qt.Checked:
				self.modifiers[index.row()]["active"] = True
			else:
				self.modifiers[index.row()]["active"] = False
		return False

	def flags(self, index):
		return (
			QtCore.Qt.ItemIsEnabled |
			QtCore.Qt.ItemIsSelectable |
			QtCore.Qt.ItemIsUserCheckable
		)

class Lesson(object):
	def __init__(self, module, moduleManager, fileTab, enterWidget, teachWidget, *args, **kwargs):
		super(Lesson, self).__init__(*args, **kwargs)
		
		self.module = module
		self._mm = moduleManager
		self.fileTab = fileTab

		self.fileTab.closeRequested.handle(self.stop)
		self.stopped = self._mm.createEvent()
		
		self._enterWidget = enterWidget
		self._teachWidget = teachWidget
		
		self._initEnterUi()
		self._initTeachUi()

	def loadFromList(self, list):
		self._wordsTableModel.updateList(list)

	@property
	def list(self):
		return self._wordsTableModel.list

	def stop(self):
		self.fileTab.close()
		self.stopped.emit()

	def _initEnterUi(self):
		ew = self._enterWidget
		ew.removeSelectedRowsButton.clicked.connect(
			self._removeSelectedRows
		)
		ew.keyboardWidget.letterChosen.handle(self._addLetter)

		self._wordsTableModel = WordsTableModel()
		ew.wordsTableView.setModel(self._wordsTableModel)

		ew.titleTextBox.textChanged.connect(
			self._wordsTableModel.updateTitle
		)
		ew.questionSubjectTextBox.textChanged.connect(
			self._wordsTableModel.updateQuestionSubject
		)
		ew.answerSubjectTextBox.textChanged.connect(
			self._wordsTableModel.updateAnswerSubject
		)
		self._wordsTableModel.modelReset.connect(self._updateTextBoxes)

	def _updateTextBoxes(self):
		list = self._enterWidget.wordsTableModel.list
		ew = self._enterWidget

		ew.titleTextBox.setText(list.title)
		ew.questionSubjectTextBox.setText(list.questionSubject)
		ew.answerSubjectTextBox.setText(list.answerSubject)

	def _removeSelectedRows(self):
		while True:
			try:
				i = self._enterWidget.wordsTableView.selectedIndexes()[0]
			except IndexError:
				break
			try:
				self._enterWidget.wordsTableModel.removeRow(i.row())
			except IndexError:
				#trying to remove the empty add row isn't going to work
				break

	def _addLetter(self, letter):
		ew = self._enterWidget
		i = ew.wordsTableView.currentIndex()

		if not i.isValid():
			return
		data = ew.wordsTableModel.data(i) + letter
		ew.wordsTableModel.setData(i, data)
		ew.wordsTableView.edit(i)
		ew.wordsTableView.itemDelegate().currentEditor.deselect()

	def _initTeachUi(self):
		sw = self._teachWidget.settingsWidget
		lw = self._teachWidget.lessonWidget

		#lessonType
		self._lessonTypeModules = list(
			self._mm.mods.supporting("lessonType") #FIXME: activeMods?
		)

		for module in self._lessonTypeModules:
			module.enable()
			sw.lessonTypeComboBox.addItem(module.name)

		#item modifiers
		itemModifiers = []
		for module in self._mm.mods.supporting("itemModifier"): #FIXME: activeMods?
			module.enable()
			itemModifiers.append({
				"name": module.name,
				"active": False,
				"module": module
			})
		self._itemModifiersModel = ModifiersListModel(itemModifiers)
		sw.modifyWordListView.setModel(self._itemModifiersModel)

		#list modifiers
		listModifiers = []
		for module in self._mm.mods.supporting("listModifier"): #FIXME: activeMods?:
			module.enable()
			listModifiers.append({
				"name": module.name,
				"active": False,
				"module": module
			})
		self._listModifiersModel = ModifiersListModel(listModifiers)
		sw.modifyWordListListView.setModel(self._listModifiersModel)

		#start lesson button
		sw.startLessonButton.clicked.connect(self._startLesson)

		#change lesson settings button
		lw.changeSettingsButton.clicked.connect(self._showSettings)

		#teachType
		self._teachTypeWidgets = []
		for module in self._mm.mods.supporting("teachType"): #FIXME: activeMods?
			module.enable()
			if module.type == "words":
				widget = module.createWidget()
				self._teachTypeWidgets.append(widget)
				lw.teachTabWidget.addTab(widget, module.name)

	def _showSettings(self):
		sw = self._teachWidget.settingsWidget
		self._teachWidget.setCurrentWidget(sw)

	def _startLesson(self):
		sw = self._teachWidget.settingsWidget
		lw = self._teachWidget.lessonWidget

		self._teachWidget.setCurrentWidget(lw)

		i = sw.lessonTypeComboBox.currentIndex()
		lessonTypeModule = self._lessonTypeModules[i]

		indexes = range(len(self.list))

		for listModifier in self._listModifiersModel.modifiers:
			indexes = listModifier["module"].modifyList(indexes, self.list)
		lessonList = [self.list[i] for i in indexes]

		self._lessonType = lessonTypeModule.createLessonType(lessonList)

		self._lessonType.newItem.handle(self._newItem)
		self._lessonType.lessonDone.handle(self._lessonDone)

		for widget in self._teachTypeWidgets:
			widget.updateLessonType(self._lessonType)
		self._lessonType.start()

	def _newItem(self, item):
		lw = self._teachWidget.lessonWidget

		item = copy.copy(item)
		for itemModifier in self._itemModifiersModel.modifiers:
			item = itemModifier["module"].modifyItem(item)

		lw.questionLabel.setText(u", ".join(item.questions))
		self._updateProgress()

	def _lessonDone(self):
		self._updateProgress()
		print "Done!" #FIXME: QMessageBox?

	def _updateProgress(self):
		lw = self._teachWidget.lessonWidget

		lw.progressBar.setMaximum(self._lessonType.totalQuestions)
		lw.progressBar.setValue(self._lessonType.askedQuestions)

class WordsLessonModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(WordsLessonModule, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		self.supports = ("lesson", "list", "loadList", "initializing")
		self.requires = (1, 0)
		self.active = False

	def initialize(self):
		for module in self._mm.activeMods.supporting("settings"):
			module.registerModule("Words Lesson", self)

	def enable(self):
		self._enterUi = self._mm.import_(__file__, "enterUi")
		self._teachUi = self._mm.import_(__file__, "teachUi")

		self.lessonCreated = self._mm.createEvent()
		self.type = "words"

		self._counter = 1
		self._references = set()

		for module in self._mm.mods.supporting("ui"):
			event = module.addLessonCreateButton("Create words lesson")
			event.handle(self.createLesson)
			self._references.add(event)
		self.active = True

	def disable(self):
		self.active = False
		#remove create button
		del self._enterUi
		del self._teachUi
		del self.lessonCreated
		del self.type
		del self._counter
		del self._references

	def createLesson(self):
		lessons = set()
		for module in self._mm.activeMods.supporting("ui"):
			enterWidget = self._enterUi.EnterWidget(self._onscreenKeyboard)
			teachWidget = self._teachUi.TeachWidget(self._onscreenKeyboard)

			fileTab = module.addFileTab(
				"Word lesson %s" % self._counter,
				enterWidget,
				teachWidget
			)

			lesson = Lesson(self, self._mm, fileTab, enterWidget, teachWidget)
			self._references.add(lesson)
			self.lessonCreated.emit(lesson)

			lessons.add(lesson)
		self._counter += 1
		return lessons

	@property
	def _onscreenKeyboard(self):
		keyboards = self._mm.mods.supporting("onscreenKeyboard").items
		for module in keyboards:
			module.enable()
		for module in self._mm.activeMods.supporting("ui"):
			keyboard = module.chooseItem(keyboards)

		return keyboard.getWidget()

	def loadFromList(self, list):
		for lesson in self.createLesson():
			lesson.loadFromList(list)

def init(moduleManager):
	return WordsLessonModule(moduleManager)
