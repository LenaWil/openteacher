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

class TxtFileModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TxtFileModule, self).__init__(*args, **kwargs)

		self.supports = ("save", "initializing")
		self.requires = (1, 0)
		self.active = False
		self._mm = moduleManager

	def initialize(self):
		for module in self._mm.activeMods.supporting("settings"):
			module.registerModule("Plain text file type", self)

	def enable(self):
		self.saves = {"words": ["txt"]}
		self.active = True

	def disable(self):
		self.active = False
		del self.saves

	def save(self, type, list, path):
		def exists(obj, attr):
			return hasattr(obj, attr) and getattr(obj, attr)

		text = u""

		if exists(list, "title"):
			text += list.title + "\n\n"
		if exists(list, "questionLanguage") and exists(list, "answerLanguage"):
			text += list.questionLanguage + " - " + list.answerLanguage + "\n\n"

		if len(list.words) != 0:
			#FIXME: choose one
			for module in self._mm.activeMods.supporting("wordsStringComposer"):
				lengths = map(lambda x: len(module.compose(x.questions)) +1, list.words)
				maxLen = max(lengths) +1
			if maxLen < 8:
				maxLen = 8

			for word in list.words:
				#FIXME: choose one
				for module in self._mm.activeMods.supporting("wordsStringComposer"):
					questions = module.compose(word.questions)
					answers = module.compose(word.answers)
				text += "%s%s %s\n" % (
					questions,
					(maxLen - len(questions)) * " ",
					answers
				)

		open(path, "w").write(text.encode("UTF-8"))

def init(moduleManager):
	return TxtFileModule(moduleManager)
