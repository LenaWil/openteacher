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

import datetime

class WrtsSaverModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(WrtsSaverModule, self).__init__(*args, **kwargs)

		self._mm = moduleManager
		self.type = "save"
		self.priorities = {
			"student@home": 532,
			"student@school": 532,
			"teacher": 532,
			"wordsonly": 532,
			"selfstudy": 532,
			"testsuite": 532,
			"codedocumentation": 532,
			"all": 532,
		}
		self.uses = (
			self._mm.mods(type="translator"),
		)
		self.requires = (
			self._mm.mods(type="wordsStringComposer"),
		)

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self.name = "WRDS"
		self._pyratemp = self._mm.import_("pyratemp")
		self.saves = {"words": ["wrts"]}

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self.name
		del self._pyratemp
		del self.saves

	@property
	def _compose(self):
		return self._modules.default(
			"active",
			type="wordsStringComposer"
		).compose

	def save(self, type, lesson, path):
		class EvalPseudoSandbox(self._pyratemp.EvalPseudoSandbox):
			def __init__(self2, *args, **kwargs):
				self._pyratemp.EvalPseudoSandbox.__init__(self2, *args, **kwargs)

				self2.register("compose", self._compose)

		templatePath = self._mm.resourcePath("template.xml")
		t = self._pyratemp.Template(
			open(templatePath).read(),
			eval_class=EvalPseudoSandbox
		)

		data = {
			"list": lesson.list,
			"date": datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z").strip() #FIXME: not datetime.now(), but the real ones!
		}
		content = t(**data)
		open(path, "w").write(content.encode("UTF-8"))

def init(moduleManager):
	return WrtsSaverModule(moduleManager)
