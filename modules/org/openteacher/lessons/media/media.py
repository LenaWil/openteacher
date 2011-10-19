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

import datetime

"""
The module
"""
class MediaLessonModule(object):
	def __init__(self, mm,*args,**kwargs):
		super(MediaLessonModule, self).__init__(*args, **kwargs)
		
		global base
		base = self
		self._mm = mm
		self.counter = 1

		self.type = "lesson"
		self.dataType = "media"
		
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.requires = (
			self._mm.mods(type="event"),
			self._mm.mods(type="mediaEnterer"),
			self._mm.mods(type="mediaTeacher"),
			self._mm.mods(type="testsViewer"),
		)

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()

		#setup translation
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

		self.name = _("Media Lesson")

		self.lessonCreated = self._modules.default(type="event").createEvent()
		self.lessonCreationFinished = self._modules.default(type="event").createEvent()
		
		module = self._modules.default("active", type="ui")
		event = module.addLessonCreateButton(_("Create media lesson"))
		event.handle(self.createLesson)
		
		self.active = True

	def disable(self):
		self.active = False

		del self.dataType
		del self.name
		del self.lessonCreated
		del self.lessonCreationFinished
	
	def createLesson(self):		
		lessons = set()
		
		module = self._modules.default("active", type="ui")
		
		self.enterWidget = self._modules.default("active", type="mediaEnterer").createMediaEnterer()
		self.teachWidget = self._modules.default("active", type="mediaTeacher").createMediaTeacher()
		self.resultsWidget = self._modules.default("active", type="testsViewer").createTestsViewer()
		
		self.fileTab = module.addFileTab(
			_("Media lesson %s") % self.counter,
			self.enterWidget,
			self.teachWidget,
			self.resultsWidget
		)
		
		lesson = Lesson(self, self.fileTab, self.enterWidget, self.teachWidget, self.resultsWidget)
		self.lessonCreated.send(lesson)
		
		lessons.add(lesson)
		
		self.counter += 1
		self.lessonCreationFinished.send()
		return lessons
	
	def loadFromList(self, list, path):
		for lesson in self.createLesson():
			# Load the list
			self.enterWidget.itemList = list
			# Update the widgets
			self.enterWidget.updateWidgets()
			# Update the results widget
			self.resultsWidget.updateList(list, "media")

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
		self.list = self.enterWidget.itemList
		self.resources = {}
		self.dataType = "media"
		
		self.fileTab.closeRequested.handle(self.stop)
		self.fileTab.tabChanged.handle(self.tabChanged)
		self.teachWidget.lessonDone.connect(self.toEnterTab)
		self.teachWidget.listChanged.connect(self.teachListChanged)
	
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
	
	def toEnterTab(self):
		self.fileTab.currentTab = self.enterWidget
	
	def tabChanged(self):
		if self.fileTab.currentTab == self.enterWidget:
			if self.teachWidget.inLesson:
				warningD = QtGui.QMessageBox()
				warningD.setIcon(QtGui.QMessageBox.Warning)
				warningD.setWindowTitle(_("Warning"))
				warningD.setStandardButtons(QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
				warningD.setText(_("Are you sure you want to go back to the enter tab? This will end your lesson!"))
				feedback = warningD.exec_()
				if feedback == QtGui.QMessageBox.Ok:
					self.teachWidget.stopLesson()
				else:
					self.fileTab.currentTab = self.teachWidget
		elif self.fileTab.currentTab == self.teachWidget:
			#stop media playing in the enter widget
			self.enterWidget.mediaDisplay.clear()
			if len(self.enterWidget.itemList["items"]) == 0:
				QtGui.QMessageBox.critical(self, _("Not enough items"), _("You need to add items to your test first"))
				self.fileTab.currentTab = self.enterWidget
			elif not self.teachWidget.inLesson:
				self.teachWidget.initiateLesson(self.enterWidget.itemList)

def init(moduleManager):
	return MediaLessonModule(moduleManager)
