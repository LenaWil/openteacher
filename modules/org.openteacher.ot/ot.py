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

class OpenTeacherFileModule(object):
	def __init__(self, moduleManager):
		self.supports = ("load", "save", "initializing")
		self.requires = (1, 0)
		self.active = False

		self._mm = moduleManager

	def initialize(self):
		for module in self._mm.activeMods.supporting("settings"):
			module.registerModule("OpenTeacher file type", self)

	def enable(self):
		self._pyratemp = self._mm.import_(__file__, "pyratemp")
		self.loads = {"ot": ["words"]}
		self.saves = {"words": ["ot"]}
		self.active = True

	def disable(self):
		self.active = False
		del self._pyratemp
		del self.loads
		del self.saves

	def getFileTypeOf(self, path):
		if path.endswith(".ot"):
			return "words"

	def load(self, path):
		list = List()

		root = ElementTree.parse(open(path)).getroot()

		list.title = root.findtext("title")
		list.questionSubject = root.findtext("question_language")
		list.answerSubject = root.findtext("answer_language")

		for treeItem in root.findall("word"):
			listItem = Item()

			known = treeItem.findtext("known")
			if known.find(",") != -1:
				listItem.questions = known.split(",")
			else:
				listItem.questions = known.split(";")

			listItem.answers.append(treeItem.findtext("foreign"))
			second = treeItem.findtext("second")
			if second is not None:
				if second.find(",") != -1:
					listItem.answers += second.split(",")
				else:
					listItem.answers += second.split(";")

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

def init(moduleManager):
	return OpenTeacherFileModule(moduleManager)
