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

class WrtsLoaderModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(WrtsLoaderModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "load"

	def enable(self):
		for module in self._mm.mods("active", type="modules"):
			module.registerModule("WRTS (.wrts) loader", self)

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

		wordList = {
			"items": list(),
			"tests": list(),
			"title": unicode(),
			"questionLanguage": unicode(),
			"answerLanguage": unicode()
		}

		#dutch: titel = title
		wordList["title"] = listTree.findtext("titel")
		#dutch: taal = language
		wordList["questionLanguage"] = listTree.findtext("taal/a")
		wordList["answerLanguage"] = listTree.findtext("taal/b")

		#counter is used as word id
		counter = 1

		#dutch: woord = word
		for wordTree in listTree.findall("woord"):
			word = {
				"id": int(),
				"questions": list(),
				"answers": list(),
				"comment": unicode()
			}
			word["id"] = counter

			#FIXME: choose one! Also check if other modules do this...
			for module in self._mm.mods("active", type="wordsStringParser"):
				word["questions"] = module.parse(wordTree.findtext("a"))
				word["answers"] = module.parse(wordTree.findtext("b"))

			wordList["items"].append(word)
			
			counter += 1

		return wordList

def init(moduleManager):
	return WrtsLoaderModule(moduleManager)
