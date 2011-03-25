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
	from elementTree import ElementTree
except ImportError:
	from xml.etree import ElementTree

class List(list): pass

class Item(object):
	def __init__(self):
		self.questions = []
		self.answers = []

class Teach2000FileModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(Teach2000FileModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.supports = ("load", "save", "initializing")
		self.requires = (1, 0)
		self.active = False

	def initialize(self):
		for module in self._mm.activeMods.supporting("settings"):
			module.registerModule("Teach2000 file type", self)

	def enable(self):
		self._pyratemp = self._mm.import_(__file__, "pyratemp")

		self.saves = {"words": ["t2k"]}
		self.loads = {"t2k": ["words"]}
		self.active = True

	def disable(self):
		del self._pyratemp

		del self.saves
		del self.loads
		self.active = False

	def getFileTypeOf(self, path):
		if path.endswith(".t2k"):
			return "words"

	def load(self, path):
		root = ElementTree.parse(open(path)).getroot()

		list = List()

		list.title = u""
		list.questionSubject = u""
		list.answerSubject = u""
		
		for item in root.findall("message_data/items/item"):
			listItem = Item()
			for question in item.findall("questions/question"):
				listItem.questions.append(question.text)

			for answer in item.findall("answers/answer"):
				listItem.answers.append(answer.text)

			list.append(listItem)
		return list

	def save(self, type, list, path):
		templatePath = self._mm.resourcePath(__file__, "template.txt")
		t = self._pyratemp.Template(open(templatePath).read())
		data = {
			"list": list
		}
		content = t(**data)
		open(path, "w").write(content.encode("UTF-8"))

def init(manager):
	return Teach2000FileModule(manager)
