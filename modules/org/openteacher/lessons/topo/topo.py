#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Milan Boers
#	Copyright 2011, Marten de Vries
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

from PyQt4 import QtGui

import os

"""
The module
"""
class TeachTopoLessonModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TeachTopoLessonModule, self).__init__(*args, **kwargs)
		
		global base
		base = self
		
		self._mm = moduleManager
		self.counter = 1
		
		self.type = "lesson"
		
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.requires = (
			self._mm.mods(type="event"),
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
		
		self.name = _("Topo Lesson")
	
		# Data type
		self.dataType = "topo"
		
		# Signals
		self.lessonCreated = self._modules.default(type="event").createEvent()
		self.lessonCreationFinished = self._modules.default(type="event").createEvent()
		
		# Add the button to start
		module = self._modules.default("active", type="ui")
		event = module.addLessonCreateButton(_("Create topography lesson"))
		event.handle(self.createLesson)
		
		self.active = True

	def disable(self):
		self.active = False

		del self.name
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
			_("Topo lesson %s") % self.counter,
			enterWidget,
			teachWidget,
			resultsWidget
		)
		
		lesson = Lesson(self, fileTab, enterWidget, teachWidget, resultsWidget)
		self.lessonCreated.send(lesson)
		
		lessons.add(lesson)
		
		self.counter += 1
		self.lessonCreationFinished.send()
		return lessons
	
	def loadFromList(self, list, path):
		for lesson in self.createLesson():
			lesson.enterWidget.mapChooser.setCurrentIndex(0)
			lesson.enterWidget.mapChooser.insertItem(0, os.path.basename(path), unicode({'mapPath': list["resources"]["mapPath"], 'knownPlaces': ''}))
			lesson.enterWidget.mapChooser.setCurrentIndex(0)
			
			# Load the list
			lesson.enterWidget.places = list["list"]
			# Update the widgets
			lesson.enterWidget.updateWidgets()
			# Update results widget
			lesson.resultsWidget.updateList(list["list"], "topo")

"""
Lesson object (that means: this techwidget+enterwidget)
"""
class Lesson(object):
	def __init__(self, moduleManager, fileTab, enterWidget, teachWidget, resultsWidget, *args, **kwargs):
		super(Lesson, self).__init__(*args, **kwargs)
		
		self.enterWidget = enterWidget
		self.teachWidget = teachWidget
		self.resultsWidget = resultsWidget
		
		self.fileTab = fileTab
		
		self.stopped = base._modules.default(type="event").createEvent()
		
		self.module = self
		self.dataType = "topo"
		self.list = self.enterWidget.places
		
		fileTab.closeRequested.handle(self.stop)
		fileTab.tabChanged.handle(self.tabChanged)
		self.teachWidget.lessonDone.connect(self.toEnterTab)
		self.teachWidget.listChanged.connect(self.teachListChanged)
	
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
		if self.fileTab.currentTab == self.enterWidget:
			if self.teachWidget.inLesson:
				warningD = QtGui.QMessageBox()
				warningD.setIcon(QtGui.QMessageBox.Warning)
				warningD.setWindowTitle(_("Warning"))
				warningD.setStandardButtons(QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
				warningD.setText(_("Are you sure you want to go back to the teach tab? This will end your lesson!"))
				feedback = warningD.exec_()
				if feedback == QtGui.QMessageBox.Ok:
					self.teachWidget.stopLesson()
				else:
					self.fileTab.currentTab = self.teachWidget
		elif self.fileTab.currentTab == self.teachWidget:
			# If there are no words
			if len(self.enterWidget.places["items"]) == 0:
				QtGui.QMessageBox.critical(self.teachWidget, _("Not enough items"), _("You need to add items to your test first"))
				self.fileTab.currentTab = self.enterWidget
			# If not in a lesson (so it doesn't start a lesson if you go back from a mistakingly click on the Enter tab)
			elif not self.teachWidget.inLesson:
				self.teachWidget.initiateLesson(self.enterWidget.places, self.enterWidget.mapChooser.currentMap["mapPath"])
	
	@property
	def resources(self):
		return {
			"mapPath": self.enterWidget.mapChooser.currentMap["mapPath"],
			"mapScreenshot": self.enterWidget.enterMap.getScreenshot()
		}

def init(moduleManager):
	return TeachTopoLessonModule(moduleManager)
