#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011-2012, Marten de Vries
#	Copyright 2011, Cas Widdershoven
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

class WordsStringCheckerModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(WordsStringCheckerModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "wordsStringChecker"
		self.requires = (
			self._mm.mods(type="wordsStringParser"),
		)

	@property
	def _parse(self):
		return self._modules.default("active", type="wordsStringParser").parse

	def check(self, givenAnswerString, word):
		givenAnswer = self._parse(givenAnswerString)

		result = {"result": "wrong"}
		compulsoryAnswerCount = 0

		if len(givenAnswer) == 1:
			result = {"result": "right"}
			difference = set(givenAnswer[0])
			for compulsoryAnswer in word["answers"]:
				oldDifference = difference.copy()
				difference -= set(compulsoryAnswer)
				if oldDifference == difference:
					result = {"result": "wrong"}
					break
			if result["result"] == "right" and len(difference) != 0:
				result = {"result": "wrong"}

		elif len(givenAnswer) > 1:
			for compulsoryGivenAnswer in givenAnswer:
				for compulsoryAnswer in word["answers"]:
					difference = set(compulsoryGivenAnswer) - set(compulsoryAnswer)
					if len(difference) == 0:
						compulsoryAnswerCount += 1

			if compulsoryAnswerCount == len(word["answers"]):
				result = {"result": "right"}

		result.update({
			"itemId": word["id"],
			"givenAnswer": givenAnswerString,
		})

		return result

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()

		self.active = True

	def disable(self):
		self.active = False

		del self._modules

def init(moduleManager):
	return WordsStringCheckerModule(moduleManager)
