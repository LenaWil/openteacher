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
	def __init__(self, moduleManager, fileTab, module, list, enterWidget, teachWidget, resultsWidget=None, *args, **kwargs):
		super(Lesson, self).__init__(*args, **kwargs)

		self.resources = {} #To be removed...

		self._mm = moduleManager
		self._modules = set(self._mm.mods("active", type="modules")).pop()

		self.module = module

		self.fileTab = fileTab
		self.fileTab.closeRequested.handle(self.stop)
		self.stopped = self._modules.default(type="event").createEvent()

		self.list = list

		self._enterWidget = enterWidget
		self._teachWidget = teachWidget
		if resultsWidget:
			self._resultsWidget = resultsWidget

		self._teachWidget.lessonDone.connect(self._lessonDone)
		self._teachWidget.listChanged.connect(self._listChanged)

	def _lessonDone(self):
		self.fileTab.currentTab = self._enterWidget
	
	def _listChanged(self, list):
		try:
			self._resultsWidget.updateList(list, "words")
		except AttributeError:
			pass

	def stop(self):
		self.fileTab.close()
		self.stopped.send()

class WordsLessonModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(WordsLessonModule, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		self.type = "lesson"
		self.requires = (
			self._mm.mods(type="ui"),
			self._mm.mods(type="event"),
			self._mm.mods(type="wordsEnterer"),
			self._mm.mods(type="wordsTeacher"),
		)
		self.uses = (
			self._mm.mods(type="translator"),
			self._mm.mods(type="testsViewer"),
		)

	def enable(self):
		self.dataType = "words"

		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self._uiModule = self._modules.default("active", type="ui")

		#Translations
		global _
		global ngettext

		#load translator
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)

		self.name = _("Words Lesson")

		self.lessonCreated = self._modules.default(type="event").createEvent()
		self.lessonCreationFinished = self._modules.default(type="event").createEvent()

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
		del self.name
		del self.lessonCreated
		del self._counter
		del self._references

	def createLesson(self, list=None):
		if list is None:
			list = {"items": [], "tests": []}

		#create widgets
		enterWidget = self._modules.default(
			"active",
			type="wordsEnterer"
		).createWordsEnterer()
		enterWidget.updateList(list)

		teachWidget = self._modules.default(
			"active",
			type="wordsTeacher"
		).createWordsTeacher()
		teachWidget.updateList(list)

		widgets = [
			enterWidget,
			teachWidget,
		]
		try:
			resultsWidget = self._modules.default(
				"active",
				type="testsViewer"
			).createTestsViewer()
		except IndexError:
			pass
		else:
			resultsWidget.updateList(list, "words")
			widgets.append(resultsWidget)

		fileTab = self._uiModule.addFileTab(
			_("Word lesson %s") % self._counter,
			*widgets
		)
		self._counter += 1

		lesson = Lesson(self._mm, fileTab, self, list, *widgets)
		self._references.add(lesson)
		self.lessonCreated.send(lesson)
		self.lessonCreationFinished.send()

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
