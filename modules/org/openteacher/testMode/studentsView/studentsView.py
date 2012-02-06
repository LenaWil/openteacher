#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011-2012, Milan Boers
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

from PyQt4 import QtGui

import os

class StudentsView(QtGui.QTreeWidget):
	def __init__(self, connection, *args, **kwargs):
		super(StudentsView, self).__init__(*args, **kwargs)
		
		self.connection = connection
		self.header().hide();
		
		self._addStudents()
	
	def _addStudents(self):
		# Keep a dictionary of name to url of student so we can call the url from the name later
		self.nameToUrl = dict()
		
		# Get list of groups
		groupList = self.connection.get("groups")
		for group in groupList:
			groupInfo = self.connection.get(group["url"])
			
			# Get list of members
			userIds = map(os.path.basename, groupInfo["members"])
			
			userWidgets = []
			
			for userId in userIds:
				userInfo = self.connection.get("users/" + userId)
				if "role" in userInfo and userInfo["role"] == "student":
					# This is a student. Add the student to the list
					item = QtGui.QTreeWidgetItem()
					item.setText(0, userInfo["username"])
					userWidgets.append(item)
					
					# Also add this name and the id to a list so we know which id belongs to this student
					self.nameToUrl[userInfo["username"]] = userInfo["url"]
			
			item = QtGui.QTreeWidgetItem()
			item.setText(0, groupInfo["name"])
			item.addChildren(userWidgets)
			self.addTopLevelItem(item)
		
		# Get list of individual users
		userList = self.connection.get("users")
		
		for user in userList:
			userInfo = self.connection.get(user["url"])
			if "role" in userInfo and userInfo["role"] == "student":
				# This is a student. Add the student to the list
				item = QtGui.QTreeWidgetItem()
				item.setText(0, userInfo["username"])
				self.addTopLevelItem(item)
				
				# Also add this name and the id to a list so we know which id belongs to this student
				self.nameToUrl[userInfo["username"]] = userInfo["url"]
	
	def getCurrentStudents(self):
		# Check if selected item is a group
		if self.currentItem().childCount() != 0:
			# Return list of all items
			feedback = []
			for i in xrange(self.currentItem().childCount()):
				text = self.connection.get(self.nameToUrl[unicode(self.currentItem().child(i).text(0))])
				feedback.append(text)
			return feedback
		else:
			return self.connection.get(self.nameToUrl[unicode(self.currentItem().text(0))])

class TestModeStudentsView(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TestModeStudentsView, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "testModeStudentsView"
		self.priorities = {
			"student@home": -1,
			"student@school": -1,
			"teacher": 546,
			"wordsonly": -1,
			"selfstudy": -1,
			"testsuite": 546,
			"codedocumentation": 546,
			"all": 546,
		}

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

		del self._modules
	
	def getStudentsView(self):
		connection = self._modules.default("active", type="testModeConnection").getConnection()
		return StudentsView(connection)

def init(moduleManager):
	return TestModeStudentsView(moduleManager)
