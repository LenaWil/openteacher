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

import datetime
import exceptions

PYTHON_EXCEPTIONS = vars(exceptions)
for name, exception in PYTHON_EXCEPTIONS.items():
	if type(exception) != type(Exception):
		#not a real exception
		del PYTHON_EXCEPTIONS[name]

class JSObject(object):
	def __init__(self, qtScriptObj, toPython, toJS, *args, **kwargs):
		super(JSObject, self).__init__(*args, **kwargs)

		self._obj = qtScriptObj
		self._toPython = toPython
		self._toJs = toJS

	def __getattr__(self, attr):
		try:
			return super(JSObject, self).__getattr__(attr)
		except AttributeError:
			result = self._toPython(self._obj.property(attr), self._obj)
			if result is None:
				raise AttributeError("No such attribute: %s" % attr)
			return result

	def __setattr__(self, attr, value):
		if attr.startswith("_"):
			super(JSObject, self).__setattr__(attr, value)
		else:
			self._obj.setProperty(attr, self._toJs(value))

	def __delattr__(self, attr):
		try:
			super(JSObject, self).__delattr__(attr)
		except AttributeError:
			self._obj.setProperty(attr, QtScript.QScriptValue())

	def iteritems(self):
		iterator = QtScript.QScriptValueIterator(self._obj)
		while iterator.hasNext():
			iterator.next()
			yield unicode(iterator.name()), self._toPython(iterator.value(), self._obj)

	def toJSObject(self):
		return self._obj

	def __eq__(self, other):
		return sorted(self.iteritems()) == sorted(other.iteritems())

	def __repr__(self):
		return repr(dict(self.iteritems()))

	__getitem__ = __getattr__
	__setitem__ = __setattr__
	__delitem__ = __delattr__

class JSError(Exception):
	def __init__(self, name, message, lineNumber, *args, **kwargs):
		super(JSError, self).__init__(*args, **kwargs)

		self.name = name
		self.message = message
		self.lineNumber = lineNumber

	def __str__(self):
		return "%s: %s (line %s)" % (self.name, self.message, self.lineNumber)

class JSEvaluator(object):
	JSError = JSError

	def __init__(self, *args, **kwargs):
		super(JSEvaluator, self).__init__(*args, **kwargs)

		self._engine = QtScript.QScriptEngine()
		self._functionCache = {}

	def eval(self, js):
		result = self._engine.evaluate(js)
		self._checkForErrors()
		return self._toPythonValue(result)

	def _pythonExceptionFor(self, jsExc):
		name = unicode(jsExc.property("name").toString())
		message = unicode(jsExc.property("message").toString())
		lineNumber = int(jsExc.property("lineNumber").toString())

		try:
			msg = message + " (line %s)" % lineNumber
			return PYTHON_EXCEPTIONS[name](msg)
		except KeyError:
			return JSError(name, message, lineNumber)

	def _checkForErrors(self):
		if self._engine.hasUncaughtException():
			exc = self._engine.uncaughtException()
			#clear exception
			self._engine.evaluate("")
			raise self._pythonExceptionFor(exc)

	def __getitem__(self, key):
		return self._toPythonValue(self._engine.globalObject().property(key))

	def __setitem__(self, key, value):
		self._engine.globalObject().setProperty(key, self._toJSValue(value))

	def _toJSValue(self, value):
		#null (None)
		if value is None:
			return self._engine.nullValue()
		#bool
		if isinstance(value, bool):
			return QtScript.QScriptValue(value)
		#string
		if isinstance(value, basestring):
			return QtScript.QScriptValue(value)

		#function
		if callable(value):
			if not value in self._functionCache:
				def wrapper(context, engine):
					args = []
					for i in range(context.argumentCount()):
						args.append(self._toPythonValue(context.argument(i)))
					#if the last arg is a dict, use keyword arguments.
					#kinda makes up for the fact JS doesn't support
					#them...
					try:
						result = value(*args[:-1], **dict(args[-1].iteritems()))
					except (IndexError, TypeError, AttributeError):
						result = value(*args)
					return QtScript.QScriptValue(self._toJSValue(result))
				self._functionCache[value] = self._engine.newFunction(wrapper)
			return self._functionCache[value]

		#number
		try:
			number = float(value)
		except TypeError:
			pass
		else:
			return QtScript.QScriptValue(number)

		#object (JSObject)
		try:
			value.toJSObject()
		except AttributeError:
			pass

		#object (dict)
		try:
			obj = self._engine.newObject()
			for k, v in value.iteritems():
				obj.setProperty(unicode(k), self._toJSValue(v))
			return obj
		except AttributeError:
			pass

		#iterable
		try:
			items = [item for item in value]
		except TypeError:
			pass
		else:
			array = self._engine.newArray(len(items))
			for i, item in enumerate(items):
				array.setProperty(i, self._toJSValue(item))
			return array

		#date
		try:
			datetime = QtCore.QDateTime(value)
		except TypeError:
			pass
		else:
			if datetime.isValid():
				return self._engine.newDate(value)

		#object (real python object)
		try:
			obj = self._engine.newObject()
			for k in dir(value):
				obj.setProperty(unicode(k), self._toJSValue(getattr(value, k)))
			return obj
		except AttributeError:
			pass

		raise NotImplementedError("Can't convert such a value to JavaScript")

	def _toPythonValue(self, value, scope=None):
		if not scope:
			scope = self._engine.globalObject()

		getProperty = lambda key: self._toPythonValue(value.property(key))
		if not value.isValid():
			return None
		elif value.isArray():
			length = getProperty("length")
			return [getProperty(i) for i in range(length)]
		elif value.isBool():
			return value.toBool()
		elif value.isDate():
			return value.toDateTime().toPyDateTime()
		elif value.isFunction():
			def _getJsArgs(args, kwargs):
				if kwargs:
					args = list(args) + [kwargs]
				return map(self._toJSValue, args)
			def wrapper(*args, **kwargs):
				jsArgs = _getJsArgs(args, kwargs)
				result = value.call(scope, jsArgs)
				self._checkForErrors()
				return self._toPythonValue(result)
			def new(*args, **kwargs):
				jsArgs = _getJsArgs(args, kwargs)
				result = value.construct(jsArgs)
				self._checkForErrors()
				return self._toPythonValue(result)
			wrapper.new = new
			return wrapper
		elif value.isNull():
			return None
		elif value.isNumber():
			number = value.toNumber()
			if round(number) == number:
				return int(number)
			else:
				return number
		elif value.isString():
			return unicode(value.toString())
		elif value.isUndefined():
			return None
		elif value.isObject():
			return JSObject(value, self._toPythonValue, self._toJSValue)
		else:# pragma : no cover
			#can't imagine a situation in which this would happen, but
			#if it ever does, an exception is better than going on
			#silently.
			raise NotImplementedError("Can't convert such a value to Python")

class JSEvaluatorModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(JSEvaluatorModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "javaScriptEvaluator"
		self.requires = (
			self._mm.mods(type="qtApp"),
		)

	def createEvaluator(self):
		return JSEvaluator()

	def enable(self):
		global QtCore, QtScript
		try:
			from PyQt4 import QtCore, QtScript
		except ImportError:# pragma: no cover
			return
		self.active = True

	def disable(self):
		self.active = False

def init(moduleManager):
	return JSEvaluatorModule(moduleManager)
