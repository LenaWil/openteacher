#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2013, Marten de Vries
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
import datetime

class TestCase(unittest.TestCase):
	def _getEvaluators(self):
		for mod in self._mm.mods("active", type="javaScriptEvaluator"):
			yield mod.createEvaluator()

	def testConvertingNumber(self):
		for js in self._getEvaluators():
			self.assertEqual(js.eval("4.2"), 4.2)

	def testConvertingNull(self):
		for js in self._getEvaluators():
			self.assertIsNone(js.eval("null"))

	def testConvertingDateTime(self):
		for js in self._getEvaluators():
			now = datetime.datetime.now()
			#a second should be enough.
			self.assertTrue(js["Date"].new() - now < datetime.timedelta(seconds=1))

	def testConvertingArray(self):
		for js in self._getEvaluators():
			self.assertEqual(list(js.eval("['a', 'b', 'c']")), ["a", "b", "c"])

	def testUnexistingProperty(self):
		for js in self._getEvaluators():
			self.assertIsNone(js["nonexistingproperty"])

	def testConvertingBoolToJs(self):
		for js in self._getEvaluators():
			self.assertEqual(js["JSON"]["stringify"](True), "true")

	def testConvertingTupleToJs(self):
		"""A non-list sequence"""
		for js in self._getEvaluators():
			self.assertEqual(
				js.eval("(function (a) {return a[0];})")((1, 2)),
				1
			)

	def testConvertingDateToJs(self):
		now = datetime.datetime.now()
		for js in self._getEvaluators():
			passThroughNow = js.eval("(function(a) {return a;})")(now)

			self.assertTrue(now - passThroughNow < datetime.timedelta(seconds=1))

	def testPythonLikeError(self):
		for js in self._getEvaluators():
			try:
				js.eval("This should raise some kind of error, right?")
			except SyntaxError, e:
				self.assertTrue(str(e))
			else:
				self.assertTrue(False, msg="It didn't raise an error!")# pragma: no cover

	def testCustomError(self):
		for js in self._getEvaluators():
			try:
				js.eval("throw {message: 'hi', name: 'test'}")
			except js.JSError, e:
				self.assertTrue(str(e))
				self.assertTrue(e.name)
				self.assertTrue(e.message)
				self.assertTrue(e.lineNumber)
			else:
				self.assertTrue(False, msg="It didn't raise an error!")# pragma: no cover

	def testScope(self):
		for js in self._getEvaluators():
			js.eval("""
				function Test () {
					this.test = 23;
					this.func = function () {
						return this.test;
					}
				};""");
			self.assertEqual(js["Test"].new().func(), 23)

	def testSettingGlobalThingy(self):
		for js in self._getEvaluators():
			js["hello"] = lambda: "Hello World!"
			self.assertEqual(js["hello"](), "Hello World!")

	def testChangingDictInJs(self):
		for js in self._getEvaluators():
			js.eval("""function test(arg) {
				arg.x = "newValue";
			}""")
			myDict = {
				"x": "oldValue",
			}
			js["test"](myDict)
			self.assertEqual(myDict["x"], "newValue")

	def testRemovingGlobalItem(self):
		for js in self._getEvaluators():
			js.eval("var a = 1");
			self.assertEqual(js["a"], 1)
			del js["a"]
			self.assertIsNone(js["a"])

	def testArgsKwargsToJs(self):
		for js in self._getEvaluators():
			args = [1, 2]
			kwargs= {"test": 1, "b": 2}
			func = js.eval("(function(one, two, kwargs) {return [one, two, kwargs]})")
			result = func(*args, **kwargs)
			self.assertEqual(result, args + [kwargs])

	def testArgsKwargsToPython(self):
		for js in self._getEvaluators():
			result = {}
			def func(*args, **kwargs):
				result["args"] = args
				result["kwargs"] = kwargs
			js["func"] = func
			js.eval("func(1, 2, {test: 1, b: 2})")
			self.assertEqual(result["args"], (1, 2))
			self.assertEqual(result["kwargs"], {"test": 1, "b": 2})

	def testArraySequence(self):
		for js in self._getEvaluators():
			sequence = js.eval("[3, 2, 1]")
			self.assertEqual(len(sequence), 3)
			self.assertEqual(sequence[0], 3)
			sequence.insert(0, 4)
			self.assertEqual(sequence[0], 4)
			self.assertEqual(sequence.index(3), 1)

class TestModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TestModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "test"
		self.requires = (
			self._mm.mods(type="javaScriptEvaluator"),
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
