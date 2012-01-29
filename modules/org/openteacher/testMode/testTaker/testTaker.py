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

from PyQt4 import QtGui
from PyQt4 import QtCore
import uuid
import urllib2

try:
	import json
except:
	import simplejson as json

class TestChooser(QtGui.QWidget):
	# Parameter: the chosen test (tests/<id>)
	testChosen = QtCore.pyqtSignal(dict)
	def __init__(self, testSelecter, *args, **kwargs):
		super(TestChooser, self).__init__(*args, **kwargs)
		
		self.testSelecter = testSelecter
		
		layout = QtGui.QVBoxLayout()
		
		comm = QtGui.QLabel("Select the test you want to take")
		layout.addWidget(comm)
		
		layout.addWidget(testSelecter)
		
		button = QtGui.QPushButton("Take test")
		button.clicked.connect(lambda: self.testChosen.emit(self.testSelecter.getCurrentTest()))
		layout.addWidget(button)
		
		self.setLayout(layout)

class TestModeTestTaker(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TestModeTestTaker, self).__init__(*args, **kwargs)
		self._mm = moduleManager
		
		self.type = "testModeTestTaker"
		
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.requires = (
			self._mm.mods(type="event"),
			self._mm.mods(type="wordsTestTeacher"),
			self._mm.mods(type="testModeConnection"),
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
		
		# FIXME: make menu option
		module = self._modules.default("active", type="ui")
		event = module.addLessonCreateButton(_("Take test"))
		event.handle(self.showTestTaker)
		
		self.active = True
	
	def showTestTaker(self):
		# First, login
		self.connection = self._modules.default("active", type="testModeConnection").getConnection()
		self.connection.loggedIn.handle(self.showTestTaker_)
		self.loginid = uuid.uuid4()
		self.connection.login(self.loginid)
	
	def showTestTaker_(self, loginid):
		# Check if this is indeed from the request I sent out
		if loginid == self.loginid:
			uiModule = self._modules.default("active", type="ui")
			
			#teachWidget = self._modules.default("active", type="wordsTestTeacher").createWordsTeacher()
			testSelecter = self._modules.default("active", type="testModeTestSelecter").getTestSelecter(True)
			testChooser = TestChooser(testSelecter)
			testChooser.testChosen.connect(self.takeTest)
			
			self.testChooseTab = uiModule.addCustomTab(_("Choose test"), testChooser)
			self.testChooseTab.closeRequested.handle(self.testChooseTab.close)
	
	"""
	testInfo: dictionary with info from /tests/<id>
	"""
	def takeTest(self, testInfo):
		# Close the test chooser.
		self.testChooseTab.close()
		
		self.teachWidget = self._modules.default("active", type="wordsTestTeacher").createWordsTeacher()
		self.teachWidget.updateList(testInfo["list"])
		
		uiModule = self._modules.default("active", type="ui")
		
		self.teachTab = uiModule.addCustomTab(_("Taking test"), self.teachWidget)
		self.teachTab.closeRequested.handle(self.teachTab.close)
		
		self.teachWidget.lessonDone.connect(lambda: self.handIn(testInfo["answers"]))
	
	# Hand in the test
	def handIn(self, answersUrl):
		answeredList = self.teachWidget.getAnsweredList()
		dialogShower = self._modules.default("active", type="dialogShower").getDialogShower()
		
		r = self.connection.post(answersUrl, {"list" : json.dumps(answeredList)})
		
		# Check if there was an error.
		if type(r) == urllib2.HTTPError:
			# Show error message
			dialogShower.showError(self.teachTab, "An error occured. The server could not be reached. Check your network connection.")
		else:
			# Show thank you message
			dialogShower.showBigMessage("Your answers have successfully been handed in!")
			# Close the teach widget
			self.teachTab.close()
	
	def disable(self):
		self.active = False

def init(moduleManager):
	return TestModeTestTaker(moduleManager)