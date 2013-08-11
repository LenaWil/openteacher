import collections
from PyQt4 import QtScript
import copy

class JSObjectCopy(dict):
	def __getattr__(self, attr):
		try:
			return super(JSObjectCopy, self).__getattr__(attr)
		except AttributeError:
			try:
				return self[attr]
			except KeyError, e:
				raise AttributeError(e)

	def __setattr__(self, attr, value):
		self[attr] = value

	def __delattr__(self, attr):
		del self[attr]

class JSObject(collections.MutableMapping):
	def __init__(self, qtScriptObj, toPython, toJS, *args, **kwargs):
		super(JSObject, self).__init__(*args, **kwargs)

		self.__dict__["_obj"] = qtScriptObj
		self.__dict__["_toPython"] = toPython
		self.__dict__["_toJs"] = toJS

	def _getPropertyOrError(self, key):
		prop = self._obj.property(key)
		if not prop.isValid() or prop.isUndefined():
			raise KeyError("No such key: %s" % key)
		return prop

	def __getitem__(self, key):
		return self._toPython(self._getPropertyOrError(key), self._obj)

	def __setitem__(self, key, value):
		self._obj.setProperty(key, self._toJs(value))

	def __delitem__(self, key):
		#raises KeyError for us if necessary
		self._getPropertyOrError(key)
		self._obj.setProperty(key, QtScript.QScriptValue())

	def __getattr__(self, attr):
		try:
			return self[attr]
		except KeyError, e:
			raise AttributeError(e)

	def __setattr__(self, attr, value):
		self[attr] = value

	def __delattr__(self, attr):
		try:
			del self[attr]
		except KeyError, e:
			raise AttributeError(e)

	def __iter__(self):
		iterator = QtScript.QScriptValueIterator(self._obj)
		while iterator.hasNext():
			iterator.next()
			yield unicode(iterator.name())

	def __len__(self):
		return sum(1 for _ in self)

	def toJSObject(self):
		return self._obj

	def __repr__(self):
		return repr(dict(self))

	def __eq__(self, other):
		return dict(self) == dict(other)

	def __copy__(self):
		return JSObjectCopy(self)

	copy = __copy__

	def __deepcopy__(self, memo):
		return JSObjectCopy(
			(copy.deepcopy(key, memo), copy.deepcopy(value, memo))
			for key, value in self.iteritems()
		)

class JSError(Exception):
	def __init__(self, name, message, oldTraceback, *args, **kwargs):
		super(JSError, self).__init__(*args, **kwargs)

		self.name = name
		self.message = message
		self.oldTraceback = oldTraceback

	def __str__(self):
		return "%s: %s" % (self.name, self.message)

class JSArray(collections.MutableSequence):
	def __init__(self, toJSValue, toPythonValue, value, *args, **kwargs):
		super(JSArray, self).__init__(*args, **kwargs)

		self._toJSValue = toJSValue
		self._toPythonValue = toPythonValue

		self._value = value

	def _checkBounds(self, key):
		if not 0 <= key < len(self):
			raise IndexError("Index out of bounds (%s)" % key)

	def __getitem__(self, key):
		self._checkBounds(key)
		return self._toPythonValue(self._value.property(key))

	def __delitem__(self, key):
		self._checkBounds(key)
		self._value.property("splice").call(self._value, [
			self._toJSValue(a)
			for a in [key, 1]
		])

	def __setitem__(self, key, value):
		self._value.setProperty(key, self._toJSValue(value))

	def __len__(self):
		return self._value.property("length").toInteger()

	def __eq__(self, other):
		return list(self) == list(other)

	def __repr__(self):
		return repr(list(self))

	def insert(self, index, value):
		self._value.property("splice").call(self._value, [
			self._toJSValue(a)
			for a in [index, 0, value]
		])

	def toJSObject(self):
		return self._value

	def __copy__(self):
		return list(self)

	def __deepcopy__(self, memo):
		return [copy.deepcopy(item, memo) for item in self]
