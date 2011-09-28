#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Cas Widdershoven
#	Copyright 2009-2011, Marten de Vries
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

	def _percents(self, test):
		results = map(lambda x: 1 if x["result"] == "right" else 0, test["results"])
		total = len(results)
		amountRight = sum(results)

		return float(amountRight) / float(total) * 100
		
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
		self.name = "ECTS" #FIXME: translate!
		self.active = True

	def disable(self):
		self.active = False
		del self.name

def init(moduleManager):
	return ECTSNoteCalculatorModule(moduleManager)
