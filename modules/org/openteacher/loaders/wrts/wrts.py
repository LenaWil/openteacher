#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011-2012, Marten de Vries
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
		self.priorities = {
			"student@home": 756,
			"student@school": 756,
			"teacher": 756,
			"wordsonly": 756,
			"selfstudy": 756,
			"testsuite": 756,
			"codedocumentation": 756,
			"all": 756,
		}
		
		self.requires = (
			self._mm.mods(type="wordsStringParser"),
		)
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.filesWithTranslations = ("wrts.py",)

	def _retranslate(self):
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)
		self.name = _("WRDS")

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		self.loads = {"wrts": ["words"]}

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self.name
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

			wsp = self._modules.default("active", type="wordsStringParser")
			word["questions"] = wsp.parse(wordTree.findtext("a"))
			word["answers"] = wsp.parse(wordTree.findtext("b"))

			wordList["items"].append(word)

			counter += 1

		return {
			"resources": {},
			"list": wordList,
		}

def init(moduleManager):
	return WrtsLoaderModule(moduleManager)
