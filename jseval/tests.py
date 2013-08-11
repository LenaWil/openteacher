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
import copy
import sys
import StringIO
import re
import os

import __init__ as jseval

class BaseTestCase(unittest.TestCase):
	def setUp(self):
		self._js = jseval.JSEvaluator()

class ExceptionTests(BaseTestCase):
	def testNonObjectException(self):
		with self.assertRaises(self._js.JSError) as cm:
			self._js.eval('throw("string exception!")')
		self.assertIn("Non-error based exception", str(cm.exception))
		self.assertIn("string exception!", str(cm.exception))

	def testRaisingExceptionInPythonCodeCalledByJS(self):
		def exc():
			raise ValueError("Hi!")
		self._js["exc"] = exc
		self._js.eval("""
			var a;
			try {
				exc();
			} catch(e) {
				a = e;
			}"""
		)
		self.assertEqual(self._js["a"].name, "ValueError")
		self.assertEqual(self._js["a"].message, "Hi!")

	def testRaiseCustomExceptionInPythonCodeCalledByJS(self):
		class CustomException(Exception):
			pass
		def exc():
			raise CustomException("Hi!")

		self._js["exc"] = exc
		with self.assertRaises(CustomException):
			self._js.eval("exc();")

	def testPythonLikeError(self):
		try:
			self._js.eval("This should raise some kind of error, right?")
		except SyntaxError, e:
			self.assertTrue(str(e))
		else:
			self.assertTrue(False, msg="It didn't raise an error!")# pragma: no cover

	def testCustomError(self):
		try:
			self._js.eval("throw {message: 'hi', name: 'test'}")
		except self._js.JSError, e:
			self.assertTrue(str(e))
			self.assertTrue(e.name)
			self.assertTrue(e.message)
		else:
			self.assertTrue(False, msg="It didn't raise an error!")# pragma: no cover

	def testTraceback(self):
		tracebackRegexes = [
			r'  File "<JS string>", line 6, in jsFunc',
			r'    pyFunc\(\);',
			r'  File ".*?tests\.py", line [0-9]+, in pyFunc',
			r'    self\._js\["jsFunc2"\]\(\)',
			r'  File "<JS string>", line 3, in jsFunc2',
			r'    pyFunc2\(\);',
			r'  File ".*?tests\.py", line [0-9]+, in pyFunc2',
			r'    raise ValueError\("Hello World!"\)',
		]

		def pyFunc2():
			raise ValueError("Hello World!")

		def pyFunc():
			self._js["jsFunc2"]()

		self._js["pyFunc"] = pyFunc
		self._js["pyFunc2"] = pyFunc2

		with self.assertRaises(ValueError) as context:
			self._js.eval("""
				function jsFunc2() {
					pyFunc2();
				}
				function jsFunc() {
					pyFunc();
				}
				jsFunc()
			""")

		traceback = context.exception.oldTraceback.split("\n")
		for line, re in zip(traceback, tracebackRegexes):
			self.assertRegexpMatches(line, re)

class SimpleValueConversionTests(BaseTestCase):
	def testConvertingNumber(self):
		self.assertEqual(self._js.eval("4.2"), 4.2)

	def testConvertingNull(self):
		self.assertIsNone(self._js.eval("null"))

	def testConvertingJSDateToPython(self):
		now = datetime.datetime.now()
		#a second should be enough.
		self.assertTrue(self._js["Date"].new() - now < datetime.timedelta(seconds=1))

	def testConvertingDateTimeToJSDateAndBack(self):
		now = datetime.datetime.now()
		passThroughNow = self._js.eval("(function(a) {return a;})")(now)

		self.assertTrue(now - passThroughNow < datetime.timedelta(seconds=1))

	def testConvertingBoolToJs(self):
		self.assertEqual(self._js["JSON"]["stringify"](True), "true")

class ArrayTests(BaseTestCase):
	def testConvertingArray(self):
		self.assertEqual(list(self._js.eval("['a', 'b', 'c']")), ["a", "b", "c"])

	def testConvertingTupleToJs(self):
		"""A non-list sequence"""
		self.assertEqual(
			self._js.eval("(function (a) {return a[0];})")((1, 2)),
			1
		)

	def testArraySequence(self):
		sequence = self._js.eval("[3, 2, 1]")
		self.assertEqual(len(sequence), 3)
		self.assertEqual(sequence[0], 3)
		sequence.insert(0, 4)
		self.assertEqual(sequence[0], 4)
		self.assertEqual(sequence.index(3), 1)

	def testArrayToString(self):
		self.assertTrue(self._js.eval("(function (seq) {return seq.toString()})")([1, 2, 3]))

	def testSettingArrayIndex(self):
		seq = [1, 2, 3]
		self._js.eval("(function (seq) {seq[0] = 4})")(seq)
		self.assertEqual(seq, [4, 2, 3])

	def testRemovingPyArrayIndex(self):
		array = self._js.eval("[1, 2, 3]")
		del array[0]
		self.assertEqual(array, [2, 3])

	def testSettingPyArrayIndex(self):
		array = self._js.eval("[1, 2, 3]")
		array[0] = 4
		self.assertEqual(array, [4, 2, 3])

	def testPyArrayRepr(self):
		self.assertTrue(repr(self._js.eval("[1, 2, 3]")))

	def testShallowCopyingArray(self):
		something = self._js.eval("[{key: 1}]")
		something2 = copy.copy(something)
		something2[0].key = 2
		something2.append(3)

		self.assertEqual(something[0].key, 2)
		with self.assertRaises(IndexError):
			something[1]

		self.assertEqual(something2[0].key, 2)
		self.assertEqual(something2[1], 3)

	def testDeepCopyingArray(self):
		something = self._js.eval("[{key: 1}]")
		something2 = copy.deepcopy(something)
		something2[0].key = 2
		something2.append(3)

		self.assertEqual(something[0].key, 1)
		with self.assertRaises(IndexError):
			something[1]

		self.assertEqual(something2[0].key, 2)
		self.assertEqual(something2[1], 3)

class DictTests(BaseTestCase):
	def testDictToString(self):
		self.assertTrue(self._js.eval("(function (mapping) {return mapping.toString()})")({"a": 1}))

	def testChangingDictInJs(self):
		self._js.eval("""function test(arg) {
			arg.x = "newValue";
		}""")
		myDict = {
			"x": "oldValue",
		}
		self._js["test"](myDict)
		self.assertEqual(myDict["x"], "newValue")

class ObjectTests(BaseTestCase):
	def testObjectToString(self):
		self.assertTrue(self._js.eval("(function (obj) {return obj.toString()})")(object()))

	def testShallowCopyingObject(self):
		something = self._js.eval("({a: {key: 1}})")
		something2 = copy.copy(something)
		something2.a.key = 2
		something2.b = 3

		self.assertEqual(something.a.key, 2)
		with self.assertRaises(AttributeError):
			something.b

		self.assertEqual(something2.a.key, 2)
		self.assertEqual(something2.b, 3)

	def testDeepCopyingObject(self):
		something = self._js.eval("({a: {key: 1}})")
		something2 = copy.deepcopy(something)
		something2.a.key = 2
		something2.b = 3

		self.assertEqual(something.a.key, 1)
		with self.assertRaises(AttributeError):
			something.b

		self.assertEqual(something2.a.key, 2)
		self.assertEqual(something2.b, 3)

	def testSetObjectAttribute(self):
		class MyObject(object):
			pass
		obj = MyObject()
		self._js.eval("(function (obj) {obj.x = 1})")(obj)
		self.assertEqual(obj.x, 1)

	def testUndefinedObjectAttribute(self):
		self.assertIsNone(self._js.eval("(function (obj) {return obj.x})")(object()))

	def testUndefinedPyObjectKey(self):
		with self.assertRaises(KeyError):
			self._js.eval("({a: 1})")["b"]

	def testUndefinedPyObjectAttribute(self):
		with self.assertRaises(AttributeError):
			self._js.eval("({a: 1})").b

	def testRemovingUndefinedPyObjectAttribute(self):
		with self.assertRaises(AttributeError):
			del self._js.eval("({a: 1})").b

	def testRemovingPyObjectAttribute(self):
		obj = self._js.eval("({a: 1})")
		del obj.a
		with self.assertRaises(AttributeError):
			obj.a

	def testPyObjectRepr(self):
		self.assertTrue(repr(self._js.eval("({a: 1})")))

class CallTests(BaseTestCase):
	def testArgsKwargsToJs(self):
		args = [1, 2]
		kwargs= {"test": 1, "b": 2}
		func = self._js.eval("(function(one, two, kwargs) {return [one, two, kwargs]})")
		result = func(*args, **kwargs)
		self.assertEqual(result, args + [kwargs])

	def testArgsKwargsToPython(self):
		result = {}
		def func(*args, **kwargs):
			result["args"] = args
			result["kwargs"] = kwargs
		self._js["func"] = func
		self._js.eval("func(1, 2, {test: 1, b: 2})")
		self.assertEqual(result["args"], (1, 2))
		self.assertEqual(result["kwargs"], {"test": 1, "b": 2})

	def testScope(self):
		self._js.eval("""
			function Test () {
				this.test = 23;
				this.func = function () {
					return this.test;
				}
			};""");
		self.assertEqual(self._js["Test"].new().func(), 23)

class OtherTests(BaseTestCase):
	def testConsoleLog(self):
		sys.stdout = tempstdout = StringIO.StringIO()
		self._js.eval("console.log('test')")
		sys.stdout = sys.__stdout__

		self.assertEqual(tempstdout.getvalue(), '"test"\n')

	def testUnexistingProperty(self):
		self.assertIsNone(self._js["nonexistingproperty"])

	def testSettingGlobalThingy(self):
		self._js["hello"] = lambda: "Hello World!"
		self.assertEqual(self._js["hello"](), "Hello World!")

	def testRemovingGlobalItem(self):
		self._js.eval("var a = 1");
		self.assertEqual(self._js["a"], 1)
		del self._js["a"]
		self.assertIsNone(self._js["a"])

if __name__ == "__main__":
	unittest.main()
