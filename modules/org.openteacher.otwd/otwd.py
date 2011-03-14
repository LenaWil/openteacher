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
	def __init__(self, *args, **kwargs):
		super(Item, self).__init__(*args, **kwargs)
		self.questions = []
		self.answers = []

class Importer(object):
	def __init__(self, manager, *args, **kwargs):
		super(Importer, self).__init__(*args, **kwargs)
		self.manager = manager
		self.imports = {"otwd": ["words"]}

	def getFileTypeOf(self, path):
		if path.endswith(".otwd"):
			return "words"

	def __call__(self, path):
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

class Exporter(object):
	def __init__(self, manager, *args, **kwargs):
		super(Exporter, self).__init__(*args, **kwargs)
		self.manager = manager
		self._pyratemp = self.manager.import_(__file__, "pyratemp")
		self.exports = {"words": ["otwd"]}

	def __call__(self, type, list, path):
		templatePath = self.manager.resourcePath(__file__, "index.xml")
		t = self._pyratemp.Template(open(templatePath).read())
		data = {
			"list": list
		}
		content = t(**data)
		print content.encode("UTF-8")

class OpenTeachingWordsFileModule(object):
	def __init__(self, manager, *args, **kwargs):
		super(OpenTeachingWordsFileModule, self).__init__(*args, **kwargs)
		self.manager = manager
		self.supports = ("state", "import", "export")

	def enable(self):
		self.importer = Importer(self.manager)
		self.exporter = Exporter(self.manager)

	def disable(self):
		del self.importer
		del self.exporter

def init(manager):
	return OpenTeachingWordsFileModule(manager)
