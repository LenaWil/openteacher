#! /usr/bin/env python
# -*- coding: utf-8 -*-

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

import unittest
import glob
import os

class TestCase(unittest.TestCase):
	def setUp(self):
		self._results = []

		files = glob.glob(self._mm.resourcePath("testFiles") + "/*")
		for file in files:
			mimetype = os.path.basename(file).split(".")[0].replace("_", "/")
			loadMods = set(self._mm.mods("active", type="load", mimetype=mimetype))
			self.assertTrue(loadMods, msg="No loader fount for mimetype: %s" % mimetype)
			for mod in loadMods:
				self._results.append(mod.load(file))

	def testHasItems(self):
		for data in self._results:
			self.assertIsNotNone(data["list"]["items"])

	def testItemHasUniqueId(self):
		for data in self._results:
			ids = set()
			for item in data["list"]["items"]:
				self.assertNotIn(item["id"], ids)
				ids.add(item["id"])

class TestModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TestModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "test"
		self.requires = (
			self._mm.mods(type="load"),
		)

	def enable(self):
		self.TestCase = TestCase
		self.TestCase._mm = self._mm
		self.active = True

	def disable(self):
		self.active = False
		del self.TestCase

def init(moduleManager):
	return TestModule(moduleManager)
