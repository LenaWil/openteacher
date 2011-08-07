#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Marten de Vries
#	Copyright 2011, Milan Boers
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

class Teach2000LoaderModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(Teach2000LoaderModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "load"

	def enable(self):
		for module in self._mm.mods("active", type="modules"):
			module.registerModule("Teach2000 (.t2k) loader", self)

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
		wordList = {
			"items": list(),
			"tests": list(),
			"title": unicode(),
			"questionLanguage": unicode(),
			"answerLanguage": unicode()
		}

		for item in root.findall("message_data/items/item"):
			word = {
				"id": int(),
				"questions": list(),
				"answers": list(),
				"comment": unicode()
			}
			word["id"] = int(item.get("id"))
			for question in item.findall("questions/question"):
				word["questions"].append(question.text)

			for answer in item.findall("answers/answer"):
				word["answers"].append(answer.text)

			wordList["items"].append(word)
			#FIXME: load tests, also results in the words!
		return wordList

def init(manager):
	return Teach2000LoaderModule(manager)
