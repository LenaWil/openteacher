from PyQt4 import QtScript
import utils
import json

PYTHON_ERROR_DEFINITION = """
var JSEvaluatorPythonError = function(name, message, oldTraceback) {
	"use strict";

	this.name = name;
	this.message = message;

	this.oldTraceback = oldTraceback;
}
JSEvaluatorPythonError.prototype = new Error();
"""

class BaseProxyClass(QtScript.QScriptClass):
	def __init__(self, obj, toJS, toPython, *args):
		super(BaseProxyClass, self).__init__(*args)

		self._obj = obj
		self._toJS = toJS
		self._toPython = toPython
		self._iteratorReferences = set()

	def newIterator(self, object):
		iterator = PropertyIterator(self.iteritems(), self.engine(), object)
		self._iteratorReferences.add(iterator)
		return iterator

	def _pyName(self, scriptName):
		return unicode(scriptName.toString())

	def queryProperty(self, object, name, flags):
		return flags, -1

class PropertyIterator(QtScript.QScriptClassPropertyIterator):
	def __init__(self, items, engine, *args):
		super(PropertyIterator, self).__init__(*args)

		self._properties = list(items)
		self._engine = engine
		self._index = -1

	def toFront(self):
		self._index = -1

	def toBack(self):
		self._index = len(self._properties) -1

	def hasNext(self):
		return self._index < len(self._properties) -1

	def next(self):
		self._index += 1

	def hasPrevious(self):
		return self._index > -1

	def previous(self):
		self._index -= 1

	def name(self):
		return self._engine.toStringHandle(self._properties[self._index][0])

class ObjectProxyClass(BaseProxyClass):
	def _toString(self, *args, **kwargs):
		return "<%s %s>" % (self.__class__.__name__, dir(self._obj))

	def iteritems(self):
		try:
			return self._obj.__dict__.iteritems()
		except AttributeError:
			return []

	def property(self, object, name, id):
		name = self._pyName(name)
		if name == "toString":
			return self._toJS(self._toString)
		try:
			return self._toJS(getattr(self._obj, name))
		except AttributeError:
			return self.engine().undefinedValue()

	def setProperty(self, object, name, id, value):
		name = self._pyName(name)
		setattr(self._obj, name, self._toPython(value))

class DictProxyClass(BaseProxyClass):
	def _toString(self, *args, **kwargs):
		return "<%s %s>" % (self.__class__.__name__, dict(self._obj))

	def iteritems(self):
		return self._obj.iteritems()

	def property(self, object, name, id):
		name = self._pyName(name)
		if name == "toString":
			return self._toJS(self._toString)
		try:
			return self._toJS(self._obj[name])
		except KeyError:
			return self.engine().undefinedValue()

	def setProperty(self, object, name, id, value):
		self._obj[self._pyName(name)] = self._toPython(value)

class SequenceProxyClass(BaseProxyClass):
	def property(self, object, name, id):
		name = self._pyName(name)
		with utils.ignored(KeyError):
			return self._toJS({
				"filter": self._filter,
				"indexOf": self._indexOf,
				"join": self._join,
				"length": self._length(),
				"push": self._push,
				"slice": self._slice,
				"splice": self._splice,
				"toJSON": self._toJSON,
				"toString": self._toString,
			}[name])
		try:
			return self._toJS(self._obj[int(name)])
		except (IndexError, ValueError):
			return self.engine().undefinedValue()

	def _length(self):
		return len(self._obj)

	def _join(self, sep):
		return sep.join(self._obj)

	def _filter(self, func):
		return [item for item in self._obj if func(item)]

	def _toString(self, *args, **kwargs):
		return "<%s %s>" % (
			self.__class__.__name__,
			json.dumps(list(self._obj)),
		)

	def _indexOf(self, data):
		try:
			return self._obj.index(data)
		except ValueError:
			return -1

	def _slice(self):
		"""Non-complete implementation?"""
		return [item for item in self._obj]

	def _splice(self, index, amount):
		"""Non-complete implementation?"""
		while amount:
			amount -= 1
			del self._obj[index]

	def _push(self, item):
		"""Non-complete implementation?"""
		self._obj.append(item)

	def _toJSON(self, *args, **kwargs):
		jsArray = self._toPython(self.engine().globalObject().property("Array"))
		return jsArray.new(*self._obj)

	def iteritems(self):
		for (i, v) in enumerate(self._obj):
			yield str(i), v

	def setProperty(self, object, name, id, value):
		self._obj[int(self._pyName(name))] = self._toPython(value)
