#! /usr/bin/env python
# -*- coding: utf-8 -*-

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

import unittest

class Word(object):
	def __init__(self, *args, **kwargs):
		super(Word, self).__init__(*args, **kwargs)

		self.questions = []
		self.answers = []

class ItemModifiersTestCase(unittest.TestCase):
	def setUp(self):
		for module in self._mm.mods(type="translator"):
			module.enable()
		for module in self._mm.mods(type="itemModifier"):
			module.enable()

	def testAttributes(self):
		for module in self._mm.mods("active", type="itemModifiers"):
			self.assertTrue(hasattr(module, "modifyItem"))
			self.assertTrue(hasattr(module, "type"))
			self.assertTrue(hasattr(module, "name"))

	def testFunctionCall(self):
		for module in self._mm.mods("active", type="itemModifiers"):
			word = Word()
			word.id = 0
			output = module.modifyItem(word)
			self.assertTrue(hasattr(output, "id"))

	def tearDown(self):
		for module in self._mm.mods("active", type="translator"):
			module.disable()
		for module in self._mm.mods("active", type="itemModifier"):
			module.disable()

class TestModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TestModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "test"

	def enable(self):
		self.TestCase = ItemModifiersTestCase
		self.TestCase._mm = self._mm
		self.active = True

	def disable(self):
		self.active = False
		del self.TestCase

def init(moduleManager):
	return TestModule(moduleManager)
