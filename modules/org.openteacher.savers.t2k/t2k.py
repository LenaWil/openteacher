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

class Teach2000SaverModule(object):
	def __init__(self, moduleManager, *args, **kwargs):
		super(Teach2000SaverModule, self).__init__(*args, **kwargs)
		self._mm = moduleManager

		self.supports = ("save", "initializing")
		self.requires = (1, 0)
		self.active = False

	def initialize(self):
		for module in self._mm.activeMods.supporting("settings"):
			module.registerModule("Teach2000 (.t2k) saver", self)

	def enable(self):
		self._pyratemp = self._mm.import_("pyratemp")
		self.saves = {"words": ["t2k"]}
		self.active = True

	def disable(self):
		del self._pyratemp
		del self.saves
		self.active = False

	def save(self, type, list, path):
		templatePath = self._mm.resourcePath("template.txt")
		t = self._pyratemp.Template(open(templatePath).read())
		data = {
			"wordList": list
		}
		content = t(**data)
		open(path, "w").write(content.encode("UTF-8"))

def init(manager):
	return Teach2000SaverModule(manager)
