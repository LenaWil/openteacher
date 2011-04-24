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

class WordList(list): pass

class Word(object):
	def __init__(self):
		self.questions = []
		self.answers = []

class Lesson(object):
	def __init__(self, module, moduleManager, fileTab, enterWidget, teachWidget, *args, **kwargs):
		super(Lesson, self).__init__(*args, **kwargs)
		
		self.module = module
		self._mm = moduleManager
		self.fileTab = fileTab

		self.fileTab.closeRequested.handle(self.stop)
		self.fileTab.tabChanged.handle(self.tabChanged)
		self.stopped = self._mm.createEvent()
		
		self._enterWidget = enterWidget
		self._teachWidget = teachWidget

	def stop(self):
		self.fileTab.close()
		self.stopped.emit()

	def tabChanged(self):
		if self.fileTab.currentTab == self._teachWidget:
			self.startLesson()

	def loadFromList(self, list):
		self._enterWidget.wordsTableModel.updateList(list)

	@property
	def list(self):
		return self._enterWidget.wordsTableModel.list

	def startLesson(self):
		lessonTypeModules = self._mm.mods.supporting("lessonType").items
		for module in lessonTypeModules:
			module.enable()
		lessonTypeModule = lessonTypeModules.pop() #FIXME: user should choose, combobox?

		lessonType = lessonTypeModule.createLessonType(self.list)
		for widget in self._teachWidget.teachTypeWidgets:
			widget.start(lessonType)
		lessonType.start()

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
		self._ui = self._mm.import_(__file__, "ui")

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
		del self._ui
		del self.lessonCreated
		del self.type
		del self._counter
		del self._references

	def createLesson(self):
		lessons = set()
		for module in self._mm.activeMods.supporting("ui"):
			enterWidget = self._ui.EnterWidget(self._mm)
			teachWidget = self._ui.TeachWidget(self._mm)

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

	def loadFromList(self, list):
		for lesson in self.createLesson():
			lesson.loadFromList(list)

def init(moduleManager):
	return WordsLessonModule(moduleManager)
