#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Marten de Vries
#	Copyright 2011, Cas Widdershoven
#	Copyright 2011, Milan Boers
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

class Lesson(object):
	def __init__(self, moduleManager, fileTab, module, list, enterWidget, teachWidget, resultsWidget, *args, **kwargs):
		super(Lesson, self).__init__(*args, **kwargs)

		self.resources = {} #To be removed...

		self._mm = moduleManager
		self.module = module

		self.fileTab = fileTab
		self.fileTab.closeRequested.handle(self.stop)
		self.stopped = self._mm.createEvent()

		self.list = list

		self._enterWidget = enterWidget
		self._teachWidget = teachWidget
		self._resultsWidget = resultsWidget

		self._teachWidget.lessonDone.connect(self._lessonDone)

	def _lessonDone(self):
		self.fileTab.currentTab = self._enterWidget

	def stop(self):
		self.fileTab.close()
		self.stopped.emit()

class WordsLessonModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(WordsLessonModule, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		self.type = "lesson"

	def enable(self):
		self.dataType = "words"

		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self._uiModule = set(self._mm.mods("active", type="ui")).pop()

		#Translations
		translator = set(self._mm.mods("active", type="translator")).pop()

		global _
		global ngettext

		_, ngettext = translator.gettextFunctions(
			self._mm.resourcePath("translations")
		)

		self._modules.registerModule(_("Words Lesson"), self)

		self.lessonCreated = self._mm.createEvent()
		self.lessonCreationFinished = self._mm.createEvent()

		self._counter = 1
		self._references = set()

		event = self._uiModule.addLessonCreateButton(_("Create words lesson"))
		event.handle(self.createLesson)
		self._references.add(event)

		self.active = True

	def disable(self):
		self.active = False
		#FIXME: remove create button
		del self.dataType
		del self._modules
		del self._uiModule
		del self.lessonCreated
		del self._counter
		del self._references

	def createLesson(self, list=None):
		if list is None:
			list = {"items": [], "tests": []}

		#create widgets
		enterWidget = self._modules.chooseItem(
			set(self._mm.mods("active", type="wordsEnterer"))
		).createWordsEnterer()
		enterWidget.updateList(list)

		teachWidget = self._modules.chooseItem(
			set(self._mm.mods("active", type="wordsTeacher"))
		).createWordsTeacher()
		teachWidget.updateList(list)

		resultsWidget = self._modules.chooseItem(
			set(self._mm.mods("active", type="testsViewer"))
		).createTestsViewer()
		resultsWidget.updateList(list)

		fileTab = self._uiModule.addFileTab(
			_("Word lesson %s") % self._counter,
			enterWidget,
			teachWidget,
			resultsWidget
		)
		self._counter += 1

		lesson = Lesson(self._mm, fileTab, self, list, enterWidget, teachWidget, resultsWidget)
		self._references.add(lesson)
		self.lessonCreated.emit(lesson)
		self.lessonCreationFinished.emit()

		return lesson

	@property
	def _onscreenKeyboard(self):
		keyboards = set(self._mm.mods("active", type="onscreenKeyboard"))
		try:
			keyboard = self._modules.chooseItem(keyboards)
		except IndexError:
			return
		return keyboard.createWidget()

	def loadFromList(self, list, path): #FIXME: change topo lesson so path can be removed
		self.createLesson(list)

def init(moduleManager):
	return WordsLessonModule(moduleManager)
