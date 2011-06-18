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

		self.items = []
		self.tests = []

class Word(object):
	def __init__(self, *args, **kwargs):
		super(Word, self).__init__(*args, **kwargs)

		self.questions = []
		self.answers = []

class WrtsLoaderModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(WrtsLoaderModule, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		self.supports = ("load", "initializing")
		self.requires = (1, 0)

	def initialize(self):
		for module in self._mm.activeMods.supporting("modules"):
			module.registerModule("WRTS (.wrts) loader", self)

	def enable(self):
		self.loads = {"wrts": ["words"]}
		self.active = True

	def disable(self):
		self.active = False
		del self.loads

	def getFileTypeOf(self, path):
		if path.endswith(".wrts"):
			return "words"

	def load(self, path):
		root = ElementTree.parse(open(path)).getroot()
		#dutch: lijst = list
		listTree = root.find("lijst")

		wordList = WordList()

		#dutch: titel = title
		wordList.title = listTree.findtext("titel")
		#dutch: taal = language
		wordList.questionLanguage = listTree.findtext("taal/a")
		wordList.answerLanguage = listTree.findtext("taal/b")

		#counter is used as word id
		counter = 1

		#dutch: woord = word
		for wordTree in listTree.findall("woord"):
			word = Word()
			word.id = counter

			for module in self._mm.activeMods.supporting("wordsStringParser"):
				word.questions = module.parse(wordTree.findtext("a"))
				word.answers = module.parse(wordTree.findtext("b"))

			wordList.items.append(word)
			
			counter += 1

		return wordList

def init(moduleManager):
	return WrtsLoaderModule(moduleManager)
