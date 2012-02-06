#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011-2012, Milan Boers
#	Copyright 2011-2012, Marten de Vries
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

import os
import tempfile
import atexit

class TeachTopoLessonModule(object):
	"""The module"""

	def __init__(self, moduleManager, *args, **kwargs):
		super(TeachTopoLessonModule, self).__init__(*args, **kwargs)
		
		self._mm = moduleManager
		self.counter = 1
		
		self.type = "lesson"
		self.priorities = {
			"student@home": 580,
			"student@school": 580,
			"teacher": 580,
			"wordsonly": -1,
			"selfstudy": 580,
			"testsuite": 580,
			"codedocumentation": 580,
			"all": 580,
		}
		
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.requires = (
			self._mm.mods(type="event"),
			self._mm.mods(type="ui"),
			self._mm.mods(type="topoTeacher"),
			self._mm.mods(type="topoEnterer"),
			self._mm.mods(type="testsViewer"),
		)

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()

		#setup translation
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

		# Add the button to start
		module = self._modules.default("active", type="ui")
		self._button = module.addLessonCreateButton()
		self._button.clicked.handle(self.createLesson)
		self._button.text = _("Create topography lesson") #FIXME: retranslate!
		
		# Data type
		self.dataType = "topo"
		
		# Signals
		self.lessonCreated = self._modules.default(type="event").createEvent()
		self.lessonCreationFinished = self._modules.default(type="event").createEvent()
		
		self.active = True

	def disable(self):
		self.active = False

		del self._button
		del self.dataType
		del self.lessonCreated
		del self.lessonCreationFinished
	
	def createLesson(self):
		lessons = set()
		
		module = self._modules.default("active", type="ui")
		
		enterWidget = self._modules.default("active", type="topoEnterer").createTopoEnterer()
		teachWidget = self._modules.default("active", type="topoTeacher").createTopoTeacher()
		resultsWidget = self._modules.default("active", type="testsViewer").createTestsViewer()
		
		fileTab = module.addFileTab(
			enterWidget,
			teachWidget,
			resultsWidget
		)
		
		lesson = Lesson(self._modules, fileTab, enterWidget, teachWidget, resultsWidget, self.counter)
		self.lessonCreated.send(lesson)
		
		lessons.add(lesson)
		
		self.counter += 1
		self.lessonCreationFinished.send()
		return lessons
	
	def loadFromLesson(self, lessonl, path):
		for lesson in self.createLesson():
			lesson.enterWidget.mapChooser.setCurrentIndex(0)
			
			lesson.enterWidget.mapChooser.insertItem(0, os.path.basename(path), unicode({'mapPath': lessonl["resources"]["mapPath"], 'knownPlaces': ''}))
			lesson.enterWidget.mapChooser.setCurrentIndex(0)
			
			# Load the list
			lesson.enterWidget.list = lessonl["list"]
			# Update the widgets
			lesson.enterWidget.updateWidgets()
			# Update results widget
			lesson.resultsWidget.updateList(lessonl["list"], "topo")

class Lesson(object):
	"""Lesson object (that means: this techwidget+enterwidget)"""

	def __init__(self, modules, fileTab, enterWidget, teachWidget, resultsWidget, counter, *args, **kwargs):
		super(Lesson, self).__init__(*args, **kwargs)
		
		self._modules = modules
		self._tempFiles = set()
		atexit.register(self._removeTempFiles)

		self.enterWidget = enterWidget
		self.teachWidget = teachWidget
		self.resultsWidget = resultsWidget

		self.fileTab = fileTab
		self.fileTab.title = ("Topo lesson %s") % counter #FIXME: retranslate

		self.stopped = self._modules.default(type="event").createEvent()
		
		self.module = self
		self.dataType = "topo"
		
		fileTab.closeRequested.handle(self.stop)
		fileTab.tabChanged.handle(self.tabChanged)
		self.teachWidget.lessonDone.connect(self.toEnterTab)
		self.teachWidget.listChanged.connect(self.teachListChanged)
	
	@property
	def list(self):
		return self.enterWidget.list
	
	def stop(self):
		# Stop lesson if in one
		if self.teachWidget.inLesson:
			self.teachWidget.stopLesson()
		self.fileTab.close()
		self.stopped.send()
	
	def toEnterTab(self):
		self.fileTab.currentTab = self.enterWidget
	
	def teachListChanged(self, list):
		self.resultsWidget.updateList(list, "topo")
	
	def tabChanged(self):
		lessonDialogsModule = self._modules.default("active", type="lessonDialogs")
		lessonDialogsModule.onTabChanged(self.fileTab, self.enterWidget, self.teachWidget, lambda: self.teachWidget.initiateLesson(self.enterWidget.list, self.enterWidget.mapChooser.currentMap["mapPath"]))

	def _removeTempFiles(self):
		for file in self._tempFiles:
			os.remove(file)

	@property
	def resources(self):
		screenshotPath = tempfile.mkstemp()[1]
		self._tempFiles.add(screenshotPath)

		screenshot = self.enterWidget.enterMap.getScreenshot()
		screenshot.save(screenshotPath, "PNG")

		return {
			"mapPath": self.enterWidget.mapChooser.currentMap["mapPath"],
			"mapScreenshot": screenshotPath,
		}

def init(moduleManager):
	return TeachTopoLessonModule(moduleManager)
