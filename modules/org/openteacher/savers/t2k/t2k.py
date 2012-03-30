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

class Teach2000SaverModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(Teach2000SaverModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.type = "save"
		self.priorities = {
			"student@home": 448,
			"student@school": 448,
			"teacher": 448,
			"wordsonly": 448,
			"selfstudy": 448,
			"testsuite": 448,
			"codedocumentation": 448,
			"all": 448,
		}
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.filesWithTranslations = ("t2k.py",)

	def _retranslate(self):
		try:
			translator = self._modules.default("active", type="translator")
		except IndexError:
			_, ngettext = unicode, lambda a, b, n: a if n == 1 else b
		else:
			_, ngettext = translator.gettextFunctions(
				self._mm.resourcePath("translations")
			)
		#TRANSLATORS: This is the name of an application. For more info
		#about Teach2000: http://www.teach2000.org/
		self.name = _("Teach2000")

	def enable(self):
		self._modules = set(self._mm.mods(type="modules")).pop()
		self._pyratemp = self._mm.import_("pyratemp")
		self.saves = {"words": ["t2k"]}

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

		del self._pyratemp
		del self.name
		del self.saves

	def save(self, type, lesson, path):
		templatePath = self._mm.resourcePath("template.xml")
		t = self._pyratemp.Template(open(templatePath).read())
		data = {
			"wordList": lesson.list
		}
		content = t(**data)
		with open(path, "w") as f:
			f.write(content.encode("UTF-8"))

		lesson.path = None

def init(moduleManager):
	return Teach2000SaverModule(moduleManager)
