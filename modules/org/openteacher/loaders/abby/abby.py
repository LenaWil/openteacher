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
import locale
import datetime

class AbbyLoaderModule(object):
	"""Loads ABBY Lingvo Tutor files (.xml)"""

	def __init__(self, moduleManager, *args, **kwargs):
		super(AbbyLoaderModule, self).__init__(*args, **kwargs)
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
		self.filesWithTranslations = ("abby.py",)

	def _retranslate(self):
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)
		#TRANSLATORS: This is the name of a file format OT can read.
		self.name = _("ABBY Lingvo Tutor")

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

		self.loads = {"xml": ["words"]}

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self.name
		del self.loads

	def getFileTypeOf(self, path):
		if path.endswith(".xml"):
			return "words"

	def load(self, path):
		wsp = self._modules.default("active", type="wordsStringParser")

		root = ElementTree.parse(open(path)).getroot()

		wordList = {
			"items": list(),
			"title": root.get("title", u""),
		}

		for wordTree in root.findall("card"):
			word = {
				"id": int(wordTree.find("./word").get("wordId")),
				"questions": wsp.parse(wordTree.findtext("word")),
				"answers": [[a.text for a in wordTree.findall("meanings/meaning/translations/word")]],
			}
			wordList["items"].append(word)

		return {
			"resources": {},
			"list": wordList,
		}

def init(moduleManager):
	return AbbyLoaderModule(moduleManager)
