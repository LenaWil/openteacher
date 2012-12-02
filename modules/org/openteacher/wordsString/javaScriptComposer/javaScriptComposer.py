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

import json

class JavascriptComposerModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(JavascriptComposerModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "wordsStringComposer"
		self.javaScriptImplementation = True
		self.requires = (
			self._mm.mods(type="qtApp"),
		)
		self.priorities = {
			"default": 20,
		}

	def _checkForErrors(self):
		if self._engine.hasUncaughtException():
			raise Exception(self._engine.uncaughtException().toString())

	def compose(self, word):
		v = self._engine.evaluate("compose(%s)" % json.dumps(word))
		self._checkForErrors()

		return unicode(v.toString())

	def enable(self):
		global QtScript
		try:
			from PyQt4 import QtScript
		except ImportError:
			return
		self._engine = QtScript.QScriptEngine()
		with open(self._mm.resourcePath("composer.js")) as f:
			self.code = f.read()
		self._engine.evaluate(self.code, f.name)
		self._checkForErrors()

		self.active = True

	def disable(self):
		self.active = False

		del self._engine
		del self.code

def init(moduleManager):
	return JavascriptComposerModule(moduleManager)
