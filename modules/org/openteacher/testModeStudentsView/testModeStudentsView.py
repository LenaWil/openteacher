#! /usr/bin/env python
# -*- coding: utf-8 -*-

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

from PyQt4 import QtGui

class StudentsView(QtGui.QTreeWidget):
	def __init__(self, connectionModule, *args, **kwargs):
		super(StudentsView, self).__init__(*args, **kwargs)
		
		self.connectionModule = connectionModule
		
		self._addStudents()
	
	def _addStudents(self):
		# Get list of users
		userList = self.connectionModule.get("users")
		
		# Keep a dictionary of name to url of student so we can call the url from the name later
		self.nameToUrl = dict()
		
		for user in userList:
			userInfo = self.connectionModule.get(user["url"])
			print userInfo
			if "role" in userInfo and userInfo["role"] == "student":
				# This is a student. Add the student to the list
				item = QtGui.QTreeWidgetItem()
				item.setText(0, userInfo["username"])
				self.addTopLevelItem(item)
				
				# Also add this name and the id to a list so we know which id belongs to this student
				self.nameToUrl[userInfo["username"]] = userInfo["url"]
	
	def getCurrentStudent(self):
		return self.connectionModule.get(self.nameToUrl[unicode(self.currentItem().text(0))])

class TestModeStudentsView(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TestModeStudentsView, self).__init__(*args, **kwargs)
		self._mm = moduleManager
		
		self.type = "testModeStudentsView"
		
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.requires = (
			self._mm.mods(type="event"),
			self._mm.mods(type="testModeConnection"),
		)

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		
		self.active = True

	def disable(self):
		self.active = False
	
	def getStudentsView(self):
		connectionModule = self._modules.default("active", type="testModeConnection")
		return StudentsView(connectionModule)

def init(moduleManager):
	return TestModeStudentsView(moduleManager)