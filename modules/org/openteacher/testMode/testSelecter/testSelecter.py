#! /usr/bin/env python
# -*- coding: utf-8 -*-

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

from PyQt4 import QtCore
from PyQt4 import QtGui
import uuid
import os

try:
	import json
except:
	import simplejson as json

class TestSelecter(QtGui.QListWidget):
	# Parameter: The current test (tests/<id>)
	testChosen = QtCore.pyqtSignal(dict)
	def __init__(self, connection, filter=False, *args, **kwargs):
		super(TestSelecter, self).__init__(*args, **kwargs)
		
		self.connection = connection
		# Are tests you already handed in answers for filtered out?
		self.filter = filter
		self.currentRowChanged.connect(self._currentRowChanged)
		
		self._addTests()
	
	def _addTests(self):
		# Get all tests
		self.testsInfo = self.connection.get("tests")
		self.testsInfos = []
		
		for test in self.testsInfo:
			if self.filter:
				# Get urls of all answers for this test
				answersUrls = self.connection.get(test["url"] + "/answers")
				# Get userids of all answers for this test
				answersIds = map(os.path.basename, answersUrls)
				
				if str(self.connection.userId) in answersIds:
					break
			
			# Get name of this test
			testInfo = self.connection.get(test["url"])
			testInfo["list"] = json.loads(testInfo["list"])
			self.testsInfos.append(testInfo)
			
			if "title" in testInfo["list"]:
				self.addItem(testInfo["list"]["title"])
			else:
				self.addItem("Unnamed")
	
	def _currentRowChanged(self, index):
		self.testChosen.emit(self.testsInfos[index])
	
	def getCurrentTest(self):
		return self.testsInfos[self.currentRow()]

class TestModeTestSelecterModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TestModeTestSelecterModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager
		#FIXME: translate + retranslate!
		self.type = "testModeTestSelecter"
		self.priorities = {
			"student@home": -1,
			"student@school": 532,
			"teacher": 532,
			"wordsonly": -1,
			"selfstudy": -1,
			"testsuite": 532,
			"codedocumentation": 532,
			"all": 532,
		}
		
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.requires = (
			self._mm.mods(type="ui"),
			self._mm.mods(type="event"),
			self._mm.mods(type="testModeConnection"),
		)

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		
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
		
		self.connection = self._modules.default("active", type="testModeConnection").getConnection()
		
		self.active = True
	
	def getTestSelecter(self, filter=False):
		return TestSelecter(self.connection, filter)

	def disable(self):
		self.active = False

def init(moduleManager):
	return TestModeTestSelecterModule(moduleManager)
