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

import unittest

class WordList(object):
	def __init__(self, *args, **kwargs):
		super(WordList, self).__init__(*args, **kwargs)

		self.words = []
		self.tests = []

class Word(object):
	pass

class Result(str):
	pass

class WordsNeverAnsweredCorrectlyTestCase(unittest.TestCase):
	def setUp(self):
		for module in self._mm.mods.supporting("wordsNeverAnsweredCorrectly"):
			module.enable()

	def testListModifier(self):
		for module in self._mm.activeMods.supporting("wordsNeverAnsweredCorrectly"):
			self.assertTrue("listModifier" in module.supports)

	def testWrongWord(self):
		wordList = WordList()
		word = Word()
		word.id = 0
		wordList.words.append(word)

		result = Result("wrong")
		result.wordId = 0
		wordList.tests.append([result])

		self._test(wordList, [0])

	def testRightWord(self):
		wordList = WordList()
		word = Word()
		word.id = 0
		wordList.words.append(word)

		result = Result("right")
		result.wordId = 0
		wordList.tests.append([result])
		
		self._test(wordList, [])

	def testWordWithoutResults(self):
		wordList = WordList()
		word = Word()
		word.id = 0
		wordList.words.append(word)

		self._test(wordList, [0])

	def testMultipleTestsAndWords(self):
		wordList = WordList()
		word1 = Word()
		word1.id = 0
		word2 = Word()
		word2.id = 1
		wordList.words.append(word1)
		wordList.words.append(word2)

		result1 = Result("right")
		result1.wordId = 0
		result2 = Result("wrong")
		result2.wordId = 0
		result3 = Result("wrong")
		result3.wordId = 1
		result4 = Result("right")
		result4.wordId = 0
		result5 = Result("wrong")
		result5.wordId = 1

		wordList.tests.append([result1, result2, result3])
		wordList.tests.append([result4, result5])

		self._test(wordList, [1])

	def _test(self, input, output):
		for module in self._mm.mods.supporting("wordsNeverAnsweredCorrectly"):
			indexes = module.modifyList(range(len(input.words)), input)
			self.assertEqual(indexes, output)

	def tearDown(self):
		for module in self._mm.activeMods.supporting("wordsNeverAnsweredCorrectly"):
			module.disable()

class TestModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TestModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.supports = ("test",)
		self.requires = (1, 0)
		self.active = False

	def enable(self):
		self.TestCase = WordsNeverAnsweredCorrectlyTestCase
		self.TestCase._mm = self._mm
		self.active = True

	def disable(self):
		self.active = False
		del self.TestCase

def init(moduleManager):
	return TestModule(moduleManager)
