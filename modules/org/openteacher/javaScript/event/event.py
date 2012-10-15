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

from PyQt4 import QtScript
try:
	import json
except ImportError:
	import simplejson as json

class Event(object):
	"""Not cool: this wrapper class was harder to write than the native
	   implementation. I'm looking at you, QtScript!

	"""
	def __init__(self, jsObj, checkForErrors):
		self._jsObj = jsObj
		self._checkForErrors = checkForErrors
		self._funcs = {}

	def _fromPythonValue(self, value):
		jsonData = json.dumps(value)
		return self._jsObj.engine().evaluate("JSON.parse('%s')" % jsonData)

	def _toPythonValue(self, value):
		stringify = self._jsObj.engine().globalObject().property("JSON").property("stringify")
		jsonData = unicode(stringify.call(args=[value]).toString())
		return json.loads(jsonData)

	def _getJsFunc(self, func):
		def wrap(func):
			def inner(context, engine):
				args = []
				for i in range(context.argumentCount()):
					args.append(self._toPythonValue(context.argument(i)))

				result = func(*args)
				return QtScript.QScriptValue(self._fromPythonValue(result))
			return inner

		if func not in self._funcs:
			self._funcs[func] = self._jsObj.engine().newFunction(wrap(func))
		return self._funcs[func]

	def handle(self, func):
		self._jsObj.property("handle").call(args=[self._getJsFunc(func)])
		self._checkForErrors()

	def unhandle(self, func):
		result = self._jsObj.property("unhandle").call(args=[self._getJsFunc(func)])
		self._checkForErrors()
		if not result.toBool():
			raise KeyError()

	def send(self, *args, **kwargs):
		jsArgs = [self._fromPythonValue(arg) for arg in args]
		self._jsObj.property("send").call(args=jsArgs)
		self._checkForErrors()

class JavascriptEventModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(JavascriptEventModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "javaScriptEvent"
		self.javascriptImplementation = True

		self.requires = (
			self._mm.mods(type="ui"),
		)

	def _checkForErrors(self):
		if self._engine.hasUncaughtException():
			raise Exception(self._engine.uncaughtException().toString())

	def createEvent(self):
		obj = self._engine.evaluate("new Event()")
		self._checkForErrors()
		return Event(obj, self._checkForErrors)

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()

		self._engine = QtScript.QScriptEngine()
		with open(self._mm.resourcePath("event.js")) as f:
			self.code = f.read()
		self._engine.evaluate(self.code)

		self._checkForErrors()

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self._engine
		del self.code

def init(moduleManager):
	return JavascriptEventModule(moduleManager)
