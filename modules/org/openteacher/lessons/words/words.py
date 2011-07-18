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

class WordList(object):
	def __init__(self, *args, **kwargs):
		super(WordList, self).__init__(*args, **kwargs)

		self.items = []
		self.tests = []

class Word(object): pass

class WordsTableModel(QtCore.QAbstractTableModel):
	QUESTIONS, ANSWERS, COMMENT = xrange(3)

	def __init__(self, composer, parser, *args, **kwargs):
		super(WordsTableModel, self).__init__(*args, **kwargs)

		self._compose = composer
		self._parse = parser

		self.updateList(WordList())

	def updateList(self, list):
		self.beginResetModel()
		self.list = list
		self.indexes = range(len(self.list.items))
		self.endResetModel()

	def sort(self, column, order):
		if column == self.QUESTIONS:
			items = sorted(self.list.items, key=lambda word: word.questions[0])
		elif column == self.ANSWERS:
			items = sorted(self.list.items, key=lambda word: word.answers[0])
		elif column == self.COMMENT:
			items = sorted(self.list.items, key=lambda word: word.comment)

		if order == QtCore.Qt.DescendingOrder:
			items.reverse()

		self.layoutAboutToBeChanged.emit()
		self.indexes = [self.list.items.index(item) for item in items]
		self.layoutChanged.emit()

	def updateTitle(self, title):
		self.list.title = unicode(title)

	def updateQuestionLanguage(self, questionLanguage):
		self.list.questionLanguage = unicode(questionLanguage)

	def updateAnswerLanguage(self, answerLanguage):
		self.list.answerLanguage = unicode(answerLanguage)

	def headerData(self, section, orientation, role):
		if role != QtCore.Qt.DisplayRole:
			return
		if orientation == QtCore.Qt.Horizontal:
			return [_("Questions"), _("Answers"), _("Comment")][section]
		elif orientation == QtCore.Qt.Vertical:
			return section +1

	def rowCount(self, parent=None):
		return len(self.list.items) +1

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
			word = self.list.items[listIndex]

			if index.column() == self.QUESTIONS:
				try:
					return self._compose(word.questions)
				except AttributeError:
					return u""
			elif index.column() == self.ANSWERS:
				try:
					return self._compose(word.answers)
				except AttributeError:
					return u""
			elif index.column() == self.COMMENT:
				try:
					return word.comment
				except AttributeError:
					return u""

	def flags(self, index):
		return (
			QtCore.Qt.ItemIsEnabled |
			QtCore.Qt.ItemIsSelectable |
			QtCore.Qt.ItemIsEditable
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
				try:
					word.id = self.list.items[-1].id +1
				except IndexError:
					word.id = 0
				self.beginInsertRows(
					QtCore.QModelIndex(),
					self.rowCount(),
					self.rowCount()
				)
				self.list.items.append(word)
				self.indexes.append(self.list.items.index(word))
				self.endInsertRows()
			else:
				word = self.list.items[listIndex]

				if index.column() == self.QUESTIONS:
					word.questions = self._parse(unicode(value.toString()))
				elif index.column() == self.ANSWERS:
					word.answers = self._parse(unicode(value.toString()))
				elif index.column() == self.COMMENT:
					word.comment = unicode(value.toString()).strip()
					if len(word.comment) == 0:
						del word.comment
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
		del self.list.items[listIndex]
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
		self._modules = set(self._mm.mods("active", type="modules")).pop()
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
		try:
			ew.keyboardWidget.letterChosen.handle(self._addLetter)
		except AttributeError:
			pass

		composers = set(self._mm.mods("active", type="wordsStringComposer"))
		parsers = set(self._mm.mods("active", type="wordsStringParser"))
		try:
			composer = self._modules.chooseItem(composers).compose
			parser = self._modules.chooseItem(parsers).parse
		except IndexError, e:
			#FIXME: nice error
			raise e

		self._wordsTableModel = WordsTableModel(composer, parser)
		ew.wordsTableView.setModel(self._wordsTableModel)

		ew.titleTextBox.textChanged.connect(
			self._wordsTableModel.updateTitle
		)
		ew.questionLanguageTextBox.textChanged.connect(
			self._wordsTableModel.updateQuestionLanguage
		)
		ew.answerLanguageTextBox.textChanged.connect(
			self._wordsTableModel.updateAnswerLanguage
		)
		self._wordsTableModel.modelReset.connect(self._updateTextBoxes)

	def _updateTextBoxes(self):
		list = self._wordsTableModel.list
		ew = self._enterWidget

		try:
			ew.titleTextBox.setText(list.title)
		except AttributeError:
			pass
		try:
			ew.questionLanguageTextBox.setText(list.questionLanguage)
		except AttributeError:
			pass
		try:
			ew.answerLanguageTextBox.setText(list.answerLanguage)
		except AttributeError:
			pass

	def _removeSelectedRows(self):
		while True:
			try:
				i = self._enterWidget.wordsTableView.selectedIndexes()[0]
			except IndexError:
				break
			try:
				self._wordsTableModel.removeRow(i.row())
			except IndexError:
				#trying to remove the empty add row isn't going to work
				break

	def _addLetter(self, letter):
		ew = self._enterWidget
		i = ew.wordsTableView.currentIndex()

		if not i.isValid():
			return
		data = self._wordsTableModel.data(i) + letter
		self._wordsTableModel.setData(i, data)
		ew.wordsTableView.edit(i)
		ew.wordsTableView.itemDelegate().currentEditor.deselect()
		
	def emit(self):
		self.tabChanged.emit()

	def _initTeachUi(self):
		sw = self._teachWidget.settingsWidget
		lw = self._teachWidget.lessonWidget
		self.tabChanged = self._mm.createEvent()
		lw.teachTabWidget.currentChanged.connect(lambda: self.tabChanged.emit())

		#lessonType
		self._lessonTypeModules = list(self._mm.mods("active", type="lessonType"))

		for module in self._lessonTypeModules:
			sw.lessonTypeComboBox.addItem(module.name)

		#item modifiers
		itemModifiers = []
		for module in self._mm.mods("active", type="itemModifier"):
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
		for module in self._mm.mods("active", type="listModifier"):
			if not module.dataType in ("all", "words"):
				continue
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
		for module in self._mm.mods("active", type="teachType"): 
			if module.dataType in ("all", "words"):
				widget = module.createWidget(self.tabChanged)
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
		try:
			lessonTypeModule = self._lessonTypeModules[i]
		except IndexError, e:
			#Show nicer error
			raise e

		indexes = range(len(self.list.items))

		for listModifier in self._listModifiersModel.modifiers:
			if listModifier["active"]:
				indexes = listModifier["module"].modifyList(
					indexes,
					self.list
				)
		self._lessonType = lessonTypeModule.createLessonType(self.list, indexes)

		self._lessonType.newItem.handle(self._newItem)
		self._lessonType.lessonDone.handle(self._lessonDone)

		for widget in self._teachTypeWidgets:
			widget.updateLessonType(self._lessonType)
		self._lessonType.start()

	def _newItem(self, item):
		#FIXME!!!: item modifiers should be applied wider, not only for
		#the question label, but also for the answers at least.
		lw = self._teachWidget.lessonWidget

		item = copy.copy(item)
		for itemModifier in self._itemModifiersModel.modifiers:
			if itemModifier["active"]:
				item = itemModifier["module"].modifyItem(item)

		composers = set(self._mm.mods("active", type="wordsStringComposer"))
		compose = self._modules.chooseItem(composers).compose
		lw.questionLabel.setText(compose(item.questions))
		self._updateProgress()

	def _lessonDone(self):
		self._updateProgress()
		print "Done!" #FIXME: QMessageBox + back to enter tab etc.?

	def _updateProgress(self):
		lw = self._teachWidget.lessonWidget

		lw.progressBar.setMaximum(self._lessonType.totalItems)
		lw.progressBar.setValue(self._lessonType.askedItems)

class WordsLessonModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(WordsLessonModule, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		self.type = "lesson"

	def enable(self):
		#Translations
		translator = set(self._mm.mods("active", type="translator")).pop()

		global _
		global ngettext

		_, ngettext = translator.gettextFunctions(
			self._mm.resourcePath("translations")
		)
		
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self._modules.registerModule(_("Words Lesson"), self)

		self._enterUi = self._mm.import_("enterUi")
		self._teachUi = self._mm.import_("teachUi")

		self._enterUi._ = self._teachUi._ = _
		self._enterUi.ngettext = self._teachUi.ngettext = ngettext

		self.lessonCreated = self._mm.createEvent()
		self.lessonCreationFinished = self._mm.createEvent()
		self.dataType = "words"

		self._counter = 1
		self._references = set()

		for module in self._mm.mods("active", type="ui"):
			event = module.addLessonCreateButton(_("Create words lesson"))
			event.handle(self.createLesson)
			self._references.add(event)
		self.active = True

	def disable(self):
		self.active = False
		#remove create button
		del self._modules
		del self._enterUi
		del self._teachUi
		del self.lessonCreated
		del self.lessonCreationFinished
		del self.dataType
		del self._counter
		del self._references

	def createLesson(self):
		lessons = set()
		for module in self._mm.mods("active", type="ui"):
			enterWidget = self._enterUi.EnterWidget(self._onscreenKeyboard)
			teachWidget = self._teachUi.TeachWidget(self._onscreenKeyboard)

			fileTab = module.addFileTab(
				_("Word lesson %s") % self._counter,
				enterWidget,
				teachWidget
			)

			lesson = Lesson(self, self._mm, fileTab, enterWidget, teachWidget)
			self._references.add(lesson)
			self.lessonCreated.emit(lesson)

			lessons.add(lesson)
		self._counter += 1
		self.lessonCreationFinished.emit()
		return lessons

	@property
	def _onscreenKeyboard(self):
		keyboards = set(self._mm.mods("active", type="onscreenKeyboard"))
		try:
			keyboard = self._modules.chooseItem(keyboards)
		except IndexError:
			return
		return keyboard.createWidget()

	def loadFromList(self, list):
		for lesson in self.createLesson():
			lesson.loadFromList(list)

def init(moduleManager):
	return WordsLessonModule(moduleManager)
