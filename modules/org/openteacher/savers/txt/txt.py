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
		self.priorities = {
			"student@home": 924,
			"student@school": 924,
			"teacher": 924,
			"wordsonly": 924,
			"selfstudy": 924,
			"testsuite": 924,
			"codedocumentation": 924,
			"all": 924,
		}
		self.requires = (
			self._mm.mods(type="wordsStringComposer"),
		)
		self.uses = (
			self._mm.mods(type="translator"),
			self._mm.mods(type="settings"),
		)
		self.filesWithTranslations = ("txt.py",)

	def _retranslate(self):
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)
		self.name = _("Plain text")
		self._maxLenSetting.update({
				"name": _("Minimum amount of spaces between words"),
				"category": _("Input and output"),
				"subcategory": _(".txt saving"),
		})

	def enable(self):
		#Translations
		self._modules = set(self._mm.mods(type="modules")).pop()
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)

		self.saves = {"words": ["txt"]}

		try:
			self._settings = self._modules.default(type="settings")
		except IndexError, e:
			self._maxLenSetting = dict()
			self._maxLenSetting["value"] = 8
		else:
			self._maxLenSetting = self._settings.registerSetting(**{
				"internal_name": "org.openteacher.savers.txt.maxLen",
				"type": "number",
				"defaultValue":8,
				"minValue": 0,
				"advanced": True,
			})

		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			pass
		else:
			translator.languageChanged.handle(self._retranslate)
		self._retranslate()

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

		def getQuestionLength(word):
			if "questions" in word:
				return len(self._compose(word["questions"]))
			else:
				return 0

		if len(lesson.list["items"]) != 0:
			lengths = map(getQuestionLength, lesson.list["items"])
			maxLen = max(lengths) + 1
			if maxLen < self._maxLenSetting["value"]:
				maxLen = 8

			for word in lesson.list["items"]:
				try:
					questions = self._compose(word["questions"])
				except KeyError:
					questions = u""
				text += u"".join([
					questions,
					(maxLen - len(questions)) * " ",
					self._compose(word["answers"]) if "answers" in word else u"",
					u"\n"
				])

		with open(path, "w") as f:
			f.write(text.encode("UTF-8"))

		lesson.path = None

def init(moduleManager):
	return TxtSaverModule(moduleManager)
