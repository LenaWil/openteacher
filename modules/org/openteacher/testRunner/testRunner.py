#! /usr/bin/env python
# -*- coding: utf-8 -*-

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

import unittest

class TestRunnerModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TestRunnerModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "testRunner"
		self.priorities = {
			"student@home": -1,
			"student@school": -1,
			"teacher": -1,
			"wordsonly": -1,
			"selfstudy": -1,
			"testsuite": 0,
			"codedocumentation": -1,
			"all": -1,
			"update-translations": -1,
			"testserver": -1,
		}
		self.requires = (
			self._mm.mods(type="execute"),
		)

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		self._execute = self._modules.default(type="execute")
		self._execute.startRunning.handle(self._run)

	def disable(self):
		self._execute.startRunning.unhandle(self._run)
		del self._execute
		del self._modules

	def _run(self):
		testSuite = unittest.TestSuite()
		for module in self._mm.mods(type="test"):
			module.enable()
			newTests = unittest.TestLoader().loadTestsFromTestCase(module.TestCase)
			testSuite.addTests(newTests)
			module.disable()
		unittest.TextTestRunner().run(testSuite)

def init(moduleManager):
	return TestRunnerModule(moduleManager)
