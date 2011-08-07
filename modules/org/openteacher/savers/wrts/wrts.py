#! /usr/bin/env python
# -*- coding: utf-8 -*-

#	Copyright 2011, Marten de Vries
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

	def enable(self):
		self._modules = set(self._mm.mods("active", type="modules")).pop()
		self._modules.registerModule("WRTS (.wrts) saver", self)
		self._pyratemp = self._mm.import_("pyratemp")
		self.saves = {"words": ["wrts"]}

		self.active = True

	def disable(self):
		self.active = False

		del self._modules
		del self._pyratemp
		del self.saves

	def save(self, type, list, path, resources):
		composers = set(self._mm.mods("active", type="wordsStringComposer"))
		composer = self._modules.chooseItem(composers)

		class EvalPseudoSandbox(self._pyratemp.EvalPseudoSandbox):
			def __init__(self2, *args, **kwargs):
				self._pyratemp.EvalPseudoSandbox.__init__(self2, *args, **kwargs)

				self2.register("compose", composer.compose)

		templatePath = self._mm.resourcePath("template.xml")
		t = self._pyratemp.Template(
			open(templatePath).read(),
			eval_class=EvalPseudoSandbox
		)

		data = {
			"list": list,
			"date": datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z").strip() #FIXME: not datetime.now(), but the real ones!
		}
		content = t(**data)
		open(path, "w").write(content.encode("UTF-8"))

def init(moduleManager):
	return WrtsSaverModule(moduleManager)
