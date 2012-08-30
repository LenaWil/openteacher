#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011-2012, Milan Boers
#	Copyright 2011-2012, Marten de Vries
#	Copyright 2011-2012, Cas Widdershoven
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

import os, weakref

#FIXME (>3.1): give media lessons a title

class MediaLessonModule(object):
	"""The module"""

	def __init__(self, mm,*args,**kwargs):
		super(MediaLessonModule, self).__init__(*args, **kwargs)
		
		self._mm = mm
		self.counter = 1

		self.type = "lesson"
		self.priorities = {
			"student@home": 667,
			"student@school": 667,
			"teacher": 667,
			"wordsonly": -1,
			"selfstudy": 667,
			"testsuite": 667,
			"codedocumentation": 667,
			"all": 667,
		}
		self.dataType = "media"

		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.requires = (
			self._mm.mods(type="event"),
			self._mm.mods(type="ui"),
			self._mm.mods(type="buttonRegister"),
			self._mm.mods(type="mediaEnterer"),
			self._mm.mods(type="mediaTeacher"),
			self._mm.mods(type="testsViewer"),
		)
		self.filesWithTranslations = ("media.py",)

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		
		self._lessons = set()

		module = self._modules.default("active", type="buttonRegister")
		self._button = module.registerButton("create")
		self._button.clicked.handle(self.createLesson)
		#reasonable priority
		self._button.changePriority.send(self.priorities["all"])

		self.lessonCreated = self._modules.default(type="event").createEvent()
		self.lessonCreationFinished = self._modules.default(type="event").createEvent()

		#setup translation
		global _
		global ngettext

		#load translator	
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()
		
		self.active = True

	def disable(self):
		self.active = False

		del self._lessons
		del self._button
		del self.dataType
		del self.lessonCreated
		del self.lessonCreationFinished
	
	def createLesson(self):		
		module = self._modules.default("active", type="ui")

		self.enterWidget = self._modules.default("active", type="mediaEnterer").createMediaEnterer()
		self.teachWidget = self._modules.default("active", type="mediaTeacher").createMediaTeacher()
		self.resultsWidget = self._modules.default("active", type="testsViewer").createTestsViewer()

		self.fileTab = module.addFileTab(
			self.enterWidget,
			self.teachWidget,
			self.resultsWidget
		)

		lesson = Lesson(self._modules, self.fileTab, self.enterWidget, self.teachWidget, self.resultsWidget, self.counter)
		self._lessons.add(weakref.ref(lesson))
		self.lessonCreated.send(lesson)

		#so it can set the changed property
		self.enterWidget.lesson = lesson

		self.counter += 1
		self.lessonCreationFinished.send()
		return lesson

	def loadFromLesson(self, lessonl):
		# Replace filenames with their real (temporary) files
		for item in lessonl["list"]["items"]:
			try:
				item["filename"] = lessonl["resources"][item["filename"]]
			except KeyError:
				#Remote-data items
				pass

		lesson = self.createLesson()
		# Load the list
		self.enterWidget.list = lessonl["list"]
		# Update the widgets
		self.enterWidget.updateWidgets()
		# Update the results widget
		self.resultsWidget.updateList(lessonl["list"], "media")

		if "path" in lessonl:
			lesson.path = lessonl["path"]
		if "changed" in lessonl:
			lesson.changed = lessonl["changed"]
		
		# Update title
		self.fileTab.title = _("Media lesson: %s") % os.path.basename(lesson.path)
		
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
			
		self._button.changeText.send(_("Create media lesson"))
		for ref in self._lessons:
			lesson = ref()
			if lesson:
				lesson.retranslate()

class Lesson(object):
	"""Lesson object (that means: this teachwidget+enterwidget)"""

	def __init__(self, modules, fileTab, enterWidget, teachWidget, resultsWidget, counter, *args, **kwargs):
		super(Lesson, self).__init__(*args, **kwargs)
		
		self._modules = modules
		
		self.enterWidget = enterWidget
		self.teachWidget = teachWidget
		self.resultsWidget = resultsWidget
		self.fileTab = fileTab
		self.counter = counter
		
		self.stopped = self._modules.default(type="event").createEvent()
		
		self.module = self
		self.resources = {}
		self.dataType = "media"
		
		self.fileTab.closeRequested.handle(self.stop)
		self.fileTab.tabChanged.handle(self.tabChanged)
		self.teachWidget.lessonDone.connect(self.toEnterTab)
		self.teachWidget.listChanged.connect(self.teachListChanged)

		self.changedEvent = self._modules.default(type="event").createEvent()

		self.retranslate()

	def retranslate(self):
		try:
			self.fileTab.title = _("Media lesson: %s") % os.path.basename(self.path)
		except AttributeError:
			self.fileTab.title = _("Media lesson: %s") % self.counter

	@property
	def changed(self):
		return self._changed

	@changed.setter
	def changed(self, value):
		self._changed = value
		self.changedEvent.send()

	@changed.deleter
	def changed(self):
		del self._changed

	@property
	def list(self):
		return self.enterWidget.list
	
	def stop(self):
		# Stop lesson if in one
		if self.teachWidget.inLesson:
			self.teachWidget.stopLesson()
		self.fileTab.close()
		# Stop media playing
		self.enterWidget.mediaDisplay.stop()
		self.teachWidget.mediaDisplay.stop()
		self.stopped.send()
	
	def teachListChanged(self, list):
		# Update results widget
		self.resultsWidget.updateList(list, "media")
		self.changed = True
	
	def toEnterTab(self):
		self.fileTab.currentTab = self.enterWidget
	
	def tabChanged(self):
		lessonDialogsModule = self._modules.default("active", type="lessonDialogs")
		lessonDialogsModule.onTabChanged(self.fileTab, self.enterWidget, self.teachWidget, lambda: self.teachWidget.initiateLesson(self.enterWidget.list))

def init(moduleManager):
	return MediaLessonModule(moduleManager)
