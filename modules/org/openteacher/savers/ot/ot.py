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

import copy

class OpenTeacherSaverModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(OpenTeacherSaverModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "save"

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self._modules.registerModule("OpenTeacher (.ot) saver", self)
		self._pyratemp = self._mm.import_("pyratemp")
		self.saves = {"words": ["ot"]}

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self._pyratemp
		del self.saves

	def save(self, type, wordList, path):
		composers = set(self._mm.mods("active", type="wordsStringComposer"))
		compose = self._modules.chooseItem(composers).compose

		#Copy, because we're going to modify it
		wordList = copy.deepcopy(wordList) # the words have to be unaltered

		for word in wordList["items"]:
			#results
			word["results"] = {"right": 0, "wrong": 0}
			for test in wordList["tests"]:
				for result in test:
					if result["itemId"] == word["id"]:
						try:
							word["results"][result] += 1
						except KeyError:
							pass
			#known, foreign and second
			try:
				word["known"] = compose(word["questions"])
			except KeyError:
				word["known"] = u""
			try:
				if len(word["answers"]) == 1 and len(word["answers"][0]) > 1:
					word["foreign"] = word["answers"][0][0]
					word["second"] = compose([word["answers"][0][1:]])
				else:
					word["foreign"] = compose(word["answers"])
					word["second"] = u""
			except KeyError:
				word["foreign"] = u""
				word["second"] = u""

		templatePath = self._mm.resourcePath("template.xml")
		t = self._pyratemp.Template(open(templatePath).read())
		data = {
			"wordList": wordList
		}
		content = t(**data)
		open(path, "w").write(content.encode("UTF-8"))

def init(moduleManager):
	return OpenTeacherSaverModule(moduleManager)
