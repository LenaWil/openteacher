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

class Word(object):
	pass

class WordsStringCheckerTestCase(unittest.TestCase):
	def setUp(self):
		self.word1 = Word()
		self.word1.id = 0
		self.word1.questions = [(u"in",)]
		self.word1.comment = u"+abl"
		self.word1.answers = [(u"in", u"op", u"bij"), (u"tijdens",)]

		self.word2 = Word()
		self.word2.id = 1
		self.word2.questions = [(u"in",)]
		self.word2.comment = u"+acc"
		self.word2.answers = [(u"naar(binnen)", u"in"), (u"tot", u"jegens")]

		for module in self._mm.mods(type="wordsStringChecker"):
			module.enable()
		for module in self._mm.mods(type="wordsStringParser"):
			module.enable()
		for module in self._mm.mods(type="modules"):
			module.enable()

	def testSingleRightAnswer(self):
		self._test(u"in", self.word1, "wrong")

	def testMultipleRightAnswers(self):
		self._test(u"in, tijdens, bij", self.word1, "right")

	def testWrongAnswersNextToRightOnes(self):
		#opp != op
		self._test(u"in, tijdens, opp", self.word1, "wrong")

	def testSingleWrongAnswer(self):
		self._test(u"opp", self.word1, "wrong")

	def testEmptyAnswer(self):
		self._test(u"", self.word1, "wrong")

	def testFullAnswer(self):
		self._test(u"1. in, op, bij 2. tijdens", self.word1, "right")

	def testFullAnswerWithExtraWrongWords(self):
		#gelijk tijdig met isn't in the answers (however it's possibly right.)
		self._test(u"1. in, op, bij 2. tijdens, gelijktijdig met", self.word1, "wrong")

	def testWordsInWeirdOrder(self):
		self._test(u"naar(binnen), jegens, tot", self.word2, "right")
	
	def testFullNotationAndDontIncludeAnNonObligatoryWord(self):
		self._test(u"1. in, naar(binnen) 2. jegens", self.word2, "right")

	def _test(self, givenAnswer, word, output):
		for module in self._mm.mods("active", type="wordsStringChecker"):
			result = module.check(givenAnswer, word)
			self.assertEqual(result, output)

	def tearDown(self):
		del self.word1
		del self.word2
		for module in self._mm.mods("active", type="wordsStringChecker"):
			module.disable()
		for module in self._mm.mods("active", type="wordsStringParser"):
			module.disable()

class TestModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TestModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "test"

	def enable(self):
		self.TestCase = WordsStringCheckerTestCase
		self.TestCase._mm = self._mm
		self.active = True

	def disable(self):
		self.active = False
		del self.TestCase

def init(moduleManager):
	return TestModule(moduleManager)
