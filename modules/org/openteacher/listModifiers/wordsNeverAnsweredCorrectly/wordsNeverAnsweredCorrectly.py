#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Marten de Vries
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

class WordsNeverAnsweredCorrectlyModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(WordsNeverAnsweredCorrectlyModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "listModifier"

	def modifyList(self, indexes, list):
		self._list = list
		newIndexes = filter(self._isNeverAnsweredCorrectly, indexes)
		del self._list
		return newIndexes

	def _isNeverAnsweredCorrectly(self, index):
		results = self._resultsFor(self._list.items[index])
		return "right" not in results

	def _resultsFor(self, word):
		results = []
		for test in self._list.tests:
			results.extend(test)
		return filter(lambda result: result.wordId == word.id, results)

	def enable(self):
		self.testName = "wordsNeverAnsweredCorrectly"
		self.dataType = "words"
		self.name = "Only words you never answered correctly" #FIXME: translate
		self.active = True

	def disable(self):
		self.active = False
		del self.testName
		del self.dataType
		del self.name

def init(moduleManager):
	return WordsNeverAnsweredCorrectlyModule(moduleManager)
