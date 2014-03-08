#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2013-2014, Marten de Vries
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

#submodules
import jsproxies
import pyproxies
import utils

#python batteries
import logging
import exceptions
import sys
import itertools
import collections
import traceback
import StringIO

#others
from PyQt4 import QtCore, QtScript

pythonExceptionStore = dict(
	(name, exc) for name, exc in vars(exceptions).iteritems()
	if type(exc) == type(Exception)
)

CONSOLE_DEFINITION = """
var console = {
	log: function () {
		for (var i = 0; i < arguments.length; i += 1) {
			var arg = arguments[i];
			if (typeof arg === "undefined") {
				console._pythonPrint("undefined");
			}
			else if (["string", "number", "boolean", "object"].indexOf(typeof arg) !== -1) {
				console._pythonPrint(JSON.stringify(arg));
			} else {
				console._pythonPrint(arg.toString());
			}
		}
	}
}
"""

TRACEBACK_TEMPLATE = """
  File "{filename}", line {lineNumber}, in {funcName}
    {line}
""".strip("\n")

class TrackingAgent(QtScript.QScriptEngineAgent):
	def __init__(self, *args):
		super(TrackingAgent, self).__init__(*args)

		self._scripts = {}
		self._lastLineNumbers = {}
		self.traceback = ""

	def scriptLoad(self, id, program, fileName, baseLineNumber):
		lines = program.split("\n")
		self._scripts[id] = dict(enumerate(lines, baseLineNumber))

	def exceptionThrow(self, id, exc, hasHandler):
		if hasHandler:
			return
		currentCtx = self.engine().currentContext()
		ctx = currentCtx
		tb = []
		while True:
			#generate traceback entry
			info = QtScript.QScriptContextInfo(ctx)
			if not (info.functionName() or info.functionType() == QtScript.QScriptContextInfo.ScriptFunction):
				#python code; we can stop because from here on python's
				#traceback mechanism takes over.
				break
			lineNumber = "?" if info.lineNumber() < 1 else info.lineNumber()
			try:
				line = unicode(self._scripts[info.scriptId()][lineNumber]).strip()
			except KeyError:
				line = "<content unknown>"
			tb.append(TRACEBACK_TEMPLATE.format(
				filename=info.fileName(),
				lineNumber=lineNumber,
				funcName=info.functionName() or "<global>",
				line=line
			))

			#get next context
			ctx = ctx.parentContext()

		tb.reverse()
		self.traceback = u"\n".join(tb)

class JSEvaluator(object):
	"""JSEvaluator is an object that helps you interacting with JS code
	   from Python. It can be used dict-like to modify the JS global
	   scope, and evaluate JavaScript code via its ``eval`` method,
	   e.g.:

	   ``evaluator.eval("3 + 2")``

	   You can also call JS functions by accessing them in the dict-
	   like way, e.g.:

	   ``evaluator["Math"]["ceil"](4.56)``

	   Or use the .new() on a value to make an instance as with the
	   JS new keyword:

	   ``evaluator["Date"].new()``

	   For more examples, see the tests for this module.

	"""
	JSError = pyproxies.JSError

	def __init__(self, *args, **kwargs):
		super(JSEvaluator, self).__init__(*args, **kwargs)

		sys.excepthook = self._excepthook

		if not QtCore.QCoreApplication.instance():
			self._app = QtCore.QCoreApplication(sys.argv)

		self._engine = QtScript.QScriptEngine()
		self._trackingAgent = TrackingAgent(self._engine)
		self._engine.setAgent(self._trackingAgent)

		self._functionCache = {}
		self._objectCache = {}
		self._proxyReferences = set()
		self._counter = itertools.count()

		self.eval(jsproxies.PYTHON_ERROR_DEFINITION)
		self.eval(CONSOLE_DEFINITION)
		self["console"]["_pythonPrint"] = self._pythonPrint

	@staticmethod
	def _tbLength(tb):
		if tb is None:
			return 0
		count = 1
		while tb.tb_next:
			count += 1
			tb = tb.tb_next
		return count

	@classmethod
	def _excepthook(cls, type, value, tb):
		if not hasattr(value, "oldTraceback"):
			#the default excepthook
			sys.__excepthook__(type, value, tb)
			return

		print >> sys.stderr, "Traceback (most recent call last):"
		#the last 2 traceback items are just JSEvaluator internals; they
		#shouldn't be frustrating the debugging process.
		limit = cls._tbLength(tb) - 2
		traceback.print_tb(tb, limit=limit)
		with utils.ignored(AttributeError):
			print >> sys.stderr, value.oldTraceback
		print "%s: %s" % (type.__name__, value)

	def _pythonPrint(self, val):
		print val

	def _newId(self):
		return next(self._counter)

	def eval(self, js, filename="<JS string>", lineNumber=1):
		result = self._engine.evaluate(js, filename, lineNumber)
		self._checkForErrors()
		return self._toPythonValue(result)

	def evalFile(self, filename):
		with open(filename) as f:
			return self.eval(f.read(), filename)

	def _pythonExceptionFor(self, jsExc):
		oldTraceback = unicode(jsExc.property("oldTraceback").toString())
		newTraceback = self._trackingAgent.traceback
		traceback = (newTraceback + "\n" + oldTraceback).strip("\n")

		name = unicode(jsExc.property("name").toString())
		if not name:
			name = "Non-error based exception"
		message = unicode(jsExc.property("message").toString())
		if not message:
			message = self["JSON"].stringify(jsExc)

		try:
			exc = pythonExceptionStore[name](message)
			exc.oldTraceback = traceback
			return exc
		except KeyError:
			return pyproxies.JSError(name, message, traceback)

	def _checkForErrors(self):
		if self._engine.hasUncaughtException():
			exc = self._engine.uncaughtException()
			self._engine.clearExceptions()
			raise self._pythonExceptionFor(exc)

	def __getitem__(self, key):
		return self._toPythonValue(self._engine.globalObject().property(key))

	def __setitem__(self, key, value):
		self._engine.globalObject().setProperty(key, self._toJSValue(value))

	def __delitem__(self, key):
		self._engine.globalObject().setProperty(key, self._engine.undefinedValue())

	def _newProxy(self, ProxyClass, value):
		proxy = ProxyClass(value, self._toJSValue, self._toPythonValue, self._engine)
		self._proxyReferences.add(proxy)
		id = self._newId()
		self._objectCache[id] = value
		return self._engine.newObject(proxy, QtScript.QScriptValue(id))

	def _toJSValue(self, value):
		with utils.ignored(ValueError):
			return self._convertImmutablePythonValue(value)
		return self._convertMutablePythonValue(value)

	def _convertImmutablePythonValue(self, value):
		#immutable values first
		with utils.ignored(TypeError):
			return QtScript.QScriptValue(value)
		#including null (None)
		if value is None:
			return self._engine.nullValue()
		raise ValueError("Unknown value type")

	def _convertMutablePythonValue(self, value):
		#function
		if callable(value):
			return self._wrapPythonFunction(value)
		#date
		try:
			datetime = QtCore.QDateTime(value)
		except TypeError:
			pass
		else:
			return self._engine.newDate(value)
		#object (JSObject)
		try:
			jsObj = value.toJSObject()
		except AttributeError:
			pass
		else:
			#reuse the current script value only when it was constructed
			#by the current engine. Otherwise Qt could throw an error.
			if jsObj.engine() == self._engine:
				return jsObj
		#object (dict-like)
		if isinstance(value, collections.Mapping):
			return self._newProxy(jsproxies.DictProxyClass, value)
		#sequence (list-like)
		if isinstance(value, collections.Sequence):
			return self._newProxy(jsproxies.SequenceProxyClass, value)
		#object (object-like)
		return self._newProxy(jsproxies.ObjectProxyClass, value)

	def _wrapPythonFunction(self, value):
		if not value in self._functionCache:
			def wrapper(context, engine):
				try:
					result = self._callPythonFunction(context, value)
				except BaseException, e:
					#store the exception class so it can be reused
					#later.
					pythonExceptionStore[e.__class__.__name__] = e.__class__

					#convert exceptions to JS exceptions
					#
					#tb_next to hide JSEvaluator internals that are
					#only distraction to library users.
					pythonTbInfo = sys.exc_info()[2].tb_next.tb_next
					newTraceback = StringIO.StringIO()
					limit = self._tbLength(pythonTbInfo)
					if hasattr(e, "oldTraceback"):
						#same here: remove distracting internals
						limit -= 2
					traceback.print_tb(pythonTbInfo, file=newTraceback, limit=limit)
					combinedTraceback = (newTraceback.getvalue().strip("\n") + "\n" + getattr(e, "oldTraceback", "")).strip("\n")
					del pythonTbInfo

					args = (e.__class__.__name__, unicode(e), combinedTraceback)
					jsError = self["JSEvaluatorPythonError"].new(*args)
					context.throwValue(self._toJSValue(jsError))
					return self._engine.undefinedValue()
				return QtScript.QScriptValue(self._toJSValue(result))
			self._functionCache[value] = self._engine.newFunction(wrapper)
		return self._functionCache[value]

	def _callPythonFunction(self, context, func):
		"""Converts JS args specified in `context` into an (args,
		   kwargs) tuple which can easily be passed into the Python
		   function `func`, which is in turn called by this function.

		"""
		args = []
		for i in range(context.argumentCount()):
			args.append(self._toPythonValue(context.argument(i)))
		#if the last arg is a dict, try to use keyword arguments.
		#kinda makes up for the fact JS doesn't support
		#them...
		try:
			return func(*args[:-1], **dict(args[-1].iteritems()))
		except (IndexError, TypeError, AttributeError):
			return func(*args)

	def _toPythonValue(self, value, scope=None):
		with utils.ignored(ValueError):
			return self._convertImmutableJSValue(value)
		return self._convertMutableJSValue(value, scope)

	def _convertImmutableJSValue(self, value):
		#immutable values are converted straight into their Python
		#equivalents.
		if not value.isValid() or value.isNull() or value.isUndefined():
			return None
		elif value.isBool():
			return value.toBool()
		elif value.isNumber():
			return self._toPythonNumber(value)
		elif value.isString():
			return unicode(value.toString())
		else:
			raise ValueError("Unknown value type")

	def _convertMutableJSValue(self, value, scope):
		#mutable values are wrapped as much as possible. Exception:
		#the Date case, where an equivalent (but new) Python object is
		#made.
		if value.scriptClass():
			return self._objectCache[int(value.data().toInteger())]
		elif value.isArray():
			return pyproxies.JSArray(self._toJSValue, self._toPythonValue, value)
		elif value.isDate():
			return value.toDateTime().toPyDateTime()
		elif value.isFunction() or value.isError():
			return self._wrapJSFunction(value, scope)
		elif value.isObject():
			return pyproxies.JSObject(value, self._toPythonValue, self._toJSValue)
		else:
			raise ValueError("Unknown value type.")

	def _getJsArgs(self, args, kwargs):
		if kwargs:
			args = list(args) + [kwargs]
		return [self._toJSValue(arg) for arg in args]

	def _toPythonNumber(self, value):
		number = value.toNumber()
		if round(number) == number:
			return int(number)
		else:
			return number

	def _wrapJSFunction(self, value, scope):
		if not scope:
			scope = self._engine.globalObject()

		name = str(value.property("name").toString())
		def wrapper(*args, **kwargs):
			jsArgs = self._getJsArgs(args, kwargs)
			result = value.call(scope, jsArgs)
			self._checkForErrors()
			return self._toPythonValue(result)
		def new(*args, **kwargs):
			jsArgs = self._getJsArgs(args, kwargs)
			result = value.construct(jsArgs)
			self._checkForErrors()
			return self._toPythonValue(result)
		wrapper.new = new
		if name:
			wrapper.__name__ = "js_" + name
			wrapper.new.__name__ = "js_new_" + name
		return wrapper
