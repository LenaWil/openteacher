#! /usr/bin/env python
# -*- coding: utf-8 -*-

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

class FrenchNoteCalculatorModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(FrenchNoteCalculatorModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "noteCalculator"

	def _calculate(self, test):
		results = map(lambda x: 1 if x["result"] == "right" else 0, test["results"])
		total = len(results)
		amountRight = sum(results)

		return int(float(amountRight) / float(total) * 20)

	def calculateNote(self, test):
		return self._calculate(test)

	def calculateAverageNote(self, tests):
		note = 0
		for test in tests:
			note += self._calculate(test)
		note /= float(len(tests))
		return str(int(note))

	def enable(self):
		self.name = _("French")
		self.active = True

	def disable(self):
		self.active = False
		del self.name

def init(moduleManager):
	return FrenchNoteCalculatorModule(moduleManager)
