#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011-2012, Marten de Vries
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

class TxtSaverModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(TxtSaverModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "save"
		self.requires = (
			self._mm.mods(type="wordsStringComposer"),
		)
		self.uses = (
			self._mm.mods(type="translator"),
		)

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self.name = "Plain text (.txt) saver"
		self.saves = {"words": ["txt"]}

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self.name
		del self.saves

	@property
	def _compose(self):
		return self._modules.default(
			"active",
			type="wordsStringComposer"
		).compose

	def save(self, type, lesson, path):		
		text = u""

		if "title" in lesson.list:
			text += lesson.list["title"] + "\n\n"
		if "questionLanguage" in lesson.list and "answerLanguage" in lesson.list:
			text += lesson.list["questionLanguage"] + " - " + lesson.list["answerLanguage"] + "\n\n"

		if len(lesson.list["items"]) != 0:
			#FIXME: questions -> not guaranteed to be there
			lengths = map(lambda word: len(self._compose(word["questions"])), lesson.list["items"])
			maxLen = max(lengths) +1
			#FIXME: should 8 be an advanced setting?
			if maxLen < 8:
				maxLen = 8

			for word in lesson.list["items"]:
				try:
					questions = self._compose(word["questions"])
				except KeyError:
					questions = u""
				text += u"".join([
					questions,
					(maxLen - len(questions)) * " ",
					#FIXME: answers -> not guaranteed to be there
					self._compose(word["answers"]),
					u"\n"
				])

		open(path, "w").write(text.encode("UTF-8"))

def init(moduleManager):
	return TxtSaverModule(moduleManager)
