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

try:
	from lxml import etree as ElementTree
except ImportError:
	try:
		from xml.etree import ElementTree
	except ImportError:
		from elementTree import ElementTree

class WordList(object):
	def __init__(self, *args, **kwargs):
		super(WordList, self).__init__(*args, **kwargs)

		self.words = []
		self.tests = []

class Word(object):
	def __init__(self, *args, **kwargs):
		super(Word, self).__init__(*args, **kwargs)

		self.questions = [[]]
		self.answers = [[]]

class Test(object): pass #FIXME: stub
class Result(str): pass #FIXME: stub

class Teach2000LoaderModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(Teach2000LoaderModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.supports = ("load", "initializing")
		self.requires = (1, 0)
		self.active = False

	def initialize(self):
		for module in self._mm.activeMods.supporting("settings"):
			module.registerModule("Teach2000 (.t2k) loader", self)

	def enable(self):
		self.loads = {"t2k": ["words"]}
		self.active = True

	def disable(self):
		del self.loads
		self.active = False

	def getFileTypeOf(self, path):
		if path.endswith(".t2k"):
			return "words" #FIXME: .t2k can contain more types

	def load(self, path):
		root = ElementTree.parse(open(path)).getroot()
		wordList = WordList()

		for item in root.findall("message_data/items/item"):
			word = Word()
			word.id = int(item.get("id"))
			for question in item.findall("questions/question"):
				word.questions[0].append(question.text)

			for answer in item.findall("answers/answer"):
				word.answers[0].append(answer.text)

			wordList.words.append(word)
			#FIXME: load tests, also results in the words!
		return wordList

def init(manager):
	return Teach2000LoaderModule(manager)
