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

		self.questions = []
		self.answers = []

class Test(list):
	pass

class Result(str):
	pass

class OpenTeacherLoaderModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(OpenTeacherLoaderModule, self).__init__(*args, **kwargs)
		self.supports = ("load", "initializing")
		self.requires = (1, 0)
		self.active = False

		self._mm = moduleManager

	def initialize(self):
		for module in self._mm.activeMods.supporting("modules"):
			module.registerModule("OpenTeacher (.ot) loader", self)

	def enable(self):
		self.loads = {"ot": ["words"]}
		self.active = True

	def disable(self):
		self.active = False
		del self.loads

	def getFileTypeOf(self, path):
		if path.endswith(".ot"):
			return "words"

	def load(self, path):
		#Create the new word list
		wordList = WordList()
		#Feed the xml parser
		root = ElementTree.parse(open(path)).getroot()

		#Stores the title, question language and answer language
		wordList.title = root.findtext("title")
		wordList.questionLanguage = root.findtext("question_language")
		wordList.answerLanguage = root.findtext("answer_language")

		#create one test, which is used for all results, because .ot
		#doesn't support multiple tests.
		test = Test()

		#because .ot doesn't give words an id, we use a counter.
		counter = 0
		for treeWord in root.findall("word"):
			#Creates the word and sets its id (which is the current
			#value of the counter)
			listWord = Word()
			listWord.id = counter

			#Parses the question
			known = treeWord.findtext("known")
			#FIXME: choose one
			for module in self._mm.activeMods.supporting("wordsStringParser"):
				listWord.questions = module.parse(known)

			#Parses the answers
			second = treeWord.findtext("second")
			if second is not None:
				foreign = treeWord.findtext("foreign") + ", " + second
			else:
				foreign = treeWord.findtext("foreign")
			#remove so the test is also reliable the next time
			del second
			for module in self._mm.activeMods.supporting("wordsStringParser"):
				listWord.answers = module.parse(foreign)

			#Parses the results, all are saved in the test made above.
			wrong, total = treeWord.findtext("results").split("/")
			wrong = int(wrong)
			total = int(total)
			right = total - wrong
			for i in range(right):
				result = Result("right")
				result.itemId = listWord.id
				test.append(result)
			for i in range(wrong):
				result = Result("wrong")
				result.itemId = listWord.id
				test.append(result)

			#Adds the generated word to the list
			wordList.words.append(listWord)
			#Increment the counter (= the next word id)
			counter += 1

		#Adds all results to the list
		wordList.tests.append(test)

		return wordList

def init(moduleManager):
	return OpenTeacherLoaderModule(moduleManager)
