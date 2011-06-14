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

class OpenTeacherSaverModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(OpenTeacherSaverModule, self).__init__(*args, **kwargs)

		self.supports = ("save", "initializing")
		self.requires = (1, 0)
		self.active = False

		self._mm = moduleManager

	def initialize(self):
		for module in self._mm.activeMods.supporting("settings"):
			module.registerModule("OpenTeacher (.ot) saver", self)

	def enable(self):
		self._pyratemp = self._mm.import_("pyratemp")
		self.saves = {"words": ["ot"]}
		self.active = True

	def disable(self):
		self.active = False
		del self._pyratemp
		del self.saves

	def save(self, type, wordList, path):
		#Copy, because we're going to modify it
		import copy
		wordList = copy.deepcopy(wordList) # the words have to be unaltered
		try:
			wordList.title
		except AttributeError:
			wordList.title = u""
		try:
			wordList.questionLanguage
		except AttributeError:
			wordList.questionLanguage = u""
		try:
			wordList.answerLanguage
		except AttributeError:
			wordList.answerLanguage = u""

		for word in wordList.words:
			#results
			word.results = {"right": 0, "wrong": 0}
			for test in wordList.tests:
				for result in test:
					if result.itemId == word.id:
						try:
							word.results[result] += 1
						except KeyError:
							pass
			#known, foreign and second
			#FIXME: choose one
			for module in self._mm.activeMods.supporting("wordsStringComposer"):
				word.known = module.compose(word.questions)
				if len(word.answers) == 1 and len(word.answers[0]) > 1:
					word.foreign = word.answers[0][0]
					word.second = module.compose([word.answers[0][1:]])
				else:
					word.foreign = module.compose(word.answers)
					word.second = None

		templatePath = self._mm.resourcePath("template.txt")
		t = self._pyratemp.Template(open(templatePath).read())
		data = {
			"wordList": wordList
		}
		content = t(**data)
		open(path, "w").write(content.encode("UTF-8"))

def init(moduleManager):
	return OpenTeacherSaverModule(moduleManager)
