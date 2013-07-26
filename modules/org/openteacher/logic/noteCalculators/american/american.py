#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Cas Widdershoven
#	Copyright 2009-2013, Marten de Vries
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

class AmericanNoteCalculatorModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(AmericanNoteCalculatorModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "noteCalculator"

		self.requires = (
			self._mm.mods("javaScriptImplementation", type="percentsCalculator"),
			self._mm.mods("javaScriptImplementation", type="bisect"),
			self._mm.mods(type="javaScriptEvaluator")
		)
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.filesWithTranslations = ("american.py",)
		self.javaScriptImplementation = True

		self.priorities = {
			"default": 935,
		}

	calculateNote = property(lambda self: self._js["calculateNote"])
	calculateAverageNote = property(lambda self: self._js["calculateAverageNote"])

	def enable(self):
		self._modules = next(iter(self._mm.mods(type="modules")))
		self.code = self._modules.default(
			"active",
			"javaScriptImplementation",
			type="percentsCalculator"
		).code
		self.code += self._modules.default(
			"active",
			"javaScriptImplementation",
			type="bisect"
		).code
		with open(self._mm.resourcePath("american.js")) as f:
			self.code += f.read()

		self._js = self._modules.default("active", type="javaScriptEvaluator").createEvaluator()
		self._js.eval(self.code)

		#Connect to the languageChanged event so retranslating is done.
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		self.active = True

	def _retranslate(self):
		#Load translations
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)
		self.name = _("American")

	def disable(self):
		self.active = False
		del self.name
		del self._modules
		del self._js
		del self.code

def init(moduleManager):
	return AmericanNoteCalculatorModule(moduleManager)
