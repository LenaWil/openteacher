#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2012, Milan Boers
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

class LessonDialogsModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(LessonDialogsModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager
		
		self.type = "lessonDialogs"
		
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.requires = ()
	
	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self.active = True
	
	def disable(self):
		self.active = False
		
		del self._modules
	
	def onTabChanged(self, fileTab, enterWidget, teachWidget, func=None):
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
			if len(enterWidget.list["items"]) == 0:
				QtGui.QMessageBox.critical(teachWidget, "Not enough items", "You need to add items to your test first")
				fileTab.currentTab = enterWidget
			elif func != None:
				func()

def init(moduleManager):
	return LessonDialogsModule(moduleManager)