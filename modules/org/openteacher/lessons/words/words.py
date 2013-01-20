#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011-2013, Marten de Vries
#	Copyright 2011-2012, Cas Widdershoven
#	Copyright 2011-2012, Milan Boers
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

import weakref

class Lesson(object):
	def __init__(self, moduleManager, fileTab, module, lessonData, enterWidget, teachWidget, resultsWidget=None, *args, **kwargs):
		super(Lesson, self).__init__(*args, **kwargs)

		self.resources = {}

		self._mm = moduleManager
		self._modules = set(self._mm.mods(type="modules")).pop()

		self.module = module

		self.fileTab = fileTab
		self.fileTab.closeRequested.handle(self.stop)
		self.stopped = self._modules.default(type="event").createEvent()

		self.changedEvent = self._modules.default(type="event").createEvent()

		self.list = lessonData["list"]
		if "changed" in lessonData:
			self.changed = lessonData["changed"]
		else:
			self.changed = False
		if "path" in lessonData:
			self.path = lessonData["path"]

		self._enterWidget = enterWidget
		self._teachWidget = teachWidget
		if resultsWidget:
			self._resultsWidget = resultsWidget

		self._enterWidget.updateLesson(self)
		self._teachWidget.updateLesson(self)

		self._teachWidget.lessonDone.connect(self._lessonDone)
		self._teachWidget.listChanged.connect(self._updateResultsWidgetWrapper)

		self.retranslate()

	@property
	def changed(self):
		return self._changed

	@changed.setter
	def changed(self, value):
		self._changed = value
		self._updateTabTitle()
		self._updateResultsWidget()
		self.changedEvent.send()

	def _updateTabTitle(self):
		title = self.list.get("title", "") or _("Unnamed")
		self.fileTab.title = _("Word lesson: %s") % title

	retranslate = _updateTabTitle

	def _lessonDone(self):
		self.fileTab.currentTab = self._enterWidget

	def _updateResultsWidgetWrapper(self, list):
		self._updateResultsWidget()

	def _updateResultsWidget(self):
		try:
			self._resultsWidget.updateList(self.list, "words")
		except AttributeError:
			pass

	def stop(self):
		#close current lesson (if one). Just reuse all the logic.
		self.fileTab.currentTab = self._enterWidget
		self.tabChanged()
		if self.fileTab.currentTab == self._teachWidget:
			#the tab change wasn't allowed.
			return False

		#ask if the user wants to save
		if self.changed:
			lessonDialogsModule = self._modules.default("active", type="lessonDialogs")
			if not lessonDialogsModule.okToClose(parent=self.fileTab.currentTab):
				return False

		#it's ok, just close.
		self.fileTab.close()
		self.stopped.send()
		return True

	def tabChanged(self):
		"""First do checks that apply to all lessons. In case they don't
		   show any problems, the callback with word specific checks is
		   called.

		"""
		#FIXME 3.1: move into separate module since this uses QtGui?
		def callback():
			#words specific checks
			for item in self._enterWidget.lesson.list["items"]:
				if not item.get("questions", []) or not item.get("answers", []):
					QtGui.QMessageBox.critical(
						self._teachWidget,
						_("Empty question or answer"),
						_("Please enter at least one question and one answer for every word.")
					)
					self.fileTab.currentTab = self._enterWidget
					break

		#generic checks
		lessonDialogsModule = self._modules.default("active", type="lessonDialogs")
		lessonDialogsModule.onTabChanged(self.fileTab, self._enterWidget, self._teachWidget, callback)

class WordsLessonModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(WordsLessonModule, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		self.type = "lesson"
		x = 493
		self.priorities = {
			"all": x,
			"selfstudy": x,
			"student@home": x,
			"student@school": x,
			"teacher": x,
			"words-only": x,
			"code-documentation": x,
			"default": -1,
		}
		self.requires = (
			self._mm.mods(type="ui"),
			self._mm.mods(type="event"),
			self._mm.mods(type="wordsEnterer"),
			self._mm.mods(type="wordsTeacher"),
			self._mm.mods(type="lessonDialogs"),
			self._mm.mods(type="buttonRegister"),
		)
		self.uses = (
			self._mm.mods(type="dataTypeIcons"),
			self._mm.mods(type="translator"),
			self._mm.mods(type="testsViewer"),
		)
		self.filesWithTranslations = ("words.py",)

	def enable(self):
		global QtGui
		try:
			from PyQt4 import QtGui
		except ImportError:
			return
		self.dataType = "words"

		self._modules = set(self._mm.mods(type="modules")).pop()
		self._uiModule = self._modules.default("active", type="ui")

		self._lessons = set()

		self._button = self._modules.default("active", type="buttonRegister").registerButton("create")
		self._button.clicked.handle(self.createLesson)
		try:
			iconPath = self._modules.default("active", type="dataTypeIcons").findIcon(self.dataType)
		except (IndexError, KeyError):
			pass
		else:
			self._button.changeIcon.send(iconPath)
		#reasonable priority
		self._button.changePriority.send(self.priorities["all"])

		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		self.lessonCreated = self._modules.default(type="event").createEvent()
		self.lessonCreationFinished = self._modules.default(type="event").createEvent()

		self.active = True

	def _retranslate(self):
		#Translations
		global _
		global ngettext

		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)
		
		self._button.changeText.send(_("Create words lesson"))
		for ref in self._lessons:
			lesson = ref()
			if lesson:
				lesson.retranslate()

	def disable(self):
		self.active = False

		self._modules.default("active", type="buttonRegister").unregisterButton(self._button)

		del self.dataType
		del self._modules
		del self._uiModule
		del self._lessons
		del self.lessonCreated
		del self._button
		del self.lessonCreationFinished

	def createLesson(self, lessonData=None):
		if not lessonData:
			lessonData = {
				"list": {},
				"resources": {},
			}

		#create widgets
		self.enterWidget = self._modules.default(
			"active",
			type="wordsEnterer"
		).createWordsEnterer()

		self.teachWidget = self._modules.default(
			"active",
			type="wordsTeacher"
		).createWordsTeacher()

		widgets = [
			self.enterWidget,
			self.teachWidget,
		]
		try:
			resultsWidget = self._modules.default(
				"active",
				type="testsViewer"
			).createTestsViewer()
		except IndexError:
			pass
		else:
			resultsWidget.updateList(lessonData["list"], "words")
			widgets.append(resultsWidget)

		self.fileTab = self._uiModule.addFileTab(*widgets)

		lesson = Lesson(self._mm, self.fileTab, self, lessonData, *widgets)
		self.fileTab.tabChanged.handle(lesson.tabChanged)
		self._lessons.add(weakref.ref(lesson))

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

	def loadFromLesson(self, lesson):
		self.createLesson(lesson)

def init(moduleManager):
	return WordsLessonModule(moduleManager)
