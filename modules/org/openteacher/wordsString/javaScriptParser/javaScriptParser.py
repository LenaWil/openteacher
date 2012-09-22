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

class JavascriptParserModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(JavascriptParserModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "wordsStringParser"
		self.javaScriptImplementation = True
		self.requires = (
			self._mm.mods(type="ui"),
		)
		self.priorities = {
			"default": 20,
		}

	def _jsArrayIter(self, v):
		for i in range(int(v.property("length").toNumber())):
			data = v.property(i)
			yield data

	def _checkForErrors(self):
		if self._engine.hasUncaughtException():
			raise Exception(self._engine.uncaughtException().toString())

	def parse(self, text):
		v = self._engine.evaluate("parse(%s)" % json.dumps(text))
		self._checkForErrors()

		result = []
		for jsArray in self._jsArrayIter(v):
			iterable = self._jsArrayIter(jsArray)
			data = (unicode(v.toString()) for v in iterable)
			result.append(tuple(data))
		return result

	def enable(self):
		self._engine = QtScript.QScriptEngine()
		with open(self._mm.resourcePath("parser.js")) as f:
			self.code = f.read()
		self._engine.evaluate(self.code, f.name)
		self._checkForErrors()

		self.active = True

	def disable(self):
		self.active = False

		del self._engine
		del self.code

def init(moduleManager):
	return JavascriptParserModule(moduleManager)
