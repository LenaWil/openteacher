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

class JavascriptCheckerModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(JavascriptCheckerModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "wordsStringChecker"
		self.javaScriptImplementation = True
		self.requires = (
			self._mm.mods("javaScriptImplementation", type="wordsStringParser"),
			self._mm.mods(type="ui"),
		)
		self.priorities = {
			"default": 20,
		}

	def _checkForErrors(self):
		if self._engine.hasUncaughtException():
			raise Exception(self._engine.uncaughtException().toString())

	def check(self, givenAnswer, word):
		v = self._engine.evaluate("check(%s, %s)" % (json.dumps(givenAnswer), json.dumps(word)))
		self._checkForErrors()

		return {"result": unicode(v.property("result").toString())}

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		self.code = self._modules.default("javaScriptImplementation", type="wordsStringParser").code

		self._engine = QtScript.QScriptEngine()
		with open(self._mm.resourcePath("checker.js")) as f:
			self.code += "\n" + f.read()
		self._engine.evaluate(self.code, f.name)
		self._checkForErrors()

		self.active = True

	def disable(self):
		self.active = False

		del self._engine
		del self.code

def init(moduleManager):
	return JavascriptCheckerModule(moduleManager)
