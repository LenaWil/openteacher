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
from PyQt4 import QtCore

import os
import uuid

try:
	import json
except:
	import simplejson as json

class TestModeUploaderModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TestModeUploaderModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager
		
		self.type = "testModeUploader"
		self.priorities = {
			"student@home": -1,
			"student@school": 560,
			"teacher": -1,
			"wordsonly": -1,
			"selfstudy": -1,
			"testsuite": 560,
			"codedocumentation": 560,
			"all": 560,
		}
		
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.requires = (
			self._mm.mods(type="event"),
			self._mm.mods(type="ui"),
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
		
		self.active = True

	def disable(self):
		self.active = False
	
	def upload(self):
		# First, login
		self.connection = self._modules.default("active", type="testModeConnection").getConnection()
		self.connection.loggedIn.handle(self.upload_)
		
		self.loginid = uuid.uuid4()
		self.connection.login(self.loginid)
	
	def upload_(self, loginid):
		# Check if this is indeed from the request I sent out
		if loginid == self.loginid:
			# Get filename
			uiModule = self._modules.default("active", type="ui")
			result = uiModule.getLoadPath(os.path.expanduser("~"), ["otwd"])
			
			# Load the list
			loadModule = self._modules.default("active", type="load", loads={"otwd": ["words"]})
			list = loadModule.load(result)
			
			# Save it to a json string
			#FIXME: serialize is private now, and that's good so let's update this.
			saveModule = self._modules.default("active", type="save", saves={"words": ["otwd"]})
			listJson = json.dumps(
				list, #the list to save
				separators=(',',':'), #compact encoding
				default=saveModule.serialize
			)
			
			postData = {"list": listJson}
			fb = self.connection.post("tests",postData)
			print fb

def init(moduleManager):
	return TestModeUploaderModule(moduleManager)
