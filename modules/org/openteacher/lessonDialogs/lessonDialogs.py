#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2012, Milan Boers
#	Copyright 2012, Marten de Vries
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

from PyQt4 import QtCore, QtGui

#FIXME: translate module (& retranslate)!
class LessonDialogsModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(LessonDialogsModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager
		
		self.type = "lessonDialogs"
		
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.requires = (
			self._mm.mods(type="ui"),
		)
	
	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		self.active = True
	
	def disable(self):
		self.active = False
		
		del self._modules
	
	def onTabChanged(self, fileTab, enterWidget, teachWidget, func=None):
		"""Does some checks and then decides if the tab may be left in
		   its new position, or if it's changed back. (This function
		   handles the changing.)

		"""
		if fileTab.currentTab == enterWidget:
			if teachWidget.inLesson:
				warningD = QtGui.QMessageBox()
				warningD.setIcon(QtGui.QMessageBox.Warning)
				warningD.setWindowTitle("Warning")
				warningD.setStandardButtons(QtGui.QMessageBox.Cancel | QtGui.QMessageBox.Ok)
				warningD.setText("Are you sure you want to go back to the teach tab? This will end your lesson!")
				feedback = warningD.exec_()
				if feedback == QtGui.QMessageBox.Ok:
					teachWidget.stopLesson(showResults=False)
				else:
					fileTab.currentTab = teachWidget
		elif fileTab.currentTab == teachWidget:
			# If there are no words
			if not "items" in enterWidget.lesson.list or len(enterWidget.lesson.list["items"]) == 0:
				QtGui.QMessageBox.critical(teachWidget, "Not enough items", "You need to add items to your test first")
				fileTab.currentTab = enterWidget
			elif func is not None:
				#no problems doing the checks, so the lesson can start.
				#call the callback.
				func()

def init(moduleManager):
	return LessonDialogsModule(moduleManager)
