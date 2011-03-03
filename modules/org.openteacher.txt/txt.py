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

class Exporter(object):
	def __init__(self, manager):
		self.manager = manager
		self.exports = {"words": ["txt"]}

	def __call__(self, type, list, path):
		text = u""

		if list.title:
			text += list.title + "\n\n"
		if list.questionSubject and list.answerSubject:
			text += list.questionSubject + " - " + list.answerSubject + "\n\n"

		if len(list) != 0:
			lengths = map(lambda x: len(u", ".join(x.questions)) +1, list)
			maxLen = max(lengths) +1
			if maxLen < 8:
				maxLen = 8

			for word in list:
				questions = u", ".join(word.questions)
				answers = u", ".join(word.answers)
				text += "%s%s %s\n" % (
					questions,
					(maxLen - len(questions)) * " ",
					answers
				)

		open(path, "w").write(text.encode("UTF-8"))

class TxtFileModule(object):
	def __init__(self, manager):
		self.manager = manager
		
		self.supports = ("state", "export")

	def enable(self):
		self.exporter = Exporter(self.manager)

	def disable(self):
		del self.exporter

def init(manager):
	return TxtFileModule(manager)
