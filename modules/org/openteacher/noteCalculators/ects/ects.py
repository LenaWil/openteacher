#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Cas Widdershoven
#	Copyright 2009-2012, Marten de Vries
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

class ECTSNoteCalculatorModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(ECTSNoteCalculatorModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "noteCalculator"
		self.requires = (
			self._mm.mods(type="percentsCalculator"),
		)
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.filesWithTranslations = ("ects.py",)

		x = 935
		self.priorities = {
			"all": x,
			"selfstudy": x,
			"student@home": x,
			"student@school": x,
			"teacher": x,
			"wordsonly": x,
		}

	def _convert(self, percents):
		if percents >= 70:
			return "A"
		elif percents >= 60:
			return "B"
		elif percents >= 55:
			return "C"
		elif percents >= 50:
			return "D"
		elif percents >= 40:
			return "E"
		elif percents >= 30:
			return "FX"
		else:
			return "F"

	def calculateNote(self, test):
		return self._convert(self._percents(test))

	def calculateAverageNote(self, tests):
		percents = 0
		for test in tests:
			percents += self._percents(test)
		percents /= float(len(tests))
		return self._convert(percents)

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()

		self._percents = self._modules.default(
			"active",
			type="percentsCalculator"
		).calculatePercents

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
		self.name = _("ECTS")

	def disable(self):
		self.active = False
		del self.name
		del self._modules

def init(moduleManager):
	return ECTSNoteCalculatorModule(moduleManager)
