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
import json

class WordListStringParserModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(WordListStringParserModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "wordListStringParser"
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
			exception = self._engine.uncaughtException()
			if unicode(exception.property("name").toString()) == "SeparatorError":
				raise ValueError(unicode(exception.property("message").toString()))
			raise Exception(exception.toString())

	def parseList(self, string):
		jsonResult = self._engine.evaluate("JSON.stringify(parseList(%s))" % json.dumps(string))
		self._checkForErrors()

		result = json.loads(unicode(jsonResult.toString()))
		for item in result["list"]["items"]:
			item["questions"] = map(tuple, item["questions"])
			item["answers"] = map(tuple, item["answers"])
		return result

	def enable(self):
		modules = set(self._mm.mods(type="modules")).pop()

		self._engine = QtScript.QScriptEngine()
		self.code = modules.default("active", "javaScriptImplementation", type="wordsStringParser").code
		with open(self._mm.resourcePath("parser.js")) as f:
			self.code += "\n\n" + f.read()
		self._engine.evaluate(self.code, f.name)
		self._checkForErrors()

		self.active = True

	def disable(self):
		self.active = False

		del self._engine
		del self.code

def init(moduleManager):
	return WordListStringParserModule(moduleManager)
